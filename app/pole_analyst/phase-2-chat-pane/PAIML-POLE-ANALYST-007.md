# Ticket: PAIML-POLE-ANALYST-007

## Title
[Application] Derive ChatState from WebSocket frames

## Description
Map inbound WS frames to the `ChatState` machine: `connected` → Idle; sending a message →
Thinking; `job_started`/`job_progress` → Working; `agent_reply` → Completed; `error` → Error.
Emits state updates to the chat pane.

## What to Do (Implementation Steps)
- [ ] Implement a frame→event adapter over `ChatbotSocketService` output.
- [ ] Feed events into the `ChatState` reducer (PAIML-POLE-ANALYST-004).
- [ ] Expose a `state$` observable for the `StatusChip`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ng lint`/`ng build` pass.
- [ ] Frame sequences produce the expected state transitions (unit-tested).

## Integration Tests to Run (Local Verification)
- [ ] UC-04: state chip moves Idle→Thinking→Working→Completed during a turn.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-008
- **Blocked By**: PAIML-POLE-ANALYST-004, PAIML-POLE-ANALYST-006

## Estimated Effort
- [M]
