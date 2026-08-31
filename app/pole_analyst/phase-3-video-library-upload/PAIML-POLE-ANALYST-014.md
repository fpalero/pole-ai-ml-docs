# Ticket: PAIML-POLE-ANALYST-014

## Title
[Test] Unit tests T3.x (list mapping, upload, badge logic, empty state)

## Description
Unit-test the video library: list DTO mapping, upload + progress, badge derivation from the
`analyzed` flag, and the empty-state rendering.

## What to Do (Implementation Steps)
- [ ] Cover `VideosService.list` mapping and URL builders.
- [ ] Cover `VideosService.upload` progress + job polling (mocked client).
- [ ] Cover badge logic (`analyzed` true/false).
- [ ] Cover empty-state render.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `npx ng test --watch=false` passes.
- [ ] Coverage for Phase 3 code is ≥ 80%.

## Integration Tests to Run (Local Verification)
- [ ] N/A (unit-level; validates UC-01/UC-05/UC-07).

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLE-ANALYST-012

## Estimated Effort
- [M]
