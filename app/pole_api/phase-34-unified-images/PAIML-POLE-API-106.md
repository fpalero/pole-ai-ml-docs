# Ticket: PAIML-POLE-API-106

## Title
Unified image endpoint via path-hash — fix RAG image 404s (`rag-images` db-scoped routes cannot serve real Chroma paths)

## Description
Phase 34 — staging-verified root cause of empty RAG image cards in the
analyst chatbot.

**Problem:** RAG answers that cite book figures render as `[]` in the FE.
The backend emits the image block, then strips it before it reaches the
client, so the user sees prose with no figure.

**Failure chain (verified on staging `ipsf-server`, namespace `pole-ai`):**

1. Chroma `image_path` metadata = `data/_OceanofPDF.../file-0343-04.png`
   (relative path, no db segment).
2. Formatter `pole_coach/nodes/formatter.py:119` copies the raw path
   verbatim into the image block `src`.
3. The serving endpoint `src/analyst_chatbot/rag_images.py` only resolves
   `<data_dir>/<db>/<file>` with `db ∈ (pole, calisthenics, psychology,
   biomechanics)` — but the real files live under
   `/data/rag/_OceanofPDF.../`, outside every db directory.
4. The LLM hallucinates `/api/rag-images/data/...` (`db=data` is invalid)
   → 404.
5. `_coerce_image_block` drops any `/data` src as a server-path leak; the
   sanitizer logs `server path leak after sanitize; scrubbing`.
6. FE receives zero image blocks → renders `[]`.

**Approved fix (user-approved):** a single unified endpoint

```text
GET /api/images/{hash}?token=<chat-token>
```

- `hash = sha256(root_id:relative_path)[:32]`, registered at startup /
  on demand from `ALLOWED_ROOTS = [/data/rag, /data/uploads,
  /data/analysis_uploads]`.
- Registry is in-memory + Redis (shared across replicas).
- Old `rag-images` routes stay as `301` redirects for one release, then
  removed.

## Evidence (staging log excerpts)

```text
# Chroma metadata returned to the formatter
image_path = "data/_OceanofPDF.../file-0343-04.png"

# Formatter passes the raw path through as src
# pole_coach/nodes/formatter.py:119  src = image_path  (no URL mapping)

# LLM-fabricated URL (no such route — db must be pole|calisthenics|psychology|biomechanics)
GET /api/rag-images/data/...  → 404  (db=data invalid)

# Sanitizer drops the block before WS emit
server path leak after sanitize; scrubbing

# FE result
blocks: []   # image card missing
```

```text
# Filesystem truth (inside the API pod)
ls /data/rag/_OceanofPDF.../file-0343-04.png   # EXISTS
ls /data/rag/data/...                          # NOT FOUND (hallucinated prefix)
ls /data/rag/<db>/file-0343-04.png             # NOT FOUND (no db segment on disk)
```

## Root Cause
Contract mismatch between three layers that never agreed on what an
image `src` is:

| Layer | Assumes `src` is | Reality |
| :--- | :--- | :--- |
| Chroma metadata | relative fs path (`data/...`) | correct at index time, unresolvable at serve time |
| `formatter.py:119` | opaque string, copied verbatim | leaks server paths into blocks |
| `rag_images.py` | `<data_dir>/<db>/<file>`, db allow-listed | real files live outside all db dirs |
| LLM | guesses `/api/rag-images/data/...` | `db=data` invalid → 404 |
| `_coerce_image_block` + sanitizer | drops `/data` srcs (path-leak guard) | correct guard, wrong fix point — drops the only locator |

No single layer is "broken" in isolation; the addressing scheme itself
(fs paths as public URLs + db-scoped routes over non-db files) cannot
work. Hence a new addressing scheme (opaque hash) instead of another
patch to the route regex.

## Architectural Decisions (ADRs)

### ADR-1 — WHY hash-by-path (`sha256(root_id:relative_path)[:32]`)
- **Context:** `src` must be opaque (no server paths leak to the client),
  stable across restarts (LLM-cached answers, FE caches), and unique
  across roots (`/data/uploads/foo.png` vs `/data/rag/foo.png` must not
  collide).
- **Decision:** hash over `root_id + relative_path`, truncated to 32 hex
  chars (128-bit — collision-infeasible for this corpus, short URLs).
- **Alternatives considered:**
  - *Signed absolute paths* — rejected: reintroduces path disclosure, ugly
    URLs, signing-key rotation invalidates caches.
  - *DB auto-increment id* — rejected: requires a migration + backfill of
    every Chroma record; hash registry can be rebuilt by scanning roots.
  - *Content hash (sha of bytes)* — rejected: re-hashing GBs of `/data/rag`
    at startup is slow; path-hash is O(filenames). Content addressing can
    be layered later without changing the route.
- **Consequence:** registry must map hash → absolute path at serve time;
  renames/moves invalidate old hashes (acceptable: re-index emits new
  hashes; old URLs 404 with a clear error, same as any CMS).

### ADR-2 — WHY Redis + in-memory two-level registry
- **Context:** API runs multi-replica on k8s; a pure in-memory map
  diverges per pod (hash registered on pod A 404s on pod B). A pure-Redis
  lookup adds ~1ms per image — fine, but wasteful for hot book figures.
- **Decision:** L1 in-process dict (hot, no TTL) + L2 Redis hash
  (`images:registry`, no TTL — entries are content-addressed and tiny).
  Miss in L1 → check L2 → on total miss, attempt on-demand registration
  by scanning `ALLOWED_ROOTS` for the relative path (bounded, single-file
  lookup, not a full rescan).
- **Alternatives considered:**
  - *In-memory only + sticky sessions* — rejected: breaks under rolling
    deploys and HPA scale-out.
  - *Postgres table* — rejected: new migration + connection for a
    key→path map Redis already covers; no relational queries needed.
- **Consequence:** Redis becomes a hard dependency of the image path
  (already required by the stack — `core/config.py`); startup must warm
  L1 from L2, and L2 from a root scan when empty (cold-start bound: number
  of files, filenames only).

### ADR-3 — WHY keep old routes as 301 for one release
- **Context:** FE versions in the wild and cached LLM answers still emit
  `/api/rag-images/<db>/<file>` URLs.
- **Decision:** old routes return `301` → `/api/images/{hash}` (resolved
  via registry; unknown → `410 Gone` with JSON body, not 404-html) for
  exactly one release, then deleted. Sunset logged (`Deprecation` header
  + server log counter) so removal is evidence-based.
- **Alternatives considered:**
  - *Remove immediately* — rejected: breaks shipped FE during rolling
    upgrade.
  - *Keep forever* — rejected: preserves the unfixable db-scoped scheme
    and its allow-list maintenance.
- **Consequence:** implementer adds a sunset test that fails after the
  removal release (forces the cleanup ticket).

## What to Do (Implementation Steps)
- [ ] (1) New router `src/analyst_chatbot/images.py` (or extend
  `rag_images.py`): `GET /api/images/{hash}?token=` — validate chat
  token (same seam as existing image routes), look up L1 → L2 →
  on-demand register, serve bytes with `Content-Type` sniffed from suffix
  (+ `Cache-Control: public, max-age=86400, immutable`,
  `Deprecation` header on the legacy routes only).
- [ ] (2) Registry module (`register(root_id, relpath) → hash`,
  `resolve(hash) → abspath | None`, `warm()` at startup): scan
  `ALLOWED_ROOTS` (`/data/rag`, `/data/uploads`, `/data/analysis_uploads`,
  env-overridable, fail-closed on traversal: `resolve()` rejects `..` and
  symlinks escaping the root).
- [ ] (3) Formatter change (`pole_coach/nodes/formatter.py:119`): emit
  `src = /api/images/{hash}` (register on the fly), never the raw path.
  Keep the `/data`-strip guard + sanitizer as defense-in-depth.
- [ ] (4) Legacy compat: old `/api/rag-images/...` routes → `301` to the
  unified URL (+ `Deprecation: true`, sunset counter); unknown hashes →
  `410` JSON `{code: "image_gone"}`.
- [ ] (5) Prompt/guard: analyst system prompt — image `src` values are
  opaque `/api/images/…` URLs; never fabricate `/api/rag-images/data/…`.
  Add a regression test asserting no `reply`/`blocks[].content` contains
  `/api/rag-images/data/`.
- [ ] (6) Tests (see below) + docs (`ENV_VARS.md`: `ALLOWED_ROOTS`,
  `IMAGES_*`; `slices.md` endpoint entry).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] **UC-01 — RAG figure renders:** a RAG answer citing
  `file-0343-04.png` emits `image.src = /api/images/{32-hex}`; `GET` with
  valid token → `200` + bytes; FE card renders (no `[]`).
- [ ] **UC-02 — no path leaks:** no `reply`/`blocks[].content`/chip string
  contains `/data/` or a raw fs path in the 40-question staging battery
  rerun; sanitizer `scrubbing` counter stays at zero for image turns.
- [ ] **UC-03 — legacy compat:** `GET /api/rag-images/pole/<file>`
  (valid token) → `301` → unified URL → `200`; unknown hash →
  `410 {code: image_gone}`; unauthenticated → `401/403` on both routes.
- [ ] **UC-04 — multi-replica:** hash registered on replica A resolves on
  replica B (Redis L2); pod restart re-warms L1 from L2 without a full
  root rescan (L2 hit logged).
- [ ] Quality gates green (see below).

## Quality Gates
- `pixi run test-api` green, coverage ≥ 80%.
- New tests in `app/pole_api/tests/test_images_unified*.py`:
  hash stability (`sha256(root:rel)[:32]` golden vector), traversal
  rejection (`..`, symlink escape), L1/L2 fallback (fake Redis), 301 +
  `Deprecation` header, 410-unknown, 401-no-token, formatter emits hash
  URLs, no-`/api/rag-images/data/` regression.
- Staging verify (ns `pole-ai`): `GET /api/images/{hash}` 200 from inside
  + outside the cluster (via ingress, with token); old route 301; rerun
  image-class questions of the chatbot battery.

## Risks and Mitigations
- **Risk:** full root scan at startup is slow (`/data/rag` is large).
  **Mitigation:** filenames-only walk, warm L1 from L2-Redis first, scan
  roots only when L2 is empty; bound + log scan time; readiness probe
  unaffected (serve from L2 while warming).
- **Risk:** stale hashes after file moves/renames. **Mitigation:**
  on-demand re-register on miss; `410 Gone` (not 404-html) with a stable
  code so the FE can hide the card gracefully; re-index emits new hashes.
- **Risk:** `ALLOWED_ROOTS` misconfiguration exposes unintended files.
  **Mitigation:** env allow-list, fail-closed (unknown root → 410),
  traversal/symlink rejection, startup log of roots, no directory
  listing route.

## Out of Scope
- Re-indexing Chroma `image_path` metadata to hashes (formatter maps at
  emit time; backfill is a separate ticket if needed).
- FE changes beyond consuming the new `src` (FE ticket if card handling
  needs work).
- Removing the legacy routes (cleanup ticket next release, enforced by
  the sunset test).

## Dependencies
- **Blocks**: —
- **Blocked By**: —

## Estimated Effort
- [M]
