# Implementation Plan — `pole_api` (Backend FastAPI)

> **Status:** Core slices implemented (Phases 1–9 done). Phase 11 (`histograms/analysis`) and Phase 12
> (`histograms/summary` frame detection) done. Phase 13 (`analysis` slice) implemented
> (see `phase-13-analysis-slice/PLAN.md`). **Phase 14 (`histogram_processed` flag + `EXTRACTED`/`HISTO`
> counts) done** — FE `pole_fe` Phase 9 support. **Phases 15–17 ✅ DONE** — rename `pola_api`→
> `pole_api`, collection renames, `skeleton_trick_histograms`, reference histograms, phase detection
> (Bhattacharyya + K=5). **Phase 18 ✅ DONE** — analyst chatbot WS. **Phase 19 ✅ DONE** — error
> contracts + reprocessing + quality gates. **Phase 20 ✅ DONE** — analysis slice enrichment for
> Stitch FE (enriched list + multi-frame pose endpoints). **Phases 21–24 ✅ DONE** — coach prompts
> (one-shot LLM coaching endpoints), coach insights (rule-based), coach UI, and Stitch detail gaps
> (metric deltas). **Phase 25 ✅ DONE** — classify-first pipeline (commit `b321fda`, merged `3a2fcf8`).
> **Phase 26 ✅ DONE** — analyst coach chatbot tools (tickets PAIML-POLE-API-074..082, commit
> `52234f7`; tools in `app/pole_api/src/analyst_chatbot/tools.py`, tests in
> `tests/test_analyst_chatbot_coach_tools.py`).
> **Source docs:** `docs/app/pola_api/slices.md` (API reference), `docs/app/pola_api/flows.md` (use
> cases UC-01..90), `docs/app/pola_api/implementation-plan.md` (phase plan).

---

## 1. Feature Context & Objective

- **Goal:** Expose the full Pole AI pipeline as a FastAPI backend organized in three slices
  (`crawler`, `training`, `video`) plus shared `core`, so the Angular frontend (`pole_fe`) can run
  Workflow A (upload → Chroma-only) and Workflow B (crawl → QC → cut → process → train → promote)
  end to end. Async long-running work is exposed as monitorable jobs.
- **Non-Functional Constraints:** async jobs run in background threads (polled by the FE); no
  class state machine (classes are stateless, pipeline stage is derived from related entities);
  separate Mongo DBs for app data (`pole_api`) and ML data (`skeleton_data`); test isolation via
  `pole_api_testing` / `skeleton_data_testing` DBs.
- **Affected Components:**
  - `app/pola_api/src/core/` — `config`, `errors`, `mongo`, `jobs` (+ `jobs_router`), `status` (placeholder), `repositories/video_repository`, `services/embed_runner`.
  - `app/pola_api/src/crawler/` — controllers (`crawls`, `posts`, `jobs`), services (`crawl_service`, `post_service`), repositories.
  - `app/pola_api/src/training/` — controllers (`classes`, `process`, `extract`, `phase_frames`, `models`, `retrain`, `train`, `jobs`), services (`class_service`, `process_service`, `extract_service`, `embed_runner`, `model_registry_service`, `train_service`), repositories (`class_repository`, `model_run_repository`).
  - `app/pola_api/src/video/` — controllers (`uploads`, `cut`, `cutter_configs`, `videos`, `jobs`), services (`upload_service`, `cutter_service`, `clip_service`, `shift_service`, `picture_service`, `thumbnail_service`, `video_deletion_service`).
  - `app/pola_api/main.py` — app assembly + CORS + `/health`.
  - `app/pola_api/conftest.py` + `tests/` — unit/integration test suite.
  - Reused packages: `pole_crawler.*`, `pole_ml.*`, `pole_tools.*`.
- **Assumptions:** Mongo + Redis are external dependencies provided via docker-compose; `pole_fe`
  polls jobs (`GET /{slice}/jobs/{id}`); `X-API-Key` auth is optional (env `API_KEY`).

---

## 2. Architectural Layering (The "Where")

- **Domain:** job entity (`{kind, entity_id, slice, status, progress, result_json, error,
  description, cancel_requested}`), class (stateless), video (shared collection), clip, upload,
  crawl, model_run, skeleton window/histogram (in `skeleton_data`).
- **Application:** per-slice services: `ClassService`, `ProcessService`, `ExtractService`,
  `ModelRegistryService`, `TrainService`, `CrawlService`, `PostService`, `UploadService`,
  `CutterService`, `ClipService`, `ShiftService`, `ThumbnailService`, `PictureService`,
  `VideoDeletionService`; shared `JobRunner` + `EmbedRunner`. **Nuevo (Fase 17):** `PhaseDetector`,
  `DetectPhasesUseCase`, `ClassifyTrickUseCase`; **nuevo slice (Fase 18):** `analyst_chatbot` +
  `AnalystFacade`.
- **Infrastructure:** `core/mongo.py` (Mongo client), `core/jobs.py` (thread job runner +
  rollback/cancel), `core/config.py` (env settings), repositories per slice, `pole_ml` /
  `pole_tools` / `pole_crawler` packages, ffmpeg (`pole_crop`) for cut/shift/thumbnails. **Nuevo
  (Fase 15):** colección `skeleton_trick_histograms`; renames `signal_histograms`→
  `skeleton_cohort_signals`, `skeleton_histograms`→`skeleton_video_signals`.
- **Presentation:** REST controllers under `/api/{slice}/...`, `/health`; jobs polling + cancel
  endpoints per slice. **Nuevo (Fase 18):** WS `/ws/analyst-chat`.

---

## 3. Resumen de Fases y Estado

| Fase | Nombre | Estado | Detalle |
| :--- | :--- | :--- | :--- |
| 1 | Fundamentals (core infrastructure) | ✅ DONE | [PLAN_PHASE_1.md](plan/PLAN_PHASE_1.md) |
| 2 | Training slice — Classes CRUD | ✅ DONE | [PLAN_PHASE_2.md](plan/PLAN_PHASE_2.md) |
| 3 | Training slice — Process + Embed + Jobs | ✅ DONE | [PLAN_PHASE_3.md](plan/PLAN_PHASE_3.md) |
| 4 | Crawler slice — Crawl + QC | ✅ DONE | [PLAN_PHASE_4.md](plan/PLAN_PHASE_4.md) |
| 5 | Video slice — Upload + auto-embed | ✅ DONE | [PLAN_PHASE_5.md](plan/PLAN_PHASE_5.md) |
| 6 | Video slice — Cut + Review + Shift + Thumbnails | ✅ DONE | [PLAN_PHASE_6.md](plan/PLAN_PHASE_6.md) |
| 7 | Training slice — Model registry + Retrain | ✅ DONE | [PLAN_PHASE_7.md](plan/PLAN_PHASE_7.md) |
| 8 | E2E + cross-slice touchpoints | ✅ DONE | [PLAN_PHASE_8.md](plan/PLAN_PHASE_8.md) |
| 9 | Extraction + histogram pipeline | ✅ DONE | [PLAN_PHASE_9.md](plan/PLAN_PHASE_9.md) |
| 10 | Production hardening | 🟡 PARTIAL / FUTURE | [PLAN_PHASE_10.md](plan/PLAN_PHASE_10.md) |
| 11 | Histogram Analysis endpoints (`histograms/analysis`) | ✅ DONE | [PLAN_PHASE_11.md](plan/PLAN_PHASE_11.md) |
| 12 | Frame-detection Summary endpoint (`histograms/summary`) | ✅ DONE | [PLAN_PHASE_12.md](plan/PLAN_PHASE_12.md) |
| 13 | Analysis slice (pole_analyst backend) | ✅ DONE | [PLAN_PHASE_13.md](plan/PLAN_PHASE_13.md) |
| 14 | Histogram status flag + `EXTRACTED`/`HISTO` counts | ✅ DONE | [PLAN_PHASE_14.md](plan/PLAN_PHASE_14.md) |
| 15 | Rename `pola_api`→`pole_api` + renames de colecciones | ✅ DONE | [PLAN_PHASE_15.md](plan/PLAN_PHASE_15.md) |
| 16 | Reference histograms por truco (`tools`) | ✅ DONE | [PLAN_PHASE_16.md](plan/PLAN_PHASE_16.md) |
| 17 | Phase detection (Bhattacharyya + K=5) en `analysis` | ✅ DONE | [PLAN_PHASE_17.md](plan/PLAN_PHASE_17.md) |
| 18 | Analyst chatbot (WS `/ws/analyst-chat`) | ✅ DONE | [PLAN_PHASE_18.md](plan/PLAN_PHASE_18.md) |
| 19 | Error contracts + reprocessing + quality gates | ✅ DONE | [PLAN_PHASE_19.md](plan/PLAN_PHASE_19.md) |
| 20 | Analysis slice enrichment (Stitch FE endpoints) | ✅ DONE | [PLAN_PHASE_20.md](plan/PLAN_PHASE_20.md) |
| 21 | Coach prompts (LLM summary / plan / pose endpoints) | ✅ DONE | [PLAN_PHASE_21.md](plan/PLAN_PHASE_21.md) |
| 22 | Coach insights (rule-based z-score insights + pose extraction + fps storage) | ✅ DONE | [PLAN_PHASE_22.md](plan/PLAN_PHASE_22.md) |
| 23 | Coach UI (Summary tab cards + notification + chat auto-suggestion) | ✅ DONE | [PLAN_PHASE_23.md](plan/PLAN_PHASE_23.md) |
| 24 | Stitch detail gaps BE (session-over-session metric deltas) | ✅ DONE (#114, merged locally 2026-08-23) | [PLAN_PHASE_24.md](plan/PLAN_PHASE_24.md) |
| 25 | Classify-first pipeline (detección de fases con la clase correcta) | ✅ DONE (`b321fda`, merged `3a2fcf8`) | [PLAN_PHASE_25.md](plan/PLAN_PHASE_25.md) |
| 26 | Analyst coach tools (chatbot: compare_sessions, cohort_percentiles, improvement_plan, metric_deep_dive, frame_pose, progress_trend, focus_recommendation, risk_scan, get_coach_summary/pose) | ✅ DONE (`52234f7`) | [PLAN_PHASE_26.md](plan/PLAN_PHASE_26.md) |
| 27 | Coach-insights positives (relax rule-based `perfect` bar to `score_pct ≥ 70` / `\|z\| ≤ 0.6`) | 📋 PLANNED | [PLAN_PHASE_27.md](plan/PLAN_PHASE_27.md) |
| 28 | Coach plain-language output | 📋 PLANNED | [phase-28-coach-plain-language-output/](phase-28-coach-plain-language-output/) |

---

## 4. Quality Gates & Testing Commands (DoD)

- **Unit Tests:** `pixi run test-api` (pytest in `app/pola_api`).
- **Integration Tests:** real Mongo on `pole_api_testing` + `skeleton_data_testing` DBs (never prod
  `pole_api` / `skeleton_data`); E2E `test_e2e.py`; `pixi run test-chatbot-live` for chatbot
  WS→jobs→ffmpeg; CLI integration (`test_cli_integration.py`); FE+BE Playwright (`fe-e2e`).
- **Automation:** CI runs `pixi run test`, `pixi run test-api`, `pixi run test-jobs`, `pixi run test-chatbot`.
- **Database Target:** `pole_api_testing` and `skeleton_data_testing` (guard: conftest asserts `_testing` suffix; aggregator guard aborts if env DB names lack the suffix). **Fase 17-19 añade** `analysis_db_testing`.
- **Coverage Requirement:** ≥ 80% (workspace default; `test-api` measured).
- **Additional Checks:** `pytest -q` for pole-train-model (≥80%), no cross-slice imports, import linter for chatbot→tools only.

### 4.1 Integration-test inventory & aggregator

| Suite | Command | Scope | DB target |
|---|---|---|---|
| BE integration | `pixi run test-api` | `app/pola_api/tests` (incl. `test_e2e.py`, `test_process_integration.py`, `test_upload_integration.py`) | `pole_api_testing` / `skeleton_data_testing` |
| CLI integration | `pixi run test` (pole-train-model) | `test_cli_integration.py` (UC-82..90 matrix) | `pole_api_testing` / `skeleton_data_testing` |
| Chatbot live | `pixi run test-chatbot-live` | `packages/chatbot/tests/test_ws_integration.py` (WS→jobs→ffmpeg) | `pole_chatbot_testing` / `skeleton_data_testing` |
| FE+BE E2E | `pixi run fe-e2e` | `app/pole_fe/e2e/` (Playwright, E2E-1..20) | `pole_api_testing` / `skeleton_data_testing` + temp Chroma |

**Aggregator** `pixi run test-integration` runs, sequentially, all four suites with the `_testing`
DB env overrides (`POLA_API_DB=pole_api_testing`, `SKELETON_DB=skeleton_data_testing`) and a temp
`CHROMA_PERSIST_DIR`. A **guard** at the top aborts the whole run if either DB name lacks the
`_testing` suffix.

---

## 5. Defined Use Cases

Los use cases UC-01..90 están documentados en `docs/app/pola_api/flows.md`. Resumen por área:

- **Classes (UC-01..06):** CRUD, duplicados, reserved name, stats.
- **Upload (UC-10..12):** multipart upload, auto-embed, verify.
- **Crawler (UC-20..24):** crawl desde hashtag/cuenta, QC de posts.
- **Cut (UC-30..35):** crop AI bulk, review clips, shift, thumbnails.
- **Process/Embed (UC-40..43):** windows + embed, idempotencia por modelo.
- **Models (UC-50..64):** train full/fine-tune, registry, activate/approve/reject.
- **Jobs (UC-70..72):** polling, cancel, history.
- **Extract (UC-82..90):** extracción de landmarks, phase-frames manuales, histogramas
  (`BiomechanicalDataProcessor` + `HistogramDataProcessor`).

> **Nuevos UCs (Fases 15-19):** detección de fases (`DESCONOCIDO` manual), referencias por truco,
> analyst chatbot. Ver las fases 16-19 y `pole_analyst` PLAN.

---

## 6. Risks and Mitigations

- **Risk:** jobs largos (train, crawl) en threads bloquean workers. **Mitigation:** monitorable jobs,
  cancel+rollback, progress; Celery/Redis al deployar a k8s (Fase 10).
- **Risk:** drift de contratos entre FE (`pole_fe`) y backend. **Mitigation:** slices.md v2.0 +
  DTOs code-accurate en implementation-plan; FE+BE E2E en `test-integration`.
- **Risk (Fase 15):** renames de colecciones rompen refs (≈101 a `signal_histograms`). **Mitigation:**
  renombrar en un solo cambio, grep completo, tests + guard `_testing` verdes, backfill opcional.
- **Risk (Fase 17):** detección por Bhattacharyya imprecisa (fases solapadas). **Mitigation:** K=5
  consenso, umbral 0.7 → `DESCONOCIDO` (modal manual), 5 métricas seleccionadas con pesos.
- **Risk:** análisis lento → SLA > 1 min. **Mitigation:** batch de landmarks, pool, one-analysis-at-a-time
  (Fase 19).
- **Risk:** chatbot WS montado condicionalmente (debe ser resiliente). **Mitigation:** routers
  condicionales + manejo de fallo en FE.

---

## 7. Open Questions and Decisions

- Decision: clases **stateless**; estado derivado de entidades.
- Decision: test DBs `pole_api_testing` / `skeleton_data_testing` con guard.
- Decision: `histogram_processed` flag para el estado `HISTO` (Phase 14).
- Decision (fases 15-19): colección `skeleton_trick_histograms` para referencias; 5 métricas con
  pesos; Bhattacharyya + K=5; `DESCONOCIDO`/trick-label `null` → flujo manual en FE; reproceso no
  automático salvo video corrupto.