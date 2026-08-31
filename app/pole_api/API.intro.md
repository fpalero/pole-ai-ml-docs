# `pole_api` — cross-cutting conventions

> This section is **hand-maintained** — it documents the conventions that the
> auto-generated endpoint reference (below, produced from `/openapi.json`)
> does not express. When a slice, job model, error code, or identifier format
> changes, update this file. Per-endpoint details are NOT maintained here.

## 1. Overview

`pole_api` is the orchestration backend of the pole-ai pipeline. It is split
into slices, all mounted under the `/api` prefix (plus one root health route
and three WebSocket routers):

| Slice | Router prefix | Description |
| :--- | :--- | :--- |
| System | `/health` (no `/api`) | Liveness probe. |
| Tools | `/api/tools` | Crop / shift / correct + histogram analysis/read/patch/summary (background jobs) + reference histograms + phase detection + health. |
| Chatbot | `/api/chatbot` | Video-analysis ReAct chatbot over WebSocket. |
| Training chatbot | `/api/training-chatbot` | Training-coaching ReAct chatbot over WebSocket. |
| Analyst chatbot | `/api/analyst-chatbot` | Athlete/coach trick-analysis ReAct chatbot over WebSocket (17 tools: histogram, classify, extract_frames, crop, compare_sessions, cohort_percentiles, improvement_plan, metric_deep_dive, frame_pose, progress_trend, focus_recommendation, risk_scan, get_coach_summary, get_coach_pose, and more). |
| Video | `/api/video` | Uploads, streaming, frame/shift, cut, clips, cutter-configs, deletion, jobs. |
| Training | `/api/training` | Classes, extract/process/embed/promote, train/retrain, model registry, phase frames, jobs. |
| Crawler | `/api/crawler` | Instagram crawl, posts, QC, jobs. |
| Analysis | `/api/analysis` | Athlete-facing video upload/list/get/stream/thumbnail + analyze + coach (summary/plan/pose-analysis/insights/metric-deltas/landmarks) + athlete-profile + jobs. |

### Routing facts (from `main.py`)

- Every slice router is included with `prefix="/api"`; each controller carries
  its own sub-prefix (e.g. `APIRouter(prefix="/video")`), so the final path is
  `/api/video/...`, `/api/training/...`, `/api/crawler/...`, `/api/tools/...`,
  `/api/analysis/...`.
- Chatbot router → `WS /api/chatbot/ws/chat`.
- Training-chatbot router → `WS /api/training-chatbot/ws/training-chat`.
- Analyst-chatbot router → `WS /api/analyst-chatbot/ws/analyst-chat`.
- All three WebSocket routers are wired **best-effort**: if their dependencies
  cannot be imported, `main.create_app` skips them and logs
  `[startup] ... router not available` (the REST API still starts).
- CORS: `allow_origins=["*"]`, `allow_methods=["*"]`, `allow_headers=["*"]`,
  with `expose_headers` including `X-Total-Count` and the `X-Count-*` family.

### Authentication (Keycloak JWT)

`pole_api` validates Keycloak JWTs on protected routes via `core/auth.py`:

- **Realm:** `pole-ai` (configured via `KEYCLOAK_AUTH_SERVER_URL`, `KEYCLOAK_REALM`).
- **Clients:** `pole-fe`, `pole-analyst`, `mcp-server` (all confidential).
- **Roles:** `analyst-user` (analysis slice), `fe-user` (training/video/crawler/tools).
- **Public endpoints:** `GET /health`, `GET /docs`, `GET /openapi.json`, media endpoints (`GET .../video`, `GET .../thumbnail`), `POST /api/analysis/videos` (upload — see Phase 13), `WS` endpoints with `?token=` query param.
- **Config:** `AUTH_ENABLED` (default `true`), `KEYCLOAK_AUTH_SERVER_URL`, `KEYCLOAK_REALM`, `KEYCLOAK_CLIENT_ID`, `KEYCLOAK_CLIENT_SECRET`.
- **WS auth:** `core/ws_auth.py` validates tokens from `?token=` query param or `Authorization` header.

## 2. Error envelope

`src/core/errors.py` registers a single handler for the `AppError` hierarchy.
Every domain error is returned as:

```json
{ "detail": "<human-readable message>" }
```

| Exception | HTTP status | Typical trigger |
| :--- | :--- | :--- |
| `BadRequestError` | 400 | Tool failure (crop range invalid, missing file, bad phase_frames). |
| `NotFoundError` | 404 | Entity or job not found. |
| `ConflictError` | 409 | Duplicate name, cannot delete video with children, cannot activate/approve in wrong state. |
| `ValidationError` | 422 | Domain validation (invalid status enum, thresholds not trained, unprocessed video selected…). |
| `ServiceUnavailableError` | 503 | LLM endpoint down (also surfaces as a 503 WS frame in the training chatbot). |
| `AppError` (base) | 500 | Unhandled app-level error. |

FastAPI's own request-validation failures (malformed body, missing fields,
type errors) return the standard **422** `{"detail": [...]}` envelope. The
chatbot WebSocket rate limiter returns a **429-equivalent** WS frame, not an
HTTP status.

## 3. Identifiers

- Path `{class_id}`, `{video_id}`, `{clip_id}`, `{config_id}`, `{post_id}`,
  `{run_id}`, `{job_id}`, `{temporal_id}` are strings.
  Mongo-backed IDs are **24-hex `ObjectId` strings**; `{run_id}` is a
  `YYYYmmdd_HHMMSS[-n]` string; `{job_id}` is an `ObjectId` string.

## 4. Shared job model & lifecycle

Almost every long-running operation (`cut`, `extract`, `process`, `embed`,
`promote`, `clip`, `train`/`retrain`, `crawl`, `upload`, `shift`, `delete`,
`delete_class`, `create`, `histogram_analysis`, `analysis`) is submitted as a
**background job** and returns `202` with `{"job_id": "..."}`.

Jobs live in the Mongo `jobs` collection (`core/jobs.py`):

```json
{
  "_id": "64f…",
  "kind": "cut",
  "entity_id": "<class_id or null>",
  "slice": "video",
  "status": "running",
  "progress": 0.5,
  "result_json": null,
  "error": null,
  "description": null,
  "created_at": "2026-08-12T…Z",
  "finished_at": null
}
```

**Status machine:** `pending → running → done | failed | stopped`.

- `stopped` = cancelled (`POST /jobs/{id}/cancel`) or orphaned by a process
  restart (startup marks leftover `pending`/`running` jobs as `stopped`).
- Cancellation is cooperative: `POST …/jobs/{job_id}/cancel` sets a
  `cancel_requested` flag; the worker checks it between items and raises
  `JobCancelled`, typically rolling back partial work (clips, windows,
  embeddings, downloaded posts…). Only `pending`/`running` jobs can be
  cancelled (otherwise `409`).

Each slice exposes its own job-status router (identical shape, scoped to its
`slice`):

- `GET  /api/{slice}/jobs?status=&limit=` — list recent jobs for the slice.
- `GET  /api/{slice}/jobs/{job_id}` — one job.
- `POST /api/{slice}/jobs/{job_id}/cancel` — request cancellation (202).

(`{slice}` ∈ `video`, `training`, `crawler`, `tools`, `analysis`.)

## 5. Status enums

| Enum | Values |
| :--- | :--- |
| Job status (`core.jobs`) | `pending`, `running`, `done`, `failed`, `stopped` |
| Clip status | `pending`, `accepted`, `discarded` |
| Clip review decision | `null`, `accepted`, `rejected`, `transition` |
| Upload status | `pending`, `processing`, `verified`, `failed` |
| Post QC status | `pending`, `accepted`, `rejected` |
| Model run status | `running`, `done`, `failed`, `active`, `rejected` |
| Model run mode | `full`, `fine-tune` |
| Crawl status | `pending`, `running`, `done`, `failed`, `stopped` |
| Cut source kind | `post`, `upload`, `video`, `path` |
| Chatbot session status | `active`, `completed`, `abandoned` |
| TrickPhase | `ENTRADA`, `EJECUCION`, `SALIDA` (automatic phase detection, Phase 17) |

## 6. Histogram metric set (M-01..M-08)

The authoritative histogram signal set (`pole_tools.services.histogram.METRICS`),
used by `/api/tools/histograms/*` and the chatbot `histogram` tool:

| Code | Metric |
| :--- | :--- |
| M-01 | `horizontal_speed` |
| M-02 | `vertical_speed` |
| M-03 | `angular_speed` (true spin — yaw velocity) |
| M-04 | `torso_tilt_speed` (inclination derivative) |
| M-05 | `wrist_stability` |
| M-06 | `hip_height` |
| M-07 | `body_tilt` |
| M-08 | `smoothness` |

## 7. WebSocket endpoints

All three WebSocket endpoints share the same wire protocol:

| Endpoint | Purpose | Tools |
| :--- | :--- | :--- |
| `WS /api/chatbot/ws/chat` | Video-analysis ReAct chatbot | `crop`, `shift`, `histogram`, `similarity`, `correct` |
| `WS /api/training-chatbot/ws/training-chat` | Training-coaching chatbot | `hyperparameter_search`, `compare_models`, `dataset_stats`, `inspect_job` |
| `WS /api/analyst-chatbot/ws/analyst-chat` | Athlete/coach analysis chatbot | 17 tools (see §8) |

Authentication: `?token=<JWT>` query param or `Authorization: Bearer <JWT>` header.

## 8. Analyst chatbot tools (Phase 18 + Phase 26)

The analyst chatbot exposes 17 tools via `AnalystFacade`:

| Tool | Category | Description |
| :--- | :--- | :--- |
| `histogram` | Analysis | Fetch per-metric histogram data for a video. |
| `classify` | Analysis | Classify which trick a video contains. |
| `extract_frames` | Analysis | Extract pose frames for a video. |
| `crop` | Analysis | Crop a segment from a video. |
| `compare_sessions` | Coach | Session-over-session metric deltas + peak flags. |
| `cohort_percentiles` | Coach | Athlete percentile rank per metric vs same-trick cohort. |
| `improvement_plan` | Coach | 4-week improvement plan (cached). |
| `metric_deep_dive` | Coach | One metric curve + cohort band + worst frames. |
| `frame_pose` | Coach | Single-frame joint angles + coaching breakdown. |
| `progress_trend` | Coach | Metric trend across all same-trick sessions. |
| `focus_recommendation` | Coach | Deterministic top-N focus areas from detections. |
| `risk_scan` | Coach | Injury-risk joint-angle frame scanning. |
| `get_coach_summary` | Coach | Read cached Phase 21 coach summary envelope. |
| `get_coach_pose` | Coach | Read cached Phase 21 coach pose envelope. |
