# Ticket: PAIML-POLA-API-022

## Title
[Presentation] Add `GET /api/tools/histograms/summary/{video_id}`

## Description
Phase 12 (§9.3.2). Add the read-only summary route returning the stored per-video summary (`200`) or
`404`. No request body; single `video_id` in the path; plural `histograms/summary` namespace.

## What to Do (Implementation Steps)
- [ ] Step 1: Add `GET /api/tools/histograms/summary/{video_id}` to `controllers/histograms.py`.
- [ ] Step 2: Response `200 {video_id, trick_label, scores, z_mean, detections, critical_*?}`.
- [ ] Step 3: `404` with `{"detail": "summary not available for '<id>'; run histograms/analysis first"}` when absent.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Endpoint returns stored summary verbatim; idempotent (repeated GETs identical).
- [ ] `404` when the video has no histogram or no summary stored yet.

## Integration Tests to Run (Local Verification)
- [ ] UC-95 (happy path), UC-96 (no summary), UC-97 (unknown video), UC-98 (idempotent).

## Dependencies
- **Blocks**: PAIML-POLA-API-023
- **Blocked By**: PAIML-POLA-API-021

## Estimated Effort
- [S]
