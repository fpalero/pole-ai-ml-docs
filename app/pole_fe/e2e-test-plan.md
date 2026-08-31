# `pole_fe` — E2E Test Plan (Playwright, FE + BE)

> **Status:** authoritative definition of `E2E-1..E2E-23`. Replaces the draft table in
> `docs/app/pole_fe/implementation-plan.md` §8.2. Each scenario is given as
> Given / When / Then + the exact endpoint(s) exercised + the database assertion.
>
> **Driver:** Playwright (`@playwright/test`) in `app/pole_fe/e2e/`.
> **Backend under test:** a real `uvicorn` instance running with
> `POLA_API_DB=pole_api_testing`, `SKELETON_DB=skeleton_data_testing`, a **temp**
> `CHROMA_PERSIST_DIR`, and `E2E_FAKES=1` (see §"Fakes convention").
>
> **Classes are stateless.** There is no stored class status. The "stage" shown in the UI is
> **derived** by the FE from related entities (uploads / posts / clips / windows / model_runs).
> Scenarios below assert derived UI stage + DB state, never a stored `status` field on `classes`.

---

## 0. Fakes / seeding convention

Real MediaPipe + ffmpeg + ChromaDB + MongoDB are used (already containerized/available).
Three heavy, externally-dependent steps are **stubbed** via the backend's E2E fake mode
(`E2E_FAKES=1`), mirroring the fakes already in `app/pola_api/tests/test_e2e.py`:

| Step | Real path | E2E fake | Why |
|------|-----------|----------|-----|
| Crawl (Instagram) | `pole_crawler.InstagramClient` + `DiskWriter` | `FakeInstagramClient` (returns one post) + `FakeDiskWriter` | No network/session needed |
| Cut (VideoCutter) | `pole_tools.VideoCutter` + ffmpeg + model | `FakeCutter` (writes a tiny `.mp4`) | Deterministic, no LSTM/Chroma prerequisite |
| Extract (landmarks) | `LandmarkExtractor` (MediaPipe) | `fake_run_extract` (sets `extracted=true` + phase_frames) | Fast; `process` requires `extracted=true` |
| Process (windows+histograms) | `BiomechanicalDataProcessor` + `HistogramDataProcessor` (MediaPipe) | `fake_run_process` (3 dummy windows, marks processed) | Fast, mirrors `test_e2e.py` |
| Embed (Chroma) | `run_embed` → ChromaDB | `fake_run_embed` (marks windows embedded) | Fast, mirrors `test_e2e.py` |
| Train (LSTM full) | `ProcessingPipeline.train_model_normal` + `save_windows_embeddings` | `FakePipeline` (stub `.keras`/metadata) | "mock/skip heavy LSTM training" |
| Retrain (fine-tune) | `ProcessingPipeline.fine_tune_model` | `FakePipeline` | same |

The four stubs mirror the four fakes already in `app/pola_api/tests/test_e2e.py`
(`_patch_crawler` / `_patch_cutter` / `_patch_embed` / `_patch_training`). Everything else is
**real**: `/health`, jobs (thread runner), stats, model registry, and the live FE/backend HTTP
round-trip. The **real MediaPipe + ChromaDB + ffmpeg** paths for `extract`/`process`/`embed`/upload
are covered by the backend integration suite (`pixi run test-api` →
`test_process_integration.py`, `test_upload_integration.py`) and the CLI integration tests
(`pixi run test`), which keep the Playwright suite fast and deterministic.

> **Known gap:** the upload endpoint currently marks uploads `verified` but does **not** auto-embed
> (no windows/embeddings are written) — see E2E-03.

Each E2E spec file seeds/cleans its own data through the API (Playwright `request` context) and
asserts DB state through the API surface (`/stats`, `/models/active`, `/videos`, `/clips`, `/jobs`)
or, where a raw collection check is required, a `mongosh`/`pymongo` helper run against the
`_testing` DBs. **No test ever targets `pola_api` / `skeleton_data` (prod).**

---

## 1. The 23 scenarios

### E2E-01 — Workflow A: create a trick
- **Category:** Workflow A (create → upload → auto-embed → verify → stats ready)
- **Seeded/Stubbed:** none
- **Given** the Tricks page is open and no class named `e2e_a_<ts>` exists
- **When** the user opens the New Trick modal, fills name + hashtags, clicks **Create**
- **Then** `POST /api/training/classes` → `201`; a success toast appears; the new card shows in the list
  with the derived **DRAFT** stage
- **Endpoint(s):** `POST /api/training/classes`
- **DB assertion:** `GET /api/training/classes?name=e2e_a_<ts>` returns exactly one class with the
  submitted `hashtags`.

### E2E-02 — Workflow A: batch upload (auto-embed)
- **Category:** Workflow A
- **Seeded/Stubbed:** real MediaPipe + Chroma (temp dir)
- **Given** a trick created in E2E-01 and ≥1 small `.mp4` fixture
- **When** the user drops the file(s) on the upload zone and clicks **UPLOAD & PROCESS**
- **Then** `POST /api/video/classes/{id}/videos` (multipart) → `202 {job_id, uploads[]}`;
  the job card polls `GET /api/video/jobs/{job_id}` to `done`; uploads transition `pending → verified`
- **Endpoint(s):** `POST /api/video/classes/{id}/videos`, `GET /api/video/jobs/{id}`
- **DB assertion:** `GET /api/video/classes/{id}/uploads` → upload `status="verified"`;
  `GET /api/training/classes/{id}/videos` → one `source="upload"` video.

### E2E-03 — Workflow A: verify upload → stats reachable
- **Category:** Workflow A
- **Seeded/Stubbed:** none
- **Given** a verified upload from E2E-02
- **When** the user confirms verification (`POST .../uploads/{uid}/verify {accepted:true}`) and opens
  the **Stats** tab
- **Then** the verify returns `200` with the upload `verified`, and `GET /stats` returns `200` with
  the `samples_info` structure
- **Endpoint(s):** `POST /api/video/classes/{id}/uploads/{uid}/verify`, `GET /api/training/classes/{id}/stats`
- **DB assertion:** upload `status="verified"`; `stats` responds `200`.
- **Note:** the current upload backend **auto-verifies** uploads (`status="verified"` after the job)
  and does **not** implement `POST /uploads/{uid}/verify` nor auto-embed (no windows/embeddings are
  written), so neither `verify` nor `readiness` is asserted here — a documented gap, not an E2E
  failure.

### E2E-04 — Workflow A (error): reject non-.mp4 upload
- **Category:** Workflow A — error state
- **Seeded/Stubbed:** none
- **Given** a trick and a non-`.mp4` file (e.g. `.txt`)
- **When** the user drops it on the upload zone
- **Then** the zone rejects it with "Only .mp4 files accepted" (client-side) — no `POST` is issued;
  if it reaches the API, `422` is returned
- **Endpoint(s):** `POST /api/video/classes/{id}/videos` (only if client validation is bypassed)
- **DB assertion:** `GET /api/video/classes/{id}/uploads` unchanged (no new upload).

### E2E-05 — Workflow B: launch crawl (stubbed Instagram)
- **Category:** Workflow B (create → crawl → QC → cut → clip accept → process → embed → train → approve)
- **Seeded/Stubbed:** `FakeClient`/`FakeStorage` (E2E fake mode)
- **Given** a trick created in the UI
- **When** the user fills the crawl form (tags from hashtags, limit) and clicks **EXECUTE CRAWL**
- **Then** `POST /api/crawler/classes/{id}/crawl` → `202 {job_id}`; job polls to `done` with
  `downloaded_count ≥ 1`; one post appears with `qc_status="pending"`
- **Endpoint(s):** `POST /api/crawler/classes/{id}/crawl`, `GET /api/crawler/jobs/{id}`
- **DB assertion:** `GET /api/crawler/classes/{id}/posts` → ≥1 post, `qc_status="pending"`,
  `source="crawler"`.

### E2E-06 — Workflow B: QC accept a post
- **Category:** Workflow B
- **Seeded/Stubbed:** none
- **Given** a pending post from E2E-05
- **When** the user marks it **Accept** in QC
- **Then** `POST /api/crawler/posts/{post_id}/qc {status:"accepted"}` → `200`; the post shows accepted
- **Endpoint(s):** `POST /api/crawler/posts/{post_id}/qc`
- **DB assertion:** post `qc_status="accepted"` (retrieved via `GET /api/crawler/classes/{id}/posts`).

### E2E-07 — Workflow B: cut sources into clips (stubbed cutter)
- **Category:** Workflow B
- **Seeded/Stubbed:** `FakeCutter` (E2E fake mode)
- **Given** ≥1 accepted post (E2E-06)
- **When** the user runs **Crop AI** (bulk cut) with the accepted post as source
- **Then** `POST /api/video/classes/{id}/cut` → `202 {job_id}`; job polls to `done` with `clips ≥ 1`;
  clips show in the Clips tab as `pending`
- **Endpoint(s):** `POST /api/video/classes/{id}/cut`, `GET /api/video/jobs/{id}`
- **DB assertion:** `GET /api/video/classes/{id}/clips?status=pending` → ≥1 clip with `local_path` on disk.

### E2E-08 — Workflow B: clip editor accept
- **Category:** Workflow B (clip editor journey)
- **Seeded/Stubbed:** none (clip already cut by the fake cutter)
- **Given** a pending clip from E2E-07
- **When** the user opens the clip editor, optionally trims/crops, and clicks **Accept** (PROMOTE)
- **Then** `POST /api/video/clips/{clip_id}/accept {label, cutter_config?}` → `200`; clip becomes
  `accepted`; a trainable `kind="clip"` video is registered
- **Endpoint(s):** `GET /api/video/clips/{clip_id}/video`, `POST /api/video/clips/{clip_id}/accept`
- **DB assertion:** clip `status="accepted"`, `label` = class name; `GET /api/training/classes/{id}/videos`
  shows a `source="cut"` / `kind="clip"` video.

### E2E-09 — Workflow B: extract + process clips → windows (stubbed)
- **Category:** Workflow B
- **Seeded/Stubbed:** `fake_run_extract` + `fake_run_process` (E2E fake mode); `_testing` DBs
- **Given** an accepted clip from E2E-08
- **When** the user runs **Extract** then **Process** (stride 5)
- **Then** `POST /api/training/classes/{id}/extract` and `POST /api/training/classes/{id}/process`
  each return `202`; both jobs poll to `done`; the video shows "processed"
- **Endpoint(s):** `POST /api/training/classes/{id}/extract`, `POST /api/training/classes/{id}/process`, `GET /api/training/jobs/{id}`
- **DB assertion:** `GET /api/training/classes/{id}/stats` → `windows_total > 0`;
  `skeleton_data_testing.skeleton_windows` has docs with `label` = class.

### E2E-10 — Workflow B: embed clips (stubbed)
- **Category:** Workflow B
- **Seeded/Stubbed:** `fake_run_embed` (E2E fake mode)
- **Given** processed windows from E2E-09
- **When** the user runs **Embed** on the same clip
- **Then** `POST /api/training/classes/{id}/embed` → `202`; job polls to `done` with `embedded > 0`
- **Endpoint(s):** `POST /api/training/classes/{id}/embed`, `GET /api/training/jobs/{id}`
- **DB assertion:** `stats.samples_info.windows_embedded > 0`; the video's `embedding_models` is non-empty.

### E2E-11 — Workflow B: train full (stubbed LSTM)
- **Category:** Workflow B
- **Seeded/Stubbed:** fake `train_model_normal` + `save_windows_embeddings` (E2E fake mode)
- **Given** embedded windows (E2E-10) and ≥2 classes selected
- **When** the user starts training from the Training Studio (mode = Train from Scratch)
- **Then** `POST /api/training/classes/{id}/train` → `202 {job_id, run_id}`; job polls to `done`;
  a run appears in the Model Registry as `done` (not active)
- **Endpoint(s):** `POST /api/training/classes/{id}/train`, `GET /api/training/jobs/{id}`
- **DB assertion:** `GET /api/training/models/{run_id}` → `status="done"`, `active=false`;
  `GET /api/training/models/active` → `null`.

### E2E-12 — Workflow B: approve & activate
- **Category:** Workflow B
- **Seeded/Stubbed:** none
- **Given** a `done` run from E2E-11
- **When** the user reviews the run and clicks **Approve & Activate**
- **Then** `POST /api/training/models/{run_id}/approve` → `200 {status:"active"}`; the ActiveModelBanner
  updates to the new run
- **Endpoint(s):** `POST /api/training/models/{run_id}/approve`, `GET /api/training/models/active`
- **DB assertion:** `GET /api/training/models/active` → `run_id` matches the approved run.

### E2E-13 — Workflow C: retrain fine-tune with a new class (stubbed)
- **Category:** Workflow C (retrain fine-tune)
- **Seeded/Stubbed:** fake fine-tune trainer (E2E fake mode)
- **Given** an active base model (E2E-12) and a new class with embedded windows
- **When** the user opens Training Studio, selects **Fine-tune Existing**, picks the base model, selects
  the new class, and starts training
- **Then** `POST /api/training/classes/{id}/retrain {classes:[new], base_model}` → `202 {job_id, run_id}`;
  job polls to `done`; the new run's encoder includes the base + new classes (n+1)
- **Endpoint(s):** `POST /api/training/classes/{id}/retrain`, `GET /api/training/models/{run_id}`
- **DB assertion:** `GET /api/training/models/{run_id}` reports `classes` = base ∪ new (n+1);
  `status="done"`, `active=false` until approved.

### E2E-14 — Trick CRUD: edit
- **Category:** Trick CRUD
- **Seeded/Stubbed:** none
- **Given** an existing trick
- **When** the user opens Edit, changes the hashtags, and saves
- **Then** `PATCH /api/training/classes/{id}` → `200`; the card reflects the new hashtags
- **Endpoint(s):** `PATCH /api/training/classes/{id}`
- **DB assertion:** `GET /api/training/classes/{id}` → `hashtags` updated.

### E2E-15 — Trick CRUD: delete (cascade job)
- **Category:** Trick CRUD
- **Seeded/Stubbed:** none
- **Given** an existing trick
- **When** the user clicks Delete and confirms
- **Then** `DELETE /api/training/classes/{id}` → `202 {job_id}` (cascade `delete_class` job); the trick
  disappears from the list
- **Endpoint(s):** `DELETE /api/training/classes/{id}`, `GET /api/training/jobs/{id}`
- **DB assertion:** `GET /api/training/classes/{id}` → `404` after the job reaches `done`.

### E2E-16 — Jobs: dashboard polls to completion
- **Category:** Jobs dashboard
- **Seeded/Stubbed:** none (a short crawl/cut fake job drives the polling)
- **Given** a job started from another flow
- **When** the user navigates to `/jobs`
- **Then** the active job card shows live progress (`GET /{slice}/jobs/{id}` every ~3s), then moves to
  history as **Done** when it reaches terminal state
- **Endpoint(s):** `GET /{slice}/jobs/{id}` (polled)
- **DB assertion:** the job document reaches `status ∈ {done, failed}`; history reflects it.

### E2E-17 — Jobs: cancel a running job (rollback)
- **Category:** Jobs dashboard
- **Seeded/Stubbed:** none (a long-running fake job)
- **Given** a running job
- **When** the user clicks **Cancel** and confirms
- **Then** `POST /{slice}/jobs/{id}/cancel` → `202`; the job ends `stopped` and its effects are rolled
  back per type
- **Endpoint(s):** `POST /{slice}/jobs/{id}/cancel`, `GET /{slice}/jobs/{id}`
- **DB assertion:** job `status="stopped"`; the rolled-back entities are absent.

### E2E-18 — Model registry: list + activate + reject
- **Category:** Model registry
- **Seeded/Stubbed:** none
- **Given** ≥2 completed runs (from E2E-11 / E2E-13)
- **When** the user lists runs, activates one, and rejects another
- **Then** `GET /api/training/models` lists them; `POST /api/training/models/{run_id}/activate` flips the
  active pointer; `POST /api/training/models/{run_id}/reject` marks the other `rejected`
- **Endpoint(s):** `GET /api/training/models`, `POST .../activate`, `POST .../reject`
- **DB assertion:** `GET /api/training/models/active` → the activated run; the rejected run is `rejected`
  and not active.

### E2E-19 — Error states: duplicate class + job failure toast
- **Category:** Error states
- **Seeded/Stubbed:** a fake crawl that raises (rate-limit) for the failure toast
- **Given** an existing trick `e2e_dup`
- **When** the user tries to create a trick with the same name, and separately triggers a crawl that
  fails server-side
- **Then** `POST /api/training/classes` → `409` mapped to the inline "This trick name already exists"
  error; the failing crawl job shows a **Failed** card/toast with the error message
- **Endpoint(s):** `POST /api/training/classes`, `POST /api/crawler/classes/{id}/crawl`
- **DB assertion:** class count unchanged (no duplicate); crawl job `status="failed"` with non-empty `error`.

### E2E-20 — Responsive smoke (tablet + mobile)
- **Category:** Responsive
- **Seeded/Stubbed:** none
- **Given** the app running
- **When** the viewport is set to 768px (tablet) and then 375px (mobile), navigating Tricks / Jobs /
  Model Registry
- **Then** the sidebar collapses / bottom-nav appears, video grid reflows to single column, and **no
  console errors** are emitted on any page
- **Endpoint(s):** page loads (no specific mutation)
- **DB assertion:** n/a (read-only smoke); asserts `page.on('console')` error count == 0.

### E2E-21 — Phase 9 happy path: extract → capture phases → Histo → chart + summary
- **Category:** Phase 9 (Extraction → Process biometric+histogram flow)
- **Seeded/Stubbed:** `fake_run_extract` + `fake_run_process` (E2E fake mode); real uploaded mp4;
  the histogram job runs the **real** `HistogramDataProcessor` against the fake-extracted landmarks
- **Given** a class with an uploaded clip (marked `clip=true`) from the setup helper
- **When** the user runs **Extract** (polled), opens the **Biomechanical Signal Analysis** panel
  BEFORE Histo, closes it, captures **Start / Execution / Exit / End** phase frames, runs **Histo**
  (polled), and reopens the panel
- **Then**
  - `POST /api/training/classes/{id}/extract` → `202 {job_id}`; job polls to `done`
  - the panel **before** Histo shows the Q2 empty state (`No histogram found for this clip`), with
    **no chart, no annotation strip, no capture buttons**
  - `PUT /api/training/clips/{video_id}/phase-frames` persists the captured bounds
  - `POST /api/tools/histograms/analysis` → `202 {job_id}`; job polls to `done`
  - the panel **after** Histo renders the synchronized chart (`.signal-chart`, 8 readout cells,
    annotation strip, 4 capture buttons); clicking the capture buttons PUTs phase-frames and shows
    the `Phase frames saved` feedback (announced via an `aria-live` region)
  - `GET /api/tools/histograms/{video_id}` → `200` with `metrics`/`resampled`
  - `GET /api/tools/histograms/summary/{video_id}` → `200` with `z_mean`/`scores`/`detections`
  - **no console errors** in the whole flow; the job-completion `aria-live` announcements are
    present (Extract/Biomech/Histo)
- **Endpoint(s):** `POST /api/training/classes/{id}/extract`, `GET /api/training/jobs/{id}`,
  `PUT /api/training/clips/{video_id}/phase-frames`, `POST /api/tools/histograms/analysis`,
  `GET /api/tools/jobs/{id}`, `GET /api/tools/histograms/{video_id}`,
  `GET /api/tools/histograms/summary/{video_id}`
- **DB assertion:** the clip has `extracted=true` + captured `phase_frames`; the video doc gains
  `histogram_processed=true`; a `skeleton_data_testing.skeleton_histograms` doc exists with
  `metrics` + 300-pt `resampled` curves; the stored summary fields are readable.

### E2E-22 — Phase 9: missing-phase-frames skip (Histo job skips the clip)
- **Category:** Phase 9 — skip path
- **Seeded/Stubbed:** `fake_run_extract`; a pymongo one-liner clears the clip's `phase_frames`
  (simulating a clip whose manual phases were never captured — same shape as the BE UC-99
  integration test)
- **Given** a class with an extracted clip that has **no** `phase_frames`
- **When** the user runs **Histo** (`POST /api/tools/histograms/analysis`)
- **Then**
  - the job still finishes `done`, with the video id in `result_json.skipped`
    (reason `no phase_frames`) and **not** in `processed`
  - the video doc does **not** get `histogram_processed=true`
  - `GET /api/tools/histograms/{video_id}` → `404` (no histogram doc)
  - `GET /api/tools/histograms/summary/{video_id}` → `404`
- **Endpoint(s):** `POST /api/tools/histograms/analysis`, `GET /api/tools/jobs/{id}`,
  `GET /api/tools/histograms/{video_id}`, `GET /api/tools/histograms/summary/{video_id}`
- **DB assertion:** no `skeleton_histograms` doc for the video; `histogram_processed` stays unset.

### E2E-23 — Phase 9: pre-Histo empty-state / post-Histo chart
- **Category:** Phase 9 — panel states (Q2 resolution)
- **Seeded/Stubbed:** `fake_run_extract`; real uploaded mp4
- **Given** a class with an extracted clip
- **When** the user opens the **Biomechanical Signal Analysis** panel, then runs **Histo** and
  reopens the panel
- **Then**
  - **pre-Histo:** the panel renders the empty state (`No histogram found for this clip`) with no
    chart and no annotation strip — nothing else (Q2)
  - **post-Histo:** the same panel renders the synchronized chart (`.signal-chart`, 8 readout
    cells, annotation strip) — and **no console errors** are emitted
- **Endpoint(s):** `GET /api/tools/histograms/{video_id}` (404 pre-Histo → 200 post-Histo),
  `POST /api/tools/histograms/analysis`, `GET /api/tools/jobs/{id}`
- **DB assertion:** `skeleton_histograms` doc exists after Histo; `histogram_processed=true`.

---

## 2. Execution & environment contract

```text
# Backend (must run before `pixi run fe-e2e`, or via Playwright webServer config):
POLA_API_DB=pole_api_testing \
SKELETON_DB=skeleton_data_testing \
CHROMA_PERSIST_DIR=$(mktemp -d) \
E2E_FAKES=1 \
uvicorn main:app --host 0.0.0.0 --port 8000   # cwd app/pola_api

# FE:
cd app/pole_fe && npx ng serve --port 4200   # environment.ts apiBaseUrl = http://localhost:8000
```

- `playwright.config.ts` declares `baseURL: http://localhost:4200` and a `webServer` array that starts
  both the backend (with the env above) and `ng serve`, or points at already-running services.
- The `_testing`-suffix guard is enforced by the `test-integration` aggregator (see
  `docs/app/pola_api/PLAN.md` §4): the run aborts if `POLA_API_DB` / `SKELETON_DB` lack the `_testing` suffix.
- `E2E_FAKES=1` enables the crawler/cutter/train fakes described in §0. Without it, the E2E suite would
  require real Instagram credentials + a trained LSTM, which is out of scope for CI.

## 3. Coverage matrix (scenario → workflow/category)

| # | Scenario | Workflow / Category |
|:-:|----------|---------------------|
| 01–04 | create / upload / verify / upload-error | Workflow A |
| 05–12 | crawl / QC / cut / clip-accept / process / embed / train / approve | Workflow B |
| 13 | retrain fine-tune | Workflow C |
| 14–15 | edit / delete | Trick CRUD |
| 16–17 | poll / cancel | Jobs dashboard |
| 18 | list / activate / reject | Model registry |
| 19 | duplicate 409 + job failure | Error states |
| 20 | tablet + mobile viewports | Responsive |
| 21 | extract → capture → histo → chart + summary | Phase 9 happy path |
| 22 | missing-phase-frames skip | Phase 9 edge state |
| 23 | pre-Histo empty / post-Histo chart | Phase 9 Q2 panel states |

All 23 are implemented in `app/pole_fe/e2e/` (Phase 9 lives in `biomech-flow.spec.ts`) and run via
`pixi run fe-e2e`; the full integration suite is
aggregated by `pixi run test-integration` (BE `test-api` + CLI integration + `test-chatbot-live` +
FE+BE `fe-e2e`), all against the `_testing` DBs.
