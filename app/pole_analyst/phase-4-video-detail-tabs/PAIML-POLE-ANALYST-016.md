# Ticket: PAIML-POLE-ANALYST-016

## Title
[Presentation] SummaryTab (metric cards)

## Description
Build the Summary tab: read `GET /api/analysis/videos/{id}/summary` and render metric cards
(phase durations, critical frame/phase/metric, max z-score) plus a short assessment paragraph.

## What to Do (Implementation Steps)
- [ ] Implement `SummaryTab` component.
- [ ] Fetch and map the summary DTO (`z_mean`, `scores`, `detections`, `critical_*`).
- [ ] Render metric cards + assessment text.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ng lint`/`ng build` pass.
- [ ] Summary renders the metric cards and handles the loading/empty states.

## Integration Tests to Run (Local Verification)
- [ ] UC-03: Summary tab shows phase durations + critical metric after analysis.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-020
- **Blocked By**: PAIML-POLE-ANALYST-003, PAIML-POLE-ANALYST-015

## Estimated Effort
- [M]
