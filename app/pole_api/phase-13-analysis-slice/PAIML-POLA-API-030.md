# Ticket: PAIML-POLA-API-030

## Title
[Application] Analyze job worker (extract landmarks → histogram → score → flag)

## Description
Implement the analysis job worker: (1) extract skeleton landmarks →
`analysis-db.skeleton-landmarks`; (2) run `HistogramDataProcessor` →
`analysis-db.video_histograms` (one-per-video); (3) compute `z_mean`/`scores`/`detections`
against `skeleton_data.signal_histograms` `mean`/`std`; (4) set `videos.analyzed=true`.

## What to Do (Implementation Steps)
- [ ] Reuse `SkeletonExtractor` to produce landmarks → `skeleton-landmarks`.
- [ ] Reuse `HistogramDataProcessor` writing to `analysis-db.video_histograms` (confirm/override
      the target collection per D-A2).
- [ ] Read `signal_histograms` `mean`/`std` and compute scores + detections.
- [ ] Set `videos.analyzed=true` on success.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pixi run test-api` passes; the worker covered by integration tests (with fakes).

## Integration Tests to Run (Local Verification)
- [ ] UC-A2: analyze job writes landmarks + histogram and sets `analyzed=true`.

## Dependencies
- **Blocks**: PAIML-POLA-API-031, PAIML-POLA-API-032, PAIML-POLA-API-033, PAIML-POLA-API-034
- **Blocked By**: PAIML-POLA-API-029

## Estimated Effort
- [L]
