# Implementation Plan — `pola_api` new `analysis` slice (Phase 13)

> **Status:** Planned (this document). Backend slice for the `pole_analyst` FE app
> (`docs/app/pole_analyst/PLAN.md`). Provides a dedicated upload + analyze + read surface,
> backed by a new **`analysis-db`** MongoDB database, decoupled from the training pipeline. In a
> future iteration this slice may be split into its own service.
>
> **Canonical API reference:** `docs/app/pola_api/POLE-API.md` (existing slices). This slice
> mirrors the repo's job model (§2 of that doc) and error envelope (`{detail}` + AppError
> hierarchy).

---

## 1. Feature Context & Objective

- **Goal:** Add an `analysis` slice (`/api/analysis`) to `pola_api` that the `pole_analyst` FE
  uses to (1) upload a user's video, (2) trigger an async analysis job that extracts skeletal
  landmarks and produces a per-video metric histogram, and (3) read back summary/histogram/pose
  data for the Summary/Histogram/Pose/Plan tabs.
- **Non-Functional Constraints:** async jobs with the repo's standard `pending → running → done |
  failed | stopped` lifecycle; error isolation (one video's failure must not fail the batch);
  no auth in v1 (Keycloak later); the FE depends on this contract, so shapes must be stable.
- **Affected Components:**
  - `app/pola_api/src/analysis/` — new router + controllers + schemas + service.
  - `app/pola_api/src/core/` — job registry (reuse `make_jobs_router`), DB connection for
    `analysis-db`, settings.
  - `app/pola_api/main.py` — mount the new router under `/api`.
  - Config/settings — new `ANALYSIS_DB` name + analysis upload folder env.
- **Assumptions:** reuses `pole_ml`/`pole_tools` processors (`SkeletonExtractor`,
  `HistogramDataProcessor`); the reference `mean`/`std` come from the existing
  `skeleton_data.signal_histograms` collection (written by `pole_fe`'s pipeline).

---

## 2. Architectural Layering (The "Where")

- **Domain:** `AnalysisVideo` (`_id`, `filename`, `local_path`, `analyzed`, `created_at`,
  `updated_at`), `SkeletonLandmarks` doc, `VideoHistogram` doc (`video_id`, `trick_label`,
  `phases`, `metrics`, `resampled`, `z_mean`, `scores`, `detections`), `AnalysisJob`.
- **Application:** `AnalysisService` with `upload_video`, `submit_analyze`, `get_video`,
  `list_videos`, `get_histogram`, `get_summary`, `get_pose`.
- **Infrastructure:** `analysis` Mongo collections in **`analysis-db`**: `videos`,
  `skeleton_landmarks`, `video_histograms`; a dedicated upload folder; `make_jobs_router` for
  `GET/POST /api/analysis/jobs/*`. Reads the reference stats from `skeleton_data` (existing DB).
- **Presentation:** FastAPI router `APIRouter(prefix="/analysis")` under `/api`.

---

## 3. Implementation Roadmap (Atomic Steps)

### Phase A: Slice skeleton + upload
- [ ] Infra Add `analysis` settings (DB name `analysis-db`, upload folder) + Mongo client for
  `analysis-db`.
- [ ] Infra `POST /api/analysis/videos` (multipart `.mp4`) → save to dedicated folder, create
  `videos` doc (`analyzed=false`), return `202 {job_id}` (verify job) or `201` doc.
- [ ] Infra `GET /api/analysis/videos` (list, with `analyzed` flag) + `GET
  /api/analysis/videos/{video_id}` + thumbnail/stream endpoints.
- [ ] Infra `GET /api/analysis/jobs` + `GET /api/analysis/jobs/{job_id}` + `POST
  /api/analysis/jobs/{job_id}/cancel` (reuse `make_jobs_router`).

### Phase B: Analyze job (extract → histogram → flag)
- [ ] App `POST /api/analysis/videos/{video_id}/analyze` → `202 {job_id}`.
- [ ] App worker: (1) extract skeleton landmarks → `analysis-db.skeleton_landmarks`; (2) run
  `HistogramDataProcessor` → `analysis-db.video_histograms` (one-per-video); (3) compute scores
  against `skeleton_data.signal_histograms` `mean`/`std`; (4) set `videos.analyzed=true`.
- [ ] App error isolation: no landmarks detected → job ends `done` with a
  `failed/skipped` entry + reason (e.g., `no_skeleton_detected`), leaving `analyzed=false`.

### Phase C: Read endpoints (Summary / Histogram / Pose)
- [ ] App `GET /api/analysis/videos/{video_id}/histogram` → `video_histograms` doc.
- [ ] App `GET /api/analysis/videos/{video_id}/summary` → `z_mean`, `scores`, `detections`,
  `critical_frame/phase/metric`.
- [ ] App `GET /api/analysis/videos/{video_id}/pose` → annotated frame (`frame_image_path` /
  overlay) + `issues`.

### Phase D: Tests
- [ ] Test unit + integration tests against `analysis_db_testing` (guarded by
  `scripts/guard-testing-db.sh`), covering upload, analyze job lifecycle, error isolation, and
  read endpoints.

---

## 4. Quality Gates & Testing Commands (DoD)

- **Unit Tests:** `pixi run test-api` (`pytest -v`, cwd `app/pola_api`, `PYTHONPATH=src`).
- **Integration Tests:** same suite with `POLA_API_DB=pole_api_testing`,
  `SKELETON_DB=skeleton_data_testing`, `ANALYSIS_DB=analysis_db_testing` + `E2E_FAKES=1`.
- **Database Target:** `analysis_db_test` (new) + `skeleton_data_test` (read-only reference).
- **Coverage Requirement:** ≥ 80% (repo default).
- **Additional Checks:** lint/typecheck per repo; `POLE-API.md` updated with the new slice.

---

## 5. Defined Use Cases (Gherkin + Technical Matrix)

### UC-A1: Upload video
- **Given** the analysis upload folder is writable
- **When** the client `POST /api/analysis/videos` with an `.mp4` file
- **Then** the system returns `202 {job_id}` (or `201` video doc)
- **And** `analysis-db.videos` has a doc with `analyzed=false`

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/analysis/videos` |
| Request Method | POST (multipart) |
| Payload Example | `file=@clip.mp4` |
| DB State (After) | `analysis-db.videos` doc (`analyzed=false`) |

### UC-A2: Analyze (happy path)
- **Given** an uploaded video
- **When** `POST /api/analysis/videos/{video_id}/analyze`
- **Then** `202 {job_id}`; job extracts landmarks → `analysis-db.skeleton_landmarks`, writes
  `analysis-db.video_histograms`, sets `analyzed=true`

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/analysis/videos/{video_id}/analyze` |
| Request Method | POST |
| DB State (Before) | `videos.analyzed=false` |
| DB State (After) | `skeleton_landmarks` + `video_histograms` docs; `analyzed=true` |

### UC-A3: Read summary / histogram / pose
- **Given** an analyzed video
- **When** `GET /api/analysis/videos/{video_id}/{summary,histogram,pose}`
- **Then** `200` with the stored data (summary computed from `skeleton_data.signal_histograms`
  `mean`/`std` vs `video_histograms`)

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/analysis/videos/{video_id}/{summary,histogram,pose}` |
| Request Method | GET |
| DB State | read-only |

### UC-A4: No skeleton detected (edge)
- **Given** a video where extraction finds no landmarks
- **When** analyze runs
- **Then** the job ends `done` with a `failed/skipped` entry (`reason=no_skeleton_detected`),
  `analyzed` stays `false`, and the FE surfaces "low quality, re-record"

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/analysis/videos/{video_id}/analyze` |
| DB State (After) | `videos.analyzed=false`; job `done` + failure reason |

### UC-A5: Invalid upload
- **Given** a non-`.mp4` or oversized file
- **When** `POST /api/analysis/videos`
- **Then** `422 {"detail":[...]}` and no `analysis-db.videos` doc

---

## 6. Risks and Mitigations

- **Risk:** `skeleton_data.signal_histograms` may be empty (no reference data yet).
  **Mitigation:** summary endpoint returns a clear "reference data unavailable" 422 rather than
  dividing by zero; FE degrades gracefully.
- **Risk:** new DB/settings ripple through deployment config.
  **Mitigation:** follow the existing slice wiring exactly; add `ANALYSIS_DB` to `.env.example`
  and the testing guard.
- **Risk:** duplicate job/worker logic. **Mitigation:** reuse `make_jobs_router` + the shared job
  worker pattern already in `core/jobs.py`.

## 7. Open Questions and Decisions

- **D-A1:** endpoint shapes above are proposals; finalize `upload` (201 vs 202) and `pose`
  (stored vs on-demand) at ticket time.
- **D-A2:** the analyze job reuses `HistogramDataProcessor` but writes to `analysis-db`
  collections instead of `skeleton_data.skeleton_histograms` — confirm the processor accepts a
  target collection/db override (or add one).
- **D-A3:** `analysis-db` naming in env (`ANALYSIS_DB=analysis_db`) to be confirmed with the
  deployment/config owner.
