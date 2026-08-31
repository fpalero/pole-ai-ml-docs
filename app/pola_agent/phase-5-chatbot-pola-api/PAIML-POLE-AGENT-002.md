# Ticket: PAIML-POLE-AGENT-002

## Status
✅ DONE — Implemented

## Title
[Infrastructure] ChatbotSession persistence — Redis + Postgres repositories

## Description
Persist `ChatbotSession` state so sessions survive server restarts and can be
resumed later.  Two storage backends are required:

- **Redis** for hot/live session state (fast reads during WebSocket
  conversations; TTL expiry for abandoned sessions).
- **Postgres** for durable, queryable long-term storage (audit, analytics,
  integration with the existing `pola_api` tooling schema).

Implement repository interfaces (abstract base + two concrete implementations)
following the same pattern used by Phase 4 `tools/repositories/`.

The Redis repo serialises `ChatbotSession` as JSON with a configurable TTL.
The Postgres repo uses a new migration adding a `chatbot_sessions` table.

## What to Do (Implementation Steps)
- [x] Define `ChatbotSessionRepository` ABC (create, get, update, delete,
  list_active).
- [x] Implement `RedisChatbotSessionRepository` using `redis.asyncio`;
  key pattern `chatbot:session:{session_id}` with TTL (default 3600s).
- [x] Implement `PostgresChatbotSessionRepository` using `asyncpg` (or
  SQLAlchemy async if pola_api uses it); add migration script for table
  `chatbot_sessions`.
- [x] Write unit tests for both repos (fakeredis + `asyncpg` mock or test
  database).
- [x] Export repos from `pole_chatbot.session` subpackage.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] Both repos pass the same ABC contract tests.
- [x] Redis TTL is honoured; expired keys return `None`.
- [x] Postgres `upsert` correctly handles new vs. existing sessions.
- [x] Migration DDL is reversible (`DROP TABLE IF EXISTS chatbot_sessions`).
- [x] Unit tests achieve ≥ 80% coverage on repo code.

## Integration Tests to Run (Local Verification)
- [x] Run `pixi run test-chatbot` — ensure new tests pass.
- [x] (Manual) Start Redis/Mongo via `pixi run redis-up`; instantiate both
  repos and round-trip a session CRUD.

## Dependencies
- **Blocks**: PAIML-POLE-AGENT-003
- **Blocked By**: PAIML-POLE-AGENT-001

## Estimated Effort
- [M]
