# pole_api — HTTP API Reference (`API.md`)

> Auto-generated from OpenAPI (version `0.1.0`) on 2026-08-29T08:05:23.
> Interactive: `/docs` · ReDoc: `/redoc` · spec: `/openapi.json`. End-to-end flows: [`API.FLOWS.md`](./API.FLOWS.md).


---

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


---

## Endpoints

### `GET /api/analysis`

Slice root — proves the analysis router is mounted under ``/api/analysis``.

**Responses**

- **200** — Successful Response — `object`


**Example**

```bash
curl -s -X GET /api/analysis
```

### `GET /api/analysis/athlete-profile`

Return the athlete's biometric profile (empty fields when unset).

**Responses**

- **200** — Successful Response — `AthleteProfile`


**Example**

```bash
curl -s -X GET /api/analysis/athlete-profile
```

### `PUT /api/analysis/athlete-profile`

Create-or-update the biometric profile (partial updates allowed).

**Request body** — `AthleteProfileUpdate` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `height_cm` | `number | null` | no | Athlete height in centimeters |
| `weight_kg` | `number | null` | no | Athlete weight in kilograms |


**Responses**

- **200** — Successful Response — `AthleteProfile`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X PUT /api/analysis/athlete-profile \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/analysis/jobs`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `status` | query | `string | null` | optional |  |
| `limit` | query | `integer` | optional (default `50`) |  |

**Responses**

- **200** — Successful Response — `list[object]`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/analysis/jobs
```

### `GET /api/analysis/jobs/{job_id}`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `job_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/analysis/jobs/<job_id>
```

### `POST /api/analysis/jobs/{job_id}/cancel`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `job_id` | path | `string` | required |  |

**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/analysis/jobs/<job_id>/cancel \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/analysis/videos`

List analysis videos, oldest first, with ``analyzed`` flag (UC-A1 read).

Supports ``skip``/``limit`` pagination and sets ``X-Total-Count`` to the
full doc count — mirroring the video slice listing convention
(``training/controllers/process.py``).

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `skip` | query | `integer` | optional (default `0`) |  |
| `limit` | query | `integer` | optional |  |

**Responses**

- **200** — Successful Response — `list[AnalysisVideo]`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/analysis/videos
```

### `POST /api/analysis/videos`

Upload a video for analysis (UC-A1).

Validates ``.mp4`` format and size (UC-A5 → 422), saves the file to
``settings.analysis_upload_dir`` and creates an ``analysis-db.videos`` doc
with ``analyzed=false``. Returns ``201`` with the created doc — PLAN.md
D-A1, finalized at ticket time: no background job is submitted at upload;
analysis is triggered later by the analyze endpoint (PAIML-POLA-API-028).



**Responses**

- **201** — Successful Response — `AnalysisVideo`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/analysis/videos \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/analysis/videos/summary`

Return enriched video summaries with histogram data (Phase 20 §1).

The Stitch Analysis History table consumes this endpoint. Returns videos
joined with their analysis results (trick_label, overall_score, phases)
sorted by ``created_at`` descending. Sets ``X-Total-Count`` header for
pagination.

**Must be declared before** ``/videos/{video_id}`` so FastAPI doesn't
match ``summary`` as a path parameter.

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `skip` | query | `integer` | optional (default `0`) |  |
| `limit` | query | `integer` | optional (default `50`) |  |

**Responses**

- **200** — Successful Response — `list[AnalysisVideoSummary]`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/analysis/videos/summary
```

### `GET /api/analysis/videos/{video_id}`

Fetch a single analysis video doc (UC-A1 read). Missing → 404.

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `AnalysisVideo`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/analysis/videos/<video_id>
```

### `PATCH /api/analysis/videos/{video_id}`

Set the video's ``trick_label`` (Class Name configuration modal).

A pure rename — persists the label on the video doc and syncs any stored
histogram doc, mirroring how the analyze worker keeps both in sync. It
does NOT re-run analysis; scoring against a named cohort is the analyze
request's ``trick_label`` option. Unknown id → 404.

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Request body** — `VideoPatchRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `trick_label` | `string` | yes | New trick label for the video |


**Responses**

- **200** — Successful Response — `AnalysisVideo`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X PATCH /api/analysis/videos/<video_id> \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `DELETE /api/analysis/videos/{video_id}`

Cascade-delete a video (library card Delete action).

Removes the video doc AND its uploaded file (under
``settings.analysis_upload_dir``), the ``video_histograms`` doc and the
``skeleton_landmarks`` doc — best-effort per item with error aggregation;
coach artifacts live ON the video doc so they are removed with it.
Returns ``{"deleted": true, "removed": {...per-item booleans}}``.
Unknown id → 404 before anything is removed.

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X DELETE /api/analysis/videos/<video_id>
```

### `POST /api/analysis/videos/{video_id}/analyze`

Queue an asynchronous analysis job for a video (UC-A2).

Returns ``202 {"job_id": ..., "previously_analyzed": bool}``; poll
``GET /api/analysis/jobs/{job_id}`` for the result (the job is submitted
with ``slice_name="analysis"`` so the analysis jobs router can see it).
Missing/invalid ``video_id`` → 404.

``previously_analyzed`` (PAIML-POLE-API-054) lets the FE ask
"¿Reprocesar?" when the video already has results; re-analysis is
idempotent (the worker replaces previous results).

The optional body carries scoring options (PAIML-POLA-API-030): an empty
``{}`` body is accepted and means "no reference cohort" (the job still
completes and flags the video, leaving the summary fields absent).

The optional ``X-WS-Connection-Id`` header (PAIML-POLE-API-052) is the
analyst WebSocket connection that triggered the run; it is attached to the
job so the lifecycle frames (``job_started`` / per-stage ``job_progress``
/ ``job_done`` / ``job_error``) are relayed to that connection via the
Redis publisher wired on ``app.state.analysis_job_event_publisher``.

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |
| `X-WS-Connection-Id` | header | `string | null` | optional |  |

**Request body** — `AnalyzeRequest | null` (media type: `optional`):

```json
{
  "anyOf": [
    {
      "$ref": "#/components/schemas/AnalyzeRequest"
    },
    {
      "type": "null"
    }
  ],
  "title": "Payload"
}
```


**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/analysis/videos/<video_id>/analyze \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/analysis/videos/{video_id}/coach-insights`

Return LLM-generated per-frame coaching insights.

``200`` with the structured perfect/adjustment/wrong insight lists;
cached on the video doc, regenerated with ``?refresh=true``. ``404``
when the video has no scored analysis yet.

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |
| `refresh` | query | `boolean` | optional (default `False`) | Force LLM regeneration |

**Responses**

- **200** — Successful Response — `CoachInsightsResponse`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/analysis/videos/<video_id>/coach-insights
```

### `POST /api/analysis/videos/{video_id}/coach-plan`

Generate-or-return-cached a 4-week plan toward ``target_trick``
(UC-C3).

The plan cache is keyed by target trick: a different trick regenerates.
Error contracts mirror the summary endpoint (409 / 503).

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |
| `refresh` | query | `boolean` | optional (default `False`) |  |

**Request body** — `CoachPlanRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `target_trick` | `string` | yes | Trick the plan progresses toward |
| `athlete_notes` | `string | null` | no | Optional free-text context from the athlete |


**Responses**

- **200** — Successful Response — `ImprovementPlanOut`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/analysis/videos/<video_id>/coach-plan \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/analysis/videos/{video_id}/coach-summary`

Generate-or-return-cached the performance summary (UC-C1/C2).

First call runs ONE LLM pass (soft budget < 10 s); later calls serve the
cached envelope from the video doc. ``?refresh=true`` forces a new
generation (last-write-wins). Not-analyzed → 409; LLM down/invalid → 503.

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |
| `refresh` | query | `boolean` | optional (default `False`) |  |

**Responses**

- **200** — Successful Response — `CoachSummaryOut`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/analysis/videos/<video_id>/coach-summary
```

### `GET /api/analysis/videos/{video_id}/histogram`

Fetch the stored per-video histogram doc (UC-A3 read). Missing → 404.

Returns the ``analysis-db.video_histograms`` doc verbatim (``video_id``,
``trick_label``, ``phases``, ``metrics``, ``resampled``, ``z_mean``,
``scores``, ``detections`` + metadata) — a read-only surface that never
recomputes anything (PAIML-POLA-API-032).

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `any`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/analysis/videos/<video_id>/histogram
```

### `GET /api/analysis/videos/{video_id}/landmarks`

Return raw + corrected landmarks for the skeleton overlay.

``200`` with per-frame raw [0,1] MediaPipe landmarks (blue skeleton)
and PoseCorrector-corrected landmarks (red corrections). ``404``
when the video has not been extracted yet.

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `VideoLandmarks`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/analysis/videos/<video_id>/landmarks
```

### `GET /api/analysis/videos/{video_id}/metric-deltas`

Session-over-session metric deltas + peak flags (Phase 24, PAIML-POLE-API-072).

Backend for the Stitch "Metric Distribution Analysis" cards: per shared
metric key, ``+X% vs last session`` deltas against the latest **prior**
analyzed video of the same trick, plus ``Peak Performance`` badges for
metric keys where the current value is the max across ALL analyzed videos
of that trick (single aggregation). Aggregate numbers only — no image or
landmark payloads are ever returned.

``200`` with empty ``metrics``/``peak_flags`` and a ``None``
``baseline_video_id`` when no comparable same-trick history exists (not
an error — the FE hides the card). ``409`` when the video has no scored
analysis yet; ``404`` when the video does not exist.

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `MetricDeltasOut`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/analysis/videos/<video_id>/metric-deltas
```

### `PUT /api/analysis/videos/{video_id}/phase-frames`

Persist manual per-phase frame bounds on the video doc.

Body: ``{"phase_frames": {"ENTRANCE": [start, end], "EXECUTION": [...],
"EXIT": [...]}}`` — uppercase keys + inclusive ``[start, end]`` lists, the
EXACT shape ``AnalyzeWorker`` reads from ``video.get("phase_frames")`` as
the authoritative manual override for the next analysis run. Malformed
bounds → 422; unknown id → 404.

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Request body** — `analysis__schemas__PhaseFramesRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `phase_frames` | `object` | yes |  |


**Responses**

- **200** — Successful Response — `AnalysisVideo`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X PUT /api/analysis/videos/<video_id>/phase-frames \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/analysis/videos/{video_id}/pose`

Return the annotated pose frame + correction issues (UC-A3).

``200`` with a :class:`PoseFrame` (the frame as a base64 data URL +
``frame_image_path`` + ``issues`` correction hints) when the video has a
``video_histograms`` doc and a frame is resolvable — stored pose frame,
``detections[].frame_image_path``, or on-demand extraction
(PAIML-POLA-API-034 D-A1 fallback). ``404`` when the video is missing, has
no histogram (not analyzed yet), or no frame could be produced.

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `PoseFrame`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/analysis/videos/<video_id>/pose
```

### `GET /api/analysis/videos/{video_id}/pose-analysis`

Generate-or-return-cached the text-only pose breakdown (UC-C4).

Inputs are landmark-derived issues, per-phase deviations and signal
stats only — image bytes are never read or sent. Errors: 409 / 503.

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |
| `refresh` | query | `boolean` | optional (default `False`) |  |

**Responses**

- **200** — Successful Response — `PoseAnalysisOut`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/analysis/videos/<video_id>/pose-analysis
```

### `GET /api/analysis/videos/{video_id}/pose/frames`

Return multiple annotated pose frames sorted by |z_score| desc (Phase 20 §2).

On the first access, lazily extracts the detection JPEGs and stamps
``frame_image_path`` on each detection (PAIML-POLE-API-066) — the FE
spinner covers this first (slower) request; subsequent calls serve the
cached paths. ``200`` with a :class:`PoseFrameGallery` containing multiple
annotated pose frames with skeleton overlays, sorted by deviation (most
deviant first). ``404`` when the video has no histogram (not analyzed yet).

Like the single-frame endpoint, each frame's JPEG is inlined as a base64
data URL so the browser can render it without filesystem access; frames
whose file is unreadable are skipped instead of failing the request.

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `PoseFrameGallery`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/analysis/videos/<video_id>/pose/frames
```

### `GET /api/analysis/videos/{video_id}/summary`

Return the stored per-video analysis summary (UC-A3 read).

Read-only endpoint (PAIML-POLA-API-033): returns the summary fields the
analyze job worker persisted on the ``analysis-db.video_histograms`` doc —
``z_mean``/``scores``/``detections`` plus the optional ``critical_*``
(most-deviant detection) — with **no recompute, no job and no frame
extraction** (PLAN.md §9 read-verbatim convention). The reference cohort
``skeleton_data.skeleton_cohort_signals`` is checked **read-only** for the
video's ``trick_label``; when empty the endpoint returns ``422
{"detail": "reference data unavailable"}`` (PLAN.md §6 risk mitigation).

The ``NotFoundError`` raised by the service is mapped to ``404`` by the
shared error handler: no ``video_histograms`` doc (never analyzed /
unknown video) or a doc without stored summary fields →
``summary not available for '<id>'; run analyze first``.

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/analysis/videos/<video_id>/summary
```

### `GET /api/analysis/videos/{video_id}/thumbnail`

Generate on demand and serve a JPG thumbnail (UC-A3). Missing → 404.

Mirrors the video slice's lazy-thumbnail pattern with an analysis-local
service (``AnalysisThumbnailService``) — the analysis slice stays decoupled
and never imports ``video`` modules. Accepts the access token via ``?token=``
as well as the ``Authorization`` header (``<img>`` cannot set headers).

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/analysis/videos/<video_id>/thumbnail
```

### `GET /api/analysis/videos/{video_id}/video`

Stream the uploaded ``.mp4`` file (UC-A3). Missing video/file → 404.

Accepts the access token via ``?token=`` as well as the ``Authorization``
header (``<video>`` cannot set headers). The analyst role is enforced here
(not at the router level) so the query-param transport is allowed.

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/analysis/videos/<video_id>/video
```

### `POST /api/crawler/classes/{class_id}/crawl`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |

**Request body** — `CrawlRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `tags` | `list[string]` | yes |  |
| `limit` | `integer` | no |  |
| `min_wait` | `integer` | no |  |
| `max_wait` | `integer` | no |  |


**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/crawler/classes/<class_id>/crawl \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/crawler/classes/{class_id}/crawls`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `list[object]`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/crawler/classes/<class_id>/crawls
```

### `GET /api/crawler/classes/{class_id}/posts`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |
| `qc_status` | query | `string | null` | optional |  |

**Responses**

- **200** — Successful Response — `list[object]`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/crawler/classes/<class_id>/posts
```

### `GET /api/crawler/jobs`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `status` | query | `string | null` | optional |  |
| `limit` | query | `integer` | optional (default `50`) |  |

**Responses**

- **200** — Successful Response — `list[object]`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/crawler/jobs
```

### `GET /api/crawler/jobs/{job_id}`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `job_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/crawler/jobs/<job_id>
```

### `POST /api/crawler/jobs/{job_id}/cancel`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `job_id` | path | `string` | required |  |

**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/crawler/jobs/<job_id>/cancel \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `POST /api/crawler/posts/{post_id}/qc`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `post_id` | path | `string` | required |  |

**Request body** — `QcRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `status` | `string` | yes |  |


**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/crawler/posts/<post_id>/qc \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/me/llm-usage`

**Responses**

- **200** — Successful Response — `object`


**Example**

```bash
curl -s -X GET /api/me/llm-usage
```

### `POST /api/tools/correct`

**Request body** — `CorrectRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `video_path` | `string` | yes | Path to the video |
| `frame_number` | `integer` | yes | Frame to correct |
| `out_dir` | `string | null` | no |  |


**Responses**

- **200** — Successful Response — `ToolResponse`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/tools/correct \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `POST /api/tools/crop`

**Request body** — `CropRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `src` | `string` | yes | Source video path |
| `start` | `number` | yes | Segment start in seconds |
| `end` | `number` | yes | Segment end in seconds |
| `out_dir` | `string | null` | no | Output directory override |
| `filename` | `string | null` | no |  |


**Responses**

- **200** — Successful Response — `ToolResponse`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/tools/crop \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/tools/health`

**Responses**

- **200** — Successful Response — `object`


**Example**

```bash
curl -s -X GET /api/tools/health
```

### `POST /api/tools/histograms/analysis`

Submit a background ``histogram_analysis`` job over ``video_ids``.

Returns ``202 {job_id}``; poll ``GET /api/tools/jobs/{job_id}`` for the
result (UC-91). Empty or invalid ``video_ids`` are rejected with a 422 by
the request schema.

**Request body** — `HistogramAnalysisRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `video_ids` | `list[string]` | yes | Video ids to run the histogram analysis on |


**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/tools/histograms/analysis \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/tools/histograms/classes`

Return the trick labels that have reference histograms available.

Phase 16 read-only endpoint (PLAN_PHASE_16 §2, PAIML-POLE-API-044): lists
the distinct ``trick_label`` values stored in
``skeleton_trick_histograms`` (via
``TrickHistogramRepository.distinct_trick_labels``) so the FE can populate
the video-selection dropdown of ``pole_fe`` Phase 11. Response shape:
``{"classes": [...]}`` — empty when no reference histograms exist yet.

Registered before ``GET /histograms/{video_id}`` so the literal
``classes`` segment is never captured by the ``video_id`` path parameter.

**Responses**

- **200** — Successful Response — `object`


**Example**

```bash
curl -s -X GET /api/tools/histograms/classes
```

### `GET /api/tools/histograms/cohort/{trick_label}`

Return the cohort signal histograms for a trick label (read-only).

Phase 13 class-stats endpoint: returns the per-metric cohort
``mean``/``std`` from the ``skeleton_cohort_signals`` collection plus every
processed clip's ``resampled`` 300-pt curves grouped by metric (see
:meth:`ToolsService.get_cohort_histogram`). **No recompute, no job** — a
pure read of the two histogram collections. ``404`` when no cohort exists
for the trick label.

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `trick_label` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/tools/histograms/cohort/<trick_label>
```

### `GET /api/tools/histograms/references`

Query-param mirror of ``GET /histograms/references/{trick_label}``.

Serves the same read (Phase 16, PAIML-POLE-API-044) but accepts the trick
label as ``?trick_label=`` to match the FE ``getClassHistogramStats`` call.
An empty/missing ``trick_label`` is rejected with a 422 carrying
``missing_metrics`` (the 5 Phase-16 reference metrics), matching the
path-param contract — the service raises that 422 itself when no
reference documents exist for the label.

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `trick_label` | query | `string` | optional |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/tools/histograms/references
```

### `POST /api/tools/histograms/references`

Generate (or regenerate) the reference histograms of a trick.

Phase 16 write endpoint: submits a background ``reference_generation`` job
over ``payload.clip_ids`` (approved/accepted clips of ``payload.trick_label``)
that rebuilds the ``skeleton_trick_histograms`` docs via
:meth:`HistogramAnalysisService.upsert_trick_histograms` (z-score binning
against cohort statistics, PAIML-POLE-API-047). Returns ``202 {job_id}``;
poll ``GET /api/tools/jobs/{job_id}`` for completion. Empty
``trick_label``/``clip_ids`` are rejected with a 422 by the request schema.

**Request body** — `ReferenceGenerationRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `trick_label` | `string` | yes | Trick to generate reference histograms for |
| `video_ids` | `list[string]` | yes | Clip (video) ids of the trick to reference |
| `bins` | `list[number] | null` | no | Optional bin edges (defaults to REFERENCE_BINS) |


**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/tools/histograms/references \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/tools/histograms/references/{trick_label}`

Return the reference histograms of a trick (per metric and phase).

Phase 16 read-only endpoint (PLAN_PHASE_16 §2, PAIML-POLE-API-044): serves
the reference distributions Phase 16 generated from approved clips (per
``metric`` x ``phase``, one doc per ``(trick_label, metric, phase)`` in
``skeleton_trick_histograms``) for the FE class-stats histograms. A pure
read via ``TrickHistogramRepository.find_by_trick`` — **no recompute, no
job**.

Response shape::

    {
        "trick_label": "handspring",
        "metrics": {
            "angular_speed": {
                "ENTRADA": {"bins": [...], "counts": [...], "total": 42,
                            "source_count": 5, "last_updated": "..."},
                "EJECUCIÓN": {...},
                "SALIDA": {...}
            },
            ...
        }
    }

When the trick has **no** reference histograms, the shared error handler
maps the service's ``ValidationError`` to a 422 whose body carries the
``missing_metrics`` list (the 5 Phase-16 reference metrics) alongside
``detail`` — the FE uses it to show which references are absent.

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `trick_label` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/tools/histograms/references/<trick_label>
```

### `GET /api/tools/histograms/summary/{video_id}`

Return the stored per-video histogram summary (UC-95..98).

Phase 12 read-only endpoint (PLAN.md §9.3.2, ticket PAIML-POLA-API-022):
returns the summary fields the ``histogram_analysis`` job persisted on
the per-video ``skeleton_video_signals`` doc — ``z_mean``/``scores``/
``detections`` plus the optional ``critical_*`` — **verbatim**, with no
recompute, no job and no frame extraction (§9.7 D-4).

No request body; a single ``video_id`` path parameter. The
``NotFoundError`` raised by the service is mapped to ``404`` by the
shared error handler: ``histogram not found`` when the video has no
histogram (UC-97), or ``summary not available for '<id>'; run
histograms/analysis first`` when the doc exists but analysis never ran
(UC-96).

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/tools/histograms/summary/<video_id>
```

### `GET /api/tools/histograms/{video_id}`

Return the full per-video histogram document (UC-91/UC-93).

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/tools/histograms/<video_id>
```

### `PATCH /api/tools/histograms/{video_id}`

Partially update the ``phases`` boundaries of a histogram document.

Only a top-level ``phases`` key may be present; any other field
(``metrics``/``resampled``/``z_mean``/``scores``/``detections``/unknown)
is rejected with a 422, as is an empty phases object (UC-92). Phase-key/
field validation is delegated to the service/repository; its
``ValueError`` is translated to a 422 here. Returns the updated document,
or 404 when no histogram doc exists (UC-93).

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Request body** — `object` (media type: `optional`):

```json
{
  "type": "object",
  "additionalProperties": true,
  "title": "Payload"
}
```


**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X PATCH /api/tools/histograms/<video_id> \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/tools/jobs`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `status` | query | `string | null` | optional |  |
| `limit` | query | `integer` | optional (default `50`) |  |

**Responses**

- **200** — Successful Response — `list[object]`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/tools/jobs
```

### `GET /api/tools/jobs/{job_id}`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `job_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/tools/jobs/<job_id>
```

### `POST /api/tools/jobs/{job_id}/cancel`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `job_id` | path | `string` | required |  |

**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/tools/jobs/<job_id>/cancel \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `POST /api/tools/shift`

**Request body** — `tools__schemas__ShiftRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `src` | `string` | yes | Source video path |
| `start` | `number` | yes |  |
| `end` | `number` | yes |  |
| `out_dir` | `string | null` | no |  |
| `filename` | `string | null` | no |  |


**Responses**

- **200** — Successful Response — `ToolResponse`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/tools/shift \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/training/classes`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `name` | query | `string | null` | optional |  |

**Responses**

- **200** — Successful Response — `list[object]`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/training/classes
```

### `POST /api/training/classes`

**Request body** — `ClassCreate` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | `string` | yes |  |
| `hashtags` | `list[string]` | no |  |
| `min_videos` | `integer | null` | no |  |
| `min_windows` | `integer | null` | no |  |
| `cutter_config` | `object | null` | no |  |


**Responses**

- **201** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/training/classes \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `POST /api/training/classes/jobs`

**Request body** — `ClassCreate` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | `string` | yes |  |
| `hashtags` | `list[string]` | no |  |
| `min_videos` | `integer | null` | no |  |
| `min_windows` | `integer | null` | no |  |
| `cutter_config` | `object | null` | no |  |


**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/training/classes/jobs \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/training/classes/{class_id}`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/training/classes/<class_id>
```

### `PATCH /api/training/classes/{class_id}`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |

**Request body** — `ClassPatch` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | `string | null` | no |  |
| `hashtags` | `list[string] | null` | no |  |
| `min_videos` | `integer | null` | no |  |
| `min_windows` | `integer | null` | no |  |
| `cutter_config` | `object | null` | no |  |


**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X PATCH /api/training/classes/<class_id> \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `DELETE /api/training/classes/{class_id}`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |

**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X DELETE /api/training/classes/<class_id>
```

### `POST /api/training/classes/{class_id}/clip`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |

**Request body** — `SetClipRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `video_ids` | `list[string]` | yes |  |
| `clip` | `boolean` | no |  |


**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/training/classes/<class_id>/clip \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `POST /api/training/classes/{class_id}/embed`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |

**Request body** — `EmbedRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `video_ids` | `list[string]` | yes |  |
| `model_id` | `string | null` | no |  |


**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/training/classes/<class_id>/embed \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `POST /api/training/classes/{class_id}/extract`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |

**Request body** — `ExtractRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `video_ids` | `list[string]` | yes |  |
| `extraction_stride` | `integer | null` | no |  |


**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/training/classes/<class_id>/extract \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `POST /api/training/classes/{class_id}/process`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |

**Request body** — `ProcessRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `video_ids` | `list[string]` | yes |  |
| `stride` | `integer` | no |  |


**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/training/classes/<class_id>/process \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `POST /api/training/classes/{class_id}/promote`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |

**Request body** — `PromoteRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `video_ids` | `list[string]` | yes |  |
| `selected` | `boolean` | no |  |


**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/training/classes/<class_id>/promote \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `POST /api/training/classes/{class_id}/retrain`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |

**Request body** — `RetrainRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `classes` | `list[string]` | yes |  |
| `reembed` | `boolean` | no |  |
| `base_model` | `string | null` | no |  |
| `use_augmentation` | `boolean` | no |  |
| `use_class_weight` | `boolean` | no |  |


**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/training/classes/<class_id>/retrain \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/training/classes/{class_id}/stats`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/training/classes/<class_id>/stats
```

### `POST /api/training/classes/{class_id}/train`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |

**Request body** — `TrainRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `classes` | `list[string]` | yes |  |
| `reembed` | `boolean` | no |  |
| `use_augmentation` | `boolean` | no |  |
| `use_class_weight` | `boolean` | no |  |


**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/training/classes/<class_id>/train \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/training/classes/{class_id}/videos`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |
| `processed` | query | `boolean | null` | optional |  |
| `kind` | query | `string | null` | optional |  |
| `clip` | query | `boolean | null` | optional |  |
| `skip` | query | `integer` | optional (default `0`) |  |
| `limit` | query | `integer` | optional |  |

**Responses**

- **200** — Successful Response — `list[object]`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/training/classes/<class_id>/videos
```

### `POST /api/training/classes/{class_id}/videos`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |

**Request body** — `VideoCreate` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `local_path` | `string` | yes |  |
| `kind` | `string` | no |  |
| `parent_id` | `string | null` | no |  |
| `source` | `string` | no |  |


**Responses**

- **201** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/training/classes/<class_id>/videos \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `PUT /api/training/clips/{video_id}/phase-frames`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Request body** — `training__controllers__phase_frames__PhaseFramesRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `phase_frames` | `object` | yes |  |


**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X PUT /api/training/clips/<video_id>/phase-frames \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/training/jobs`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `status` | query | `string | null` | optional |  |
| `limit` | query | `integer` | optional (default `50`) |  |

**Responses**

- **200** — Successful Response — `list[object]`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/training/jobs
```

### `GET /api/training/jobs/{job_id}`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `job_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/training/jobs/<job_id>
```

### `POST /api/training/jobs/{job_id}/cancel`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `job_id` | path | `string` | required |  |

**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/training/jobs/<job_id>/cancel \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/training/models`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `mode` | query | `string | null` | optional |  |
| `status` | query | `string | null` | optional |  |

**Responses**

- **200** — Successful Response — `list[object]`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/training/models
```

### `GET /api/training/models/active`

**Responses**

- **200** — Successful Response — `object | null`


**Example**

```bash
curl -s -X GET /api/training/models/active
```

### `GET /api/training/models/chroma`

Lista las colecciones Chroma disponibles (embeddings_<run_id>, movement_embeddings...).

**Responses**

- **200** — Successful Response — `list[string]`


**Example**

```bash
curl -s -X GET /api/training/models/chroma
```

### `GET /api/training/models/{run_id}`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `run_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/training/models/<run_id>
```

### `POST /api/training/models/{run_id}/activate`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `run_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/training/models/<run_id>/activate \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `POST /api/training/models/{run_id}/approve`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `run_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/training/models/<run_id>/approve \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `POST /api/training/models/{run_id}/reject`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `run_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/training/models/<run_id>/reject \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `PATCH /api/training/videos/{video_id}`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Request body** — `VideoPatch` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `selected_for_training` | `boolean | null` | no |  |
| `clip` | `boolean | null` | no |  |
| `kind` | `string | null` | no |  |


**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X PATCH /api/training/videos/<video_id> \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/video/classes/{class_id}/clips`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |
| `status` | query | `string | null` | optional |  |

**Responses**

- **200** — Successful Response — `list[object]`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/video/classes/<class_id>/clips
```

### `POST /api/video/classes/{class_id}/clips/apply`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/video/classes/<class_id>/clips/apply \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `POST /api/video/classes/{class_id}/cut`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |

**Request body** — `CutRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sources` | `list[CutSource]` | yes |  |
| `cutter_override` | `object | null` | no |  |
| `model_id` | `string | null` | no |  |
| `chroma_only` | `boolean` | no |  |
| `config_id` | `string | null` | no |  |


**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/video/classes/<class_id>/cut \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/video/classes/{class_id}/uploads`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `list[object]`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/video/classes/<class_id>/uploads
```

### `POST /api/video/classes/{class_id}/videos`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `class_id` | path | `string` | required |  |



**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/video/classes/<class_id>/videos \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/video/clips/pending-counts`

**Responses**

- **200** — Successful Response — `object`


**Example**

```bash
curl -s -X GET /api/video/clips/pending-counts
```

### `DELETE /api/video/clips/{clip_id}`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `clip_id` | path | `string` | required |  |

**Responses**

- **204** — Successful Response
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X DELETE /api/video/clips/<clip_id>
```

### `POST /api/video/clips/{clip_id}/accept`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `clip_id` | path | `string` | required |  |

**Request body** — `AcceptRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `label` | `string | null` | no |  |


**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/video/clips/<clip_id>/accept \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `POST /api/video/clips/{clip_id}/decision`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `clip_id` | path | `string` | required |  |

**Request body** — `DecisionRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `decision` | `string | null` | no |  |


**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/video/clips/<clip_id>/decision \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `POST /api/video/clips/{clip_id}/discard`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `clip_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/video/clips/<clip_id>/discard \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/video/clips/{clip_id}/video`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `clip_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/video/clips/<clip_id>/video
```

### `GET /api/video/cutter-configs`

**Responses**

- **200** — Successful Response — `list[object]`


**Example**

```bash
curl -s -X GET /api/video/cutter-configs
```

### `POST /api/video/cutter-configs`

**Request body** — `CutterConfigCreate` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | `string` | yes |  |
| `params` | `object` | yes |  |


**Responses**

- **201** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/video/cutter-configs \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/video/cutter-configs/{config_id}`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `config_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/video/cutter-configs/<config_id>
```

### `PATCH /api/video/cutter-configs/{config_id}`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `config_id` | path | `string` | required |  |

**Request body** — `CutterConfigPatch` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | `string | null` | no |  |
| `params` | `object | null` | no |  |


**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X PATCH /api/video/cutter-configs/<config_id> \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `DELETE /api/video/cutter-configs/{config_id}`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `config_id` | path | `string` | required |  |

**Responses**

- **204** — Successful Response
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X DELETE /api/video/cutter-configs/<config_id>
```

### `GET /api/video/jobs`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `status` | query | `string | null` | optional |  |
| `limit` | query | `integer` | optional (default `50`) |  |

**Responses**

- **200** — Successful Response — `list[object]`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/video/jobs
```

### `GET /api/video/jobs/{job_id}`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `job_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/video/jobs/<job_id>
```

### `POST /api/video/jobs/{job_id}/cancel`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `job_id` | path | `string` | required |  |

**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/video/jobs/<job_id>/cancel \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `DELETE /api/video/shift/{temporal_id}`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `temporal_id` | path | `string` | required |  |

**Responses**

- **204** — Successful Response
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X DELETE /api/video/shift/<temporal_id>
```

### `POST /api/video/shift/{temporal_id}/commit`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `temporal_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/video/shift/<temporal_id>/commit \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/video/shift/{temporal_id}/video`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `temporal_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/video/shift/<temporal_id>/video
```

### `POST /api/video/videos/delete`

**Request body** — `DeleteVideosRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `video_ids` | `list[string]` | yes |  |


**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/video/videos/delete \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `DELETE /api/video/videos/{video_id}`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Responses**

- **204** — Successful Response
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X DELETE /api/video/videos/<video_id>
```

### `POST /api/video/videos/{video_id}/frame`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Request body** — `FrameRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `time` | `number` | yes |  |
| `caption` | `string | null` | no |  |


**Responses**

- **201** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/video/videos/<video_id>/frame \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/video/videos/{video_id}/metadata`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/video/videos/<video_id>/metadata
```

### `POST /api/video/videos/{video_id}/shift`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Request body** — `video__controllers__videos__ShiftRequest` (media type: `optional`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `start` | `number` | yes |  |
| `end` | `number` | yes |  |


**Responses**

- **202** — Successful Response — `object`
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X POST /api/video/videos/<video_id>/shift \
  -H 'Content-Type: application/json' \
  -d '<json-body>'
```

### `GET /api/video/videos/{video_id}/thumbnail`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/video/videos/<video_id>/thumbnail
```

### `GET /api/video/videos/{video_id}/video`

| Param | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `video_id` | path | `string` | required |  |

**Responses**

- **200** — Successful Response
- **422** — Validation Error — `HTTPValidationError`


**Example**

```bash
curl -s -X GET /api/video/videos/<video_id>/video
```

### `GET /health`

**Responses**

- **200** — Successful Response — `object`


**Example**

```bash
curl -s -X GET /health
```
