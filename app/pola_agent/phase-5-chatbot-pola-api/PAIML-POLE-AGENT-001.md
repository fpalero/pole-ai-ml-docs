# Ticket: PAIML-POLE-AGENT-001

## Status
✅ DONE — Implemented

## Title
[Domain] ChatbotSession state model and schema

## Description
Define the `ChatbotSession` domain model that tracks conversation state
across a multi-turn coaching session.  Currently the chatbot holds no
persistent session – every WS message is stateless, which prevents crop
confirmation chains and session resumption.  This model is the foundational
building block for Phase 5 session persistence, prompt enforcement, resume,
rate limiting, and the pola_api consolidation.

The model must capture:
- `original_video` path (the source uploaded clip).
- `current_crop` (latest crop bounds, nullable until first crop).
- `confirmed` flag (whether the current crop is accepted by the user).
- `history` of user/agent messages for context.
- Metadata: `session_id` (UUID), `created_at`, `updated_at`, `status`
  (`ACTIVE` / `COMPLETED` / `ABANDONED`).

## What to Do (Implementation Steps)
- [x] Create `packages/chatbot/src/pole_chatbot/session_schema.py` with a
  Pydantic `ChatbotSession` model.
- [x] Enforce session status lifecycle: `ACTIVE` → `COMPLETED` / `ABANDONED`.
- [x] Add a `ChatbotSessionCreate` (input) variant for new-session payloads.
- [x] Export from `pole_chatbot` `__init__` (or dedicated `session` subpackage)
  for consumption by persistence, service, and router layers.
- [x] Keep the model free of persistence-layer concerns — pure domain schema.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] `ChatbotSession` Pydantic model validates all required fields.
- [x] Session status transitions are enforced (e.g. cannot re-activate a
  completed session).
- [x] Unit tests cover model instantiation, serialisation, and status
  transitions.
- [x] No regressions in existing `pixi run test-chatbot` suite.

## Integration Tests to Run (Local Verification)
- [x] Run `pixi run test-chatbot` — verify model import does not break existing
  unit tests.
- [x] Manually instantiate a session and print its JSON — sanity check.

## Dependencies
- **Blocks**: PAIML-POLE-AGENT-002, PAIML-POLE-AGENT-004, PAIML-POLE-AGENT-005
- **Blocked By**: None

## Estimated Effort
- [S]
