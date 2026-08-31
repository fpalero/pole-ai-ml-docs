# Ticket: PAIML-POLE-ANALYST-017

## Title
[Presentation] HistogramTab (metric chart)

## Description
Build the Histogram tab: read `GET /api/analysis/videos/{id}/histogram` and render the
trick-metric histogram chart (resampled metrics + `scores`) with labeled axes, a highlighted
marker, and a legend.

## What to Do (Implementation Steps)
- [ ] Implement `HistogramTab` + `MetricChart` component.
- [ ] Map the histogram DTO (`metrics`, `resampled`, `scores`) into chart data.
- [ ] Render axes, legend, and the current-video marker.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `ng lint`/`ng build` pass.
- [ ] Chart renders with axes + legend and is unit-tested for data transforms.

## Integration Tests to Run (Local Verification)
- [ ] UC-03: Histogram tab shows the chart for an analyzed video.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-020
- **Blocked By**: PAIML-POLE-ANALYST-003, PAIML-POLE-ANALYST-015

## Estimated Effort
- [M]
