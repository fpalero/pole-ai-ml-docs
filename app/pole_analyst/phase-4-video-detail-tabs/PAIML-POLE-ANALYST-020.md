# Ticket: PAIML-POLE-ANALYST-020

## Title
[Test] Unit tests T4.x (job polling, tab DTO mapping, chart transforms)

## Description
Unit-test the detail tabs: analysis job polling lifecycle, each tab's DTO mapping, and chart
data transforms.

## What to Do (Implementation Steps)
- [ ] Cover `AnalysisService.trigger` polling (done/failed termination).
- [ ] Cover Summary/Histogram/Pose DTO mapping.
- [ ] Cover Plan reply parsing and chart data transforms.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `npx ng test --watch=false` passes.
- [ ] Coverage for Phase 4 code is ≥ 80%.

## Integration Tests to Run (Local Verification)
- [ ] N/A (unit-level; validates UC-02/UC-03/UC-04).

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLE-ANALYST-016, PAIML-POLE-ANALYST-017, PAIML-POLE-ANALYST-018, PAIML-POLE-ANALYST-019

## Estimated Effort
- [M]
