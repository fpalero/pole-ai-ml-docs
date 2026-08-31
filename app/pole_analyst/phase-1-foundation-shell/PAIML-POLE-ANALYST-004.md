# Ticket: PAIML-POLE-ANALYST-004

## Title
[Domain] ChatState model + reducer

## Description
Define the chatbot state model and its transition logic (Idle → Thinking → Working → Completed /
Error) used by the left chat pane to drive the `StatusChip`. Pure, framework-agnostic so it can
be unit-tested in isolation.

## What to Do (Implementation Steps)
- [ ] Define `ChatState` union type (`Idle | Thinking | Working | Completed | Error`).
- [ ] Implement a reducer/transition function mapping events → next state.
- [ ] Define the event inputs (`connected`, `message_sent`, `job_started`, `job_progress`,
      `agent_reply`, `error`).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ng lint`/`ng build` pass.
- [ ] All transitions are explicit and covered by unit tests.

## Integration Tests to Run (Local Verification)
- [ ] UC-04: state chip reflects Idle→Thinking→Working→Completed across a chat turn.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-005, PAIML-POLE-ANALYST-007
- **Blocked By**: PAIML-POLE-ANALYST-001

## Estimated Effort
- [S]
