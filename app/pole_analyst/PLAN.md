# Implementation Plan — `pole_analyst` (Angular Frontend: "Pole AI Coach")

> **Status:** Phases 1–6 built (shell, chat pane, video library/upload, detail tabs, edge/error
> hardening, Playwright E2E — PAIML-POLE-ANALYST-001..027). Phases 8–14 shipped (progress panel,
> results view, manual phases + reproceso, analyst chatbot UI, Stitch refresh 12–14 —
> PAIML-POLE-ANALYST-028..051). Phase 15 (sidebar) ✅. Design source: `docs/app/pole_analyst/fe_design.md`
> (Stitch prompt). This app is distinct from `pole_fe` (the training workflow manager) —
> `pole_analyst` is the athlete-facing video-analysis coach: upload → analyze → feedback →
> conversation.
>
> **Backend dependency:** a new `analysis` slice in `pola_api` (planned separately at
> `docs/app/pola_api/phase-13-analysis-slice/PLAN.md`). This FE plan consumes that slice.
> **Sibling reference:** `docs/app/pole_fe/` (Angular 22 conventions, vitest unit runner,
> Playwright E2E, SignalStore, Tailwind) — reuse those patterns, not new tooling.
>
> **Nueva fase 16 (PLANNED):** coach tabs — contenido LLM estructurado (summary / plan / pose)
> consumiendo los endpoints coach de `pola_api` Fase 21 (PAIML-POLE-API-062..064).
>
> **Stitch design refresh (fases 12-14):** tab navigation en videos page, Analysis History table,
> Results→Summary merge, Pose Gallery (multi-frame), Metric Detail Modal. Backend dependency:
> `pola_api` Fase 20 (enriched list + multi-frame pose endpoints).

---

## 1. Feature Context & Objective

- **Goal:** Una SPA Angular, "Pole AI Coach", dividida en dos panes. **Izquierda** = chat con un
  chatbot de análisis de video que muestra su estado en vivo (Idle / Thinking / Working / Completed /
  Error). **Derecha** = tools panel con dos modos: (1) una **video library + upload** (lista de videos
  subidos con badges "Analyzed / Not analyzed") y (2) una **video detail** con cuatro tabs — **Summary,
  Histogram, Pose, Plan**. El propósito del chatbot es analizar el video del usuario y dar feedback de
  mejora; el usuario puede conversar sobre ese feedback.
- **Nuevo (fases 8-11):** la detección automática de fases se integra en el flujo de análisis: el
  usuario sube → progress panel (Extraction → Processing → Phase detection → Classification & analysis
  → Summary) → resultado con fases detectadas + feedback + error frames. Si la detección es
  `DESCONOCIDO` se abre el modal manual; si el LSTM falla se pregunta el nombre del truco; si re-subes
  un video analizado se pregunta reproceso.
- **Non-Functional Constraints:** WebSocket resiliente (sin disconnects visibles; auto-reconnect +
  session resume), job polling sin leaks, state chip sincronizado con frames WS, light theme de Stitch
  tokens, lazy-loaded features, WCAG 2.1 AA.
- **Affected Components (nueva app bajo `app/pole_analyst/`):**
  - `core/` — `ApiClient` (HttpClient wrapper), `ChatbotSocketService` (WS), `JobsStoreService`
    (job polling), DTO models, error interceptor.
  - `features/chat/` — chat pane (message list, state chip, composer).
  - `features/videos/` — video library + upload.
  - `features/analysis/` — video detail tabs (Summary/Histogram/Pose/Plan) + progress panel + results.
  - `shared/` — UI atoms (badge, card, tab-bar, status-chip, upload-dropzone, chart, image-frame).
- **Assumptions / Decisions (locked):**
  - Backend `pola_api` expone un nuevo **`analysis` slice** (`/api/analysis`) más el WS del analyst
    chatbot `/ws/analyst-chat`; `ng serve` proxya `/api` + `/ws`.
  - Upload usa el endpoint de análisis dedicado (sin `class_id`). Video + landmarks + histogramas viven
    en **`analysis-db`**; la referencia `mean`/`std` para scoring viven en
    **`skeleton_data.skeleton_cohort_signals`** (producidas por `pole_fe`).
  - Análisis se dispara vía `POST /api/analysis/videos/{id}/analyze` (async job), NO por la tool
    directa `histogram` del chatbot.
  - "Analyzed" es el flag `analyzed` en `analysis-db.videos`, `true` cuando el histograma del video se
    ha producido.
  - Detección de fases automática con modal manual como fallback; clasificación LSTM con fallback a
    pregunta del truco.

---

## 2. Architectural Layering (The "Where")

- **Domain (models/DTOs):** espejo de los contratos del backend:
  `VideoRecord` (`_id`, `filename`, `analyzed`, `created_at`), `Job`, `VideoHistogramDoc`
  (`video_id`, `trick_label`, `phases`, `metrics`, `resampled`, `z_mean`, `scores`, `detections[]`),
  `AnalysisSummary` (`z_mean`, `scores`, `detections`, `critical_*`, `phases` detectadas + `confidence`),
  `PhaseDetectionResult` (`detected`, `phases`, `confidence`, `trick_label`), `PoseFrame` (`frame`,
  `overlay_path`/`frame_image_path`, `issues`), `ChatWsFrame` (`connected` / `agent_reply` /
  `session_resumed` / `error` / relaid job events), `ChatState`.
- **Application (services):**
  - `VideosService` — upload (`POST /api/analysis/videos` multipart), list (`GET
    /api/analysis/videos`), thumbnail/stream URLs.
  - `AnalysisService` — trigger (`POST /api/analysis/videos/{id}/analyze`), read summary +
    histogram (`GET /api/analysis/videos/{id}/summary`, `/{id}/histogram`), pose frame, phases manuales.
  - `ChatbotService` — ciclo de vida WS (connect, send `message`/`resume`, derivar estado de frames).
  - `JobsStoreService` — poll `GET /api/analysis/jobs/{job_id}` (2s) para el job de análisis.
- **Infrastructure:** `core/api-client` (HttpClient + upload progress + error normalization),
  interceptor mapeando el envelope `{detail}`, `chatbot-socket` (WebSocket con reconnect + backoff +
  `session_id` resume), lazy routes, `ng serve` proxy config.
- **Presentation:** pages/components — `ChatPane`, `VideosLibraryPane`, `ProgressPanel` (5 etapas),
  `ResultsView` (timeline de fases + feedback + error frames), `ManualPhasesModal`, `VideoDetailPanel`
  (tab bar + `SummaryTab` / `HistogramTab` / `PoseTab` / `PlanTab`), `StatusChip`, `UploadDropzone`,
  `VideoCard`, `MetricChart`, `AnnotatedFrame`.

---

## 3. Resumen de Fases y Estado

| Fase | Nombre | Estado | Detalle |
| :--- | :--- | :--- | :--- |
| 1 | Foundation & App Shell | ✅ DONE | [PLAN_PHASE_1.md](plan/PLAN_PHASE_1.md) |
| 2 | Chat Pane (left) | ✅ DONE | [PLAN_PHASE_2.md](plan/PLAN_PHASE_2.md) |
| 3 | Video Library + Upload (right, default) | ✅ DONE | [PLAN_PHASE_3.md](plan/PLAN_PHASE_3.md) |
| 4 | Video Detail Tabs (right, detail mode) | ✅ DONE | [PLAN_PHASE_4.md](plan/PLAN_PHASE_4.md) |
| 5 | Edge / Error / Reconnect hardening | ✅ DONE | [PLAN_PHASE_5.md](plan/PLAN_PHASE_5.md) |
| 6 | Integration & E2E | ✅ DONE | [PLAN_PHASE_6.md](plan/PLAN_PHASE_6.md) |
| 7 | Keycloak Auth (future, last) | 🔒 FUTURE / DEFERRED | [PLAN_PHASE_7.md](plan/PLAN_PHASE_7.md) |
| 8 | Upload + Progress Panel (detección de fases) | ✅ DONE | [PLAN_PHASE_8.md](plan/PLAN_PHASE_8.md) |
| 9 | Results View: fases + feedback + error frames | ✅ DONE | [PLAN_PHASE_9.md](plan/PLAN_PHASE_9.md) |
| 10 | Manual phases modal + LSTM-fail + reproceso | ✅ DONE | [PLAN_PHASE_10.md](plan/PLAN_PHASE_10.md) |
| 11 | Analyst chatbot UI (WS `/ws/analyst-chat`) | ✅ DONE | [PLAN_PHASE_11.md](plan/PLAN_PHASE_11.md) |
| 12 | Stitch Design: Tab Navigation + Analysis History | ✅ DONE | [PLAN_PHASE_12.md](plan/PLAN_PHASE_12.md) |
| 13 | Stitch Design: Results→Summary merge + Tab Reorder | ✅ DONE | [PLAN_PHASE_13.md](plan/PLAN_PHASE_13.md) |
| 14 | Stitch Design: Pose Gallery + Metric Detail Modal | ✅ DONE | [PLAN_PHASE_14.md](plan/PLAN_PHASE_14.md) |
| 15 | Stitch Design: Sidebar Navigation | ✅ DONE | [PLAN_PHASE_15.md](plan/PLAN_PHASE_15.md) |
| 16 | Coach tabs (LLM summary / plan / pose estructurado) | ✅ DONE (`-058` #110 · `-059` #111) | [PLAN_PHASE_16.md](plan/PLAN_PHASE_16.md) |
| 17 | Stitch detail views (Filter Modal + distribution cards + parity pass) | ✅ DONE (#113/#115/#116, merged locally 2026-08-23) | [PLAN_PHASE_17.md](plan/PLAN_PHASE_17.md) |
| 18 | Stitch sidebar submenu (Dashboard colapsable) | ✅ DONE (#117, merged locally 2026-08-24) | [PLAN_PHASE_18.md](plan/PLAN_PHASE_18.md) |
| 19 | Stitch tabs parity round 2 (PO requirements 2026-08-23) | 🟡 PARTIAL (`-064/-065` ✅ #119/#118 · `-066` 📋 · `-067` ❌ cancelado por PO) | [plan/PLAN_PHASE_19.md](plan/PLAN_PHASE_19.md) |
| 20 | Sidebar Option B (solo menú lateral; sin Coach/Upload) | ✅ DONE (#120, merged locally 2026-08-24) | [plan/PLAN_PHASE_20.md](plan/PLAN_PHASE_20.md) |


---

## 4. Quality Gates & Testing Commands (DoD)

- **Unit Tests:** `npx ng test --watch=false` (Angular 22 vitest runner) — target ≥ 80% coverage
  en `src/app`.
- **Integration/E2E:** Playwright (`npx playwright test`, specs en `app/pole_analyst/e2e/`)
  contra `pola_api` con `POLA_API_DB=pole_api_testing`, `SKELETON_DB=skeleton_data_testing`,
  `ANALYSIS_DB=analysis_db_testing`, `E2E_FAKES=1` (guardado por `scripts/guard-testing-db.sh`,
  nunca prod DBs).
- **Backend para dev/E2E:** correr `pixi run api` (uvicorn `app/pola_api`) con las bases `_testing`
  para E2E; `ng serve` proxya `/api` + `/ws`.
- **Database Target:** `pole_api_testing` / `skeleton_data_testing` / `analysis_db_testing`.
- **Coverage Requirement:** ≥ 80% (repo default).
- **Additional Checks:** lint (`npx ng lint`), typecheck (`npx ng build`), accessibility spot
  checks (WCAG 2.1 AA), sin subscription leaks (RxJS takeUntilDestroyed).

---

## 5. Defined Use Cases (Gherkin + Technical Matrix)

> Todos los paths apuntan al **nuevo `analysis` slice** (backend contract en
> `docs/app/pola_api/phase-13-analysis-slice/PLAN.md`). Los shapes de endpoints son propuestos y a
> confirmar a nivel de ticket.

### UC-01: Upload video (happy path)
- **Given** la librería está vacía
- **When** el usuario suelta un `.mp4` en el upload dropzone
- **Then** el FE `POST /api/analysis/videos` (multipart `file`)
- **And** el backend guarda en la carpeta de análisis y devuelve `201` con el video doc (`analyzed=false`)
- **And** el FE muestra la card como "Not analyzed"

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/analysis/videos` |
| Request Method | POST (multipart/form-data) |
| Required Headers | `Content-Type: multipart/form-data` |
| Payload Example | `file=@clip.mp4` |
| DB State (Before) | sin doc `analysis-db.videos` para este archivo |
| DB State (After) | doc `analysis-db.videos` (`analyzed=false`) |

### UC-02: Request analysis (happy path) — con detección de fases
- **Given** un video subido (aún sin analizar)
- **When** el usuario pulsa "Analyze" (o le pide al chatbot que analice)
- **Then** el FE `POST /api/analysis/videos/{video_id}/analyze` devuelve `202 {job_id}`
- **And** hace poll a `GET /api/analysis/jobs/{job_id}` hasta `done`
- **And** el progress panel muestra las 5 etapas (Extraction → Processing → Phase detection →
  Classification & analysis → Summary)
- **And** la etapa de phase detection devuelve las fases detectadas (o `DESCONOCIDO` → modal manual)
- **And** el job extrae landmarks → `analysis-db.skeleton-landmarks`, corre `HistogramDataProcessor` →
  `analysis-db.video_histograms`, computa scores contra `skeleton_cohort_signals`, clasifica con LSTM
  (o pregunta el truco), setea `analyzed=true`
- **And** la card pasa a "Analyzed"

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/analysis/videos/{video_id}/analyze` |
| Request Method | POST |
| Payload Example | (empty o `{}`) |
| DB State (Before) | `analysis-db.videos` `analyzed=false`; sin docs `video_histograms`/`skeleton-landmarks` |
| DB State (After) | `analysis-db.videos` `analyzed=true`; docs `video_histograms` + `skeleton-landmarks` |

### UC-03: View Summary / Histogram / Pose / Plan
- **Given** el video está analizado
- **When** el usuario abre el video y cambia de tab
- **Then** Summary → `GET /api/analysis/videos/{id}/summary` (200); Histogram →
  `GET /api/analysis/videos/{id}/histogram` (200); Pose → frame analizado (skeleton overlay + hints);
  Plan → último `agent_reply` text

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/analysis/videos/{video_id}/summary`, `/api/analysis/videos/{video_id}/histogram` |
| Request Method | GET |
| DB State (Before) | `video_histograms` + summary presentes |
| DB State (After) | sin cambios (read-only) |

### UC-04: Chat conversation (happy path)
- **Given** un WS conectado (`{"type":"connected","ws_connection_id":W}`)
- **When** el usuario envía `{"type":"message","message":"how can I improve my invert?"}`
- **Then** el state chip se mueve Idle→Thinking→Working (en job events)→Completed
- **And** el server responde `{"type":"agent_reply","reply":"…","tool_calls":[…]}`

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/ws/analyst-chat` |
| Request Method | WebSocket (message frames) |
| Frames (client→server) | `{"type":"message","message":"…"}`, `{"type":"resume","session_id":S}` |
| Frames (server→client) | `connected`, `agent_reply`, `session_resumed`, `error`, relaid `job_*` |
| DB State | chatbot session `active` → `completed` |

### UC-05: Invalid upload (non-`.mp4` / too large)
- **Given** el upload dropzone
- **When** el usuario selecciona un archivo no `.mp4` o sobredimensionado
- **Then** el FE lo bloquea inline (o mapea un `422` del backend) y pide otro / video más corto

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/analysis/videos` |
| Request Method | POST |
| Payload Example | `file=@not_a_video.txt` |
| HTTP / DB State | `422` `{"detail":[…]}`; sin nuevo doc `analysis-db.videos` |

### UC-06: No detectable skeleton / low quality
- **Given** un video subido cuya extracción no encontró landmarks
- **When** se pide análisis
- **Then** el chatbot muestra "couldn't detect athlete — low quality, re-record" (sin error genérico),
  y la card sigue "Not analyzed"

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/analysis/videos/{video_id}/analyze` |
| DB State (After) | job `done` con entrada `result_json.failed`/`skipped` (error-isolated, job no `failed`) |

### UC-07: Empty library
- **Given** sin uploads
- **When** la página carga
- **Then** el chatbot muestra el mensaje explainer y el panel derecho muestra el upload panel

### UC-08: Phase detection baja confianza → modal manual
- **Given** un análisis con detección `DESCONOCIDO` (confianza < 0.7)
- **When** el usuario ve el resultado
- **Then** se abre el modal manual de fases; al confirmar se re-lanza la fase de classification &
  analysis

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `PUT /api/training/clips/{video_id}/phase-frames` |
| DB State (After) | `phase_frames` corregidos; re-análisis disparado |

### UC-09: LSTM falla → preguntar nombre del truco
- **Given** la clasificación LSTM devuelve `null`/baja confianza
- **When** el usuario ve el resultado
- **Then** el FE pregunta el nombre del truco (input con sugerencias) y lo envía al backend

### UC-10: Re-upload de video analizado → reproceso
- **Given** un video ya analizado
- **When** el usuario lo sube de nuevo
- **Then** el FE pregunta "¿Reprocesar?"; no reprocesa automáticamente salvo video corrupto

---

## 6. Risks and Mitigations

- **Risk:** los WebSocket routers son condicionales (no montados si faltan deps de `pole_chatbot`).
  **Mitigation:** el FE debe manejar un WS handshake fallido con banner claro + auto-retry; el chat
  state cae a `Error`.
- **Risk:** la extracción de pose frames depende del modelo MediaPipe; modelo ausente → degradado.
  **Mitigation:** el Pose tab cae a `detections[].frame_image_path` y muestra el estado
  health/degraded del slice analysis.
- **Risk:** el análisis es un background job lento; el usuario puede irse/reconectar.
  **Mitigation:** persistir `session_id` + `job_id` y reanudar en reconnect; poll idempotente.
- **Risk:** el slice `analysis` backend aún no está construido — el FE dev puede quedar bloqueado.
  **Mitigation:** construir el FE contra el contrato acordado con una capa mock/stub (ng serve proxy a
  un JSON mock) hasta que el slice aterrice; wiring final en E2E de fase 6.
- **Risk:** las FE apps duplicadas (`pole_fe` vs `pole_analyst`) divergen en tooling.
  **Mitigation:** reutilizar las convenciones Angular 22 + vitest + Playwright de `pole_fe` verbatim.
- **Risk (fases 8-10):** el backend de detección (fases 1-3 de `pola_api`) aún no existe. **Mitigation:**
  construir el FE contra el contrato con mock/stub; wiring final en la fase de integración.

---

## 7. Decisions (resolved)

- **D-1 (analysis trigger):** el análisis se dispara por el FE vía
  `POST /api/analysis/videos/{id}/analyze` (async job). El WS del chatbot se usa para conversación y
  el improvement plan, no para producir el histograma.
- **D-2 (upload):** nuevo endpoint de upload del slice `analysis` (`POST /api/analysis/videos`, sin
  `class_id`); los archivos van a una carpeta dedicada, metadata en `analysis-db.videos`.
- **D-3 (data split):** `skeleton_data` = store de referencia/modelo (`skeleton_video_signals` +
  `skeleton_cohort_signals` de `pole_fe`); `analysis-db` = store del usuario (`videos`,
  `skeleton-landmarks`, `video_histograms`). El scoring lee el `mean`/`std` de referencia de
  `skeleton_data.skeleton_cohort_signals`.
- **D-4 (analyzed flag):** `analysis-db.videos.analyzed` (bool), `true` cuando el histograma del
  video (`video_histograms`) se ha producido.
- **D-5 (scope):** este doc es FE-only; el slice `analysis` está planeado en
  `docs/app/pola_api/phase-13-analysis-slice/PLAN.md`.
- **D-6 (fases 8-11):** la detección de fases automática alimenta el progress panel; fallback modal
  manual (`DESCONOCIDO`), pregunta de truco (LSTM fail) y prompt de reproceso — según decisiones del
  PO en la feature de detección automática de fases.