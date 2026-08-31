# Ticket: PAIML-POLE-AGENT-003

## Status
✅ DONE — Implemented

## Title
[Application] ChatbotSession service with session resume

## Description
Wrap the `ChatbotSessionRepository` behind a `ChatbotSessionService` that
provides the application-layer orchestration:

- **create** a new session from `original_video` and initial user message.
- **update** session fields as the conversation progresses (e.g. `current_crop`
  after a `crop` tool run, `confirmed` flag after user confirmation).
- **resume** an existing session given a `session_id` — retrieve state from
  persistence so a disconnected user can rejoin the same coaching flow.
- **close** a session (mark `COMPLETED` or `ABANDONED`).

The service must coordinate `Redis` (hot) and `Postgres` (durable) repos:
hot reads from Redis with fallback to Postgres, writes to both.

The resume flow is the key deliverable — it enables the eventual `WS /ws/chat`
to accept an optional `session_id` query param and restore the conversation.

## What to Do (Implementation Steps)
- [x] Create `packages/chatbot/src/pole_chatbot/session_service.py`.
- [x] Implement `ChatbotSessionService` class injecting both repos.
- [x] Implement read-through cache: read Redis → hit Postgres on miss → backfill
  Redis.
- [x] Implement write-through: write Postgres first, then Redis (or vice versa
  with consistency trade-off documented).
- [x] Add `resume(session_id: str) → ChatbotSession | None`.
- [x] Add `close(session_id: str, status: SessionStatus)`.
- [x] Write unit tests with mock repos.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] `create` returns a valid `ChatbotSession` persisted in both backends.
- [x] `resume` with a valid `session_id` returns the full session state.
- [x] `resume` with an unknown `session_id` returns `None`.
- [x] Read-through cache works: Redis miss → Postgres hit → Redis backfill.
- [x] `close` transitions status correctly and persists the change.
- [x] ≥ 80% coverage on `session_service.py`.

## Integration Tests to Run (Local Verification)
- [x] Run `pixi run test-chatbot` — all tests pass.
- [x] (Manual) Create session, kill process, restart, resume by `session_id` —
  verify state is restored.

## Dependencies
- **Blocks**: PAIML-POLE-AGENT-006, PAIML-POLE-AGENT-008
- **Blocked By**: PAIML-POLE-AGENT-002

## Estimated Effort
- [M]
