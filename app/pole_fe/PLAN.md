# Implementation Plan — `pole_fe` (Angular Frontend)

> **Status:** Phases 1–8 built (shell, tricks CRUD + detail, video editor, training studio, model
> registry, system jobs). Phase 8 E2E Playwright suite (E2E-1..20) done — spec en
> `docs/app/pole_fe/e2e-test-plan.md`. Phase 9 (Extraction → Process biometric+histogram flow +
> Biomechanical Signal Analysis) DONE (PAIML-POLE-FE-006/008) — **FE + BE
> integration** (small `pola_api` Phase 14 for the `HISTO` flag/counts; see §3 Phase 9).
> **Phase 11 (Class stats histograms + video selection) PLANNED** — parte de la feature de detección
> automática de fases (handspring): `pole_fe` genera y visualiza los histogramas de referencia.
> Future work: WCAG/performance audits, cluster selector, `pole_fe` → `pola_api` production wiring,
> y Chatbot FE (new) for the agent.
> **Source docs:** `docs/app/pole_fe/implementation-plan.md` (8-phase plan + DTOs),
> `docs/app/pole_fe/fe_technical_spec.md`, `fe_UI_design_*.md` (Stitch designs),
> `docs/app/pola_api/slices.md` + `flows.md`.

---

## 1. Feature Context & Objective

- **Goal:** Proporcionar el "Pole AI Workflow Manager" — una SPA Angular que permite a un analista
  ejecutar el pipeline completo de entrenamiento LSTM (Workflows A/B/C) y a un coach/analista revisar
  clips: crear trucos, crawlear Instagram, QC posts, cortar/revisar clips, subir + verificar videos,
  procesar/embed, entrenar/retrain, aprobar modelos, y monitorizar system jobs.
- **Non-Functional Constraints:** reactive job polling (RxJS) sin memory leaks; design tokens de
  Stitch; lazy-loaded feature modules; infinite-scroll grids; WCAG 2.1 AA; bundle inicial < 200KB.
- **Affected Components:**
  - `app/pole_fe/src/app/core/` — `api` client + interceptor, `jobs-store` service, models.
  - `app/pole_fe/src/app/features/tricks/` — dashboard (list CRUD) + detail (videos, clips,
    crawl, upload, stats, editor modal, crop modal).
  - `app/pole_fe/src/app/features/training/` — training studio.
  - `app/pole_fe/src/app/features/model-registry/` — registry page.
  - `app/pole_fe/src/app/features/system-jobs/` — jobs dashboard.
  - `app/pole_fe/src/app/shared/` — UI atoms (badge, button, card, dialog, batch-upload, video
    player, notification bell, etc.).
- **Assumptions:** backend contract = `docs/app/pola_api/slices.md`; `pole_fe` corre `ng serve` y
  proxya `/api` + `/ws` a `pola_api`.

---

## 2. Architectural Layering (The "Where")

- **Domain:** FE models/DTOs espejo del backend: `TrickClass`, `VideoRecord`, `Clip`, `Crawl`,
  `Post`, `VideoUpload`, `ModelRun`, `Job` (ver implementation-plan Appendix C).
- **Application:** feature services (`TricksService`, `TrainingService`, `ModelRegistryService`,
  `JobsService`), converters, y SignalStore-based stores por feature.
- **Infrastructure:** `core/api/api-client` (HttpClient wrapper + upload progress), interceptor
  (error normalization), `jobs-store` (cross-page job hydration), lazy routes.
- **Presentation:** pages (`tricks/dashboard`, `tricks/detail`, `training/studio`,
  `model-registry/registry`, `system-jobs/dashboard`) + shared UI components.

---

## 3. Resumen de Fases y Estado

| Fase | Nombre | Estado | Detalle |
| :--- | :--- | :--- | :--- |
| 1 | Foundation & App Shell | ✅ DONE | [PLAN_PHASE_1.md](plan/PLAN_PHASE_1.md) |
| 2 | Tricks CRUD | ✅ DONE | [PLAN_PHASE_2.md](plan/PLAN_PHASE_2.md) |
| 3 | Tricks detail — Video Management | ✅ DONE | [PLAN_PHASE_3.md](plan/PLAN_PHASE_3.md) |
| 4 | Tricks detail — Video Editor + Shift | ✅ DONE | [PLAN_PHASE_4.md](plan/PLAN_PHASE_4.md) |
| 5 | Training Studio | ✅ DONE | [PLAN_PHASE_5.md](plan/PLAN_PHASE_5.md) |
| 6 | Model Registry | ✅ DONE | [PLAN_PHASE_6.md](plan/PLAN_PHASE_6.md) |
| 7 | System Jobs | ✅ DONE | [PLAN_PHASE_7.md](plan/PLAN_PHASE_7.md) |
| 8 | Integration, E2E & Polish | ✅ E2E DONE (Playwright) | [PLAN_PHASE_8.md](plan/PLAN_PHASE_8.md) |
| 9 | Extraction → Process (biometric + histogram) flow | ✅ DONE | [PLAN_PHASE_9.md](plan/PLAN_PHASE_9.md) |
| 10 | Future — Chatbot FE + cluster selector | FUTURE | [PLAN_PHASE_10.md](plan/PLAN_PHASE_10.md) |
| 11 | Class stats histograms + video selection (referencias) | ✅ DONE | [PLAN_PHASE_11.md](plan/PLAN_PHASE_11.md) |

---

## 4. Quality Gates & Testing Commands (DoD)

- **Unit Tests:** `npx ng test --watch=false` (Angular 22 `@angular/build:unit-test` con el runner
  **vitest**; specs importan `vi` de `vitest`) — target ≥ 80% coverage en `src/app`.
- **Integration Tests:** Playwright FE+BE E2E (`pixi run fe-e2e`; specs en `app/pole_fe/e2e/`, ver
  `docs/app/pole_fe/e2e-test-plan.md`) contra un backend en `pole_api_testing` /
  `skeleton_data_testing` + un temp `CHROMA_PERSIST_DIR` + `E2E_FAKES=1`.
- **Automation:** `pixi run test-integration` (aggregator: BE `test-api` + CLI integration +
  `test-chatbot-live` + FE+BE `fe-e2e`, guarded por el sufijo `_testing` DB); `tsc --noEmit`.
- **Database Target:** backend integration usa `pole_api_testing` / `skeleton_data_testing` only
  (aggregator aborta si los nombres de DB no tienen el sufijo `_testing`).
- **Coverage Requirement:** ≥ 80%.
- **Additional Checks:** sin console errors en ninguna página; sin subscription leaks (component
  destroy); bundle budgets enforced por `angular.json`.

---

## 5. Defined Use Cases (Gherkin + Technical Matrix)

### UC-FE-01: Create a trick from the New Trick modal
- **Given** la Tricks page está abierta y no existe un trick `handspring`
- **When** el usuario rellena el form (name + hashtags) y pulsa Create
- **Then** el sistema llama `POST /api/training/classes` y muestra un toast de éxito
- **And** la nueva trick card aparece en la lista con estado DRAFT

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/training/classes` |
| Request Method | POST |
| Required Headers | `Content-Type: application/json` |
| Payload Example | `{"name":"handspring","hashtags":["#gymnastics"]}` |
| DB State (Before) | no class named handspring |
| DB State (After) | class created; toast "Trick created" |

### UC-FE-02: Duplicate name inline error
- **Given** ya existe un trick `handspring`
- **When** el usuario envía el mismo nombre en New Trick
- **Then** el sistema muestra error inline "This trick name already exists"
- **And** el modal permanece abierto, Create disabled

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/training/classes` |
| Request Method | POST |
| Required Headers | `Content-Type: application/json` |
| Payload Example | `{"name":"handspring",...}` |
| DB State (Before) | handspring exists |
| DB State (After) | unchanged (409 mapped to inline error) |

### UC-FE-03: Bulk process clips from the detail page
- **Given** un trick detail con ≥1 clip seleccionado
- **When** el usuario pulsa Process y confirma
- **Then** el sistema llama `POST /api/training/classes/{id}/process` y hace poll al job
- **And** la video grid se actualiza a "processed" tras `done`

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/training/classes/{id}/process` |
| Request Method | POST |
| Required Headers | `Content-Type: application/json` |
| Payload Example | `{"video_ids":["64b..."],"stride":5}` |
| DB State (Before) | clips unprocessed |
| DB State (After) | windows created; UI badges update |

### UC-FE-04: Crop AI bulk cut with model/filter config
- **Given** un trick con sources aceptados y un cutter config
- **When** el usuario abre el modal CROP CLIPS, selecciona modelo + filter, y ejecuta bulk cut
- **Then** el sistema llama `POST /api/video/classes/{id}/cut` con `cutter_override`
- **And** el job progress se muestra en el WorkflowJobCard; aparecen pending clips en el Clips tab

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/video/classes/{id}/cut` |
| Request Method | POST |
| Required Headers | `Content-Type: application/json` |
| Payload Example | `{"sources":[...],"cutter_override":{...},"chroma_only":true}` |
| DB State (Before) | no clips |
| DB State (After) | clips `pending`; counts in `GET /clips/pending-counts` |

### UC-FE-05: Monitor → cancel a system job
- **Given** un crawl job en ejecución
- **When** el usuario navega a `/jobs`, observa el progreso, y pulsa Cancel → confirma
- **Then** el sistema llama `POST /api/crawler/jobs/{id}/cancel`
- **And** el job pasa a history como "Cancelled"; los efectos se revierten por tipo

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/crawler/jobs/{id}/cancel` |
| Request Method | POST |
| Required Headers | `Content-Type: application/json` |
| Payload Example | `{}` |
| DB State (Before) | job running |
| DB State (After) | job `stopped`; downloads rolled back |

### UC-FE-06: Compare and approve a model candidate
- **Given** un run completado `#R-0892` y un baseline activo
- **When** el usuario selecciona el candidato, revisa deltas/verdict, y pulsa Approve & Activate
- **Then** el sistema llama `POST /api/training/models/{run_id}/approve`
- **And** el ActiveModelBanner se actualiza; el run activo previo se archiva; la clase muestra promoted

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/training/models/{run_id}/approve` |
| Request Method | POST |
| Required Headers | `Content-Type: application/json` |
| Payload Example | `{}` |
| DB State (Before) | run `done`, not active |
| DB State (After) | run `active`; `active.json` written |

> **Nuevos UCs de la Fase 11 (referencias):** ver `plan/PLAN_PHASE_11.md`.

---

## 6. Risks and Mitigations

- **Risk:** job polling filtra subscriptions entre route changes. **Mitigation:** subscriptions
  canceladas en destroy (QA checklist + tests T1.9..T1.11/T7.31).
- **Risk:** backend contract drift (stateless classes, `_testing` DBs, nuevos endpoints). **Mitigation:** DTOs en Appendix C code-accurate y versioned con slices.md v2.0.
- **Risk:** el bundle crece con charting (ng2-charts) + video players. **Mitigation:** lazy routes + lazy image loading + bundle budgets.
- **Risk:** flakiness de Playwright E2E contra MediaPipe/ffmpeg reales. **Mitigation:** `E2E_FAKES=1`
  stubs crawl/cut/train (espejo de `test_e2e.py`); upload/process/embed usan MediaPipe real + temp
  Chroma dir; `_testing` DBs dedicadas; `_testing`-suffix guard.
- **Risk:** los eventos de chat job no tienen cliente FE aún. **Mitigation:** definir el contrato
  `WS_MESSAGE_TYPES` en shared models ahora; construir el Chatbot FE en la Fase 9/10.
- **Risk (Fase 11):** referencia vacía / video sin `phase_frames` → 422. **Mitigation:** empty-state
  con métricas faltantes + reporte `skipped` del job.

---

## 7. Open Questions and Decisions

- Decision: FE refleja clases **stateless**; el estado del pipeline se deriva de entidades (sin status field).
- Decision: `selected_for_training` (training toggle) es un flag manual por video vía PATCH desde FE — nunca automático.
- Decision: PROMOTE es class-level vía readiness gate + navegación a Training Studio (según UX actualizada).
- Decision: Playwright E2E vive en `app/pole_fe/e2e/` + `playwright.config.ts`; run via `pixi run fe-e2e` (CI wiring TBD). Open: si el Chatbot FE va en este repo (nueva app) o como parte de `pole_fe`.
- Open: cluster selector behavior (UI placeholder only; sin backend contract aún).
- Decision: Phase 9 (Extraction → Process biometric+histogram flow) es **FE + BE integration** — consume
  los endpoints ya implementados de `pola_api` extract/process/histograms más el pequeño **Phase 14**
  `histogram_processed` flag + clip-scoped counts (`PAIML-POLA-API-036..038`).
- Decision (Phase 9, PO 2026-08-13): **Q1 resuelto** — `HISTO` status deriva del flag
  `histogram_processed` + `X-Count-*` counts (sin N+1); **Q2 resuelto** — el panel Biomechanical Signal
  Analysis es **post-analysis only** y muestra nada cuando no existe histograma.

> **Note (pola_api Phase 11 histogram refactor — FE impact).** El backend está eliminando
> `POST /api/tools/analyze`, `/api/tools/reference/*`, y `/api/tools/attempts/*` y añadiendo
> `/api/tools/histograms/*`. Antes de Phase 9, el FE **no consumía** estos REST endpoints — sus
> screens `tricks` solo usaban `/api/training/*`, `/api/video/*`, `/api/crawler/*`. **Phase 9 cambia
> esto:** el nuevo flujo extraction → process consume `POST /api/tools/histograms/analysis`,
> `GET /api/tools/histograms/{video_id}`, y `GET /api/tools/histograms/summary/{video_id}` (ver §3
> Phase 9). El otro touchpoint es la **chatbot chat page** (`features/chatbot`), que renderiza chips
> genéricos de tool-call WS; trata `analyze` y `histogram` como nombres de tool opacos y extrae los
> artefactos `deviation_plot`/`critical_frame_path` de los resultados de `analyze`. Si la tool
> `analyze` del chatbot backend se elimina (como está planeado), esos artefactos dejarán de producirse
> y los example chips de `chatbot-chat.page.spec.ts` para `analyze` deberían actualizarse a una tool
> aún soportada — sin cambio estructural FE requerido.