# Ticket: PAIML-POLA-API-033

## Title
[Application] `GET /api/analysis/videos/{video_id}/summary`

## Description
Expose the summary read endpoint returning `z_mean`, `scores`, `detections`, and
`critical_frame`/`critical_phase`/`critical_metric` — derived from the user's `video_histograms`
against the reference `skeleton_data.signal_histograms`.

## What to Do (Implementation Steps)
- [ ] Implement `AnalysisService.get_summary(video_id)`.
- [ ] Implement `GET /api/analysis/videos/{video_id}/summary`.
- [ ] Return `404` when no summary; `422` "reference data unavailable" when `signal_histograms`
      is empty (per risk mitigation).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pixi run test-api` passes; endpoint covered.

## Integration Tests to Run (Local Verification)
- [ ] UC-A3: analyzed video → `200` summary with scores + critical fields.

## Dependencies
- **Blocks**: PAIML-POLA-API-035
- **Blocked By**: PAIML-POLA-API-030

## Estimated Effort
- [M]
