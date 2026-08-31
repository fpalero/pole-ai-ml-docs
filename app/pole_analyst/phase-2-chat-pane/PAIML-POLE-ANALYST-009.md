# Ticket: PAIML-POLE-ANALYST-009

## Title
[Test] Unit tests T2.x (frame→state mapping, reconnect, resume)

## Description
Unit-test the chat pane: frame→state mapping, the WS reconnect + resume logic, and the composer
send flow.

## What to Do (Implementation Steps)
- [ ] Cover frame→state mapping (connected/message/job/agent_reply/error).
- [ ] Cover reconnect with backoff + session resume (mock WS).
- [ ] Cover composer send and message rendering.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `npx ng test --watch=false` passes.
- [ ] Coverage for Phase 2 code is ≥ 80%.

## Integration Tests to Run (Local Verification)
- [ ] N/A (unit-level; validates UC-04 chat behavior).

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLE-ANALYST-008

## Estimated Effort
- [M]
