# Ticket: PAIML-POLE-AGENT-013

## Status
✅ DONE — Implemented

## Title
[Presentation] Chatbot FE — WebSocket client for `WS /ws/chat`

## Description
Phase 7 adds the user-facing chatbot frontend: a WebSocket client that connects
to the consolidated chatbot endpoint (`WS /ws/chat` in `pola_api`, or the
`/api/chatbot/ws/chat` mounted router from Phase 5).  The FE renders the
turn-by-turn coaching conversation, surfaces job progress events
(`job_started`/`job_progress`/`job_done`/`job_error`) relayed over the WS, and
displays agent replies with any generated artifacts (deviation plot, critical
frame, correction overlay).

Scope note: the plan references the `pole_fe` plan (Phase 9) for the UI shell.
This ticket covers the WS client + chat UI wired to the backend — it does not
introduce a new app if `pole_fe` already hosts the UI.  Location decision must
be recorded (see Open Questions in PLAN.md).

## What to Do (Implementation Steps)
- [x] Decide and record FE location: **inside the existing `pole_fe` Angular app**
  (`app/pole_fe/src/app/features/chatbot/`, lazy route `/chatbot`). `pole_fe`
  exists (Phases 1-7 built) and its PLAN Phase 9 lists the Chatbot FE; per scope
  no new app is introduced. Decision recorded in `docs/app/pola_agent/PLAN.md`
  Open Questions §7.
- [x] Implement a WebSocket client service: connect to `WS /api/chatbot/ws/chat`
  (consolidated `pola_api` slice), handle reconnection with backoff, heartbeat
  (keepalive watchdog — the Phase 5 router rejects unknown frame types, so no
  app-level ping), and clean close.
- [x] Implement the message protocol: send `{"type":"message","message":...}`;
  handle inbound `agent_reply` and job event frames.
- [x] Implement the chat UI: message list (user vs agent bubbles), typing/
  processing indicator while a job or agent turn is in flight, and an input box
  for turn-by-turn messages.
- [x] Render job progress as inline status chips (started / progress % /
  done / error) per tool invocation (crop, shift, analyze).
- [x] Render agent artifacts: deviation plot image, critical frame, and pose
  correction overlay when present in the reply payload.
- [x] Surface session state: allow resuming a session via `session_id` (Phase 5
  feature) and show connection status.
- [x] Handle error states: WS disconnect, 429 rate-limit notice, 503 LLM
  unavailable fallback (UC-AG-05), and the manual-timestamps prompt after crop
  failure (UC-AG-04).
- [x] Add unit tests for the WS client state machine (mock WS server) and
  component tests for the message rendering.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] FE connects to `WS /ws/chat` and drives a full crop → confirm → analyze
  conversation (UC-AG-01, UC-AG-03).
- [x] Job progress events render live during crop/shift jobs.
- [x] Agent artifacts (plot / frame / overlay) render in the thread.
- [x] Error paths (disconnect, 429, 503, manual-timestamps prompt) are handled
  gracefully with user-facing messages.
- [x] Unit tests for the WS client pass; no regressions in the backend suites.
- [x] Runs against the consolidated `pola_api` chatbot (Phase 5) — not the
  deprecated standalone app.

## Integration Tests to Run (Local Verification)
- [x] UC-AG-01 and UC-AG-03 driven from the FE against a local `pola_api`:
  verify replies, job events, and artifacts.
- [x] UC-AG-04: corrupt source → FE shows the manual-timestamps prompt.
- [x] UC-AG-05: LLM down → FE shows fallback advice / 503 state.

## Dependencies
- **Blocks**: None (final phase)
- **Blocked By**: Phase 5 consolidation (`PAIML-POLE-AGENT-008`) and Phase 6
  hardening are not hard blockers but are prerequisites for a representative
  demo; Phase 5 consolidation must be merged.

## Estimated Effort
- [L]
