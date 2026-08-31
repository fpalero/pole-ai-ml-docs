# `pole-api` — Specification (FastAPI backend)

**Status:** Spec for review (Phase 1 complete). Implementation not started.
**Date:** 2026-08-05
**Supersedes:** `docs/project/pole-api-plan.md` (kept as the original plan; this spec records the agreed, refined decisions).

---

## 1. Context

`pole-api` is a new sibling repo under `pole-ai/` that orchestrates the Pole AI pipeline:

- **`pole-train-model`** — ML pipeline (`ml.*` under `src/`, imports as `ml.*` via `PYTHONPATH=./src`; tools import as `tools.*`).
- **`pole-crawler`** — Instagram crawler (`src.client.InstagramClient`, `src.storage.DiskWriter`).
- **`pole-api`** — FastAPI backend that imports both directly (cross-repo `sys.path`).
- **`pole-ui`** — future Next.js frontend (not in this spec).

The API turns raw trick videos into curated training data and managed model lifecycle:

```
upload/crawl → cut → review (human) → process/embed (Chroma-only) → stats (human decides)
   → retrain → model run → approve (human) → active model
```

---

## 2. Agreed decisions (from clarification)

| Topic | Decision |
|-------|----------|
| Repo location | New sibling repo `pole-ai/pole-api` (matches `pole-api-plan.md`). |
| Auth | **Deferred for v1.** No Keycloak/OIDC yet. API runs without auth (behind reverse proxy / VPN) or optionally with a single `X-API-Key` (env `API_KEY`, disabled when unset). |
| Data stores | **PostgreSQL** (curation state + jobs, via SQLAlchemy), **MongoDB** (ML windows, unchanged), **ChromaDB** (128-d embeddings). |
| Async jobs | v1: in-process background jobs (`threading`/`BackgroundTasks`) + `jobs` table + polling. Later: Celery/Redis. |
| Class status | **Class status machine** in Postgres so the FE knows the current step and which human step is pending. |
| Human interaction steps | 1) Raw video QC before cut (accept/reject per downloaded post). 2) Clip review (accept/discard per cut clip). 3) Upload verification step. 4) Approve promoted model after retrain. |
| New-class ingestion | **Auto-embed on upload**: multipart upload → `process-data` (windows→Mongo) + `process-embeddings` (pending→ChromaDB) automatically. The trick becomes Chroma-only immediately. |
| Crawl | `POST /api/classes/{id}/crawl` with `tags[]`, `limit`, anti-bot waits. Videos land in the trick folder. |
| Cut | `POST /api/classes/{id}/cut`, source = uploaded video, downloaded post, or a raw video path. Chroma-only mode for new classes; hybrid (LSTM+Chroma) for promoted classes. |
| Cutter config | **Per-class config in DB** (JSON), overridable per call. Generated from the `config/*.yaml` template. No manual YAML management. |
| Retrain | `POST /api/classes/{id}/retrain` accepts **`classes[]`** (the list of classes to include). User picks which non-promoted classes to promote based on stats; also used to retrain on scraped-extra videos of existing classes. `mode: full|fine-tune`, `augment`, `class_weight`, `reembed`, `base_model`. |
| Model registry | **Versioned runs + active pointer.** Each retrain writes `models/runs/<run_id>/`. `GET /api/models` lists runs; `POST /api/models/{id}/activate` sets the active model. |
| Model selection | **Active pointer + per-call override** (`model_id` param) on cut/process/evaluate endpoints. |
| New tools (audit-clips, blip-caption, evaluate, find-by-similarity) | **Not included in v1** (explicit user decision). Can be added later as separate endpoints. |
| Transition filter mode (chroma/clip/none) | **Not exposed as an API parameter in v1.** The cut endpoint uses the VideoCutter default (`chroma`); the mode can be wired later. |
| Predict/evaluate endpoint | Not in v1 (auto-embed only). A future `evaluate-video` / `find-by-similarity` endpoint can be added later. |

---

## 3. Architecture

```
pole-ui (future, Next.js) ── HTTPS ──► pole-api (FastAPI)
   ├─ routers: classes, uploads, crawls, posts, clips, models, jobs
   ├─ services: crawler, cutter, process, stats, train, model_registry
   ├─ PostgreSQL ← curation state (classes, crawls, posts, clips, uploads, jobs, model_runs)
   ├─ MongoDB    ← ML windows (owned by pole-train-model, unchanged)
   ├─ ChromaDB   ← 128-d embeddings (FeaturesEmbeddings/)
   └─ long jobs → in-process worker threads + GET /api/jobs/{id} polling
```

### Cross-repo import mechanics
`pole-api` adds the sibling repos to `sys.path` at startup:

```python
sys.path.insert(0, "<pole-ai>/pole-train-model/src")   # ml.*, tools.*
sys.path.insert(0, "<pole-ai>/pole-crawler")           # src.client, src.storage
```

Paths are resolved from `POLE_AI_ROOT` (default: parent of `pole-api`). Shared data dirs stay owned by `pole-train-model` and are referenced via the same root:

| Dir | Purpose |
|-----|---------|
| `<root>/pole-train-model/models/` | MediaPipe task, active model, epoch checkpoints |
| `<root>/pole-train-model/models/runs/<run_id>/` | versioned model runs (this spec) |
| `<root>/pole-train-model/FeaturesEmbeddings/` | ChromaDB persist |
| `<root>/pole-train-model/videos/<trick>/` | accepted clips used as training input |
| `<root>/pole-train-model/downloads/<trick>/` | raw crawled videos |
| `<root>/pole-train-model/curated/<trick>/` | cut clips pending review |
| `<root>/pole-train-model/config/` | cutter YAML template |

---

## 4. Data model (PostgreSQL)

```
classes(id, name UNIQUE, status, hashtags jsonb, min_videos int, min_windows int,
        cutter_config jsonb, created_at, updated_at)

uploads(id, class_id FK, original_filename, stored_path, status[pending|processing|verified|failed],
        job_id, error, created_at)

crawls(id, class_id FK, tag, limit, status[pending|running|done|failed], downloaded_count,
       result_json, error, created_at)

posts(id, crawl_id FK, class_id FK, username, timestamp, url, local_path,
      qc_status[pending|accepted|rejected], created_at)

clips(id, class_id FK, post_id FK NULL, upload_id FK NULL, src_video, clip_path,
      status[pending|accepted|discarded], label, confidence, reviewed_by, reviewed_at, created_at)

jobs(id, kind, entity_id, status[pending|running|done|failed], progress float,
     result_json, error, created_at, finished_at)

model_runs(id, run_id UNIQUE, mode[full|fine-tune], classes jsonb, model_path, encoder_path,
           metrics jsonb, status[done|rejected|active], created_at)
```

### Class status machine

```
draft ──► uploading ──► awaiting_upload_verification ──► chroma_only
                                    │
draft ──► crawling ──► awaiting_qc ──► cutting ──► reviewing ──► processing ──► chroma_only
                                                                         │
chroma_only ──► retraining ──► awaiting_approval ──► promoted ──► (active model includes class)
        │                ▲
        └── (stay Chroma-only if user decides not to promote)
```

Statuses: `draft`, `uploading`, `awaiting_upload_verification`, `crawling`, `awaiting_qc`, `cutting`, `reviewing`, `processing`, `chroma_only`, `retraining`, `awaiting_approval`, `promoted`, `failed`.

---

## 5. Endpoints (v1)

### 5.1 Classes

| Method | Path | Body / Query | Returns |
|--------|------|--------------|---------|
| POST | `/api/classes` | `{name, hashtags[], min_videos?, min_windows?, cutter_config?}` | class |
| GET | `/api/classes` | `?status=&promotion_candidates=` | list |
| GET | `/api/classes/{id}` | — | class + pipeline state |
| GET | `/api/classes/{id}/stats` | — | samples-info + Chroma distribution + promotion readiness |
| PATCH | `/api/classes/{id}` | partial update (hashtags, cutter_config, thresholds) | class |
| DELETE | `/api/classes/{id}` | — | 204 |

### 5.2 Uploads (new-class ingest, auto-embed)

| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/api/classes/{id}/videos` | `multipart/form-data`, file(s) `.mp4` | uploads[] + job_id |
| GET | `/api/classes/{id}/uploads` | — | list |
| POST | `/api/classes/{id}/uploads/{upload_id}/verify` | `{accepted: bool}` | upload (human step) |

Upload flow (auto): save file → `uploads.status=processing` → job runs `process-data` (windows→Mongo, label=trick) + `process-embeddings` (pending→ChromaDB) → `status=verified` pending user confirm → `awaiting_upload_verification` → class status → `chroma_only`.

### 5.3 Crawler

| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/api/classes/{id}/crawl` | `{tags[], limit, min_wait?, max_wait?, sort?}` | job_id |
| GET | `/api/classes/{id}/crawls` | — | list |
| GET | `/api/classes/{id}/posts` | `?qc_status=` | posts (raw videos) |
| POST | `/api/posts/{id}/qc` | `{status: accepted\|rejected}` | post (human step) |

Crawl job: for each tag → `InstagramClient.get_posts(tag)` → sleep anti-bot → `download_video_from_url` → `DiskWriter.save_video(trick, ...)` into `downloads/<trick>/` + `.meta.json`. Creates `posts` rows with `qc_status=pending`.

### 5.4 Cut & review

| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/api/classes/{id}/cut` | `{sources: [{kind: video\|post\|upload, ref}], cutter_override?, model_id?}` | job_id |
| GET | `/api/classes/{id}/clips` | `?status=` | list |
| GET | `/api/clips/{id}/video` | — | mp4 stream (FileResponse) |
| POST | `/api/clips/{id}/accept` | `{label?}` | clip (human step) |
| POST | `/api/clips/{id}/discard` | — | clip (human step) |

Cut job: builds a `VideoCutter` with the class's cutter config (from DB, YAML generated on the fly) → for each source runs `process_video(video_path, target_class=trick, output_dir=curated/<trick>/)` → creates `clips` rows with `status=pending`. Classifier mode: `chroma` if class not promoted, `hybrid` if promoted (unless overridden).

### 5.5 Process (explicit fallback; auto-embed is default)

| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/api/classes/{id}/process` | `{model_id?, stride?}` | job_id |

Runs `process-data` on accepted clips (or `videos/<trick>/`) + `process-embeddings` (pending → ChromaDB). Idempotent (Mongo tracking fields prevent re-embedding).

### 5.6 Models registry

| Method | Path | Body | Returns |
|--------|------|------|---------|
| GET | `/api/models` | `?mode=&status=` | list of runs |
| GET | `/api/models/active` | — | active run |
| GET | `/api/models/{run_id}` | — | run detail (classes, metrics, paths) |
| POST | `/api/models/{run_id}/activate` | — | run (sets active pointer) |

Registry layout: `models/runs/<run_id>/lstm_model_normal.keras`, `lstm_model_normal_encoder.pkl`, `metadata.json`. The active pointer is stored in `model_runs.active` (Postgres) and mirrored to `models/runs/<run_id>/active.json` for ML tooling. `run_id` format: `%Y%m%d_%H%M%S`.

### 5.7 Retrain

| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/api/classes/{id}/retrain` | `{classes[] (labels to include), mode: full\|fine-tune, augment?, class_weight?, reembed?, base_model?, model_id?}` | job_id + run_id |
| POST | `/api/models/{run_id}/approve` | — | run (human gate → active) |
| POST | `/api/models/{run_id}/reject` | — | run |

Retrain behavior (mirrors `train-model`):
- `mode=full` → `ProcessingPipeline.train_model_normal` (rebuild net with n+1 classes).
- `mode=fine-tune` → `ModelTrainer.fine_tune` (swap softmax head, freeze base) using `base_model` (defaults to active run).
- Writes model + encoder to `models/runs/<run_id>/`, inserts a `training_runs` Mongo doc, marks windows `trained`, and re-embeds (`--reembed` default on) so ChromaDB matches the new model.
- New run is `status=done` (NOT active). Human must approve via `/api/models/{run_id}/approve` → sets `active`, class status → `promoted`.
- Class list: the user selects which Chroma-only classes to promote plus existing classes to keep (e.g. `["handspring","shouldermount","transition","backflip"]`).

### 5.8 Jobs

| Method | Path | Query | Returns |
|--------|------|-------|---------|
| GET | `/api/jobs/{id}` | — | status/progress/result/error |
| GET | `/api/jobs` | `?kind=&entity_id=&status=` | list |

---

## 6. Workflows

### Workflow A — New trick (Chroma-only, no LSTM)
1. `POST /api/classes` `{name, hashtags}` → class `draft`.
2. `POST /api/classes/{id}/videos` (multipart `.mp4`) → job auto-embeds → uploads `verified`.
3. User `POST /api/classes/{id}/uploads/{uid}/verify` → class `chroma_only`.
4. `GET /api/classes/{id}/stats` shows the new label with embedded/pending/trained counts.
5. Until promoted, the trick is served by the ChromaDB kNN path (`HybridClassifier` fallback / `ChromaClassifier`).

### Workflow B — Crawl → cut → review → process
1. `POST /api/classes/{id}/crawl` `{tags, limit}` → job downloads → class `awaiting_qc`.
2. User QC: `GET /api/classes/{id}/posts` then `POST /api/posts/{id}/qc` per video.
3. `POST /api/classes/{id}/cut` on accepted posts → clips `pending` → class `reviewing`.
4. User review: stream `GET /api/clips/{id}/video`, `POST /api/clips/{id}/accept|discard`.
5. `POST /api/classes/{id}/process` on accepted clips → windows→Mongo + embeddings→ChromaDB → `chroma_only`.

### Workflow C — Promote a class to LSTM
1. `GET /api/classes?promotion_candidates=true` (or per-class `/stats`) shows Chroma labels not in the active model's encoder.
2. User calls `POST /api/classes/{id}/retrain` `{classes:[new + existing], mode: full|fine-tune}` → job → run `done`.
3. User reviews `GET /api/models/{run_id}` (metrics/classes) → `POST /api/models/{run_id}/approve` → run `active`, class `promoted`.
4. All cut/process/evaluate calls now default to the new active model (override with `model_id`).

### Workflow D — More data for an existing (promoted) class
Same as B, then retrain (full or fine-tune) so the new scraped windows are added to ChromaDB and used in the LSTM. No promotion gate needed (class already `promoted`).

---

## 7. Services ↔ existing `pole-train-model` reuse

| pole-api service | Reuses |
|------------------|--------|
| `crawler_service` | `pole-crawler` `InstagramClient`, `DiskWriter`, `PostMetadata` |
| `cutter_service` | `tools.video_cutter.VideoCutter` (`config_path`, `classifier_mode`) |
| `process_service` | `ProcessingPipeline.process_data`, `ProcessingPipeline.save_windows_embeddings`, `SkeletonExtractor`, `SkeletonStorage`, `WindowRepository` |
| `stats_service` | `tools.samples_info.aggregate_windows`, `WindowRepository.get_all_batches`, `ChromaClassifier.get_statistics` |
| `train_service` | `ProcessingPipeline.train_model_normal` / `fine_tune_model`, `ModelTrainer.fine_tune`, `WindowRepository.insert_training_run` / `mark_trained`, `ModelPersistence` |
| `model_registry` | filesystem + `model_runs` table |

No new ML logic is written — all ML behavior is delegated to the existing `src/` modules.

---

## 8. Environment variables (pole-api)

```
POLE_AI_ROOT                     # default: parent of pole-api
MONGODB_URI / MONGO_URI          # passed through to ml.* config (get_mongo_uri)
POSTGRES_URI                     # default postgresql+psycopg2://pole:pole@localhost:5432/pole_api
API_KEY                          # optional; when set, requires X-API-Key header
INSTAGRAM_USERNAME               # crawler user
INSTAGRAM_CSRFTOKEN / INSTAGRAM_SESSIONID / INSTAGRAM_DS_USER_ID / INSTAGRAM_IG_DID
SESSION_FILE_PATH                # optional path to an existing instaloader session file
FFMPEG_BIN                       # default "ffmpeg"
```

---

## 9. Directory layout (target)

```
pole-api/
├── pyproject.toml / requirements.txt
├── docker-compose.yml           # PostgreSQL (dev)
├── .env.example
├── README.md
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app, sys.path injection, router mount
│   ├── config.py                # env settings
│   ├── db.py                    # SQLAlchemy engine/session
│   ├── models.py                # ORM models
│   ├── schemas.py               # Pydantic schemas
│   ├── jobs.py                  # job runner (threads) + job helpers
│   ├── services/
│   │   ├── __init__.py
│   │   ├── class_service.py
│   │   ├── crawler_service.py
│   │   ├── cutter_service.py
│   │   ├── process_service.py
│   │   ├── stats_service.py
│   │   ├── train_service.py
│   │   └── model_registry.py
│   └── routers/
│       ├── __init__.py
│       ├── classes.py
│       ├── uploads.py
│       ├── crawls.py
│       ├── posts.py
│       ├── clips.py
│       ├── models.py
│       └── jobs.py
└── tests/
```

---

## 10. Edge cases & notes

1. **Embeddings are model-specific** — after a retrain the `feature_vector` changes; old embeddings for that model are stale. Re-embed after retrain (default `reembed=true`). Never treat an embedding as permanent.
2. **Duplicate Chroma entries** — prevented by Mongo `embedding_models` (list) tracking + `get_pending_embeddings` (a window is embeddable when the current model is **not** already in its list).
3. **Mongo/Postgres consistency** — classes in Postgres vs labels in Mongo/Chroma must stay in sync; validate trick-name collisions and reserved `transition` label up front.
4. **Instagram anti-bot** — keep `limit` low; crawler sleeps `random.uniform(min_wait, max_wait)` between downloads.
5. **Class/encoder consistency** — LSTM `label_encoder.classes_`, Chroma `label` metadata, and the retrain `classes[]` list must match; the retrain service unions active-model classes with the requested new ones.
6. **Cross-repo imports** — `ml.*` / `tools.*` / `src.*` resolved via pinned relative layout; documented in the API README.
7. **Jobs are in-process** — long jobs are tied to a single process (v1); replaced by Celery/Redis under k8s later.
8. **Stale-model guard** — the FE/UI can flag a stale model after a retrain by comparing the active run's `run_id`.

---

## 11. Out of scope (v1) / future

- Keycloak/OIDC auth, `pole-ui`.
- `audit-clips`, `blip-caption`, `evaluate-video`, `find-by-similarity` endpoints.
- Real-time prediction endpoint (browser/tfjs inference, M7 of the original plan).
- Celery/Redis workers, kustomize manifests, shared PVC.
- Automatic promotion heuristics.
