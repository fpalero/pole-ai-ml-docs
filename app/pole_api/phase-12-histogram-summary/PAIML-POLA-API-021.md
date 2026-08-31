# Ticket: PAIML-POLA-API-021

## Title
[Application] Add `HistogramService.get_summary(video_id)` (read-only)

## Description
Phase 12 (§9.3.1). Add the read-only service method that returns the already-stored per-video summary
(`z_mean`, `scores`, `detections`, optional `critical_*`) from `skeleton_histograms`. No recompute, no
job, no frame extraction.

## What to Do (Implementation Steps)
- [ ] Step 1: Add `get_summary(video_id) → VideoSummary` to `HistogramService`.
- [ ] Step 2: Read the stored `skeleton_histograms` doc via `HistogramRepository.get` and map the summary fields.
- [ ] Step 3: Raise/return a not-found signal when the doc or summary fields are absent (analysis never ran).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Returns the stored summary verbatim (no computation).
- [ ] Absent summary → surfaced as `404` at the controller with an actionable message.

## Integration Tests to Run (Local Verification)
- [ ] UC-95 (happy path), UC-96 (no summary stored), UC-97 (unknown video).

## Dependencies
- **Blocks**: PAIML-POLA-API-022, PAIML-POLA-API-023
- **Blocked By**: PAIML-POLA-API-007, PAIML-POLA-API-008, PAIML-POLA-API-011 (Phase 11 merged + CI green)

## Estimated Effort
- [S]
