# Ticket: PAIML-POLE-ANALYST-037

## Title
[Presentation] Tool-call chips + artefactos de imagen

## Description
Phase 11 (§2). Render analyst chatbot tool calls as chips: `histogram` (histogram analysis),
`classify` (classification only), `extract_frames` / `crop` (image editing), and link image artifacts
returned by the tools.

## What to Do (Implementation Steps)
- [ ] Tool-call chips for histogram/classify/extract_frames/crop in the chat pane.
- [ ] Link image artifacts (`frame_image_path`s) returned by tools.
- [ ] Unit tests: chip rendering + artifact links.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Tools render as chips with image artifacts.
- [ ] `npx ng test --watch=false` green on new modules.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`.

## Dependencies
- **Blocks**: None
- **Blocked By**: PAIML-POLE-ANALYST-036, PAIML-POLE-API-051

## Estimated Effort
- [M]