# Ticket: PAIML-POLE-ANALYST-019

## Title
[Presentation] PlanTab (improvement plan + detected errors)

## Description
Build the Plan tab: render the chatbot's latest `agent_reply` as an improvement plan (ordered
advice steps) plus a "Detected errors" card. The content comes from the chat conversation, not a
REST endpoint.

## What to Do (Implementation Steps)
- [ ] Implement `PlanTab` component.
- [ ] Subscribe to the last `agent_reply` and parse it into advice steps + detected errors.
- [ ] Render the plan list and errors card (with severity indicators).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ng lint`/`ng build` pass.
- [ ] Plan renders the parsed advice/errors from the last assistant reply.

## Integration Tests to Run (Local Verification)
- [ ] UC-04: after a chat turn, the Plan tab shows the improvement plan.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-020
- **Blocked By**: PAIML-POLE-ANALYST-003, PAIML-POLE-ANALYST-006

## Estimated Effort
- [M]
