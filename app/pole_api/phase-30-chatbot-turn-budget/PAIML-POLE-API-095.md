# Ticket: PAIML-POLE-API-095

## Title
[Chatbot] Save deepseek-v4-flash staging model config + per-turn wall-clock deadline (fix chatbot session error)

## Description
Phase 30 — staging model decision + session-error fix.

**(1) Saved staging model configuration (user-confirmed).** The analyst chatbot
slice on staging (`ipsf-server`, ConfigMap `pole-ai-pole-api-env`) is pinned to:

- `LLM_PROVIDER=openrouter`
- `OPENROUTER_MODEL=deepseek/deepseek-v4-flash`
- `POLE_RAG_DATA_DIR=/data/rag`

Validated at LLM level (HTTP 200 with `tool_calls`) and through the staging WS
(`wss://pole-coach.duckdns.org/api/analyst-chatbot/ws/analyst-chat`): Q1
answered in 22.7s, Q2 in 33s with substantive grounded answers and RAG tool
calls. This ticket records the decision so it survives restarts/redeploys.

**(2) Chatbot session error — root cause + fix.** Staging evidence: turn
`b22e494f` (session `7ac10f38…`, 68-char message) started 22:15:18, ran 4+
LLM rounds (`messages 2→4→8→12`), and only logged "turn done" at 22:24:39 —
**duration 561.22s (9.3 min)** — while the client WS had long disconnected
("chatbot not answering"). Coach-summary calls on the same model took
150–202s each.

Root cause: **no wall-clock budget for a whole turn**. `chatbot_llm_timeout`
(`LLM_TIMEOUT`, default 120s) caps each individual LLM call, but a turn
chains up to `chatbot_max_agent_iterations` (default 6) sequential calls, and
`services.run_turn` degenerate/empty-reply retries can re-enter `agent.run()`.
Worst case ≈ 12 min per user message.

Fix (implemented in `feature/PAIML-POLE-API-095-chatbot-session-error`):
- `PoleLangGraphAgent(..., max_turn_seconds=…)` — deadline carried in graph
  state (`AgentState.turn_deadline`), never on `self` (one instance serves
  concurrent sessions).
- `_call_model_node` short-circuits past-deadline turns (no new LLM call) and
  otherwise passes the remaining budget as a per-call `timeout` override.
- `OllamaLLM.chat` / `OpenRouterLLM.chat` accept `timeout=` (OpenRouter:
  race-free per-request `httpx.Timeout`, capped at the client default;
  Ollama: best-effort tighten-only narrowing, restored afterwards).
- `run()` also enforces the deadline between graph super-steps; on expiry the
  turn ends with `TURN_TIMEOUT_MESSAGE` and status **ACTIVE** (session stays
  usable — no ABANDONED).
- Config: `Settings.chatbot_max_turn_seconds` (`CHATBOT_TURN_TIMEOUT`,
  default 120) → `ChatbotSettings.max_turn_seconds` → all three agent
  constructions in `app/pole_api/main.py` (chatbot, training, analyst).

## What to Do (Implementation Steps)
- [x] Add `TURN_TIMEOUT_MESSAGE` (`packages/chatbot/src/pole_chatbot/guardrails.py`).
- [x] Add `max_turn_seconds` + `turn_deadline` state + short-circuit +
      stream-loop backstop (`agent_langgraph.py`).
- [x] Add per-call `timeout` override (`llm.py`, both adapters + helper).
- [x] Wire `CHATBOT_TURN_TIMEOUT` through `core/config.py` + `main.py`.
- [x] Tests: `TestTurnDeadline` (6 tests), settings-reflection assertion,
      fake-LLM `timeout` kwarg updates (chatbot + pole_api suites).
- [ ] Deploy to staging; rerun WS chat battery; confirm P95 turn < deadline
      and no 500s+ turns in `turn_completed` metrics.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] `pixi run test-chatbot` green (233 passed).
- [x] Analyst/training chatbot API suites green (251 passed:
      `test_analyst_chatbot*.py`, `test_training_chatbot.py`,
      `test_chatbot_router.py`, WS integration).
- [ ] Staging: no turn exceeds `CHATBOT_TURN_TIMEOUT` + one LLM call;
      expired turns reply gracefully with session ACTIVE.
- [ ] Staging ConfigMap keeps `OPENROUTER_MODEL=deepseek/deepseek-v4-flash`.

## Integration Tests to Run (Local Verification)
- [x] `pixi run test-chatbot` (233 passed)
- [x] App chatbot suites with `PYTHONPATH=app/pole_api/src` (251 passed)
- [ ] Staging WS battery after deploy

## Dependencies
- **Blocks**: None.
- **Blocked By**: None (backend-only; model config already live on staging).

## Estimated Effort
- [S]
