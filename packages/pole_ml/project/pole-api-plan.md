# Plan: `pole-api` (FastAPI backend) + `pole-ui` (frontend) for trick re-training & curation

**Status:** Plan agreed (Phase 1 complete). Implementation not started.
**Date:** 2026-08-03
**Scope of this document:** Documentation / design only. No code changes were made as part of writing this plan.

> **2026-08-05:** refined decisions (repo layout, auth deferral, class status machine, model registry,
> auto-embed upload, per-class cutter config, human-interaction steps, class-list retrain) are recorded
> in `docs/project/pole-api-spec.md`. That spec supersedes the endpoint sketch in §4 below.

---

## 1. Context & repositories

Monorepo `pole-ai/` today:

| Repo | Role |
|------|------|
| `pole-crawler` | Instagram crawler (instaloader). CLI `main.py`; importable `src.client.InstagramClient`, `src.storage.DiskWriter`. |
| `pole-train-model` | ML pipeline. `ml.*` under `src/` (ProcessingPipeline, SkeletonEmbedding, ChromaClassifier, VideoCutter, ModelTrainer …). Data dirs: `models/`, `FeaturesEmbeddings/`, `videos/`. |
| `infrastracture/` | Kustomize manifests (postgres, scrapper, nextcloud). Target for the eventual k8s deployment. |
| `docs/` | Project docs. |

New components (siblings under `pole-ai/`):
- **`pole-api`** — FastAPI backend (orchestrates crawl → cut → review → retrain).
- **`pole-ui`** — Next.js frontend review app.

### Integration mechanics
- `pole-train-model` imports as `ml.*` via `PYTHONPATH=./src` (not a clean pip package).
- `pole-crawler` ships as a flat `src` package (import as `src.client`, `src.storage`).
- Therefore **`pole-api` adds `../pole-train-model/src` and `../pole-crawler` to `sys.path` at startup** and imports the modules directly. Relative layout is pinned and documented.
- Shared data directories (`models/`, `FeaturesEmbeddings/`, `videos/`, `downloads/`, `curated/`) remain owned by `pole-train-model` and are mounted/shared with the API container (later, via PVC in k8s).

---

## 2. Goals

1. Register a **new trick / class** via the API.
2. **Crawl Instagram** by hashtag through `pole-crawler` (direct Python import).
3. **Auto-cut** downloaded videos with `VideoCutter` in a Chroma-only mode suitable for unseen classes.
4. **Human review**: watch the cut, **accept (label) or discard** it.
5. **Review sample counts** (via the `samples-info` tool in `docs/project/retraining-tool-plan.md`) and let the user **decide when to promote** a class to the LSTM.
6. **Re-train** on the user-accepted samples through the modified `train-model` tool (ChromaDB few-shot by default; `full`/`fine-tune` on promotion). MongoDB window documents track which windows were embedded and trained.
7. **Compress the trained LSTM to a TensorFlow.js model** so `pole-ui` can run **real-time trick recognition in the browser** — no classification round-trip to the API. Acceptance criteria: exported payload **< 2 MB** and **< 30 ms/frame** inference on a mid-range device.

---

## 3. Architecture

```
pole-ui (Next.js, Keycloak OIDC login)
   │  HTTPS
pole-api (FastAPI, OAuth2/JWT via Keycloak)
   ├─ endpoints (classes, crawl, process, cut, clips, review, retrain, jobs)
   ├─ PostgreSQL  ← curation state (classes, crawls, posts, clips, verdicts, jobs)
   ├─ MongoDB     ← ML windows (unchanged, owned by pole-train-model)
   ├─ ChromaDB    ← 128-d embeddings (FeaturesEmbeddings/)
   └─ long jobs → v1: FastAPI BackgroundTasks + GET /api/jobs/{id} polling
                  later: Celery + Redis broker (k8s target)
```

### Execution model
- **v1:** FastAPI `BackgroundTasks` (in-process) + a `jobs` table + status polling. No extra infra.
- **later:** Celery + Redis broker; deploy via kustomize manifests mirroring the `pole-ai/infrastracture/` patterns. Redis is the synchronization mechanism for background tasks in the deployed environment.

### Authentication (v1, decided)
- **OAuth2 / OIDC with JWT via Keycloak.**
- Public client for `pole-ui` (authorization-code flow, SPA).
- Confidential client for `pole-api`; JWTs validated server-side (`python-jose`).
- Local dev: Keycloak runs via **docker-compose** alongside PostgreSQL.

### Data stores (decided)
- **PostgreSQL** — curation state only.
- **MongoDB** — remains the ML window / embedding source for the training pipeline (unchanged). This is a **dual-DB** design, accepted and documented here.

---

## 4. Endpoints (v1)

```
Auth (Keycloak OIDC)
  GET  /api/auth/discovery      # OIDC discovery (optional helper)

Classes
  POST /api/classes             # create trick: {name, hashtags[], limit, min_videos?, min_windows?}
  GET  /api/classes             # list classes
  GET  /api/classes/{id}        # detail
  GET  /api/classes/{id}/stats  # windows/clips/embedding counts (sourced from samples-info)

Pipeline triggers (each returns job_id, runs in background)
  POST /api/classes/{id}/crawl     # pole-crawler → downloads/<trick>/
  POST /api/classes/{id}/process   # process-data (windows→Mongo) + process-embeddings (pending→ChromaDB)
  POST /api/classes/{id}/cut       # VideoCutter (chroma-only) → curated/<trick>/

Review
  GET  /api/clips?class_id=&status=          # list cuts
  GET  /api/clips/{id}/video                 # stream mp4 (FileResponse)
  POST /api/clips/{id}/accept                # {label} keep as training sample
  POST /api/clips/{id}/discard               # drop (bad cut)

Retrain
  POST /api/classes/{id}/retrain             # wraps retraining-tool plan
     body: {mode: full|fine-tune, augment?, class_weight?, reembed?}

Jobs
  GET  /api/jobs/{id}                        # status/progress/result/error
```

### Retrain endpoint (decided)
Wraps the retraining-tool plan:
- A new class is **ChromaDB-only (few-shot, no retrain)** right after `process`; the user sees sample counts via `/api/classes/{id}/stats` (sourced from the `samples-info` tool) and **decides when to promote**.
- On promotion, `retrain` invokes the modified `train-model` with the class list (old classes + new trick) and `mode=full` (from scratch) or `mode=fine-tune` (swap softmax head to n+1).
- Optional `augment` (SkeletonAugmenter) and `class_weight` (balanced, default on).
- Mandatory `reembed` after a retrain for feature-space consistency.

### Cut mode (decided)
Use **`VideoCutter --chroma-only`** for a brand-new trick: detection driven by `_validate_segment_with_chroma` (kNN) instead of the LSTM, avoiding false positives to old classes before a retrain.

---

## 5. Data model (PostgreSQL)

```
classes(id, name UNIQUE, hashtags[], status, min_videos, min_windows, created_at)
crawls(id, class_id FK, tag, status, downloaded_count)
posts(id, crawl_id FK, username, timestamp, url, local_path)
clips(id, class_id FK, post_id FK, src_video, clip_path,
      status[pending|accepted|discarded], label, confidence,
      reviewed_by, reviewed_at)
jobs(id, kind, entity_id, status[pending|running|done|failed],
     progress, result_json, error)
```

---

## 6. Integration details

- **Crawler (direct import):** `src.client.InstagramClient(username, session_path)` → `get_posts(tag)` → `download_video_from_url(url)` → `src.storage.DiskWriter(base_dir).save_video(tag, path, meta)` → `downloads/<trick>/<user>_<ts>.mp4` + `.meta.json`.
- **Instagram session:** require env vars (`INSTAGRAM_CSRFTOKEN`, `INSTAGRAM_SESSIONID`, …) on the API service; in k8s later via Secrets, never committed.
- **Process job:** runs `process-data` then `process-embeddings` on the accepted clips. `ProcessingPipeline.process_data(video_path, stride)` stores windows (label by folder, clips under `videos/<trick>/`) with `embedding_models=[]`; `save_windows_embeddings` embeds windows not yet embedded by the model to ChromaDB `movement_embeddings` and appends the model to `embedding_models` (idempotent per model).
- **Stats job:** runs the `samples-info` tool — aggregates Mongo windows per class/video to power `/api/classes/{id}/stats` and the promotion decision.
- **Retrain job:** runs the modified `train-model` with the selected class list (`--classes`), `--mode full|fine-tune`, `--augment`, `--reembed`; writes a `training_runs` doc and marks windows `trained`.
- **Cut job:** instantiate `VideoCutter` with the trick's YAML props + chroma-only mode → `curated/<trick>/`.
- **Mongo access:** `get_mongo_uri()` / `MONGO_URI` env; fail fast with a clear message if unreachable.
- **Shared paths:** `models/`, `FeaturesEmbeddings/`, `videos/`, `downloads/`, `curated/` shared across API and ML containers (dev: shared volume/symlinks; prod: PVC).
- **Frontend model export (tfjs):** after every retrain, export the `.keras` LSTM to a TensorFlow.js LayersModel (`tensorflowjs_converter --quantization_bytes 1`, i.e. int8 weights). Artifacts: `models/frontend/lstm_model_normal_tfjs/` (`model.json` + weight shards) and `labels.json` (class order copied from the label encoder). **Acceptance criteria:** total model payload **< 2 MB** (source `.keras` ≈ 2.8 MB) and **< 30 ms/frame** inference in the browser on the tfjs WebGL backend. The frontend must build the exact same `(30, 14)` biomechanical-feature window (MediaPipe pose → 14 features, same normalization as training) before inference, so the exported model matches training inputs. The export is versioned by `training_runs.run_id` so the UI can flag a stale model after a retrain.

---

## 7. Milestones

| Milestone | Scope |
|-----------|-------|
| **M0** | Scaffold `pole-api`: FastAPI, SQLAlchemy + PostgreSQL, Keycloak OIDC (docker-compose), health check, job-status pattern. |
| **M1** | Classes CRUD + `crawl` job (pole-crawler import; Instagram session via env). |
| **M2** | `process` job (runs `process-data` + `process-embeddings`; Mongo tracking fields + backfill). |
| **M3** | `cut` job (`VideoCutter --chroma-only`), clip listing/streaming, accept/discard. |
| **M4** | `samples-info`-powered stats + `retrain` endpoint (runs the modified `train-model`; user-driven promotion: full / fine-tune / keep Chroma-only). |
| **M5** | `pole-ui` (Next.js): Keycloak login, video review screen (watch/accept/discard), per-class pipeline status + job polling. |
| **M6** | Error/retry UX; end-to-end run on one real trick. |
| **M7** | Frontend model export: tfjs quantization step + `labels.json`; `pole-ui` real-time browser inference (< 30 ms/frame) using the MediaPipe feature window. |
| **Later** | Celery + Redis workers; kustomize manifests (`pole-api`, `pole-ui`, `postgres`, `keycloak`, `redis`); shared PVC for `models/`/`FeaturesEmbeddings/`/`downloads/`/`curated/`. |

---

## 8. Risks & notes

- **Dual database** (Mongo for ML windows, Postgres for curation) — accepted; documented in §3.
- **LSTM false positives** for unseen classes → Chroma-only cut mode (from the retraining plan).
- **Feature drift** after `full` retrain → mandatory `reembed` after any retrain.
- **Instagram anti-bot** — the crawler already rate-limits between requests; keep `limit` low on crawl jobs.
- **Cross-repo imports** via `sys.path` (not pip packages) — pinned relative layout; documented here and in the API README.
- **Secrets** (Instagram session, Keycloak creds, Mongo URI) via env / k8s secrets; never committed.
- **Model/browser parity** — the tfjs export must use identical input preprocessing (30×14 features, same normalization) or frontend inference silently degrades; pin the feature contract and validate the exported model against the same clips used by the backend.
- **v1 polling limitation** — long jobs are tied to a single process; acceptable for the first iteration, replaced by Celery/Redis under k8s later.

---

## 9. Options not chosen (reference)

- Login without Keycloak / simple API key — rejected; OAuth2+JWT+Keycloak decided.
- FastAPI BackgroundTasks only + JSON-file curation — rejected; PostgreSQL chosen for curation.
- Frontend inside `pole-api` or `pole-ui` inside `pole-train-model` — rejected; standalone `pole-ui` repo decided.
- Full retrain only on the retrain endpoint — rejected; reuse capacity (full / fine-tune / Chroma few-shot) decided.

---

## 10. Related documents

- `docs/project/retraining-tool-plan.md` — the ingestion flow (`process-data` + `process-embeddings` with Mongo tracking fields), `samples-info`, and modified `train-model` used by the API (process / stats / retrain jobs).
- `docs/project/testing-plan.md` — test conventions; coverage gate `fail_under = 80` (current 89.31 %).
- `../pole-crawler/README.md` — crawler usage and Instagram session env vars.