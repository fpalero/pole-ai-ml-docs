# Implementation Plan — `pole-crawler` (Instagram Video Crawler)

> **Status:** Core crawler complete (InstagramClient, DiskWriter/PostMetadata, make_session,
> notifications, CLI main). Consumed by `pola_api` crawler slice. Future work: resilient download
> resume, better anti-bot strategy, deduplication/QC integration.
> **Source docs:** `docs/packages/pole_crawler/README.md` (CI Docker usage),
> `packages/pole-crawler/ci/Dockerfile`, `docs/app/pola_api/flows.md` UC-20..24.

---

## 1. Feature Context & Objective

- **Goal:** Download Instagram videos for a given hashtag set into `downloads/<trick>/`, writing
  `.meta.json` sidecars, with anti-bot waits between requests. Feeds the training pipeline (posts
  → QC → cut).
- **Non-Functional Constraints:** anti-bot random waits (`min_wait`/`max_wait`); session-based auth
  (env: `INSTAGRAM_*`, `SESSION_FILE_PATH`); runs headless in Docker (CI); must not hit Instagram
  rate limits (job `failed` with actionable error on rate-limit).
- **Affected Components:**
  - `packages/pole-crawler/src/pole_crawler/` — `client.py` (InstagramClient), `storage.py`
    (DiskWriter, PostMetadata), `make_session.py`, `notifications.py`.
  - `packages/pole-crawler/main.py` — CLI.
  - `packages/pole-crawler/ci/` — Dockerfile + docker-compose + downloads dir.
  - Consumer: `app/pola_api/src/crawler/` (`CrawlService`, `PostService`).
- **Assumptions:** Instagram session cookies provided via env; ffmpeg not needed here (raw
  download); `.meta.json` carries username/timestamp/caption/url.

---

## 2. Architectural Layering (The "Where")

- **Domain:** `PostMetadata` (username, timestamp, caption, url, tag, local_path).
- **Application:** `InstagramClient.get_posts` (pagination, hashtag search), `DiskWriter.save_video`
  (bytes → disk + meta sidecar), wait/backoff policy.
- **Infrastructure:** `make_session.py` (session file from env), `notifications.py` (log/notify),
  Docker CI image.
- **Presentation:** `main.py` CLI (`--tags`, `--username`, `--sort`, `--limit`, `--min-wait`,
  `--max-wait`); `pixi run crawl` / `pixi run make-session`.

---

## 3. Implementation Roadmap (Atomic Steps)

### Phase 1: Session + client — ✅ DONE
- [x] `make_session.py` — build Instagram session from env vars, persist to `SESSION_FILE_PATH`.
- [x] `InstagramClient` — hashtag search + post pagination + video download with retry/waits.

### Phase 2: Storage + CLI — ✅ DONE
- [x] `DiskWriter.save_video` + `PostMetadata` (`downloads/<tag>/<username>_<ts>_<tag>_<n>.mp4` +
  `.meta.json`).
- [x] `main.py` CLI (args above) + `notifications.py`.

### Phase 3: API integration — ✅ DONE
- [x] `pola_api` crawler slice wraps the client (`CrawlService`), persists posts in shared `videos`
  collection with `source="crawler"`, `qc_status="pending"` (UC-20..24).

### Phase 4: Future — resilience & dedup
- [ ] Application resume support for interrupted downloads (skip existing files / `.part` resume).
- [ ] Application smarter anti-bot (rotating session, exponential backoff, proxy hooks).
- [ ] Application deduplication (by media_id / shortcode) before QC.
- [ ] Tests unit/integration for storage + client with a fake HTTP session.

---

## 4. Quality Gates & Testing Commands (DoD)

- **Unit Tests:** pytest for `pole_crawler` (add if missing) — target ≥ 80%.
- **Integration Tests:** `pixi run test-api` covers crawler slice against `_testing` DB
  (UC-20..24); real IG hit not required in CI.
- **Automation:** CI Docker build (`ci/Dockerfile`) + `pixi run crawl` smoke with fake session.
- **Database Target:** `pole_api_testing.videos` (`source="crawler"`).
- **Coverage Requirement:** ≥ 80% (workspace default).
- **Additional Checks:** no real downloads during tests (mocked InstagramClient); `.env` never committed.

---

## 5. Defined Use Cases (Gherkin + Technical Matrix)

### UC-CR-01: Crawl a class hashtag set
- **Given** valid Instagram session env vars and class `handspring` exists
- **When** user runs `pixi run crawl --tags handspring,pole --username ... --limit 10`
- **Then** command exits 0
- **And** filesystem `downloads/handspring/` has `.mp4` files with `.meta.json`; API posts `pending`

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | CLI `python main.py` (also `POST /api/crawler/classes/{id}/crawl`) |
| Request Method | CLI / POST |
| Required Headers | n/a / `Content-Type: application/json` |
| Payload Example | `--tags=handspring,pole --limit=10 --min-wait=5 --max-wait=10` |
| DB State (Before) | no posts for class |
| DB State (After) | posts `qc_status=pending`, `local_path` exists, `downloaded_count` > 0 |

### UC-CR-02: Rate-limit / anti-bot failure
- **Given** Instagram returns rate-limit (or 0 posts)
- **When** the crawl runs
- **Then** the API job ends `failed` with error (or `done` with `downloaded_count=0`)
- **And** the FE shows the crawl error and allows retry

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `POST /api/crawler/classes/{id}/crawl` |
| Request Method | POST |
| Required Headers | `Content-Type: application/json` |
| Payload Example | `{"tags":["handspring"],"limit":10,"min_wait":5,"max_wait":10}` |
| DB State (Before) | no crawls |
| DB State (After) | crawl `failed`/`done(0)`; retry allowed |

### UC-CR-03: QC a post (accept/reject)
- **Given** a `pending` post exists for a class
- **When** user submits `POST /api/crawler/posts/{id}/qc` with `{"status":"accepted"}`
- **Then** system returns HTTP `200`
- **And** database `videos` post has `qc_status="accepted"`, enabling cut

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/crawler/posts/{id}/qc` |
| Request Method | POST |
| Required Headers | `Content-Type: application/json` |
| Payload Example | `{"status": "accepted"}` |
| DB State (Before) | post `pending` |
| DB State (After) | post `accepted`; ≥1 accepted enables cut step |

---

## 6. Risks and Mitigations

- **Risk:** Instagram blocks or rate-limits the session. **Mitigation:** random waits, clear error
  surfaced to jobs, retry possible; CI uses fake session for tests.
- **Risk:** session cookies expire. **Mitigation:** `make_session` + `SESSION_FILE_PATH`; document
  refresh flow.
- **Risk:** large download volume (≈2.5 GB data dir). **Mitigation:** ignored in git; per-class
  dirs; resume strategy in Phase 4.
- **Risk:** broken/partial downloads at QC. **Mitigation:** `.meta.json` + local_path existence
  checks in cut validation (non-existent path → 422).

---

## 7. Open Questions and Decisions

- Decision: posts persist in the shared `videos` collection with `source="crawler"` (slice
  decoupling).
- Decision: anti-bot waits configured per crawl request (`min_wait`/`max_wait`).
- Decision: `--sort` default is `top` in `main.py` (Docker README says `recent` — reconcile in
  docs/README).
- Open: deduplication strategy (by shortcode) — planned Phase 4.
- Open: whether crawler gains its own test suite or relies solely on `pola_api` integration tests.
