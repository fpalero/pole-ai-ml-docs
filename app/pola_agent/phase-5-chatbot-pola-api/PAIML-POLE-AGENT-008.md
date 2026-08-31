# Ticket: PAIML-POLE-AGENT-008

## Status
✅ DONE — Implemented

## Title
[Presentation] Mount chatbot router as a slice in `pola_api`

## Description
The chatbot currently runs as its own standalone FastAPI app
(`python -m pole_chatbot`, port 8001).  Consolidate it as a first-class
slice inside `pola_api` so a single server serves both the tools API
(Phase 4) and the chatbot WebSocket.

The consolidated chatbot slice must:

- Reuse `pola_api`'s existing FastAPI app, config, DB pools, and middleware.
- Mount `WS /ws/chat` under the `pola_api` app (or as a sub-router under
  `/api/chatbot/`).
- Delegate tool calls through `ToolsService` (already implemented in
  Phase 4) instead of directly importing `pole_tools` services.
- Keep the chatbot's `Jobs` integration (Redis + Mongo) functional under
  the unified lifecycle.
- Clean up the standalone `python -m pole_chatbot` entrypoint (deprecate or
  remove) and the dedicated port 8001.

This is the largest Phase 5 ticket — it bridges all previous tickets into a
single deployable API surface.

## What to Do (Implementation Steps)
- [x] Create `app/pola_api/src/chatbot/` package with `__init__`, `router.py`,
  `deps.py`.
- [x] Move the `ChatbotRouter` (`WS /ws/chat`) logic from
  `packages/chatbot/src/pole_chatbot/ws.py` into
  `app/pola_api/src/chatbot/router.py`, adapting to `pola_api` dependency
  injection patterns.
- [x] Create a `ChatbotDeps` module that provides `ChatbotSessionService`,
  `ReActAgent`, `ToolRegistry`, `JobOrchestrator` as FastAPI dependencies.
- [x] Wire the chatbot router into `pola_api`'s main app (e.g.
  `app.include_router(chatbot_router, prefix="/api/chatbot")`).
- [x] Ensure `ToolsService` is the sole entry point for tool calls (remove any
  direct `pole_tools` imports from chatbot slice).
- [x] Add `pola_api` lifecycle hooks for Redis/Mongo/OpenCode health checks
  that the chatbot depends on.
- [x] Update `app/pola_api/src/config.py` to include `ChatbotSettings`
  (LLM URL, model, rate limits, metrics flag).
- [x] Deprecate the standalone `pole_chatbot` entrypoint: add a deprecation
  warning or remove `__main__` block; document migration path.
- [x] Write integration tests for the consolidated router (WS connect,
  send message, receive `agent_reply` + job events).
- [x] Run full `pixi run test-api` suite to verify no regressions.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] `WS /api/chatbot/ws/chat` (or `/ws/chat` under pola_api) accepts
  connections and processes messages.
- [x] Tool calls (crop, shift, analyze, correct) work through
  `ToolsService` facade — no direct `pole_tools` imports.
- [x] Job events are relayed to the WS client via the unified lifecycle.
- [x] `ChatbotSessionService` is injected and functional (session
  create/resume).
- [x] Rate limiting is active on the WS endpoint.
- [x] Metrics are emitted when configured.
- [x] Standalone `python -m pole_chatbot` emits a deprecation message.
- [x] All existing `pola_api` tests pass (`pixi run test-api`).
- [x] ≥ 80% coverage on the new `app/pola_api/src/chatbot/` slice.

## Integration Tests to Run (Local Verification)
- [x] Run UC-AG-01 through UC-AG-06 against the consolidated `pola_api`
  endpoint — all must pass.
- [x] `pixi run test-api` — full suite green.
- [x] `pixi run test-chatbot` — existing chatbot unit tests still pass
  (standalone package is not broken).
- [x] (Manual) Start `pola_api`, connect with a WS client to
  `/ws/chat`, send "Crop my_video.mp4" — verify agent reply and job events.
- [x] Verify standalone `pole_chatbot` emits deprecation warning.

## Dependencies
- **Blocks**: None
- **Blocked By**: PAIML-POLE-AGENT-003, PAIML-POLE-AGENT-004,
  PAIML-POLE-AGENT-005, PAIML-POLE-AGENT-006, PAIML-POLE-AGENT-007

## Estimated Effort
- [L]
