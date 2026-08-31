# Ticket: PAIML-POLE-API-044

## Title
[Infrastructure] Endpoints `GET /api/tools/histograms/references/{trick_label}` y `/classes`

## Description
Phase 16 (§2). Serve reference data for the FE:
- `GET /api/tools/histograms/references/{trick_label}` — reference histograms of the trick (per metric and phase).
- `GET /api/tools/histograms/classes` — tricks with available reference histograms (for video selection in `pole_fe` Phase 11).

## What to Do (Implementation Steps)
- [ ] `GET /api/tools/histograms/references/{trick_label}`: return metrics with histograms per phase; 422 with `missing_metrics` if reference empty.
- [ ] `GET /api/tools/histograms/classes`: list `trick_label` with reference histograms available.
- [ ] Wire to `TrickHistogramRepository.find_by_trick`.
- [ ] API tests for both endpoints (happy path + empty reference 422).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Both endpoints return reference data as specified; empty reference → 422 with `missing_metrics`.
- [ ] `pixi run test-api` green (guarded `_testing` DBs).

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-API-045, PAIML-POLE-FE-009, PAIML-POLE-FE-011
- **Blocked By**: PAIML-POLE-API-041, PAIML-POLE-API-043

## Estimated Effort
- [S]