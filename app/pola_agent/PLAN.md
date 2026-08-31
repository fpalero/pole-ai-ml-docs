# Implementation Plan — `pola_agent` (Conversational AI Coaching Agent)

> **Status:** Core analysis engine built (`packages/pole-tools`: HistogramAnalyzer, PoseCorrector,
> OpenCodeLLMClient, Crop/Shift tools, PhaseDetector). Chatbot backend + shared jobs package
> built (`packages/chatbot`, `packages/jobs`). `tools` API slice in `pola_api` is implemented
> (Phase 4): `ToolsService` facade, `POST /api/tools/crop|shift|analyze|correct`, reference
> metrics/thresholds endpoints, PostgreSQL repos + migration (the reference/analyze surface was later
> removed by `pola_api` Phase 11 — reference data now lives in Mongo `signal_histograms`). **All phases complete:**
> Phase 5 (chatbot consolidation into `pola_api`) ✅, Phase 7 (Chatbot FE + training chatbot) ✅.
> **Ollama + LangGraph integration** added to `packages/chatbot`: `OllamaLLM` adapter wraps
> `ChatOllama` with OpenAI-format msg/tool conversion; `PoleLangGraphAgent` implements a
> `StateGraph`-based agent with `agent`/`tool` nodes + conditional routing. Activated via
> `LLM_PROVIDER=ollama` + `OLLAMA_MODEL` env vars (default backward-compatible with opencode).
> **Source docs:** `docs/app/pola_agent/agent_requirements.md` (M-01..M-08, PD-01..05, TC, LLM
> prompts), `agent-react.md` (ReAct design), `pose_correction.md`,
> `docs/app/pola_agent/implementation_plan.md` (v1.1, incl. §12 process-data split + §13 jobs/chatbot).

---

## 1. Feature Context & Objective

- **Goal:** A conversational AI coaching agent that analyzes a pole-dance trick video over a
  WebSocket turn-by-turn chat: crop → confirm → (shift → confirm)* → analyze (phases, Z-score,
  critical frame, deviation plot) → LLM coaching feedback → optional pose correction overlay.
- **Non-Functional Constraints:** LLM provider is OpenCode-compatible over HTTP (`opencode serve`,
  `/v1/chat/completions`); reference statistics live in **PostgreSQL** (`reference_metrics`,
  `reference_thresholds`, `attempt_logs`); ReAct loop bounded (`max_iterations`, default 6); job
  events (`job_started/progress/done/error`) forwarded to the WebSocket; chatbot slice may only
  call the `tools` slice facade (no direct `pole_ml`/`pole_crop`/DB imports).
- **Affected Components:**
  - `packages/pole-tools/` — `histogram_analyzer.py`, `pose_corrector.py`, `phase_detector.py`,
    `llm_client.py`, `crop_tool.py`, `shift_tool.py`, `schema.py`, `exceptions.py`,
    `services/` (crop, shift, histogram, similarity), tests.
  - `packages/chatbot/` — `agent.py`, `tools.py`, `llm.py`, `ws.py`, `job_handlers.py`,
    `app.py`, `config.py`, tests (incl. `test_ws_integration.py`).
  - `packages/jobs/` — `models.py`, `queue.py`, `events.py`, `repository.py`, `worker.py`,
    `orchestrator.py`, `router.py`.
  - `app/pola_api/src/tools/` + migration `001_tools_postgres.sql` (Phase 4 complete).
  - Planned: `app/pola_api/src/chatbot/` slice (design in implementation_plan §2/§7).
- **Assumptions:** `opencode serve` runs as a sidecar (LLM unavailable → fallback advice or 503);
  ffmpeg binary present; reference data is the Mongo `skeleton_data.signal_histograms` cohort
  (produced by the histogram-analysis job).

---

## 2. Architectural Layering (The "Where")

- **Domain:** `CropResult`/`ShiftResult`/`AnalysisResult` (Pydantic in `pole_tools.schema`),
  trick classification (STATIC/SPIN/MOMENTUM), phase model (ENTRANCE/EXECUTION/EXIT), reference
  cohort (mean/std per metric, 300 pts, Mongo `signal_histograms`), attempt log.
- **Application:** `HistogramAnalyzer.analyze/feedback`, `PoseCorrector.correct/overlay`,
  `PhaseDetector.detect`, `CropTool`/`ShiftTool`, `ToolsService` facade (implemented in
  `pola_api`), `ReActAgent.run` (ReAct loop), `ToolRegistry.invoke`, session service (planned).
- **Infrastructure:** `OpenCodeLLMClient` (httpx OpenAI-compatible), `pole_crop.ffmpeg`
  (crop/shift/thumbnails), `pole_ml` (landmarks, embeddings, Chroma), PostgreSQL repos
  (`app/pola_api/src/tools/repositories/`), `JobOrchestrator` + `JobWorker` (Redis queue + Mongo jobs).
- **Presentation:** `ChatbotRouter` — `WS /ws/chat` (message in → `agent_reply` + job events out);
  implemented `POST /api/tools/crop|shift|analyze|correct` + reference/attempt/health endpoints.

---

## 3. Implementation Roadmap (Atomic Steps)

### Phase 0: Foundation — ✅ DONE
- [x] Create `packages/pole-tools`, `packages/pole-crop`, `packages/jobs`, `packages/chatbot`
  (pyproject, src layout) + editable deps in root `pixi.toml`.
- [x] Env settings: `OPENCODE_URL`, `OPENCODE_MODEL`, `AGENT_MAX_ITERATIONS`, `MONGODB_URI`,
  `REDIS_URL`, `CHATBOT_OUT_DIR`, DB names.
- [x] Infrastructure PostgreSQL migrations for `reference_metrics`, `reference_thresholds`,
  `attempt_logs` (implemented in `app/pola_api/migrations/001_tools_postgres.sql`).

### Phase 1: Reusable tools package — ✅ DONE
- [x] `OpenCodeLLMClient` (multimodal wrapper over `/chat/completions`, injectable httpx).
- [x] `CropTool` / `ShiftTool` wrapping `pole_crop.ffmpeg.crop_segment` (explicit boundaries).
- [x] `HistogramAnalyzer` — M-01..M-08 metrics, classify (STATIC/SPIN/MOMENTUM), phase resample
  (100/phase, 300 total), Z-score, critical frame, deviation plot, feedback prompt.
- [x] `PoseCorrector` — straighten_leg / point_foot / level_hips + red/green overlay.
- [x] `PhaseDetector` — automatic phase boundary detection (PD-01..05).
- [x] `services/` facade (`crop_clip`, `shift_clip`, `compute_histogram`, `compute_metrics`,
  `embed_window`, `classify_window`) — the only import surface for the chatbot.
- [x] Unit tests (pole-tools: 35 tests; ≥80%).

### Phase 2: Shared jobs package — ✅ DONE
- [x] `Job` model + Mongo `JobRepository`; Redis `JobQueue` (FIFO of ids); `JobEventPublisher`
  / `JobEventSubscriber` (`job:started/progress/done/error`).
- [x] `JobWorker` with retries/backoff/cancel (`JobCancelled`), `JobContext.set_progress`.
- [x] `JobOrchestrator` tying submit/list/cancel/worker/subscriber together.
- [x] FastAPI `JobRouter` mixin (`POST /api/jobs`, `GET /api/jobs/{id}`, `GET /api/jobs`,
  `POST /api/jobs/{id}/cancel`, `WS /api/jobs/{id}/progress`).
- [x] Unit tests (fakeredis + mongomock) + `pixi run test-jobs`.

### Phase 3: Chatbot backend — ✅ DONE
- [x] `OpenCodeClient` (text chat), `ToolRegistry` (sync `histogram`/`similarity`, job-mode
  `crop`/`shift`), `ReActAgent` (tool-call loop, error capture, iteration budget).
- [x] `ChatbotRouter` — `WS /ws/chat`: incoming `{type:"message"}` → `agent_reply` + relayed job
  events filtered by `ws_connection_id`.
- [x] Worker-side `JOB_HANDLERS` (`crop`, `shift`) with progress stages.
- [x] Integration test `test_ws_integration.py` (real Redis + Mongo + ffmpeg, `pixi run
  test-chatbot-live`).

### Phase 4: Tools API slice in `pola_api` — ✅ DONE
- [x] Application `ToolsService` facade: `crop`, `shift`, `analyze`, `correct`.
- [x] Presentation `POST /api/tools/crop`, `/shift`, `/analyze`, `/correct`.
- [x] Infrastructure PostgreSQL repos for `reference_metrics`, `reference_thresholds`,
  `attempt_logs` (base, Postgres, in-memory) + migration.
- [x] Infrastructure map package exceptions (`ToolError`, `VideoError`, `LLMError`) to HTTP codes
  (`PoleToolError` handling + `BadRequestError` in `pola_api` core errors).
- [x] Additional endpoints: `GET/POST /api/tools/reference/metrics`,
  `GET/POST /api/tools/reference/thresholds`, `GET /api/tools/attempts/{id}`,
  `GET /api/tools/health`.
- [x] Unit + API integration tests (`pola_api` tools test suite: 13 tests; full `pola_api`
  suite: 267 passed).

### Phase 5: Chatbot slice in `pola_api` (consolidation) — ✅ DONE
- [x] Presentation mount chatbot router in `pola_api` (consolidated under `app/pola_api/src/chatbot/`).
- [x] Application `ChatbotSession` state (`original_video`, `current_crop`, `confirmed`, history)
  with Redis/Postgres persistence; session resume via `session_id`.
- [x] Application prompt enforces Crop → Confirm → (Shift → Confirm)* → Analyze → (Correct?).
- [x] Application graceful LLM off-script handling (parse errors, max iterations, rephrase).
- [x] Presentation rate limiting per session (429/queue) + metrics (tool latency, LLM tokens).
- [x] `PoleLangGraphAgent` — LangGraph `StateGraph` with `agent`/`tool` nodes, conditional
  routing, `_TokenMetricsCallback` for token tracking. Activated via `LLM_PROVIDER=ollama`.

### Phase 6: Reference data + hardened analysis — ✅ DONE (re-planned to Mongo)
> **2026-08-13 re-plan:** reference data no longer uses PostgreSQL. It is now the Mongo
> `skeleton_data.signal_histograms` cohort (mean/std per `(trick_label, metric)`, 300-pt) produced
> by `pole_ml.HistogramDataProcessor` + `pola_api /histograms/analysis`, scored by
> `/histograms/summary` (fixed `|z|>1` detection). The Postgres `seed_reference.py` /
> `discover_thresholds.py` CLIs and their pixi tasks were **removed** (endpoints no longer exist;
> thresholds are fixed, not LLM-discovered).
> **PO decision 2026-08-13:** automatic phase detection is **no longer a requirement** — phases are
> entered **manually** via `PUT /api/training/clips/{id}/phase-frames`. The `PhaseDetector` and its
> fallback in `histogram_analyzer` are **removed** via `PAIML-POLE-AGENT-015` (was "implemented but
> API wiring deferred"; the deferred wiring is now resolved by **removal**, not by wiring).
- [x] Infra reference data → Mongo `signal_histograms` cohort (via histogram analysis job; no manual seeding).
- [x] Tests pole-tools hardening suite (`pixi run test-hardening`): HA-S4 retry/fallback, fallback-rate gate.
- [x] ~~App automatic phase detection — `PhaseDetector` implemented in `pole_tools` (PD-01..05)~~ **REMOVED (PO)** — auto-detection deleted via `PAIML-POLE-AGENT-015`; phases are manual only.

### Phase 7: Chatbot FE + training chatbot — ✅ DONE
- [x] **Decision:** Chatbot FE lives inside the existing `pole_fe` Angular app
  (`app/pole_fe/src/app/features/chatbot/`, lazy route `/chatbot`), not a new
  frontend project — see Open Questions §7 (PAIML-POLE-AGENT-013).
- [x] Presentation Chatbot FE — WS client for `/api/chatbot/ws/chat` (consolidated
  `pola_api` slice from Phase 5, not the deprecated standalone app): connect /
  reconnect with backoff / heartbeat watchdog / clean close, message protocol
  (`message` in; `agent_reply` + `job_*` events out), chat UI (user/agent
  bubbles), inline job progress chips per tool invocation, artifact rendering
  (deviation plot / critical frame / correction overlay), session resume via
  `session_id`, error states (disconnect / 429 / 503 / manual-timestamps).
- [x] Application training chatbot (Path A: slice in `pola_api`).
  `app/pola_api/src/training_chatbot/` with `WS /ws/training-chat`,
  `TrainingFacade`, 4 tools (hyperparameter_search, dataset_stats,
  compare_models, inspect_job), job event relay, session resume.

---

## 4. Quality Gates & Testing Commands (DoD)

- **Unit Tests:** `pixi run test` (pole-train-model, ≥80%), `pixi run test-jobs`,
  `pixi run test-chatbot` (unit, excludes integration).
- **Integration Tests:** `pixi run test-chatbot-live` (real Redis/Mongo/ffmpeg WS→jobs→crop E2E);
  `pixi run test-api` for `pola_api` slices.
- **Automation:** CI runs unit suites; chatbot→tools-only import linter for `src/chatbot/`.
- **Database Target:** `pole_chatbot_testing` (chatbot), `pole_api_testing` + `skeleton_data_testing` (API), PostgreSQL `reference_*` (future).
- **Coverage Requirement:** ≥ 80% per package.
- **Additional Checks:** `REDIS`/`MONGO` up via `pixi run redis-up` + docker-compose Mongo; OpenCode sidecar health-check at startup.

---

## 5. Defined Use Cases (Gherkin + Technical Matrix)

### UC-AG-01: Histogram analysis of a clean STATIC trick
- **Given** a clean static trick video with landmarks and phase_frames
- **When** user sends a message asking to analyze the video
- **Then** agent runs crop → confirm → analyze and replies with feedback
- **And** analysis returns `trick_type=STATIC`, phases within ±2 frames, feedback < 10 s

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `WS /ws/chat` |
| Request Method | WebSocket |
| Required Headers | `Upgrade: websocket` |
| Payload Example | `{"type": "message", "message": "Analyze clean_invert.mp4"}` |
| DB State (Before) | no attempt log |
| DB State (After) | `attempt_logs` row (when persistence lands); analysis dict returned |

### UC-AG-02: Known execution flaw detected
- **Given** a video with bent knees in EXECUTION
- **When** the analysis pipeline runs
- **Then** critical frame is in EXECUTION phase with `max_z_score > 2.0`
- **And** deviation plot + critical frame image generated and sent to LLM

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `WS /ws/chat` |
| Request Method | WebSocket |
| Required Headers | `Upgrade: websocket` |
| Payload Example | `{"type": "message", "message": "Check my handspring"}` |
| DB State (Before) | reference data present |
| DB State (After) | `max_z_score > 2.0`; plot artifact written to `chatbot_output/` |

### UC-AG-03: Crop → shift → confirm → analyze (ReAct multi-step)
- **Given** a long raw video
- **When** user asks to crop, then says "shift by 1s", then confirms
- **Then** agent runs `crop` (job), `shift` (job), then `analyze`
- **And** the WS receives `job_started`/`job_progress`/`job_done` for each job before `agent_reply`

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `WS /ws/chat` |
| Request Method | WebSocket |
| Required Headers | `Upgrade: websocket` |
| Payload Example | sequence of `message` frames |
| DB State (Before) | source video available |
| DB State (After) | shifted clip artifact exists; job events relayed with matching `ws_connection_id` |

### UC-AG-04: Crop fails → ask for manual timestamps
- **Given** a corrupt/unprocessable source
- **When** the `crop` tool raises `ToolError`
- **Then** agent replies asking for manual timestamps
- **And** the session remains open; no LLM feedback is fabricated

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `WS /ws/chat` |
| Request Method | WebSocket |
| Required Headers | `Upgrade: websocket` |
| Payload Example | `{"type":"message","message":"Crop x.mp4"}` |
| DB State (Before) | missing/corrupt source |
| DB State (After) | job `failed` with error; agent asks for timestamps |

### UC-AG-05: LLM unavailable → fallback advice
- **Given** the OpenCode endpoint is down
- **When** feedback is requested
- **Then** the LLM client raises `LLMError` after one retry
- **And** the agent returns fallback advice (or 503 "LLM unavailable") without crashing

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `WS /ws/chat` |
| Request Method | WebSocket |
| Required Headers | `Upgrade: websocket` |
| Payload Example | any analysis request |
| DB State (Before) | reference + metrics computed |
| DB State (After) | fallback advice returned; error logged |

### UC-AG-06: Pose correction overlay on a critical frame
- **Given** a critical frame image with detected issues (bent knee / flexed foot / uneven hips)
- **When** the agent runs `correct`
- **Then** `PoseCorrector.correct` returns corrected landmarks + issue list
- **And** `overlay` produces a red/green annotated image

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `WS /ws/chat` |
| Request Method | WebSocket |
| Required Headers | `Upgrade: websocket` |
| Payload Example | `{"type":"message","message":"Show me the correction"}` |
| DB State (Before) | landmarks for critical frame |
| DB State (After) | overlay artifact saved; no mutation of original landmarks |

---

## 6. Risks and Mitigations

- **Risk:** LLM prompt drift (agent skips confirmation). **Mitigation:** strict system prompt +
  unit tests on ReAct traces (CA-S4) + max iterations fallback.
- **Risk:** MediaPipe `z` noise in pose correction. **Mitigation:** correct on x/y only; side-view
  guidance.
- **Risk:** `opencode serve` sidecar down. **Mitigation:** startup health-check, retry once, fallback
  advice, 503 contract.
- **Risk:** reference cohort empty → scoring degraded. **Mitigation:** the `signal_histograms` cohort
  is produced by the histogram-analysis job; missing cohort → summary returns "reference data
  unavailable" (422/404 contract) rather than fabricated feedback.
- **Risk:** `pole_tools` is a merged namespace across two distributions. **Mitigation:** keep
  `config` in pole-train-model, facade re-exports only the surface; import linter for chatbot.
- **Risk:** long video timeouts in CropTool. **Mitigation:** downsampled frames for detection
  (future), explicit `ToolError` with actionable message.

---

## 7. Open Questions and Decisions

- Decision: OpenCode served over HTTP (`/chat/completions`) — no LangChain dependency (ReAct loop is custom in `pole_chatbot.agent`).
- Decision: Ollama integration via `OllamaLLM` adapter + `PoleLangGraphAgent` (LangGraph `StateGraph`). Activated via `LLM_PROVIDER=ollama` + `OLLAMA_MODEL` env vars. Default remains `LLM_PROVIDER=opencode` for backward compatibility. ReActAgent guardrails (crop→confirm→analyze, off-script recovery, iteration limits) are preserved in `PoleLangGraphAgent` via `AgentState` TypedDict with `pending_tool_calls` field.
- Decision: `packages/jobs` (Redis+Mongo) v1 for long tools; existing training jobs stay on the thread runner.
- Decision: chatbot consolidated into `pola_api` as `app/pola_api/src/chatbot/` slice (Phase 5 ✅).
  Standalone `python -m pole_chatbot` deprecated.
- Decision: phase boundaries manual (`phase_frames`) until automatic detection (PD) is analyzed.
- Decision: PostgreSQL `reference_*` tables and `attempt_logs` migration created in `pola_api`; seeding/bootstrap is pending Phase 6.
- Decision: Chatbot FE location — **inside the existing `pole_fe` Angular app**
  (`app/pole_fe/src/app/features/chatbot/`). `pole_fe` already hosts the UI shell
  (Phases 1-7) and its PLAN Phase 9 explicitly lists the Chatbot FE; the ticket
  scope (PAIML-POLE-AGENT-013) forbids introducing a new app when `pole_fe`
  exists. Implemented as a lazy-loaded feature module wired to the consolidated
  `pola_api` endpoint `WS /api/chatbot/ws/chat` (Phase 5).
- Open: session persistence backend (Postgres vs Redis) — backend-owned
  (Phase 5 `ChatbotSessionService`); the FE only stores the last known
  `session_id` locally for resume. Artifact URLs: backend writes plots/frames to
  `chatbot_output/` but does not static-mount it yet; FE builds
  `<apiBaseUrl>/chatbot_output/<basename>` URLs and degrades gracefully on image
  load failure (documented in the artifact renderer).
