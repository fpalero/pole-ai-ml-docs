# Repository Development Status — `pole-ai`

This document gives an at-a-glance view of every project in the `pole-ai` monorepo,
its phases, the phase status, and a short (≤ 2 line) description of each defined ticket.
It is generated from the authoritative plans under `docs/app/<project>/PLAN.md` and
`docs/package/<project>/PLAN.md` plus the ticket files `PAIML-*.md`.

## Status Legend

| Status | Meaning |
| :--- | :--- |
| **Complete / Done** | Phase finished (plan marked DONE/Complete, or all tickets shipped). |
| **In Progress** | Partially implemented; work ongoing. |
| **Pending** | Planned with tickets already defined. |
| **Deferred** | Planned but intentionally postponed (no active work). |

---

## Repository Status Overview

| Project | Type | Description | Progress |
| :--- | :--- | :--- | :--- |
| [`pola_agent`](#apppola_agent) | App | Conversational AI coaching agent (crop → analyze → LLM feedback over WebSocket). | 8/8 phases done |
| [`pola_api`](#apppola_api) | App | FastAPI backend: training, crawler, video, tools & analysis slices. | 25/26 phases done · 1 partial |
| [`pole_analyst`](#apppole_analyst) | App | Angular FE "Pole AI Coach" — athlete video-analysis coach (upload → analyze → feedback → chat). | 18/20 phases done · 1 partial · 1 future |
| [`pole_fe`](#apppole_fe) | App | Angular FE training-workflow manager (tricks, video editor, studio, model registry, jobs). | 10/11 phases done · 1 future |
| [`infra`](#appinfra) | App | CI/CD deploy pipeline: Helm, GHCR build-push, DEV/STAGING/PROD auto-deploy + observability logs. | Phases 1–2 landed · 3–5 ticketed · 6–8 planned |
| [`keycloak`](#appkeycloak) | App | Temporary magic-link access (custom login theme, verify-email, Redis cooldown/activation, expiry purge). | 4 phases planned |
| [`dev-ops`](#appdev-ops) | App | CI workflows (PR gate, phase-completion, full-suite, MediaPipe, nightly docs). | Pending analysis |
| [`chatbot`](#packageschatbot) | Package | ReAct conversational agent backend (WebSocket, tools, OpenCode client). | Complete (v1) |
| [`jobs`](#packagesjobs) | Package | Shared job infrastructure (Mongo repo, Redis queue, worker, orchestrator, router). | Complete (v1) |
| [`pole_crawler`](#packagespole_crawler) | Package | Instagram video crawler (client, disk writer, anti-bot). | Complete (core) |
| [`pole_crop`](#packagespole_crop) | Package | FFmpeg video service (crop, shift, thumbnails, frame capture). | Complete (v1) |
| [`pole_ml`](#packagespole_ml) | Package | ML pipeline: skeleton extraction, histogram features, LSTM training, embeddings, Chroma. | Core complete · 1 pending phase |
| [`pole_tools`](#packagespole_tools) | Package | Reusable tools (HistogramAnalyzer, PoseCorrector, Crop/Shift, LLM client). | Complete (Phase 1) |
| [`crew`](#packagescrew) | Package | CrewAI-based multi-agent implementation engine (tickets → worktrees → PRs). | Phase 1 planned |

---

## Apps

### `app/pole_api`
**FastAPI backend** orchestrating training (classes, process/embed, model registry, retrain),
crawler (crawl + QC), video (upload, cut, review, shift, thumbnails), tools/histogram/analysis
slices, coach services (LLM prompts + rule-based insights), and the analyst chatbot.
Reuses `pole_ml`, `pole_tools`, `pole_crawler`, `pole_crop`, `packages/chatbot` and `packages/jobs`.
Auth via Keycloak JWT (`core/auth.py`). **All 26 phases done** (2026-08-28).

| Phase | Description | Status |
| :--- | :--- | :--- |
| 1 — Fundamentals | Core config, error handling, shared Mongo client, thread job runner. | **Done** |
| 2 — Training: Classes CRUD | Classes endpoints + async create job + validation. | **Done** |
| 3 — Training: Process + Embed + Jobs | Window extraction, Chroma embed, promote, clip, video registration. | **Done** |
| 4 — Crawler: Crawl + QC | Crawl classes, list crawls/posts, QC posts. | **Done** |
| 5 — Video: Upload + auto-embed | Multipart upload + auto-embed job + verify. | **Done** |
| 6 — Video: Cut + Review + Shift + Thumbnails | Cutter/Clip/Shift/Thumbnail services + cutter configs. | **Done** |
| 7 — Training: Model registry + Retrain | Train/fine-tune, model runs, activate/approve/reject. | **Done** |
| 8 — E2E + cross-slice touchpoints | End-to-end workflows against real Mongo/Chroma + slice decoupling tests. | **Done** |
| 9 — Extraction + histogram pipeline | Two-phase split: LandmarkExtractor job, phase-frames, Biomechanical + Histogram processors. | **Done** |
| 10 — Production hardening | Auth, distributed jobs, chatbot slices mount, prod wiring, housekeeping. | **Partial / Future** |
| 11 — Histogram Analysis endpoints | Reconcile 8 metrics, cohort stats, analysis job, read/PATCH endpoints; remove legacy reference/attempt. | **Done** |
| 12 — Frame-detection Summary endpoint | Read-only `histograms/summary` computed in-job and stored on the per-video doc. | **Done** |
| 13 — Analysis slice | New `analysis` slice (upload, analyze job, histogram/summary/pose reads) backing `pole_analyst`. | **Done** |
| 14 — Histogram status flag + counts | Mark `videos.histogram_processed=true` on both histogram paths + clip-scoped `extracted`/`histo` counts (`X-Count-*`). | **Done** |
| 15 — Rename `pola_api`→`pole_api` + collection renames | Standardize naming: `pola_api`→`pole_api` (directory, imports). Rename `signal_histograms`→`skeleton_cohort_signals`, `skeleton_histograms`→`skeleton_video_signals`. Create `skeleton_trick_histograms`. | **Done** |
| 16 — Reference histograms per trick | Generate and expose per-trick reference histograms (`skeleton_trick_histograms`) from approved clips. 5 metrics (`angular_speed`, `body_tilt`, `hip_height`, `wrist_stability`, `torso_tilt_speed`). POST/GET endpoints + background job. | **Done** |
| 17 — Phase detection (Bhattacharyya + K=5) | Automatic phase detection (ENTRADA/EJECUCIÓN/SALIDA) using reference histograms + Bhattacharyya distance + temporal consensus (K=5). `PhaseDetector` in analysis slice. | **Done** |
| 18 — Analyst chatbot (`/ws/analyst-chat`) | New `analyst_chatbot` slice: conversational chatbot for athlete/coach. WS `/ws/analyst-chat` with `AnalystFacade`, tools (`histogram`, `classify`, `extract_frames`, `crop`). Relays analysis job events. | **Done** |
| 19 — Error contracts + reprocessing + quality gates | Consolidated error contracts (empty reference, corrupt video, no skeleton, low phase confidence, unclassified LSTM). Idempotent reprocessing. SLA <1 min, one-analysis-at-a-time. | **Done** |
| 20 — Analysis slice enrichment (Stitch FE) | Enriched list (`AnalysisVideoSummary`) + multi-frame pose endpoints backing the Stitch `pole_analyst` FE. | **Done** |
| 21 — Coach prompts (LLM endpoints) | One-shot LLM coaching endpoints: summary / plan / pose-analysis (text-only inputs, cached envelopes). | **Done** |
| 22 — Coach insights (rule-based) | fps storage, lazy pose extraction, `CoachInsightsService` (threshold-based frame classification), insights endpoint + chatbot tool + worker integration. | **Done** |
| 23 — Coach UI (pole_analyst) | Summary tab coach-insight cards + DetectedError card + PhaseDurations bar; analysis-completion notification + chat auto-suggestion. | **Done** |
| 24 — Stitch detail gaps BE | Session-over-session metric deltas endpoint + peak flags (`PAIML-POLE-API-072` #114). | **Done** |
| 25 — Classify-first pipeline | Single detection pass with the correct reference histograms — classify before phase detection (`PAIML-POLE-API-073`). | **Done** |
| 26 — Analyst coach tools (chatbot) | 9 chatbot tools: compare_sessions, cohort_percentiles, improvement_plan, metric_deep_dive, frame_pose, progress_trend, focus_recommendation, risk_scan, get_coach_summary/pose. | **Done** |

#### Phase 20 — Analysis enrichment (6 tickets)
- **PAIML-POLE-API-056 — Enriched analysis summary list schema + repository** — `VideoSummaryRepository` aggregation (`videos/summary`).
- **PAIML-POLE-API-057 — Enriched list service + controller** — `GET /api/analysis/videos/summary` returning `AnalysisSummaryRecord[]`.
- **PAIML-POLE-API-058 — Enriched list integration tests** — Cover aggregation + empty/no-skeleton cases.
- **PAIML-POLE-API-059 — Multi-frame pose schema + service + controller** — `GET /pose/frames` returning `PoseFrameGallery`.
- **PAIML-POLE-API-060 — Multi-frame pose integration tests** — Cover multi-frame + single-frame fallback.
- **PAIML-POLE-API-061 — Docs: enriched list + multi-frame pose** — Regenerate API docs.

#### Phase 21 — Coach prompts (LLM) (3 tickets)
- **PAIML-POLE-API-062 — Coach prompt registry** — `CoachPrompts` with templates + builders + JSON schemas for summary/plan/pose-analysis.
- **PAIML-POLE-API-063 — Coach services** — `CoachService` (deterministic data gather + one-shot LLM + cached envelopes).
- **PAIML-POLE-API-064 — Coach REST endpoints** — `GET /coach-summary`, `POST /coach-plan`, `GET /pose-analysis`.

#### Phase 22 — Coach insights (rule-based) (5 tickets)
- **PAIML-POLE-API-065 — Store fps on video doc at upload** — `fps` field on analysis video doc.
- **PAIML-POLE-API-066 — Lazy pose frame extraction** — Extract pose frames on-demand (not eagerly).
- **PAIML-POLE-API-067 — CoachInsightsService** — Threshold-based frame classification (|z| ≤ 0.5 perfect / ≤ 2 adjustment / > 2 wrong).
- **PAIML-POLE-API-068 — Coach insights endpoint + chatbot tool** — `GET /coach-insights` + chatbot tool integration.
- **PAIML-POLE-API-069 — Integrate coach insights into analysis worker** — Pre-compute insights during analysis with get-or-compute fallback.

#### Phase 23 — Coach UI (2 tickets)
- **PAIML-POLE-API-070 — Summary tab enhancement** — Structured coach content in Summary tab.
- **PAIML-POLE-API-071 — Analysis completion notification + chat auto-suggestion** — Auto-dismiss notification + chat suggestion after analysis.

#### Phase 24 — Metric deltas (1 ticket)
- **PAIML-POLE-API-072 — Metric deltas endpoint** — `GET /metric-deltas` returning session-over-session comparison + peak flags.

#### Phase 25 — Classify-first pipeline (1 ticket)
- **PAIML-POLE-API-073 — Classify before phase detection** — `ClassifyTrick` picks correct trick class → correct reference histograms for phase detection.

#### Phase 16 — Reference histograms per trick (3 tickets)
- **PAIML-POLE-API-043 — `TrickHistogramRepository` + `get_trick_references`** — Mongo-backed repo keyed by `(trick_label, metric, phase)`; GET endpoint returning metrics keyed by phase with 8-bin histograms.
- **PAIML-POLE-API-044 — `POST /api/tools/histograms/references`** — Background job (202) generating reference histograms: z-score binning of pooled 100-pt phase curves from approved clips against cohort mean/std.
- **PAIML-POLE-API-045 — `POST /api/tools/histograms/classes`** — Generate class-level histograms from all clips with `phase_frames`; GET endpoint for class statistics.

#### Phase 17 — Phase detection (Bhattacharyya + K=5) (4 tickets)
- **PAIML-POLE-API-046 — `PhaseDetector` with Bhattacharyya distance** — Implement phase boundary detection using reference histograms + Bhattacharyya distance metric.
- **PAIML-POLE-API-047 — Z-score normalization before binning** — Ensure reference curves are z-scored against cohort mean/std before binning (PAIML-POLE-API-047).
- **PAIML-POLE-API-048 — Temporal consensus (K=5)** — Sliding-window temporal consensus filter: require 5 consecutive frames of the same phase before committing.
- **PAIML-POLE-API-049 — `DetectPhasesUseCase` + persistence** — Integrate phase detection into `AnalyzeWorker`; persist `phase_frames` on video doc.

#### Phase 18 — Analyst chatbot (`/ws/analyst-chat`) (3 tickets)
- **PAIML-POLE-API-050 — `analyst_chatbot` slice settings + Mongo client** — Wire config, mount conditional WS router at `/ws/analyst-chat`.
- **PAIML-POLE-API-051 — `AnalystFacade` + tools (`histogram`, `classify`, `extract_frames`, `crop`)** — ReAct facade over analysis-domain tools; WS message handler.
- **PAIML-POLE-API-052 — Relay analysis job events to analyst WS** — Forward analysis pipeline progress/result events to connected analyst WS clients.

#### Phase 19 — Error contracts + reprocessing + quality gates (3 tickets)
- **PAIML-POLE-API-053 — Consolidated error contracts** — Standardize 5 error scenarios: empty reference, corrupt video, no skeleton, low phase confidence, unclassified LSTM.
- **PAIML-POLE-API-054 — Idempotent reprocessing** — `previously_analyzed` flag on re-POST so re-analysis replaces, not duplicates.
- **PAIML-POLE-API-055 — Quality gates (SLA + one-analysis-at-a-time)** — Analysis SLA <1 min; one-analysis-at-a-time concurrency gate; coverage ≥80%.

#### Phase 20 — Analysis slice enrichment (Stitch FE) (6 tickets)
- **PAIML-POLE-API-056 — Enriched analysis list schema + repository** — `AnalysisVideoSummary` Pydantic model + Mongo aggregation joining `videos` + `video_histograms`.
- **PAIML-POLE-API-057 — Enriched list service + controller** — `GET /api/analysis/videos/summary` returning per-video summary data (trick_label, overall_score, phases).
- **PAIML-POLE-API-058 — Enriched list integration tests + UC-B1/B2** — Integration tests for the enriched list endpoint + UC validation.
- **PAIML-POLE-API-059 — Multi-frame pose schema + service + controller** — `GET .../pose/frames` multi-frame pose endpoints.
- **PAIML-POLE-API-060 — Multi-frame pose integration tests + UC-B3/B4/B5** — Integration tests for the multi-frame pose endpoints + UC validation.
- **PAIML-POLE-API-061 — Update POLE-API.md + cross-ticket regression test** — Document the new endpoints; ensure no regressions across the phase.

#### Phase 21 — Coach prompts (LLM endpoints) (3 tickets)
- **PAIML-POLE-API-062 — Coach prompt registry** — Templates + builder functions + JSON schemas for one-shot coach prompts.
- **PAIML-POLE-API-063 — Coach services** — Deterministic data gather + one-shot LLM call + persistence of coach envelopes.
- **PAIML-POLE-API-064 — Coach REST endpoints** — coach-summary / coach-plan / pose-analysis endpoints (text-only inputs).

#### Phase 22 — Coach insights (rule-based) (5 tickets)
- **PAIML-POLE-API-065 — Store fps on video doc at upload time** — Persist frame rate for coach pose extraction.
- **PAIML-POLE-API-066 — Lazy pose frame extraction** — Extract pose frames on first `/pose/frames` access.
- **PAIML-POLE-API-067 — `CoachInsightsService`** — Threshold-based frame classification + persistence of rule-based insights.
- **PAIML-POLE-API-068 — Coach insights endpoint + chatbot tool** — Expose rule-based insights via REST + analyst chatbot.
- **PAIML-POLE-API-069 — Integrate coach insights into analysis worker** — Compute insights as part of the analysis pipeline.

#### Phase 23 — Coach UI (pole_analyst) (2 tickets)
- **PAIML-POLE-API-070 — Summary tab enhancement** — CoachInsights cards + DetectedError card + PhaseDurations bar.
- **PAIML-POLE-API-071 — Analysis completion notification + chat auto-suggestion** — Notify on analysis completion and auto-suggest next steps in the chat.

#### Phase 24 — Stitch detail gaps BE (1 ticket)
- **PAIML-POLE-API-072 — Metric deltas endpoint** — Session-over-session comparison + peak flags via `MetricDeltasService`.

#### Phase 25 — Classify-first pipeline (1 ticket)
- **PAIML-POLE-API-073 — Classify before phase detection** — Single detection pass with the correct reference histograms.

#### Phase 26 — Analyst coach tools (chatbot) (9 tickets)
- **PAIML-POLE-API-074 — `compare_sessions` tool** — Session-over-session metric deltas + peak flags via `MetricDeltasService`.
- **PAIML-POLE-API-075 — `cohort_percentiles` tool** — Athlete percentile rank per metric vs the same-trick cohort.
- **PAIML-POLE-API-076 — `improvement_plan` tool** — Expose cached/`CoachService.plan` 4-week plan via chat.
- **PAIML-POLE-API-077 — `metric_deep_dive` tool** — One metric curve + cohort band + worst frames.
- **PAIML-POLE-API-078 — `frame_pose` tool** — Single-frame joint angles + coaching breakdown.
- **PAIML-POLE-API-079 — `progress_trend` tool** — Metric trend across all same-trick sessions.
- **PAIML-POLE-API-080 — `focus_recommendation` tool** — Deterministic top-N focus areas from detections.
- **PAIML-POLE-API-081 — `risk_scan` tool** — Injury-risk joint-angle frame scanning.
- **PAIML-POLE-API-082 — `get_coach_summary`/`get_coach_pose` tools** — Read cached Phase 21 coach envelopes.

---

### `app/pole_analyst`
**Angular SPA "Pole AI Coach"** — the athlete-facing video-analysis coach: upload → analyze →
feedback → conversation. Two panes (chat left, tools right), resilient WebSocket, light theme,
lazy-loaded features. Consumes the `pola_api` `analysis` slice (done). Phases 1–18, 20 done
(`PAIML-POLE-ANALYST-001..069`); Phase 19 PARTIAL (`-066`); Phase 7 (Keycloak) deferred.

| Phase | Description | Status |
| :--- | :--- | :--- |
| 1 — Foundation & App Shell | Angular 22 scaffold, design tokens, two-pane shell, ApiClient, shared atoms, ChatState. | **Done** |
| 2 — Chat Pane | ChatbotSocketService, state mapping, chat UI, composer. | **Done** |
| 3 — Video Library + Upload | List/upload services, library pane, empty state. | **Done** |
| 4 — Video Detail Tabs | Analyze trigger + Summary/Histogram/Pose/Plan tabs. | **Done** |
| 5 — Edge / Error / Reconnect | Invalid upload, no-skeleton state, reconnect + placeholders. | **Done** |
| 6 — Integration & E2E | Playwright E2E suite (025/026 merged) + QA/accessibility pass (027). | **Done** |
| 7 — Keycloak Auth | OIDC login + per-user library (deferred, last). | **Future / Deferred** |
| 8 — Upload + Progress Panel | Analysis progress panel with live 5-stage state, job progress indicators. | **Done** |
| 9 — Results View | Results view with phase timeline, feedback, error frames, summary DTOs. | **Done** |
| 10 — Manual Phases Modal | Manual phases modal with drag boundaries, trick-name prompt, reprocess-on-reupload. | **Done** |
| 11 — Analyst Chatbot UI | WS `/ws/analyst-chat` client, tool-call chips with image artifacts. | **Done** |
| 12 — Stitch: Tab Navigation + Analysis History | Tab bar, `AnalysisHistoryTable`/`AnalysisHistoryPage`, history service + router wiring. | **Done** |
| 13 — Stitch: Results→Summary merge + Tab Reorder | Merge `ResultsView` into `SummaryTab`, remove Results tab, consolidate summary DTOs. | **Done** |
| 14 — Stitch: Pose Gallery + Metric Detail Modal | Multi-frame pose DTOs, `PoseGallery`, `MetricDetailModal` wired into `HistogramTab`. | **Done** |
| 15 — Sidebar Navigation | Design-token migration to Stitch teal, `SidebarComponent`, layout refactor, route wiring, sidebar E2E. | **Done** |
| 16 — Coach tabs (LLM structured content) | Coach DTOs + `AnalysisService` methods; Summary/Plan/Pose tabs render structured coach content. | **Done** |
| 17 — Stitch detail views | Video Library Filter Modal + Metric Distribution cards (session deltas + peak badges) + parity pass. | **Done** |
| 18 — Stitch sidebar submenu | Collapsible Dashboard group (structural parity). | **Done** |
| 19 — Stitch tabs parity round 2 | Statistics tab radar/spider + Pose Data tab (PO requirements 2026-08-23). | **Partial** |
| 20 — Sidebar Option B | Sidebar simplification (remove Coach nav item + Upload button); E2E realignment. | **Done** |

#### Phase 12 — Stitch: Tab Navigation + Analysis History (5 tickets)
- **PAIML-POLE-ANALYST-038 — Enriched analysis summary list DTOs** — `AnalysisSummaryRecord` DTO for the history table.
- **PAIML-POLE-ANALYST-039 — VideosLibraryPane tab bar** — Library tabs for switching views.
- **PAIML-POLE-ANALYST-040 — AnalysisHistoryTable component** — Table rendering enriched summary data.
- **PAIML-POLE-ANALYST-041 — AnalysisHistoryService** — `GET /api/analysis/videos/summary` integration.
- **PAIML-POLE-ANALYST-042 — Router: history route + navigation wiring** — `/history` route + sidebar nav.

#### Phase 13 — Stitch: Results→Summary merge + Tab Reorder (3 tickets)
- **PAIML-POLE-ANALYST-043 — Merge ResultsView into SummaryTab** — Consolidate results display into SummaryTab.
- **PAIML-POLE-ANALYST-044 — Remove Results tab + update AnalysisTabId** — Drop the separate Results tab.
- **PAIML-POLE-ANALYST-045 — Consolidate results-summary.ts into summary.ts** — Merge DTO files.

#### Phase 14 — Stitch: Pose Gallery + Metric Detail Modal (6 tickets)
- **PAIML-POLE-ANALYST-046 — Multi-frame pose DTOs** — `PoseFrameGallery` DTO.
- **PAIML-POLE-ANALYST-047 — PoseGallery component** — Multi-frame pose gallery (correct/adjustment/improve).
- **PAIML-POLE-ANALYST-048 — Replace PoseTab with PoseGallery** — Swap single-frame for gallery.
- **PAIML-POLE-ANALYST-049 — MetricDetailModal component** — Histogram chart modal for drill-down.
- **PAIML-POLE-ANALYST-050 — Wire MetricDetailModal in HistogramTab** — Click-to-drill-down from stat cards.
- **PAIML-POLE-ANALYST-051 — PoseGalleryService** — Multi-frame pose fetch with single-frame fallback.

#### Phase 15 — Stitch: Sidebar Navigation (6 tickets)
- **PAIML-POLE-ANALYST-052 — Design Token Migration to Stitch Teal Palette** — Update design tokens.
- **PAIML-POLE-ANALYST-053 — Create SidebarComponent** — Collapsible nav group with icon rail.
- **PAIML-POLE-ANALYST-054 — Refactor AppComponent Layout** — Two-pane split with sidebar.
- **PAIML-POLE-ANALYST-055 — Wire Sidebar Nav to routes + remove TabBar** — Navigation wiring.
- **PAIML-POLE-ANALYST-056 — Unit Tests for Sidebar + App Shell** — Cover sidebar + layout.
- **PAIML-POLE-ANALYST-057 — Playwright E2E Tests for Sidebar Navigation** — E2E for sidebar nav.

#### Phase 16 — Coach tabs (LLM structured content) (2 tickets)
- **PAIML-POLE-ANALYST-058 — Coach tab content rendering** — Summary/Plan/Pose tabs render structured coach data.
- **PAIML-POLE-ANALYST-059 — Legacy fallback for plan.ts** — Backward-compatible plan rendering.

#### Phase 17 — Stitch detail views (3 tickets)
- **PAIML-POLE-ANALYST-060 — Video Library Filter Modal** — Filter by class/trick/date/score.
- **PAIML-POLE-ANALYST-061 — Metric Distribution analysis cards** — Session deltas + peak badges.
- **PAIML-POLE-ANALYST-062 — Detail-page parity pass** — Match Stitch design mockups.

#### Phase 18 — Stitch sidebar submenu (1 ticket)
- **PAIML-POLE-ANALYST-063 — Sidebar collapsible Dashboard group** — Collapsible nav group.

#### Phase 19 — Stitch tabs parity round 2 (4 tickets)
- **PAIML-POLE-ANALYST-064 — Statistics tab redesign** — Spider/radar of 5 metrics + legend + agent explanation.
- **PAIML-POLE-ANALYST-065 — Pose Data tab** — Annotated pose list + coach insights + skeleton accents.
- **PAIML-POLE-ANALYST-066 — Plan tab auto-generates for detected trick** — Open (not started).
- **PAIML-POLE-ANALYST-067 — Sidebar Upload button investigation** — Investigate missing upload button + fix (cancelled by PO).

#### Phase 20 — Sidebar Option B (1 ticket)
- **PAIML-POLE-ANALYST-068 — Sidebar simplification: remove Coach nav + Upload button** — Option B: sidebar only (chat always visible).
- **PAIML-POLE-ANALYST-069 — Option-B E2E realignment** — Playwright E2E tests realigned to new layout.

#### Phase 12 — Stitch: Tab Navigation + Analysis History (5 tickets)
- **PAIML-POLE-ANALYST-038 — DTOs for enriched analysis summary list** — TypeScript DTOs for the enriched `GET /api/analysis/videos/summary` list.
- **PAIML-POLE-ANALYST-039 — VideosLibrary tab bar** — Tab bar for the videos library view.
- **PAIML-POLE-ANALYST-040 — AnalysisHistoryTable + AnalysisHistoryPage** — Analysis History table + page components.
- **PAIML-POLE-ANALYST-041 — AnalysisHistoryService** — Service wiring the enriched analysis summary data.
- **PAIML-POLE-ANALYST-042 — Router: history route + navigation wiring** — Add history route and connect navigation.

#### Phase 13 — Stitch: Results→Summary merge + Tab Reorder (3 tickets)
- **PAIML-POLE-ANALYST-043 — Merge ResultsView into SummaryTab** — Merge the results view into the summary tab.
- **PAIML-POLE-ANALYST-044 — Remove Results tab, update AnalysisTabId** — Remove the Results tab and update the tab id enum.
- **PAIML-POLE-ANALYST-045 — Consolidate results-summary.ts into summary.ts** — Merge the results-summary DTO into summary.

#### Phase 14 — Stitch: Pose Gallery + Metric Detail Modal (6 tickets)
- **PAIML-POLE-ANALYST-046 — DTOs for multi-frame pose response** — DTOs for the multi-frame pose endpoint.
- **PAIML-POLE-ANALYST-047 — PoseGallery component** — Gallery component for multiple annotated pose frames.
- **PAIML-POLE-ANALYST-048 — Replace PoseTab with PoseGallery** — Swap the single-frame PoseTab for the gallery.
- **PAIML-POLE-ANALYST-049 — MetricDetailModal component** — Modal for a single metric's detail/breakdown.
- **PAIML-POLE-ANALYST-050 — Wire MetricDetailModal in HistogramTab** — Connect the metric detail modal to the histogram tab.
- **PAIML-POLE-ANALYST-051 — PoseGalleryService** — Service for loading multi-frame pose data.

#### Phase 15 — Sidebar Navigation (6 tickets)
- **PAIML-POLE-ANALYST-052 — Design Token Migration to Stitch Teal Palette** — Move CSS custom properties to the Stitch teal design tokens + sidebar tokens.
- **PAIML-POLE-ANALYST-053 — Create SidebarComponent** — New sidebar navigation component.
- **PAIML-POLE-ANALYST-054 — Refactor AppComponent Layout** — Sidebar + slim top bar layout.
- **PAIML-POLE-ANALYST-055 — Wire Sidebar Navigation to Routes + Remove TabBar** — Connect sidebar to routes; remove the legacy tab bar.
- **PAIML-POLE-ANALYST-056 — Unit Tests for Sidebar + Updated App Shell** — Unit test coverage for the new shell.
- **PAIML-POLE-ANALYST-057 — Playwright E2E Tests for Sidebar Navigation** — E2E coverage for sidebar navigation.

#### Phase 16 — Coach tabs (LLM structured content) (2 tickets)
- **PAIML-POLE-ANALYST-058 — Coach DTOs + AnalysisService methods** — `coachSummary` / `generatePlan` / `poseAnalysis` service methods.
- **PAIML-POLE-ANALYST-059 — SummaryTab / PlanTab / PoseTab render structured coach content** — Render coach content with legacy fallback.

#### Phase 17 — Stitch detail views (3 tickets)
- **PAIML-POLE-ANALYST-060 — Video Library Filter Modal** — Status filters (Stitch screen parity).
- **PAIML-POLE-ANALYST-061 — Metric Distribution Analysis cards** — Session deltas + Peak Performance badges.
- **PAIML-POLE-ANALYST-062 — Detail-page parity pass** — vs the Stitch "Analysis Details" screen.

#### Phase 18 — Stitch sidebar submenu (1 ticket)
- **PAIML-POLE-ANALYST-063 — Sidebar collapsible Dashboard group** — Stitch structural parity.

#### Phase 19 — Stitch tabs parity round 2 (4 tickets)
- **PAIML-POLE-ANALYST-064 — Statistics tab redesign** — Spider/radar of the 5 metrics + metric legend + agent explanation.
- **PAIML-POLE-ANALYST-065 — Pose Data tab** — Annotated pose list with coach insights + skeleton accents.
- **PAIML-POLE-ANALYST-066 — Plan tab auto-generate for detected trick** — No manual entry when the trick is known (📋 PLANNED).
- **PAIML-POLE-ANALYST-067 — Sidebar Upload button** — Investigate "missing" PO report and fix placement (❌ cancelled by PO).

#### Phase 20 — Sidebar Option B (2 tickets)
- **PAIML-POLE-ANALYST-068 — Sidebar simplification (Option B)** — Remove the Coach nav item and Upload button.
- **PAIML-POLE-ANALYST-069 — Option-B E2E realignment** — Retire tab-bar expectations, triage detail-tab failures.

---

### `app/pole_fe`
**Angular FE training-workflow manager.** Tricks CRUD, video management + editor/shift, training
studio, model registry, system jobs, class stats histograms. Playwright E2E done.

| Phase | Description | Status |
| :--- | :--- | :--- |
| 1 — Foundation & App Shell | Scaffold, design system, routing, API layer. | **Done** |
| 2 — Tricks CRUD | Trick list/detail/CRUD screens. | **Done** |
| 3 — Tricks detail: Video Management | Video upload/list + auto-embed. | **Done** |
| 4 — Tricks detail: Video Editor + Shift | Cut/shift/review workflow. | **Done** |
| 5 — Training Studio | Process/embed/train/retrain UI. | **Done** |
| 6 — Model Registry | Model list/activate/reject screens. | **Done** |
| 7 — System Jobs | Jobs dashboard + polling. | **Done** |
| 8 — Integration, E2E & Polish | Playwright E2E-1..20 + polish. | **Done** |
| 9 — Extraction → Process (biometric + histogram) | `Extract`/`Biomech`/`Histo` actions, `EXTRACTED`/`HISTO` statuses, Biomechanical Signal Analysis view. | **Done** |
| 10 — Future: Chatbot FE + cluster selector | Chatbot FE delivered (via `pola_agent` AGENT-013); cluster selector + API-reachability banner remain. | **Future** |
| 11 — Class stats histograms + reference generation | Class-level cohort histograms panel (mean curves + 8-bin charts) + "Generate Reference" action with job progress. | **Done** |

#### Phase 8 — Integration, E2E & Polish (4 tickets)
- **PAIML-POLE-FE-001 — Playwright setup** — Add `@playwright/test`, `playwright.config.ts`, `e2e/`, browser install + FE+BE driver on `_testing` DBs.
- **PAIML-POLE-FE-002 — E2E Workflow A + Trick CRUD** — E2E-01..04 and E2E-14..15; real MediaPipe + ChromaDB (temp dir).
- **PAIML-POLE-FE-003 — E2E Workflow B + C** — E2E-05..12 and E2E-13; crawl/cut/train with `E2E_FAKES`, extract/process/embed real.
- **PAIML-POLE-FE-004 — E2E Jobs + Model registry + Errors + Responsive** — E2E-16..20: jobs poll/cancel, model registry, error states, responsive.

#### Phase 9 — Extraction → Process (biometric + histogram) flow (4 tickets)
- **PAIML-POLE-FE-005 — Pipeline DTOs + service wiring** — `extracted`/`phase_frames`/`histogram_processed` on `VideoRecordDto`; `HistogramDto`/`HistogramSummaryDto`; `extract`/`setPhaseFrames`/`submitHistogramAnalysis`/`getHistogram`/`getHistogramSummary`. Blocked by `PAIML-POLA-API-036`.
- **PAIML-POLE-FE-006 — Extract/Biomech/Histo actions + EXTRACTED/HISTO statuses** — Bulk toolbar actions + filter pills, counts from `X-Count-extracted`/`X-Count-histo`. Blocked by `PAIML-POLA-API-037`.
- **PAIML-POLE-FE-007 — Biomechanical Signal Analysis view** — Synchronized video + 8-signal chart + temporal annotation (`PUT /clips/{id}/phase-frames`); post-analysis only (empty state when no histogram).
- **PAIML-POLE-FE-008 — Tests + E2E** — Unit + Playwright E2E for extraction → process (biometric + histogram), incl. pre-Histo empty state → post-Histo chart.

#### Phase 11 — Class stats histograms + reference generation (4 tickets)
- **PAIML-POLE-FE-009 — Reference histogram DTOs + API service** — `generateReferences()`, `getClassReferences()`, `getTrickReferences()`.
- **PAIML-POLE-FE-010 — Generate reference histograms action + job progress** — Button + `JobPollService` progress.
- **PAIML-POLE-FE-011 — Class histogram stats panel** — Per-class cohort mean curves + 8-bin charts.
- **PAIML-POLE-FE-012 — E2E spec for reference histograms + empty state** — Playwright E2E-24/25.

---

### `app/pola_agent`
**Origin project.** Conversational AI coaching agent (crop → analyze → LLM feedback over WebSocket).
Consolidated into `pole_api` as `chatbot` + `training_chatbot` slices. No longer a standalone host.

| Phase | Description | Status |
| :--- | :--- | :--- |
| 0 — Foundation | Create tool/crop/jobs/chatbot packages + env + Postgres migrations. | **Done** |
| 1 — Reusable tools package | LLM client, Crop/Shift, HistogramAnalyzer, PoseCorrector. | **Done** |
| 2 — Shared jobs package | Job model + Mongo repo, Redis queue, worker, orchestrator. | **Done** |
| 3 — Chatbot backend | OpenCode client, ToolRegistry, ReActAgent, `WS /ws/chat`. | **Done** |
| 4 — Tools API slice in `pole_api` | `ToolsService` facade, `POST /api/tools/*`. | **Done** |
| 5 — Chatbot slice in `pole_api` | Consolidate standalone chatbot into pole_api. | **Done** |
| 6 — Reference data + hardened analysis | Reference data in Mongo; **automatic phase detection REMOVED (PO 2026-08-13)**. | **Done** |
| 7 — Chatbot FE + training chatbot | Chatbot FE in `pole_fe` + training chatbot Path A. | **Done** |

---

### `app/keycloak`
**Keycloak realm config + temp-access orchestration.** Custom login theme ("Get temporary access"),
magic-link delivery, per-app role mapping, 2-hour session limits, expiry purge.

| Phase | Description | Status |
| :--- | :--- | :--- |
| 1 — Core realm setup | Configure realm SMTP, magic-link delivery, confidential client, custom login theme, 2h session limits. | **PLANNED** |
| 2 — pole_api temp-access orchestration | Temp-access settings + Keycloak admin client + Redis repo; public endpoints + lazy activation; 2h + cooldown. | **PLANNED** |
| 3 — Expiry purge | Delete all temp-user data + disable user (cascade). | **PLANNED** |
| 4 — Tests + docs | Unit/integration tests + Keycloak README + ENV_VARS. | **PLANNED** |

#### Phase 1 — Core realm setup (4 tickets)
- **PAIML-KEYCLOAK-001 — Configure realm SMTP magic-link delivery** — Verify realm email settings + test magic link.
- **PAIML-KEYCLOAK-002 — Add confidential pole-api-admin client** — Service account for admin operations.
- **PAIML-KEYCLOAK-003 — Custom login theme** — `pole-ai-login` theme with "Get temporary access" button.
- **PAIML-KEYCLOAK-004 — Cap pole-fe/pole-analyst sessions to 2 hours** — Access + refresh token lifetimes.

#### Phase 2 — pole_api temp-access orchestration (6 tickets)
- **PAIML-KEYCLOAK-005 — Temp-access settings + Keycloak admin client + Redis repository** — Wire config + `temp:req`/`temp:active` repo.
- **PAIML-KEYCLOAK-006 — Public temporary-access endpoints + lazy activation hook** — `POST /api/temp-access/request` + `GET /api/temp-access/activate`.
- **PAIML-KEYCLOAK-007 — Enforce 2h window + cooldown at request time** — Block if active session exists or cooldown not met.
- **PAIML-KEYCLOAK-008 — Owner-scoped audit of temp-user resources** — `GET /api/temp-access/audit` listing resources.
- **PAIML-KEYCLOAK-009 — Expiry purge** — Delete temp-user data + disable Keycloak user.
- **PAIML-KEYCLOAK-010 — Expiry sweeper** — Background job to enforce expiry.

#### Phase 3 — Tests + docs (2 tickets)
- **PAIML-KEYCLOAK-011 — Unit + integration tests** — Cover temp-access flow + cooldown + purge.
- **PAIML-KEYCLOAK-012 — Temp-access docs** — Keycloak README + ENV_VARS.

---

### `app/infra`
**Kubernetes (k3s) deployment.** Helm charts, GitHub Actions CI/CD, health checks, Slack notifications.

| Phase | Description | Status |
| :--- | :--- | :--- |
| 1 — Helm charts + local K3s | Base Helm charts for pole_api/pole_fe/pole_analyst + k3s local cluster. | **Done** |
| 2 — CI/CD: GHCR build + Trivy scan | Build & push Docker images to GHCR + Trivy security scan. | **PLANNED** |
| 3 — DEV environment auto-deploy | GitHub Env `dev` + auto-deploy on main merge. | **PLANNED** |
| 4 — STAGING environment | GitHub Env `staging` + manual deploy gate. | **PLANNED** |
| 5 — PROD environment + notifications | GitHub Env `prod` + Slack webhook + deploy notifications. | **PLANNED** |

#### Phase 2 — CI/CD: GHCR build + Trivy scan (4 tickets)
- **INFRA-001 — GHCR Build & Push** — `docker/build-push-action` to `ghcr.io/fpalero/pole-ai-*`.
- **INFRA-002 — Docker Layer Caching** — `docker/build-push-action` cache-from/cache-to.
- **INFRA-003 — Trivy Security Scan** — `aquasecurity/trivy-action` on built images.
- **INFRA-004 — GitHub Env `dev`** — Create dev environment with protection rules.

#### Phase 3 — DEV environment auto-deploy (2 tickets)
- **INFRA-005 — DEV Auto-Deploy** — Helm deploy on push to main via `appleboy/ssh-action`.
- **INFRA-006 — Health Check Verification** — curl health endpoints post-deploy.

#### Phase 4 — STAGING environment (2 tickets)
- **INFRA-007 — Env `staging`** — Create staging environment.
- **INFRA-008 — STAGING Deploy** — Manual deploy gate for staging.

#### Phase 5 — PROD environment + notifications (7 tickets)
- **INFRA-009 — Env `prod`** — Create production environment.
- **INFRA-010 — PROD Deploy w/ rollback** — Production deploy with auto-rollback on failure.
- **INFRA-011 — Slack Webhook Secrets** — Store Slack webhook in GitHub secrets.
- **INFRA-012 — Slack Notification Job** — Send deploy status to Slack.
- **INFRA-013 — Document Env Protection Rules** — Document required reviewers + wait timers.
- **INFRA-014 — Update README CI/CD** — Document the full CI/CD pipeline.
- **INFRA-015 — Health Check Verification Script** — Reusable health check script.

---

### `app/infra`
**CI/CD deploy pipeline.** Helm umbrella charts for local k3s, GHCR build & push, DEV/STAGING/PROD
auto-deploy + observability (elastic-stack, pole-api structured logging, packages log shipping).
Phases 1–2 have largely landed in code (`build-push.yml`, `deploy-prod.yml`, `deploy-staging.yml`,
repository_dispatch deploy-dev); Phases 3–5 are ticketed; Phases 6–8 are planned.
24 tickets (`PAIML-INFRA-001..024`, counter=24); 8 phase folders
(`phase-1-ghcr-build-push` … `phase-8-packages-logs`).

| Phase | Description | Status |
| :--- | :--- | :--- |
| 1 — Helm Charts & Local Deploy (Foundation) | Umbrella `helm/pole-ai` chart + build-push/deploy/teardown scripts + local registry mirror. | **Landed in code** |
| 2 — Build & Push to GHCR | `.github/workflows/build-push.yml` (push to main/develop), Docker layer caching, SHA/branch/semver tags, Trivy scan. | **Landed in code** |
| 3 — DEV Auto-Deploy | GitHub Environment `dev` + `.github/workflows/deploy-dev.yml` + Helm `--wait` + health check. | **Ticketed** |
| 4 — STAGING & PROD Pipelines | `deploy-staging.yml` / `deploy-prod.yml`, manual gates, auto-rollback, Slack notifications. | **Landed in code (partial)** |
| 5 — Documentation & Health Verification | Environment protection rules + infrastructure README + post-deploy health verification. | **Ticketed** |
| 6 — Elasticsearch + Kibana foundation | ES subchart (single-node, ILM 7-day), Kibana ingress + Keycloak SSO, cluster health check. | **Planned** |
| 7 — Structured logging in pole_api | python-json-logger, LOG_LEVEL/LOG_SERVICE_NAME env, JSON format tests. | **Planned** |
| 8 — Structured logging in packages + shipping | Shared logger in pole_tools, migrate pole_ml/crawler/jobs, Filebeat DaemonSet. | **Planned** |

---

### `app/keycloak`
**Temporary magic-link access.** Custom Keycloak login theme offering Login / Get temporary access;
verify-email magic link; per-app roles; Redis `temp:req` cooldown + `temp:active` window; expiry
purge of all temp-user resources. 4 phases 📋 PLANNED, 12 tickets (`PAIML-KEYCLOAK-001..012`,
counter=12). No `temp_access.py` / theme in code yet.

| Phase | Description | Status |
| :--- | :--- | :--- |
| 1 — Keycloak realm, SMTP & custom login theme | `PAIML-KEYCLOAK-001..004`. | **Planned** |
| 2 — pole_api temp-access orchestration | Endpoint + Redis + activation (`PAIML-KEYCLOAK-005..007`). | **Planned** |
| 3 — Temp-user data isolation & expiry purge | `PAIML-KEYCLOAK-008..010`. | **Planned** |
| 4 — Tests, docs & verification | `PAIML-KEYCLOAK-011..012`. | **Planned** |

---

### `app/dev-ops`
**CI workflows.** Planned dev-ops CI pipeline (PR gate, phase-completion, full-suite, MediaPipe
dedicated action, nightly docs, branch protection). **Pending analysis** — counter=0, only `PLAN.md` +
`PROJECT_VARS.md`; no tickets or phase folders defined yet.

| Phase | Description | Status |
| :--- | :--- | :--- |
| 1–7 | CI foundation → PR workflow → phase-completion → full-suite → MediaPipe action → nightly docs → branch protection/secrets/docs. | **Pending Analysis** |

---

## Packages

### `packages/chatbot`
> Plan: [packages/chatbot/PLAN.md](packages/chatbot/PLAN.md)

**Conversational agent backend (`pole-chatbot`).** ReAct + LangGraph agent over WebSocket,
`ToolRegistry`, `OllamaLLM` + `OpenRouterLLM` adapters, OpenCode client, worker job handlers.
`PoleLangGraphAgent` implements StateGraph with `agent`/`tool` nodes + conditional routing.
`AgentState` requires `pending_tool_calls` field. Activated via `LLM_PROVIDER=ollama` +
`OLLAMA_MODEL` env vars. **Status: Complete (v1).**

### `packages/jobs`
> Plan: [packages/jobs/PLAN.md](packages/jobs/PLAN.md)

**Shared job infrastructure (`pole-jobs`).** `Job` model with `entity_name` + paginated history,
Mongo `JobRepository`, Redis `JobQueue`, Redis pub/sub events, `JobWorker` (retries/backoff/cancel),
`JobOrchestrator`, FastAPI `JobRouter` mixin. **Status: Complete (v1).**

### `packages/pole_crawler`
> Plan: [packages/pole_crawler/PLAN.md](packages/pole_crawler/PLAN.md)

**Instagram video crawler.** `InstagramClient`, `DiskWriter`/`PostMetadata`, session management,
notifications, CLI main; anti-bot waits. Consumed by the `pole_api` crawler slice. **Status:
Complete (core).**

### `packages/pole_crop`
> Plan: [packages/pole_crop/PLAN.md](packages/pole_crop/PLAN.md)

**FFmpeg video service.** `crop_segment`, `probe_duration`, `probe_metadata`, `capture_frame`,
frame-accurate re-encode + stream-copy modes. Consumed by `pole_tools`. **Status: Complete (v1).**

### `packages/pole_ml`
> Plan: [packages/pole_ml/PLAN.md](packages/pole_ml/PLAN.md)

**ML training/inference pipeline (`pole_ml` + `pole_tools` CLI).** Skeleton extraction,
biomechanical features, sliding windows, LSTM training, embeddings, Chroma, hybrid classifier,
video cutter, two-phase extraction split. ~549 tests at 81.63% coverage. **Status: Core complete.**

| Phase | Description | Status |
| :--- | :--- | :--- |
| 8 — CLI integration gap-fill | Idempotent re-run + `--phase-frames` skip path tests. | **Pending** |

#### Phase 8 — CLI integration gap-fill (1 ticket)
- **PAIML-POLE-ML-001 — CLI integration gap-fill** — Add missing UC-82..90 CLI tests: idempotent re-run and the `--phase-frames` skip path.

### `packages/pole_tools`
> Plan: [packages/pole_tools/PLAN.md](packages/pole_tools/PLAN.md)

**Reusable tools package (`pole-tools`).** HTTP-free wrappers — `CropTool`, `ShiftTool`,
`HistogramAnalyzer`, `PoseCorrector`, `OpenCodeLLMClient` — plus a services
facade and 35 unit tests. Consumed by `packages/chatbot`. **Status: Complete (Phase 1).** No phase
folders or tickets defined; future work is tracked under `pola_agent` and `pola_api` Phases 6/11.

## Dev-tooling engine

### `crew`
> Plan: [packages/crew/PLAN.md](packages/crew/PLAN.md)

**CrewAI-based multi-agent implementation engine.** Top-level `crew/` dev-tooling package that
implements opencode tickets end-to-end: parses `PAIML-*.md` tickets, builds the dependency graph,
runs Developer → Reviewer → Tester crews in isolated `git worktree`s, opens PRs against `develop`,
and runs a phase-end staging integration gate. Two flows: `crew-implement` and `crew-phase-end`.

| Phase | Description | Status |
| :--- | :--- | :--- |
| 1 — Guardrails (anti-infinite-loop) | Structural + algorithmic guardrails to prevent agent infinite loops: `max_iter`/`max_rpm` on agents, task validation functions, explicit tool success states. | **Pending** |

#### Phase 1 — Guardrails (anti-infinite-loop) (7 tickets)
- **PAIML-CREW-001 — Guardrails module** — Create `crew/guardrails.py` with `apply_guardrails()`, task validators, and `tool_result()` helper.
- **PAIML-CREW-002 — Tool refactor (SUCCESS/ERROR)** — Refactor all tools in `crew_implement.py` to return explicit `SUCCESS:` / `ERROR:` prefixed messages.
- **PAIML-CREW-003 — Apply guardrails to agents + tasks** — Wire `apply_guardrails()` on all 5 agents; add `guardrail=` to dev/review/test tasks.
- **PAIML-CREW-004 — Phase-end guardrails** — Apply the same guardrails to `crew/crew_phase_end.py` workflow.
- **PAIML-CREW-005 — Unit tests** — Unit tests for guardrail functions, tool result formatting, and validator logic.
- **PAIML-CREW-006 — Documentation update** — Update `crew/README.md` with new env vars (`CREW_MAX_ITER`, `CREW_MAX_RPM`) and guardrail behavior.
- **PAIML-CREW-007 — Fix `detect_project` for `docs/packages/`** — Make `detect_project()` recognize the plural `packages` segment so package tickets load (prerequisite).
