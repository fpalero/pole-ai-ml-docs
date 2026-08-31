# Ticket: PAIML-POLE-ANALYST-013

## Title
[Presentation] Empty library state + welcome chatbot message

## Description
When there are no uploads, show the friendly empty state in the right pane (icon + "No video
selected" + upload hint) and have the chatbot post the explainer/welcome message asking for a
first video.

## What to Do (Implementation Steps)
- [ ] Implement the empty-state component (illustration, message, upload CTA).
- [ ] On first load with an empty library, push the welcome assistant message into the chat.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ng lint`/`ng build` pass.
- [ ] Empty library renders the empty state and a welcome message.

## Integration Tests to Run (Local Verification)
- [ ] UC-07: empty library shows upload panel + explainer message.

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLE-ANALYST-012

## Estimated Effort
- [S]
