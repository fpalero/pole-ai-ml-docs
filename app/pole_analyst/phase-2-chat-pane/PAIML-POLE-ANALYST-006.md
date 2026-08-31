# Ticket: PAIML-POLE-ANALYST-006

## Title
[Infrastructure] ChatbotSocketService (WebSocket client + reconnect + resume)

## Description
Implement the WebSocket client for the video-analysis chatbot (`/api/chatbot/ws/chat`). It must
send `{type:"message",message,session_id?}` and `{type:"resume",session_id}` frames, parse server
frames (`connected`, `agent_reply`, `session_resumed`, `error`, relaid job events), and
auto-reconnect with exponential backoff, resuming the session by `session_id` after a drop.

## What to Do (Implementation Steps)
- [ ] Implement connect/handshake handling and `connected` frame correlation.
- [ ] Implement `sendMessage` and `resume` methods.
- [ ] Parse and expose typed server frames via an RxJS subject.
- [ ] Implement auto-reconnect (exponential backoff) + `session_id` resume.
- [ ] Ensure no subscription leaks (takeUntilDestroyed).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ng lint`/`ng build` pass.
- [ ] Reconnect after a dropped socket resumes the session by `session_id`.
- [ ] Frame parsing is typed and covered by unit tests.

## Integration Tests to Run (Local Verification)
- [ ] UC-04: chat turn round-trips over the WS and survives a simulated reconnect.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-007, PAIML-POLE-ANALYST-008, PAIML-POLE-ANALYST-019, PAIML-POLE-ANALYST-022, PAIML-POLE-ANALYST-023
- **Blocked By**: PAIML-POLE-ANALYST-002

## Estimated Effort
- [L]
