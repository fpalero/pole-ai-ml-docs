# Pole Agent — Implementation & Test Plan (v1.1)

**Date:** 2026-08-11
**Scope:** Conversational AI coaching agent + analysis features (Histogram Analyzer, Pose Correction) as a slice/package split inside the `pole-ai` monorepo.

**Design decisions:**
1. Reference statistics live in a **PostgreSQL** `reference_metrics` table.
2. LLM provider is **OpenCode** (`opencode serve`, OpenAI-compatible endpoint — supports multimodal models).
3. Chatbot transport is **WebSocket** (turn-by-turn).
4. Reusable logic lives in a new **`packages/pole-tools`** package.
5. API wiring lives in two new slices: **`tools`** and **`chatbot`**.
6. The `chatbot` slice may ONLY call the `tools` slice facade. It never imports `pole_ml`, `pole-crop`, or the DB directly.

**Prerequisite docs:** `agent_requirements.md`, `agent-react.md`, `pose_correction.md`, `docs/packages/pole_ml/project/pole-api-spec.md`.

---

## 1. Goals & Deliverables

| # | Deliverable | Purpose | Location |
|:-:|:------------|:--------|:---------|
| 1 | `packages/pole-tools` | Reusable, HTTP-free tools (Crop, Shift, Histogram, Pose, OpenCode LLM client) | `packages/pole-tools/` |
| 2 | `tools` API slice | FastAPI endpoints + `ToolsService` facade | `app/pola_api/src/tools/` |
| 3 | `chatbot` API slice | ReAct agent over WebSocket | `app/pola_api/src/chatbot/` |
| 4 | Histogram Analyzer | Phases, Z-score vs `reference_metrics`, deviation plot, OpenCode feedback | `packages/pole-tools/src/pole_tools/histogram_analyzer.py` |
| 5 | Pose Corrector | Detect bent knees / flexed feet / uneven hips on critical frame | `packages/pole-tools/src/pole_tools/pose_corrector.py` |

---

## 2. High-Level Architecture

### 2.1 Layered split

```text
pole-ui / CLI / Postman
        |
        | HTTP / WebSocket
        v
+-----------------------------+
| app/pola_api/src/chatbot/   |  (ReAct agent + WebSocket, session state)
+-------------+---------------+
              |
              | ONLY this dependency is allowed
              v
+-----------------------------+
| app/pola_api/src/tools/     |  (ToolsService facade + controllers + repositories)
+-------------+---------------+
              |
              v
+-----------------------------+
| packages/pole-tools/        |  (CropTool, ShiftTool, HistogramAnalyzer,
|  PoseCorrector, OpenCodeLLM)|
+------+------+------+--------+
       |      |      |
       v      v      v
  pole-crop  pole-train-model  opencode serve
```

### 2.2 Dependency rules

- `chatbot` -> `tools` slice only.
- `tools` slice -> `packages/pole-tools` + PostgreSQL repos.
- `packages/pole-tools` -> `pole-crop` (ffmpeg), `pole-train-model` (ML), `opencode` (LLM via `opencode serve`). No FastAPI imports.
- Enforce with a lightweight import linter in CI (e.g., forbid `pole_ml`/`pole_crop` imports under `src/chatbot/`).

---

## 3. Data Model (PostgreSQL)

Owned by the `tools` slice. Tables: `reference_metrics`, `reference_thresholds`, `attempt_logs`.

### `reference_metrics`
| Column | Type | Notes |
|--------|------|-------|
| `id` | SERIAL PK | |
| `trick_type` | VARCHAR(50) | STATIC / SPIN / MOMENTUM |
| `metric_name` | VARCHAR(50) | horizontal_speed, vertical_speed, angular_speed, wrist_stability |
| `phase` | VARCHAR(20) | ENTRANCE / EXECUTION / EXIT |
| `mean_array` | JSONB | Float[100] |
| `std_array` | JSONB | Float[100] |
| `gradient_array` | JSONB | Float[100] |

### `reference_thresholds`
| Column | Type | Notes |
|--------|------|-------|
| `trick_type` | VARCHAR(50) PK | |
| `config` | JSONB | LLM-generated thresholds + phase percentages |
| `created_date` | TIMESTAMP | |

### `attempt_logs`
| Column | Type | Notes |
|--------|------|-------|
| `attempt_id` | UUID PK | |
| `video_filename` | VARCHAR(255) | |
| `date_recorded` | TIMESTAMP | |
| `trick_type` | VARCHAR(50) | |
| `entrance_end_frame` | INTEGER | |
| `execution_end_frame` | INTEGER | |
| `total_frames` | INTEGER | |
| `phase_durations` | JSONB | seconds per phase |
| `critical_frame` | INTEGER | |
| `critical_phase` | VARCHAR(20) | |
| `critical_metric` | VARCHAR(50) | |
| `max_z_score` | FLOAT | |
| `ai_feedback` | TEXT | |
| `feedback_rating` | INTEGER | 1-5, future |

---

## 4. Implementation Phases

### Phase 0 — Foundation
- Create `packages/pole-tools/` (pyproject, src layout).
- Add `pole-tools` editable dep to root `pixi.toml`.
- Create `app/pola_api/src/tools/` and `app/pola_api/src/chatbot/` slices.
- Add `OPENCODE_URL`, `OPENCODE_MODEL`, `AGENT_MAX_ITERATIONS` to `.env.example`. `opencode serve` must run as a sidecar (OpenAI-compatible `/v1/chat/completions`).
- Add Postgres migrations for the three tables.

### Phase 1 — Reusable Tools Package
| Task | Reused asset |
|------|--------------|
| `OpenCodeLLMClient` (multimodal wrapper over `opencode serve`) | opencode (OpenAI-compatible) |
| `CropTool` (trick boundary detection) | `pole_tools.video_cutter` |
| `ShiftTool` (re-cut) | `pole-crop` (`crop_segment`) |
| `HistogramAnalyzer` skeleton + metrics | `pole_ml.processors.skeleton_extractor` |
| Trick classification STATIC/SPIN/MOMENTUM | new wrapper over metrics |
| Phase detection state machine + fallback | new code |
| Frame mapping, resampling, Z-score | new code |
| Deviation plot | matplotlib |
| LLM feedback prompt + parsing | `OpenCodeLLMClient` |
| `PoseCorrector` + overlay | algorithm from `pose_correction.md` |

### Phase 2 — Tools API Slice
- `ToolsService` facade: `crop`, `shift`, `analyze`, `correct`.
- Controllers: `POST /api/tools/crop`, `/shift`, `/analyze`, `/correct`.
- Repositories for the three Postgres tables.
- Map package exceptions to HTTP error responses.

### Phase 3 — Chatbot API Slice
- WebSocket endpoint `/ws/chatbot` with `session_id` handshake.
- `ChatbotSession` state: `original_video`, `current_crop`, `confirmed`, `history`.
- Session persistence (Postgres or Redis).
- ReAct agent bound to `ToolsService` only.
- Prompt enforces: Crop -> Confirm -> (Shift -> Confirm)* -> Analyze -> (Correct?).
- Graceful handling of malformed LLM output / parsing errors.

### Phase 4 — Integration & Hardening
- Register `tools` and `chatbot` routers in `main.py`.
- Rate limiting per session.
- Metrics/logging: tool latency, LLM tokens (from `opencode serve` usage), fallback rate.
- CLI demo for WebSocket conversation.
- Load test 5 concurrent sessions.

---

## 5. Testing Strategy

| Layer | Tooling | Coverage |
|-------|---------|----------|
| Unit (tools pkg) | `pytest` in `packages/pole-tools/tests/` | >= 80% |
| Unit (slices) | `pytest` in `app/pola_api/tests/` | >= 80% services |
| Integration | `TestClient` + `TestClient.websocket_connect` + mocked LLM | all endpoints |
| E2E | CLI demo + sample videos | 5 happy, 5 sad |
| Performance | locust / pytest-benchmark | section 8 targets |

Fixtures: `clean_invert.mp4`, `bent_knees_invert.mp4`, `fireman_spin.mp4`, `momentum_handspring.mp4`, `poor_lighting.mp4`, `untrimmed_practice.mp4`.

---

## 6. Feature-by-Feature Test Cases

### 6.1 Histogram Analyzer

**Happy path**
| ID | Scenario | Expected |
|:-:|:---------|:---------|
| HA-H1 | Clean STATIC trick | `STATIC`; phases within +/-2 frames; feedback < 10 s |
| HA-H2 | Known execution flaw | Critical frame in EXECUTION; Z > 2.0; red dot on plot |
| HA-H3 | SPIN trick | `SPIN`; angular-speed heuristics used |
| HA-H4 | MOMENTUM trick | `MOMENTUM`; vertical hip peak triggers transition |
| HA-H5 | Reference threshold discovery | Valid JSON in DB; `0 < entrance < execution < 100` |

**Sad path**
| ID | Scenario | Expected |
|:-:|:---------|:---------|
| HA-S1 | Poor video quality | Abort "ERROR: Poor video quality"; no LLM call |
| HA-S2 | Missing user height | Error asking for height |
| HA-S3 | Invalid/corrupt video | 400 before MediaPipe |
| HA-S4 | LLM (opencode) timeout / down | Retry once, then fallback advice |
| HA-S5 | Missing reference data | 422 "Reference thresholds not trained" |
| HA-S6 | Ambiguous trick | Default STATIC + warning |

### 6.2 Pose Corrector

**Happy path:** PC-H1 bent knee straightened on hip-ankle line; PC-H2 foot aligned with shin; PC-H3 hips leveled; PC-H4 auto critical frame; PC-H5 red/green overlay image.

**Sad path:** PC-S1 perfect pose (empty issues, original==corrected); PC-S2 missing landmarks (422); PC-S3 degenerate bone (skip leg); PC-S4 invalid frame number (400).

### 6.3 ReAct Chatbot (WebSocket)

**Happy path**
| ID | Scenario | Expected bot behavior |
|:-:|:---------|:----------------------|
| CA-H1 | Straight analysis | Crop -> Confirm -> Analyze -> Feedback |
| CA-H2 | One shift | Shift -> Confirm -> Analyze |
| CA-H3 | Multiple shifts | Tracks current crop; relative shifts |
| CA-H4 | Ask correction | Runs CorrectSkeletonPose after feedback |
| CA-H5 | Resume session | State restored via `session_id` |

**Sad path**
| ID | Scenario | Expected bot behavior |
|:-:|:---------|:----------------------|
| CA-S1 | Crop fails | Ask for manual timestamps |
| CA-S2 | Shift out of bounds | Clamp to 0; warn + re-confirm |
| CA-S3 | Analysis fails | Return error; offer new video; keep session |
| CA-S4 | LLM off-script | handle_parsing_errors; max iterations; ask rephrase |
| CA-S5 | Missing video | Ask "Which video?" |
| CA-S6 | Too many sessions | 429 or polite queue |

---

## 7. File Locations

```text
packages/pole-tools/
├── pyproject.toml
└── src/pole_tools/
    ├── __init__.py
    ├── schema.py               # shared Pydantic models
    ├── llm_client.py           # OpenCode wrapper (opencode serve)
    ├── crop_tool.py            # CropTool
    ├── shift_tool.py           # ShiftTool
    ├── histogram_analyzer.py   # full analyzer
    ├── pose_corrector.py       # PoseCorrector + overlay
    └── exceptions.py           # tool errors

app/pola_api/src/
├── tools/
│   ├── __init__.py
│   ├── services/tools_service.py      # facade for chatbot
│   ├── controllers/tools.py           # /api/tools/* endpoints
│   ├── repositories/reference_repository.py
│   ├── repositories/attempt_repository.py
│   └── schemas.py
└── chatbot/
    ├── __init__.py
    ├── services/agent_service.py      # ReAct loop
    ├── services/session_service.py    # session state
    ├── controllers/chatbot.py         # /ws/chatbot + /api/chatbot/*
    └── schemas.py

app/pola_api/tests/
├── unit/tools/       test_crop_tool.py, test_histogram.py, test_pose_corrector.py
├── unit/chatbot/     test_agent_service.py, test_session_service.py
└── integration/      test_tools_api.py, test_chatbot_ws.py

packages/pole-tools/tests/
├── fixtures/*.mp4
├── test_crop_tool.py
├── test_shift_tool.py
├── test_histogram_analyzer.py
└── test_pose_corrector.py
```

---

## 8. Non-Functional Verification

| Requirement | Target | Test |
|:------------|:-------|:-----|
| Video processing | < 10 s (5 s / 150 frames) | HA-H1 timed |
| Phase detection | < 100 ms | benchmark `detect()` |
| LLM feedback | < 8 s | HA-H1 timed, no upload |
| Phase accuracy | +/-3 frames | 10 labeled videos |
| Fallback rate | <= 5% | 50 test videos |
| Concurrency | 5 sessions | load test `/ws/chatbot` |
| Storage | 1000 attempt logs | insert + query latency |

---

## 9. Risks & Mitigations

| Risk | Mitigation |
|:-----|:-----------|
| MediaPipe `z` noisy | Restrict correction to x/y; side-view for 3D |
| LLM prompt drift (skips confirm) | Strict prompt + unit test on ReAct traces |
| `opencode serve` not running | Health-check at startup; return 503 "LLM unavailable" with fallback advice |
| ffmpeg missing | `FFMPEG_BIN` check at startup |
| Long video timeouts in CropTool | Downsampled frames for detection |
| Reference data missing | Explicit "not trained" error; run discovery first |

---

## 10. Reused Assets

| File / Module | Provides |
|:--------------|:---------|
| `opencode serve` (sidecar) | OpenAI-compatible `/v1/chat/completions` + multimodal |
| `pole_tools.video_cutter.VideoCutter` | crop boundary detection |
| `pole_crop.ffmpeg.crop_segment` | re-cut / shift |
| `pole_ml.processors.skeleton_extractor` | landmarks + metrics |
| `pole_tools.samples_info` | reference statistics pattern |
| `docs/packages/pole_ml/project/pole-api-spec.md` | backend/data conventions |

---

## 11. Acceptance Criteria

- [ ] `packages/pole-tools` importable and covered (>= 80%).
- [ ] `tools` slice endpoints work; errors map to HTTP codes.
- [ ] `chatbot` slice only imports from `tools` slice (CI check).
- [ ] WebSocket happy paths CA-H1..CA-H5 pass.
- [ ] Sad paths HA/PC/CA return graceful responses, no crashes.
- [ ] Performance targets in section 8 met.

---

## 12. Process-Data Split — DataExtractor / DataProcessor (PENDING APPROVAL)

**Status:** design only. This section supersedes the combined process-data flow. Breaking change (no backward compatibility; adjust failing tests).

### 12.1 Two-phase pipeline

```
Phase 1 — Extract (fills DB)                 Phase 2 — Process (reads DB)
┌──────────────────────────────┐            ┌──────────────────────────────────────────────┐
│ interface DataExtractor      │            │ interface DataProcessor                      │
│   └ LandmarkExtractor        │            │   ├ BiomechanicalDataProcessor → skeleton_windows
│      (refactor of existing   │            │   └ HistogramDataProcessor   → skeleton_histograms
│       SkeletonExtractor)     │            │   (list, executed in a loop)                 │
└──────────────────────────────┘            └──────────────────────────────────────────────┘
   writes videos.landmarks + extracted=true   each reads videos.landmarks from DB (never in-memory)
```

- **Phase 1 — `LandmarkExtractor.extract(video_id)`**: MediaPipe frame-by-frame over the video file, every `extraction_stride` frame; writes `videos.landmarks` and sets `videos.extracted = true`.
- **Phase 2 — processors run in a loop**, each `process(video_id)` reads `videos.landmarks` from Mongo:
  - `BiomechanicalDataProcessor` (renamed from "SlidingWindows"): per-frame 14 biomechanical features → 30-frame sliding windows → `skeleton_data.skeleton_windows` (schema unchanged).
  - `HistogramDataProcessor`: all 8 metrics M-01..M-08 → computes raw `metrics` + `resampled[300]` using the **user-set** `phase_frames` from the video doc → one doc per video in `skeleton_data.skeleton_histograms`.
- `process` validates `videos.extracted == true` before running.

### 12.2 Interfaces

```python
class DataExtractor:
    def extract(self, video_id: str) -> dict: ...

class DataProcessor:
    def process(self, video_id: str) -> dict: ...
```

### 12.3 `skeleton_histograms` document (one per video)

```json
{
  "video_id": "<mongo _id>",
  "trick_label": "handspring",
  "total_frames": 150,
  "extraction_stride": 5,
  "phase_frames": {
    "ENTRANCE":  [0, 45],
    "EXECUTION": [45, 102],
    "EXIT":      [102, 149]
  },
  "metrics": {
    "horizontal_speed":  [raw per-frame values...],
    "vertical_speed":    [raw per-frame values...],
    "angular_speed":     [raw per-frame values...],
    "wrist_stability":   [raw per-frame values...],
    "hip_angle":         [raw per-frame values...],
    "knee_angle":        [raw per-frame values...],
    "shoulder_angle":    [raw per-frame values...],
    "body_tilt_angle":   [raw per-frame values...]
  },
  "resampled": {
    "horizontal_speed": [300 values: ENTRANCE(0..99), EXECUTION(100..199), EXIT(200..299)]
  },
  "generated_at": "<utc timestamp>"
}
```

- `metrics` = raw per-frame values, no processing.
- `resampled` = 300 points per metric (100 per phase, ordered ENTRANCE → EXECUTION → EXIT).
- `phase_frames` = absolute frame indices (not percentages), **set manually by the user** and stored on the video document **before** processing runs (see 12.5). `HistogramDataProcessor` reads them from the DB — it never auto-detects phases.
- `metrics` and `resampled` are computed and stored by `HistogramDataProcessor`.
- Idempotent: delete + re-insert per video.

### 12.4 Config
- New `extraction_stride` (per-call param + env var, default 5) for extraction.
- Sliding window keeps its own `window_size=30` + `stride` (process param), unchanged.
- **Metric units are scale-free** (no real-world meters): angular speed (M-03) in **rad/s** (dimensionless); linear speeds (M-01/M-02) in **normalized units per second** computed from normalized landmarks. All 8 metrics M-01..M-08 are computed by default.
- **Two DBs, both env-configurable:** app DB `POLA_API_DB` (default `pola_api`, holds `videos` incl. `landmarks`/`phase_frames`) and ML data DB `SKELETON_DB` (default `skeleton_data`, holds `skeleton_windows` + `skeleton_histograms`). `LandmarkExtractor` writes **only** to the app DB `videos` collection; `BiomechanicalDataProcessor` and `HistogramDataProcessor` write **only** to the ML data DB. Processors accept a `database_name` constructor arg (defaults above); the API passes `settings.skeleton_db` / `settings.app_database`; CLI tools read the env vars directly.

### 12.5 Endpoints & CLI
- CLI: new `pixi run extract-data`; `process-data` becomes processing-only (reads from DB).
- API: new `POST /api/training/classes/{id}/extract`; existing `/process` now only processes and requires `extracted=true`.
- **Extract applies to clips only** (`kind == "clip"`); process also requires clips (as today).
- New endpoint to set phase frames manually (required before `process`): `PUT /api/training/clips/{id}/phase-frames` with `{ENTRANCE: [s,e], EXECUTION: [s,e], EXIT: [s,e]}` → stored on the video doc. If missing, `HistogramDataProcessor` skips that clip with a clear error.
- Job runnables return dicts so `_describe_done` builds readable descriptions; new keys: `extracted` ("extracted N clips"), `histograms` ("wrote N histograms").
- `embed` job unchanged (reads `skeleton_windows`).

### 12.6 Deferred (blocked on analysis work)
- Automatic phase detection (`PD-01..PD-03` thresholds in `agent_requirements.md`) was **removed** (PO decision 2026-08-13) — it is no longer a requirement. Phase boundaries are entered manually via the phase-frames endpoint; every histogram/analysis path requires explicit `phase_frames`.

### 12.7 Tests
- Full unit + integration matrix per phase in 12.9 (unit, API integration, CLI integration).

### 12.8 User use cases (mirror into `docs/app/pola_api/flows.md`, next numbers UC-82+)

| UC | Actor | Title | Happy path | Assertions |
|----|-------|-------|------------|------------|
| UC-82 | Analyst | Extract landmarks from clips | Select class → register clip(s) → `POST /classes/{id}/extract` → poll job → `done` | `videos[].extracted == true`, `videos[].landmarks` non-empty (frame/timestamp/33×4 + visibility_count) |
| UC-83 | Analyst | Set phase frames manually | After extract → `PUT /clips/{id}/phase-frames` `{ENTRANCE:[s,e], EXECUTION:[s,e], EXIT:[s,e]}` | Video doc stores `phase_frames`; persists across process |
| UC-84 | Analyst | Process biomechanical windows | extract + (optionally phase-frames) → `POST /classes/{id}/process` → job `done` | `skeleton_windows` docs created per video (30×14 features); `processed=true` |
| UC-85 | Analyst | Process histogram metrics | Same flow → process runs `HistogramDataProcessor` | One `skeleton_histograms` doc per video: raw `metrics` (8), `resampled` 300, `phase_frames` copied, `generated_at` |
| UC-86 | Coach/Analyst | View histogram analysis | `GET /clips/{id}/histogram` (or via chatbot later) | Returns raw + resampled + phase_frames + trick_label |
| UC-87 | Analyst | Cancel an extract job | `POST /jobs/{id}/cancel` while running | Job `stopped`; clips already done → `extracted=false` + `landmarks` removed (rollback) |
| UC-88 (sad) | Analyst | Process without extract | `POST /process` on non-extracted clip | Job fails with clear error; no windows/histograms written |
| UC-89 (sad) | Analyst | Extract a non-clip video | `POST /extract` with `kind != clip` | `422` "only clips can be extracted" |
| UC-90 (sad) | Analyst | Process histogram without phase-frames | `POST /process` (HistogramDataProcessor) on clip missing `phase_frames` | Clip skipped; `result_json.skipped` includes it with reason |

### 12.9 Testing strategy

**Separation principle:** same collection names, separate DBs — tests never touch prod data.

| Data | Prod DB | Test DB | Env var |
|------|---------|---------|---------|
| App data (classes, videos, jobs, clips, uploads...) | `pola_api` | `pole_api_testing` | `POLA_API_DB` |
| Windows + histograms | `skeleton_data` | `skeleton_data_testing` | `SKELETON_DB` |
| Chroma embeddings | `app/pola_api/FeaturesEmbeddings` | temp dir per session (`tmp_path`) | `CHROMA_PERSIST_DIR` |

- `app/pola_api/conftest.py`: rename `TEST_DATABASE = "pola_api_test"` → `"pole_api_testing"`; set `SKELETON_DB=skeleton_data_testing` before app creation; `clean_db` also clears `skeleton_data_testing.skeleton_windows` + `skeleton_histograms`; session teardown drops both `_testing` DBs.
- **Guard:** integration/conftest asserts env DB names end with `_testing` before running, so a misconfigured run can never target prod DBs.
- `core/config.py` gains `skeleton_db` (`SKELETON_DB`); API services pass both DB names into `pole_ml` processors.

**12.9.1 Unit tests** (pole-train-model package; fast; reuse `patch_mongo`/`patch_mediapipe_pose`/`patch_chroma` fixtures from `tests/conftest.py`; no real Mongo):
- Phase 1 — `LandmarkExtractor`:
  - frame dict shape (`frame`, `timestamp`, `landmarks` 33×4, `visibility_count`); normalization invariance (translation + scale); visibility filter ≥ 0.7; `extraction_stride` sampling; MediaPipe failure / missing file → error raised.
- Phase 2 — `BiomechanicalDataProcessor`:
  - 14 features per frame (3 angle triads × 3 + 2 velocity = 14); window shape `(30,14)`; stride; short-video zero-pad; writes `skeleton_windows` with existing schema (`window_id`, `features`, `label`, `video_id`, `selected_for_training`); reads landmarks from DB (in-memory fake), skips clip with no landmarks.
- Phase 2 — `HistogramDataProcessor`:
  - all 8 metrics M-01..M-08 present on synthetic landmarks with known motion (expected scale-free values); resampling → 100 per phase, total 300, ordering ENTRANCE→EXECUTION→EXIT; reads `phase_frames` from DB; missing `phase_frames` → skip + error; doc shape (12.3); delete+re-insert idempotency.

**12.9.2 Integration tests — API** (real Mongo on `_testing` DBs; `TestClient`; multi-call flows; MediaPipe real model on `sources/videos` fixtures, e.g. `clean_invert.mp4`, `momentum_handspring.mp4`):
- UC-82 extract flow: create class → register clip → `POST extract` → poll job → assert `videos[].extracted` + `landmarks`; assert docs live in `pole_api_testing.videos` (not prod).
- UC-83 phase-frames: `PUT /clips/{id}/phase-frames` → assert persisted on video doc.
- UC-84 biomechanical flow: UC-82/83 + `POST process` → poll → assert `skeleton_data_testing.skeleton_windows` docs (count, schema).
- UC-85 histogram flow: same → assert one `skeleton_histograms` doc: `metrics` length == sampled frames, `resampled` length == 300, `phase_frames` match, `generated_at` set.
- UC-87 cancel extract: start extract → cancel → job `stopped` + rollback (`extracted=false`, `landmarks` removed).
- Sad paths UC-88/89/90: process before extract, extract non-clip (422), histogram without phase-frames (`result_json.skipped`).
- Idempotency: re-run extract/process → no duplicate windows/histograms (delete+re-insert).
- Embed E2E (existing `test_process_integration.py`) adapted to run entirely against `pole_api_testing` + `skeleton_data_testing`.

**12.9.3 Integration tests — CLI** (subprocess or direct call with env `POLA_API_DB=pole_api_testing`, `SKELETON_DB=skeleton_data_testing`, `MONGODB_URI=test`; assert on `_testing` DBs):
- Seed a clip in `pole_api_testing.videos` → `extract-data` → assert `videos.landmarks` written + `extracted=true`.
- `process-data` (runs both processors) → assert `skeleton_data_testing.skeleton_windows` + `skeleton_histograms` docs.
- CLI `process-data` without prior extract → clear error + non-zero exit.
- CLI re-run → no duplicate docs (idempotent).
- CLI histogram with/without `--phase-frames` (skip path).
- CLI runs through `pixi run extract-data` / `pixi run process-data` with the env overrides.

---

### 12.10 Detailed implementation split (code changes)

**Goal:** Replace the combined `ProcessingPipeline.process_video()` (extract + windows in one pass) with two explicit phases.

#### 12.10.1 New files in `packages/pole-train-model/src/pole_ml/processors/`

| File | Purpose |
|------|---------|
| `data_extractor.py` | `DataExtractor` ABC + `LandmarkExtractor` (refactor of `SkeletonExtractor.extract_skeleton_sequence`). Writes `videos.landmarks` + `extracted=true` to app DB. |
| `data_processor.py` | `DataProcessor` ABC. |
| `biomechanical_processor.py` | `BiomechanicalDataProcessor` (renamed from sliding-window logic). Reads landmarks from app DB, computes 14 features/frame, builds 30-frame windows, writes `skeleton_data.skeleton_windows`. |
| `histogram_processor.py` | `HistogramDataProcessor`. Reads landmarks + `phase_frames` from app DB, computes 8 metrics M-01..M-08, resamples to 300 (100/phase), writes `skeleton_data.skeleton_histograms`. |

#### 12.10.2 `LandmarkExtractor` (in `data_extractor.py`)

```python
class DataExtractor(ABC):
    @abstractmethod
    def extract(self, video_id: str) -> dict: ...

class LandmarkExtractor(DataExtractor):
    def __init__(
        self,
        mongo_uri: str,
        app_db_name: str = "pola_api",
        model_path: str = "...",
        extraction_stride: int = 5,
        visibility_threshold: float = 0.7,
    ):
        self.mongo_uri = mongo_uri
        self.app_db_name = app_db_name
        self.extraction_stride = extraction_stride
        # reuse existing SkeletonExtractor logic internally
        self._extractor = SkeletonExtractor(
            model_path=model_path,
            visibility_threshold=visibility_threshold,
        )

    def extract(self, video_id: str) -> dict:
        # 1. Load video doc from app DB (videos collection)
        # 2. Run MediaPipe frame-by-frame with self.extraction_stride
        # 3. Produce list of frame dicts: {frame, timestamp, landmarks[33][4], visibility_count}
        # 4. Write to video doc: landmarks + extracted=true + extraction_stride
        # 5. Return summary: {"video_id": ..., "frames_extracted": N, "total_frames": M}
```

- Reuses: `SkeletonExtractor.extract_skeleton_sequence`, `normalize_coordinates`, `_filter_by_visibility` (private methods stay).
- **No** sliding windows, **no** biomechanical features, **no** `skeleton_data` DB writes.

#### 12.10.3 `BiomechanicalDataProcessor` (in `biomechanical_processor.py`)

```python
class DataProcessor(ABC):
    @abstractmethod
    def process(self, video_id: str) -> dict: ...

class BiomechanicalDataProcessor(DataProcessor):
    def __init__(
        self,
        mongo_uri: str,
        app_db_name: str = "pola_api",
        skeleton_db_name: str = "skeleton_data",
        window_size: int = 30,
        stride: int = 5,
    ):
        self.mongo_uri = mongo_uri
        self.app_db_name = app_db_name
        self.skeleton_db_name = skeleton_db_name
        self.window_size = window_size
        self.stride = stride
        # reuse feature extraction from SkeletonExtractor
        self._extractor = SkeletonExtractor(model_path="...")  # only for extract_biomechanical_features

    def process(self, video_id: str) -> dict:
        # 1. Read landmarks from app DB (videos collection)
        # 2. Validate extracted=true
        # 3. For each frame: compute 14 features via _extractor.extract_biomechanical_features
        # 4. Build sliding windows (window_size, stride) → (n_windows, 30, 14)
        # 5. Write windows to skeleton_db.skeleton_windows (existing schema)
        # 6. Return {"video_id": ..., "windows_created": N}
```

- Reuses: `SkeletonExtractor.extract_biomechanical_features`, `ProcessingPipeline._create_sliding_windows` (adapted to read from DB), `SkeletonStorage.save_skeleton_data`.
- **No** MediaPipe extraction, **no** landmark persistence.

#### 12.10.4 `HistogramDataProcessor` (in `histogram_processor.py`)

```python
class HistogramDataProcessor(DataProcessor):
    def __init__(
        self,
        mongo_uri: str,
        app_db_name: str = "pola_api",
        skeleton_db_name: str = "skeleton_data",
        extraction_stride: int = 5,
    ):
        ...

    def process(self, video_id: str) -> dict:
        # 1. Read landmarks + phase_frames from app DB
        # 2. If phase_frames missing → return {"skipped": True, "reason": "no phase_frames"}
        # 3. Compute 8 metrics per frame (M-01..M-08):
        #    - M-01 horizontal_speed: dx/dt of hip center X
        #    - M-02 vertical_speed: dy/dt of hip center Y
        #    - M-03 angular_speed: d(angle_torso)/dt
        #    - M-04 wrist_stability: rolling std of wrist distance (window=5)
        #    - M-05 hip_angle: angle(shoulder, hip, knee)
        #    - M-06 knee_angle: angle(hip, knee, ankle)
        #    - M-07 shoulder_angle: angle(elbow, shoulder, hip)
        #    - M-08 body_tilt_angle: angle(shoulder_mid, hip_mid, vertical)
        #    All in scale-free units (normalized coords/sec, rad/s).
        # 4. Resample each metric to 100 points per phase (3 phases = 300 total):
        #    np.interp(np.linspace(0, 1, 100), phase_normalized_positions, metric_values)
        # 5. Write histogram doc to skeleton_db.skeleton_histograms (delete+re-insert)
        # 6. Return {"video_id": ..., "metrics": 8, "resampled_points": 300}
```

- New metric computation (not in existing code). Uses landmarks from app DB.
- Resampling uses `phase_frames` (absolute frame indices) to segment the timeline.

#### 12.10.5 Database schema changes

**`pola_api` DB → `videos` collection** (add fields):
```json
{
  "landmarks": [
    {"frame": 0, "timestamp": 0.0, "landmarks": [[x,y,z,v]*33], "visibility_count": 28},
    ...
  ],
  "extracted": true,
  "extraction_stride": 5,
  "phase_frames": {"ENTRANCE": [0,45], "EXECUTION": [45,102], "EXIT": [102,149]}
}
```

**`skeleton_data` DB → `skeleton_histograms` collection** (new):
```json
{
  "video_id": "<mongo _id>",
  "trick_label": "handspring",
  "total_frames": 150,
  "extraction_stride": 5,
  "phase_frames": {"ENTRANCE": [0,45], "EXECUTION": [45,102], "EXIT": [102,149]},
  "metrics": {"horizontal_speed": [...], ...},
  "resampled": {"horizontal_speed": [300 values], ...},
  "generated_at": "2026-08-11T..."
}
```

#### 12.10.6 API changes (`app/pola_api/src/training/`)

| Endpoint | Controller | Service method | Job type |
|----------|------------|----------------|----------|
| `POST /classes/{id}/extract` | new `extract.py` | `ExtractService.extract` | `extract` |
| `PUT /clips/{id}/phase-frames` | new `phase_frames.py` | `VideoRepository.update` | (sync) |
| `POST /classes/{id}/process` | existing `process.py` | `ProcessService.process` (now runs processors list) | `process` |

**`ExtractService`** (new):
- Validates clips only (`kind == "clip"`).
- Submits `extract` job per video (or batch).
- Job runnable calls `LandmarkExtractor.extract(video_id)` for each.

**`ProcessService.process`** (modified):
- Validates `videos[].extracted == true`.
- Submits `process` job.
- Job runnable runs **both** processors in a loop:
  ```python
  processors = [
      BiomechanicalDataProcessor(...),
      HistogramDataProcessor(...),
  ]
  for p in processors:
      result = p.process(video_id)
      # accumulate results
  ```

#### 12.10.7 CLI tools (`packages/pole-train-model/src/pole_tools/`)

| Tool | File | Behavior |
|------|------|----------|
| `extract-data` | `extract_data.py` | Reads `POLA_API_DB`, `SKELETON_DB` env. Iterates videos in `videos` collection (or passed `--video-ids`), calls `LandmarkExtractor.extract`. |
| `process-data` | `process_data.py` (modified) | **No longer extracts**. Reads landmarks from `POLA_API_DB.videos`, runs `BiomechanicalDataProcessor` + `HistogramDataProcessor` per video. Validates `extracted=true`. |

#### 12.10.8 Config (`app/pola_api/src/core/config.py`)

Add to `Settings`:
```python
skeleton_db: str = "skeleton_data"      # from SKELETON_DB env
extraction_stride: int = 5               # from EXTRACTION_STRIDE env
```

#### 12.10.9 Reused assets (no duplication)

| Existing code | Reused in |
|---------------|-----------|
| `SkeletonExtractor.extract_skeleton_sequence` | `LandmarkExtractor` |
| `SkeletonExtractor.extract_biomechanical_features` | `BiomechanicalDataProcessor` |
| `ProcessingPipeline._create_sliding_windows` | `BiomechanicalDataProcessor` (adapted) |
| `SkeletonStorage.save_skeleton_data` | `BiomechanicalDataProcessor` |
| `VideoRepository` | `LandmarkExtractor`, `HistogramDataProcessor` (read) |
| `SkeletonRepository` | `HistogramDataProcessor` (no — writes to Mongo, not Chroma) |

#### 12.10.10 Removed / deprecated

- `ProcessingPipeline.process_video()` (combined extract+windows) — **deleted**.
- `run_process_windows()` in `embed_runner.py` — replaced by `ExtractService` + `ProcessService`.
- `pole_tools/process_data.py` combined logic — split into `extract_data.py` + updated `process_data.py`.

---

## 13. Shared Job Package & Chatbot Frontend

### 13.1 `packages/jobs` — shared job infrastructure

New pip-editable package (`packages/jobs`) used by **both** `app/pola_api` and `packages/chatbot`.

| Responsibility | Detail |
|----------------|--------|
| Job model | `Job(id, type, payload, status, progress, result, error, created_at, updated_at)` persisted in Mongo (`jobs` collection). |
| Queue | Redis (BullMQ or lightweight `rpush`/`blpop` + pub/sub). Workers consume; producers enqueue. |
| Events | `job:started`, `job:progress`, `job:done`, `job:error` published to Redis channels. |
| Worker base | Abstract `JobWorker` that loads a handler function (`Callable[[dict], Any]`) and emits progress. |
| FastAPI mixin | `JobRouter` exposing `POST /jobs`, `GET /jobs/{id}`, `WS /jobs/{id}/progress` (optional). |
| Retry / cancel | Configurable max retries, exponential backoff; `POST /jobs/{id}/cancel` → sets `stopped`. |

**Scope for v1:** only **new long tools** (crop, shift, future heavy tools) use `packages/jobs`. Existing training jobs (process, embed, retrain) stay in `app/pola_api` and can be migrated later.

### 13.2 Chatbot backend (`packages/chatbot`)

- Imports `packages.jobs` + `pole_tools`/`pole_ml`/`pole_crop` (service layer).
- ReAct agent registers tools as **job invocations** (fire-and-forget → returns `task_id` immediately).
- Redis listener subscribes to `job:progress` / `job:done` / `job:error` → forwards to the correct WebSocket via `ws_connection_id` stored in job payload.
- WebSocket message types:
  ```json
  {"type": "job_started", "task_id": "...", "tool": "crop"}
  {"type": "job_progress", "task_id": "...", "progress": 0.4, "stage": "encoding", "message": "Cutting clip 3/5"}
  {"type": "job_done", "task_id": "...", "result": {...}}
  {"type": "job_error", "task_id": "...", "error": "..."}
  ```

### 13.3 Two frontends

| Frontend | Purpose | Job tracking |
|----------|---------|--------------|
| **Training FE** (existing Angular) | LSTM pipeline: crawl → QC → cut → review → process → embed → retrain → promote | Polls `GET /api/jobs/{id}` via `app/pola_api` (proxies to `packages.jobs`). |
| **Chatbot FE** (new) | Video analysis: crop, shift, histogram, pose correction, similarity search, trick feedback | WebSocket from `packages/chatbot` (real-time push via `packages.jobs` events). |

Both FEs share the same job contract (`packages/jobs` — no duplication.

### 13.4 Wiring (pixi.toml)

```toml
[pypi-dependencies]
# existing...
pole-jobs = { path = "packages/jobs", editable = true }
chatbot = { path = "packages/chatbot", editable = true }
```

- `packages/chatbot/pyproject.toml`: `[project].dependencies = ["pole-jobs", "pole-tools", "pole-train-model", "pole-crop"]`
- `app/pola_api` adds `pole-jobs` to its deps (thin import for new job types).

### 13.5 Training chatbot (Path A shipped) → Path B extraction

**Status (PAIML-POLE-AGENT-014):** Path **A** is live as a thin ReAct agent
slice `app/pola_api/src/training_chatbot/` exposing `WS /ws/training-chat`
(full path `/api/training-chatbot/ws/training-chat`). It coaches data
scientists through the ML training workflow.

| Path | Description |
|------|-------------|
| **A. Slice in `pole_api` (shipped, v1)** | Thin ReAct agent + tools for training (hyperparameter search, model comparison, dataset stats, job inspection). Talks to `pole_ml` and `pole-jobs` through a single service facade (`TrainingFacade` — the only module allowed to import those packages). Single process, no proxy. |
| **B. Separate `packages/training-chatbot` (scale out)** | Mirrors `packages/chatbot` pattern. pola_api proxies `WS /ws/training-chat` → the training chatbot service. Independent scaling, same architecture as the video-analysis chatbot. |

#### FE WebSocket contract (identical for Path A and Path B)

- Client → server:
  - `{"type": "message", "message": "..."}` — one turn; a session is created lazily.
  - `{"type": "message", "message": "...", "session_id": S}` — resume session `S`.
  - `{"type": "resume", "session_id": S}` — resume a persisted session without a message.
- Server → client:
  - `{"type": "connected", "ws_connection_id": W}`.
  - `{"type": "agent_reply", "reply", "tool_calls"}` after each turn.
  - `{"type": "session_resumed", "session_id", "original_video"}` (`original_video` is
    empty for training sessions; kept for wire compatibility).
  - `{"type": "error", "error", ...}` — protocol/rate-limit errors, and on
    LLM-down: `{"type": "error", "error": "LLM unavailable", "status": 503,
    "fallback_advice": "..."}` (UC-AG-05).
  - relayed job events (`job_started` / `job_progress` / `job_done` /
    `job_error`) whose `ws_connection_id` matches the connection.

Training tools (all `sync`, wired via `ToolRegistry` on the shared ReAct core):
`hyperparameter_search`, `compare_models`, `dataset_stats`, `inspect_job`.

#### Path A → B extraction trigger

Extract Path A to `packages/training-chatbot` (Path B) when **any** of:

- **Traffic**: concurrent `WS /ws/training-chat` connections or per-second
  message volume outgrows the pola_api event loop budget (latency target
  < 100 ms round trip), making independent scaling desirable.
- **Tool set**: the tool registry grows beyond the four coaching tools (e.g.
  real grid-sweep jobs, dataset mutation, model activation) and needs its own
  worker fleet / rate limits decoupled from the video-analysis chatbot.
- **Failure isolation**: the training assistant should keep serving when
  pola_api or the video-analysis chatbot is down (or vice versa).

#### Extraction contract (Path B shape)

1. New package `packages/training-chatbot` mirrors `packages/chatbot`
   (ReAct core is already shared; only the system prompt, tool registry and
   `TrainingFacade` move out of `app/pola_api/src/training_chatbot/`).
2. pola_api keeps only a thin WS proxy — same frames, same `WS /ws/training-chat`
   path, same `session_id` resume semantics — so the FE (PAIML-POLE-AGENT-013
   or a future training FE) does not change.
3. `TrainingFacade` becomes the package's public boundary over `pole_ml` /
   `pole-jobs` (unchanged rule: no direct imports outside it).
4. Job events keep flowing through `pole_jobs` `JobEventPublisher`/subscriber;
   the proxy relays them filtered by `ws_connection_id`.
