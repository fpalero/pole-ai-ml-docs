# Implementation Plan — `chatbot` (`pole-chatbot` Conversational Agent Backend)

> **Status:** Complete for v1 — ReAct agent over WebSocket, ToolRegistry (histogram/similarity sync,
> crop/shift job-mode), OpenCode client, worker job handlers, real integration test
> (WS→jobs→ffmpeg). **Phase 4 (sessions/rate limits/metrics) ✅** — `ChatbotSession` schema
> (`session_schema.py`), Redis + Postgres repositories (`session/`), `ChatbotSessionService`
> (read-through/write-through), `RateLimiter` (Redis sliding-window, 429), `MetricsCollector`
> (tool latency + LLM tokens). **Phase 5 (consolidation into `pola_api`) ✅** — chatbot router
> mounted as `app/pola_api/src/chatbot/` slice. **Ollama + LangGraph integration added:**
> `OllamaLLM` wraps `ChatOllama` with OpenAI-format msg/tool conversion; `PoleLangGraphAgent`
> implements a `StateGraph`-based agent with `agent`/`tool` nodes + conditional routing.
> Activated via `LLM_PROVIDER=ollama` + `OLLAMA_MODEL` env vars (default backward-compatible
> with opencode). `AgentState` TypedDict requires `pending_tool_calls` field; `_TokenMetricsCallback`
> extends `BaseCallbackHandler` with `config=` parameter.
> **Source docs:** `docs/app/pola_agent/implementation_plan.md` §13 (chatbot + jobs),
> `agent-react.md` (ReAct design), `agent_requirements.md` (prompts/thresholds).

---

## 1. Feature Context & Objective

- **Goal:** A turn-by-turn conversational agent that analyzes a pole-dance video: the user chats
  over WebSocket, the ReAct agent decides when to crop, confirm, shift, analyze, or correct, and
  job progress is pushed live to the same socket. Sync tools (histogram, similarity) answer inline;
  long tools (crop, shift) run as `pole-jobs` jobs whose events stream back.
- **Non-Functional Constraints:** LLM = OpenCode-compatible HTTP (`/chat/completions`) or Ollama
  (via `OllamaLLM` adapter + `PoleLangGraphAgent`); agent iteration budget (`max_iterations`,
  default 6); per-socket event relay via `ws_connection_id`; chatbot may only call
  `pole_tools.services` (import discipline); unit tests exclude integration
  (`-m 'not integration'`), live test separate.
- **Affected Components:**
  - `packages/chatbot/src/pole_chatbot/` — `agent.py`, `agent_langgraph.py`, `tools.py`,
    `llm.py`, `ws.py`, `job_handlers.py`, `app.py`, `config.py`, `__main__.py`.
  - `packages/chatbot/src/pole_chatbot/session/` — `base.py` (ABC), `redis_repo.py`,
    `postgres_repo.py`.
  - `packages/chatbot/src/pole_chatbot/session_schema.py`, `session_service.py`, `metrics.py`.
  - `packages/chatbot/tests/` — unit (`test_agent`, `test_agent_langgraph`, `test_tools`,
    `test_llm`, `test_ws`, `test_session_schema`, `test_session_repositories`,
    `test_session_service`, `test_metrics`) + `test_ws_integration.py` (live).
- **Assumptions:** Redis + Mongo up (dev via docker-compose); OpenCode sidecar on `OPENCODE_URL`
  (or Ollama server on `OLLAMA_HOST`); `pole-jobs`/`pole-tools`/`pole-train-model`/`pole-crop`
  installed editable.

---

## 2. Architectural Layering (The "Where")

- **Domain:** WebSocket message types (`agent_reply`, `error`, and relayed `job_started`/
  `job_progress`/`job_done`/`job_error`); tool specs (name/description/parameters, mode
  sync|job); session message history.
- **Application:** `ReActAgent` (loop: llm.chat → tool_calls → invoke → observe),
  `PoleLangGraphAgent` (LangGraph StateGraph: agent/tool nodes + conditional routing),
  `ToolRegistry` (register/invoke/specs), `ChatbotSettings`, `ChatbotSessionService`
  (read-through/write-through), `RateLimiter`, `MetricsCollector`,
  worker `JOB_HANDLERS` (crop/shift with progress stages).
- **Infrastructure:** `OpenCodeClient` (httpx), `OllamaLLM` (wraps `ChatOllama` with OpenAI
  format conversion), `JobOrchestrator` (Mongo+Redis from `pole-jobs`),
  `pole_tools.services` facade, `ChatbotRouter` (WS `/ws/chat`), `RedisChatbotSessionRepository`,
  `PostgresChatbotSessionRepository`.
- **Presentation:** `WS /ws/chat` (in: `{type:"message"}`, out: `agent_reply` + job events);
  FastAPI app + worker entry points.

---

## 3. Implementation Roadmap (Atomic Steps)

### Phase 1: Core agent + tools — ✅ DONE
- [x] `config.py` (env settings), `llm.py` (OpenCodeClient text chat, `OpenCodeError`).
- [x] `tools.py` — `ToolSpec`/`ToolRegistry`, default tools (`histogram`, `similarity` sync;
  `crop`, `shift` job-mode with `ws_connection_id`).
- [x] `agent.py` — `ReActAgent.run(user_message, session_messages, ws_connection_id)` with tool
  invocation, per-call error capture, iteration budget fallback.

### Phase 2: Job handlers + WebSocket — ✅ DONE
- [x] `job_handlers.py` — `JOB_HANDLERS` for crop/shift calling `pole_tools.services` with
  `ctx.set_progress` stages.
- [x] `ws.py` — `ChatbotRouter` WS `/ws/chat`: per-socket relay thread (subscriber filtered by
  `ws_connection_id`), agent run via `asyncio.to_thread`, session = message history, cleanup on
  disconnect.
- [x] `app.py` — `build_orchestrator`, `build_app`, `start_worker` (daemon thread).

### Phase 3: Testing — ✅ DONE
- [x] Unit tests (fakeredis/mongomock/FakeLLM): llm, agent, tools, job_handlers, ws.
- [x] Live integration `test_ws_integration.py` (`pixi run test-chatbot-live`): real Redis/Mongo +
  ffmpeg; asserts `job_started`/`job_progress` before `job_done` and non-empty `.mp4`.

### Phase 4: Sessions, rate limits, metrics — ✅ DONE
- [x] Application `ChatbotSession` persistence (`session_schema.py`, Redis + Postgres repos in
  `session/`) + resume via `session_id` (CA-H5).
- [x] Application rate limiting per session (`RateLimiter` — Redis sliding-window, 429 + Retry-After).
- [x] Application metrics/logging: `MetricsCollector` (tool latency, LLM tokens, session events).
- [x] Infrastructure health-check on LLM sidecar (503 "LLM unavailable" contract).

### Phase 5: Ollama + LangGraph integration — ✅ DONE
- [x] `OllamaLLM` adapter (`llm.py`) — wraps `ChatOllama` with OpenAI-format msg/tool conversion;
  `_lc_tool_to_openai_tool` / `_convert_messages` for LangChain↔OpenAI interop.
- [x] `PoleLangGraphAgent` (`agent_langgraph.py`) — LangGraph `StateGraph` with `agent`/`tool`
  nodes, conditional `_should_continue` routing, `_TokenMetricsCallback` extending
  `BaseCallbackHandler`. Guardrails: crop→confirm→analyze workflow, off-script recovery,
  iteration limits, `AgentState` TypedDict with `pending_tool_calls`.
- [x] `config.py` — `ChatbotSettings` fields: `llm_provider` (opencode|ollama), `ollama_model`,
  `ollama_host`. `app.py` auto-wires `OllamaLLM` + `PoleLangGraphAgent` when `LLM_PROVIDER=ollama`.
- [x] Unit tests: 11 new LangGraph agent tests (`test_agent_langgraph.py`), full suite 173/173
  passing.

### Phase 6: Consolidation + FE + training chatbot — ✅ DONE
- [x] Presentation mount chatbot router into `pola_api` (single entry; keep worker separate) —
  implemented as `app/pola_api/src/chatbot/` slice (PAIML-POLE-AGENT-008).
- [x] Presentation Chatbot FE — WS client consuming the event contract (`pole_fe` Phase 9).
- [x] Application training chatbot (Path A slice in `pola_api`) — `training_chatbot/` with
  `TrainingFacade`, 4 tools, job relay, session resume.

---

## 4. Quality Gates & Testing Commands (DoD)

- **Unit Tests:** `pixi run test-chatbot` (pytest, excludes integration via pyproject addopts) — ≥ 80%.
- **Integration Tests:** `pixi run test-chatbot-live` (real Redis/Mongo/ffmpeg; requires
  `pixi run redis-up` + Mongo compose).
- **Automation:** CI runs unit suites; import linter: chatbot → `pole_tools.services` only.
- **Database Target:** `pole_chatbot_testing` Mongo + Redis queue `chat-test`; Chroma temp dir.
- **Coverage Requirement:** ≥ 80%.
- **Additional Checks:** `pixi run chatbot-api` / `chatbot-worker` smoke; OpenCode sidecar health
  check; ws cleanup joins listener threads.

---

## 5. Defined Use Cases (Gherkin + Technical Matrix)

### UC-CH-01: Straight analysis (crop → confirm → analyze)
- **Given** a valid video path and an OpenCode-compatible LLM
- **When** user sends `{"type":"message","message":"Analyze clean_invert.mp4"}`
- **Then** the agent calls the crop tool, asks for confirmation, then analyzes
- **And** the WS receives `agent_reply` (and job events for crop/shift)

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `WS /ws/chat` |
| Request Method | WebSocket |
| Required Headers | `Upgrade: websocket` |
| Payload Example | `{"type": "message", "message": "Analyze clean_invert.mp4"}` |
| DB State (Before) | no job docs |
| DB State (After) | job docs done; output clip exists; agent reply sent |

### UC-CH-02: Job event streaming for a long tool
- **Given** a job-mode tool (crop) invoked with `ws_connection_id`
- **When** the worker processes it
- **Then** the WS receives `job_started` → `job_progress` (stages) → `job_done`
- **And** events not matching the socket id are filtered

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `WS /ws/chat` (relayed events) |
| Request Method | WebSocket |
| Required Headers | `Upgrade: websocket` |
| Payload Example | `{"type":"job_progress","task_id":"...","progress":0.2,"stage":"cutting"}` |
| DB State (Before) | job queued with `ws_connection_id` |
| DB State (After) | events relayed in order; job done in Mongo |

### UC-CH-03: Tool error is fed back to the LLM
- **Given** a tool that raises (e.g., missing file)
- **When** the agent invokes it
- **Then** the error is appended as a tool message (JSON with `{"error": ...}`)
- **And** the agent continues (rephrasing / fallback), no crash

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `WS /ws/chat` |
| Request Method | WebSocket |
| Required Headers | `Upgrade: websocket` |
| Payload Example | `{"type":"message","message":"Crop nonexistent.mp4"}` |
| DB State (Before) | source missing |
| DB State (After) | job `failed` with error; agent asks for manual timestamps |

### UC-CH-04: Iteration budget exhaustion
- **Given** an LLM that keeps calling tools
- **When** `max_iterations` is reached
- **Then** the agent returns the fallback reply ("couldn't finish within the allowed steps")
- **And** the loop terminates cleanly

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `WS /ws/chat` |
| Request Method | WebSocket |
| Required Headers | `Upgrade: websocket` |
| Payload Example | scripted FakeLLM repeating tool calls |
| DB State (Before) | n/a |
| DB State (After) | fallback reply; no runaway loop |

### UC-CH-05: Resume session via session_id (future)
- **Given** an existing session with confirmed crop
- **When** user reconnects with the same `session_id`
- **Then** the agent restores state (`current_crop`, history) and continues
- **And** shift/analyze operate on the restored crop

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `WS /ws/chat?session_id=<id>` |
| Request Method | WebSocket |
| Required Headers | `Upgrade: websocket` |
| Payload Example | handshake + `{"type":"message",...}` |
| DB State (Before) | session persisted (Phase 4) |
| DB State (After) | resumed history in agent reply |

### UC-CH-06: Live end-to-end crop job
- **Given** real Redis + Mongo + ffmpeg
- **When** the integration test sends an analysis request
- **Then** the socket receives `job_started` and `job_progress` before `job_done`
- **And** the produced `.mp4` artifact exists and is non-empty

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `WS /ws/chat` (via `pixi run test-chatbot-live`) |
| Request Method | WebSocket |
| Required Headers | `Upgrade: websocket` |
| Payload Example | `{"type":"message","message":"Crop <fixture>.mp4 0 5"}` |
| DB State (Before) | queue empty, fixture present |
| DB State (After) | job done, artifact non-empty, queue cleaned |

---

## 6. Risks and Mitigations

- **Risk:** LLM prompt drift (skips confirmation). **Mitigation:** strict system prompt + ReAct
  trace unit tests + iteration budget.
- **Risk:** OpenCode sidecar down. **Mitigation:** health-check at startup, retry once, fallback
  advice / 503.
- **Risk:** WebSocket relay thread leaks on disconnect. **Mitigation:** stop_event + join in
  cleanup; tests assert no stray threads.
- **Risk:** event filtering mismatch (wrong `ws_connection_id`). **Mitigation:** uuid per
  connection; integration test asserts filtered delivery.
- **Risk:** session loss on restart. **Mitigation:** session persistence (Phase 4) — currently
  in-memory per connection.
- **Risk:** import discipline violated (chatbot → `pole_ml`). **Mitigation:** import linter in CI.

---

## 7. Open Questions and Decisions

- Decision: chatbot is **consolidated into `pola_api`** as `app/pola_api/src/chatbot/` slice (Phase 5 ✅).
  Standalone `python -m pole_chatbot` is deprecated. `ChatbotDeps` provides dependency injection;
  `ChatbotRouter` handles `WS /api/chatbot/ws/chat`.
- Decision: ReAct loop is custom (no LangChain dependency); OpenCode over HTTP only. Ollama
  integration uses `OllamaLLM` adapter + `PoleLangGraphAgent` (LangGraph `StateGraph`) activated
  via `LLM_PROVIDER=ollama`. Guardrails (crop→confirm→analyze, off-script recovery, iteration
  limits) preserved in `PoleLangGraphAgent`.
- Decision: job events contract matches `pole_jobs.events` and the FE WS types in the agent plan §13.
- Implemented: session persistence (`ChatbotSession` + Redis/Postgres repos + `ChatbotSessionService`).
- Implemented: rate limiting (`RateLimiter` — Redis sliding-window).
- Implemented: training chatbot (Path A slice in `pola_api` — `training_chatbot/`).
- Implemented: analyst chatbot (Path A slice in `pola_api` — `analyst_chatbot/`).
