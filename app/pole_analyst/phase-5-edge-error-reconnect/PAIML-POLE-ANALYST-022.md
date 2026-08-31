# Ticket: PAIML-POLE-ANALYST-022

## Title
[Presentation] No-detectable-skeleton error state

## Description
When analysis finds no detectable skeleton, surface a chatbot message with the likely cause
("couldn't detect athlete — low quality, re-record") and keep the card "Not analyzed" (no
generic error).

## What to Do (Implementation Steps)
- [ ] Detect the analysis job's `no_skeleton_detected`/failure result.
- [ ] Push a friendly assistant message with the likely cause.
- [ ] Keep the card's "Not analyzed" badge (do not set `analyzed=true`).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ng lint`/`ng build` pass.
- [ ] No-skeleton failure surfaces a specific message, not a generic error.

## Integration Tests to Run (Local Verification)
- [ ] UC-06: no-skeleton video → chatbot explains low-quality cause; card stays "Not analyzed".

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-024
- **Blocked By**: PAIML-POLE-ANALYST-015, PAIML-POLE-ANALYST-006

## Estimated Effort
- [S]
