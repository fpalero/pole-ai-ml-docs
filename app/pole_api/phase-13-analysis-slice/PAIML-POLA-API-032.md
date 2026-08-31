# Ticket: PAIML-POLA-API-032

## Title
[Application] `GET /api/analysis/videos/{video_id}/histogram`

## Description
Expose the per-video histogram read endpoint returning the `analysis-db.video_histograms` doc
(`video_id`, `trick_label`, `phases`, `metrics`, `resampled`, `z_mean`, `scores`, `detections`).

## What to Do (Implementation Steps)
- [ ] Implement `AnalysisService.get_histogram(video_id)`.
- [ ] Implement `GET /api/analysis/videos/{video_id}/histogram`.
- [ ] Return `404` when no histogram exists.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pixi run test-api` passes; endpoint covered.

## Integration Tests to Run (Local Verification)
- [ ] UC-A3: analyzed video → `200` histogram doc.

## Dependencies
- **Blocks**: PAIML-POLA-API-035
- **Blocked By**: PAIML-POLA-API-030

## Estimated Effort
- [S]
