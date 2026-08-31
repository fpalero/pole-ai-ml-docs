# Ticket: PAIML-POLE-ANALYST-008

## Title
[Presentation] Chat pane (message list + StatusChip + composer)

## Description
Build the left chat pane: header "Coach" with subtitle, a `StatusChip` showing the current
state, a scrollable message list (user/assistant bubbles with structured assistant content), and
a composer input with a send button.

## What to Do (Implementation Steps)
- [ ] Implement `ChatPane` header + subtitle + `StatusChip` bound to `state$`.
- [ ] Implement the message list (user right-aligned accent bubble; assistant left-aligned card
      with avatar + structured content).
- [ ] Implement the composer (input + circular send button).
- [ ] Wire send → `ChatbotSocketService.sendMessage`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ng lint`/`ng build` pass.
- [ ] Messages render in correct bubbles; the chip reflects live state.

## Integration Tests to Run (Local Verification)
- [ ] UC-04: user sends a message and sees the assistant reply in the chat.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-009
- **Blocked By**: PAIML-POLE-ANALYST-003, PAIML-POLE-ANALYST-006, PAIML-POLE-ANALYST-007

## Estimated Effort
- [M]
