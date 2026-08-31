# Ticket: PAIML-POLE-API-050

## Status
✅ DONE — Implemented

## Title
[Infrastructure] Slice `analyst_chatbot` (router + services + sessions) + WS `/ws/analyst-chat`

## Description
Phase 18 (§1). New `analyst_chatbot` slice mirroring `training_chatbot`: `router.py` + `services.py` +
`sessions.py`. WS `/ws/analyst-chat` with wire protocol identical to `/ws/training-chat`:
Client→server `{"type":"message","message":"…"}`, `{"type":"resume","session_id":S}`;
Server→client `connected`, `agent_reply`, `session_resumed`, `error`, and relaid job events
(`job_started`, `job_progress`, `job_done`, `job_error`). Sessions persisted, resume after reconnect.

## What to Do (Implementation Steps)
- [x] `analyst_chatbot/router.py` with WS `/ws/analyst-chat`.
- [x] `analyst_chatbot/services.py` (ReActAgent loop) + `sessions.py` (session persistence/resume).
- [x] Wire protocol identical to `training_chatbot` (`ChatbotSessionService`).
- [x] Register router in `main.py`; add slice to docs/AGENTS structure.
- [x] Unit + WS integration tests (message, resume, error frames).

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] WS `/ws/analyst-chat` functional with resume; frames match training-chat protocol.
- [x] `pixi run test-api` green (guarded `_testing` DBs).

## Integration Tests to Run (Local Verification)
- [x] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-API-051, PAIML-POLE-API-052, PAIML-POLE-ANALYST-036
- **Blocked By**: PAIML-POLE-API-048

## Estimated Effort
- [M]