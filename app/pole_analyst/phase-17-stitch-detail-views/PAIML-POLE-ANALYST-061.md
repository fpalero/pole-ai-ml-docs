# Ticket: PAIML-POLE-ANALYST-061

## Title
[Features] Metric Distribution Analysis cards — session deltas + Peak Performance badges

## Description
Phase 17 Phase B (PLAN_PHASE_17.md). Renders the SummaryTab "Metric Distribution Analysis"
section from `GET /api/analysis/videos/{id}/metric-deltas` (pole_api Phase 24, PAIML-POLE-API-072):
per-metric card with current value, previous value, colored delta badge (`+12% vs last session`),
and `Peak Performance` flag per the Stitch analysis-details screen.

## What to Do (Implementation Steps)
- [ ] DTOs (`MetricDeltas`, `MetricDelta`, `PeakFlag`) in `core/models/api.models.ts` +
      `AnalysisService.metricDeltas(videoId)`.
- [ ] Pure mappers in `features/analysis/models/distribution.ts` (+ spec): view shapes, delta
      sign/color logic, empty-baseline → section hidden.
- [ ] `MetricDistributionCardComponent` (standalone): value, delta badge, peak chip.
- [ ] Wire section into SummaryTab below AI Insights; loading skeleton; hide when metrics list empty.
- [ ] CONSTRAINT (API-072 review M1): `Peak Performance` badge renders ONLY when a baseline exists
      (i.e., together with deltas) — never keyed off empty `peak_flags` alone.
- [ ] Unit specs for mappers, component, and SummaryTab integration point.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Cards match the Stitch screen layout and app conventions.
- [ ] Section hidden (no empty shell) when no comparable baseline session exists.
- [ ] No subscription leaks; lint/typecheck green.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-analyst`
- [ ] Playwright smoke: analyzed video renders distribution cards against `_testing` backend.

## Dependencies
- **Blocks**: none
- **Blocked By**: PAIML-POLE-API-072

## Estimated Effort
- [M]
