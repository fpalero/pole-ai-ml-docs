# PLAN PHASE 6 — Ship `pole_rag` to staging (image + data dir + seed + verify)

> **Project:** `pole_rag` · **State:** 📋 PLANNED ·
> **Back to:** [PLAN.md](../PLAN.md)

## Scope

Ship the already-built local `pole_rag` seeder + chatbot tools (Phases 1–5,
PAIML-POLE-RAG-001..026) into the staging `pole-api` pod and its `/data` PVC,
then prove the 4 chatbot RAG tools return hits on staging. No new collections,
no new endpoints, no contract changes — this phase is wiring + data + proof.

How to use this plan (Diátaxis: how-to guide — you are working to ship, not
learning RAG concepts):

- If you want the *why* behind the storage choice, read **Decision record**
  below first, then follow **Tasks** in ticket order 027 → 028 → 029 → 030.
- If you want facts while working (file paths, env names, DB layout), use the
  **Reference** boxes inside each ticket — they describe, they do not instruct.

## Decision record — why `/data/rag`, why seed-then-copy

**Status quo (verified live on staging, `ipsf-server`):**

- `pole_rag` is **absent from the pole-api image**. The live pod raises
  `ModuleNotFoundError: No module named 'pole_rag'`; `base.Dockerfile` COPY +
  install lists (`packages/pole-crawler`, `pole-train-model`, `pole-crop`,
  `jobs`, `chatbot`, `pole-tools`, `analysis-tools`) contain no `pole_rag`
  entry, and the thin `Dockerfile` only layers `app/pole_api/*` with
  `PYTHONPATH=/app/src`. The 4 chatbot tools (`query_pole`,
  `query_calisthenics`, `query_psicology`, `query_biomechanics` in
  `packages/chatbot/src/pole_chatbot/rag_tools.py`) therefore raise `ToolError`
  on every call today.
- `/data/chroma` on staging is **OCCUPIED** by the `movement_embeddings` store
  (7712 entries, video similarity flow). It must not be disturbed, migrated,
  or pointed at RAG data.
- Missing-DB behaviour is safe: `pole_rag.query` raises `FileNotFoundError`
  per tool call, surfaced as `ToolError` — no pod crash. The image can roll
  before the DBs land.
- Query time needs two things on disk: the Chroma SQLite files **and** the
  `all-MiniLM-L6-v2` embedder weights (384-dim, `sentence-transformers`).

**Decision:**

- **RAG home is `/data/rag/{pole,calisthenics,psicology,biomechanics}/chroma.sqlite3`**
  (one Chroma persistent dir per resource under `/data/rag`, alongside — never
  inside — `/data/chroma`). `pole_rag/config.default_data_dir()` gains a
  `POLE_RAG_DATA_DIR` env override defaulting to the package `data/` dir;
  staging sets it to `/data/rag` via Helm.
- **Seed locally (fast), transfer into the PVC.** Seeding needs Marker PDFs +
  Ollama `llama3.2-vision` + HF weights — all cached locally. Seeding on the
  staging pod would be slow and fragile. The runbook seeds the 4 DBs locally,
  then `kubectl cp`s them into the staging PVC (verified writable as
  `appuser`).
- **Embedder model at query time:** bake `sentence-transformers/all-MiniLM-L6-v2`
  into the base image if the size budget allows; otherwise mount it from the
  PVC via `HF_HOME`/`SENTENCE_TRANSFORMERS_HOME` under `/data/rag/models`.
  Ticket 029 records which lane was taken.

Related: keycloak Phase 8 close-out
(`app/keycloak/plan/PLAN_PHASE_8.md`, 2026-09-04 note) references this record.

## Tasks

- [ ] Ticket 027 — ship `pole_rag` in the pole-api image (`base.Dockerfile`
      COPY + install/`PYTHONPATH`; slow base-image rebuild lane, NOT the thin
      app build). Repo `pole-ai-ml`.
- [ ] Ticket 028 — `POLE_RAG_DATA_DIR` env override in
      `pole_rag/config.default_data_dir()` defaulting to the package data dir.
      Repo `pole-ai-ml` (code only; Helm value is ticket 029).
- [ ] Ticket 029 — staging wiring (Helm `pole-ai` release: `POLE_RAG_DATA_DIR=/data/rag`,
      `/data/rag` dir owned by `appuser`) + local seed of the 4 DBs + `kubectl cp`
      transfer runbook into the staging PVC + embedder-model availability.
      Repo `pole-ai-ml-infra` (Helm files); seed/cp steps are an ops runbook
      that modifies no repo files.
- [ ] Ticket 030 — verification: RAG tool returns hits on staging;
      `FileNotFoundError`→`ToolError` preserved for unknown DBs.
      Repo `pole-ai-ml`.

Ticket order: 027 → 028 → 029 → 030 (linear; each blocks the next).

## Dependencies

- Phases 1–5 (`pole_rag` seeder, CLI, chatbot tools 025/026): `query`,
  `ChromaStore`, `rag_tools.py` handlers, `ToolError` contract.
- Staging: Helm release `pole-ai`, deploy `pole-ai-pole-api`, `/data` PVC
  (all owned by `pole-ai-ml-infra`); pole-api image build lane (owned by
  `pole-ai-ml`).

## Acceptance Criteria

- `pole_rag` importable in the rolled staging pod (no `ModuleNotFoundError`).
- `POLE_RAG_DATA_DIR=/data/rag` effective on staging; unset locally still
  resolves to `packages/pole_rag/data/`.
- `/data/rag/{pole,calisthenics,psicology,biomechanics}/chroma.sqlite3` present
  on the staging PVC; `/data/chroma` untouched (movement store intact).
- Chatbot `query_pole --data_dir /data/rag` (and siblings) return k hits with
  `source_document` metadata on staging; unknown DB still raises `ToolError`.
- Embedder `all-MiniLM-L6-v2` resolvable at query time (baked or `HF_HOME`).

## Risks and Mitigations

- **Risk:** base-image rebuild is slow (TF/MediaPipe lane). **Mitigation:**
  batch the `pole_rag` COPY with the embedder-model bake decision (ticket 027);
  thin app builds stay fast and unaffected.
- **Risk:** `SCAN`/`KEYS` confusion does not apply here, but `kubectl cp` to a
  `Recreate`-strategy single-replica pod can race a rollout. **Mitigation:**
  copy only when the deploy is stable (`rollout status` green); re-verify
  after any subsequent rollout.
- **Risk:** seeding 4 DBs locally is heavy (~560 MB sources). **Mitigation:**
  seed per-resource, resume per folder; transfer per DB; verify counts with
  `rag-inspect` before and after copy.
