# Ticket: PAIML-POLE-AGENT-006

## Status
✅ DONE — Implemented

## Title
[Infrastructure] Rate limiting per session — 429 + queue

## Description
A single user session should not be able to overwhelm the chatbot backend
with rapid-fire messages (intentional or accidental).  Implement per-session
rate limiting that:

- Limits each session to **N messages per sliding window** (e.g. 10 req / 30 s).
- Returns **HTTP 429 Too Many Requests** with `Retry-After` header when the
  limit is exceeded.
- Optionally queues overflow messages when the limit is hit (configurable
  queue depth; drop oldest when full).
- Integrates into the `pola_api` middleware stack so it applies to
  `WS /ws/chat` incoming message frames.

Since Phase 5 consolidates the chatbot into `pola_api`, the rate limiter
should be implemented as a `pola_api` middleware or dependency that leverages
`ChatbotSessionService` (PAIML-POLE-AGENT-003) for session-keyed counters.

## What to Do (Implementation Steps)
- [x] Implement `RateLimiter` class in `app/pola_api/src/infrastructure/`
  (or `src/chatbot/`) using Redis INCR + EXPIRE for sliding-window counters.
- [x] Key format: `ratelimit:chatbot:{session_id}:{window_ts}`.
- [x] Return 429 + `Retry-After` header; do not silently drop.
- [x] Optional: implement a small in-memory queue per session (depth 3–5) for
  deferred processing; drop oldest when full.
- [x] Expose as a FastAPI dependency `RateLimitDep` or ASGI middleware.
- [x] Make limits configurable via `ChatbotSettings` (env vars
  `CHATBOT_RATE_LIMIT_MAX`, `CHATBOT_RATE_LIMIT_WINDOW_S`).
- [x] Unit-test the rate limiter with fakeredis.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] Within a sliding window, the Nth+1 message returns 429.
- [x] `Retry-After` header is present and accurate.
- [x] A different session is NOT affected by another session's rate limit.
- [x] Window reset after expiry allows new messages.
- [x] Queue overflow behaviour is documented and test-covered.
- [x] ≥ 80% coverage on rate limiter code.

## Integration Tests to Run (Local Verification)
- [x] Start Redis; fire 15 rapid WS messages on one session — verify 429
  after limit.
- [x] Check that a second session is unaffected.
- [x] `pixi run test-api` — all tests pass.

## Dependencies
- **Blocks**: PAIML-POLE-AGENT-008
- **Blocked By**: PAIML-POLE-AGENT-003

## Estimated Effort
- [M]
