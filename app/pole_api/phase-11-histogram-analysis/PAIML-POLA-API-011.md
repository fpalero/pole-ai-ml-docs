# Ticket: PAIML-POLA-API-011

## Title
[Application] Second pass: signed z-scores, 0-100 scores, and detections

## Description
Phase 11 (§8.3.2 bullet 5, §8.7 A-8). After the cohort aggregation, compute — against the **updated**
`signal_histograms` — each video's signed 8×300 z-score matrix (std-floor `max(std, σ_floor)`), derive
per-metric `z_mean` + 0-100 `scores`, collect `detections` where `|z| > 1`, and persist these onto the
per-video `skeleton_histograms` doc. This is the data Phase 12 reads back.

## What to Do (Implementation Steps)
- [ ] Step 1: Compute signed `z[metric][i] = (resampled − mean) / max(std, σ_floor)` for all 8 metrics × 300 pts.
- [ ] Step 2: `z_mean[metric] = mean_i(z[metric][i])` (signed).
- [ ] Step 3: `score[metric] = 100 · exp(−|z_mean[metric]| / 2)`.
- [ ] Step 4: For every point with `|z| > 1`, append `{index, phase, metric, z_score, frame}` (index→frame via phase_bounds + per-video `phases`).
- [ ] Step 5: Write `z_mean`, `scores`, `detections` (+ optional `critical_*`) onto the per-video doc.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Signed z, signed `z_mean`, and 0-100 `scores` match the confirmed formulas (§8.7 A-8 / §9.7 D-3/D-6).
- [ ] `detections` contains one entry per point with `|z| > 1`, each with correct phase/metric/frame.
- [ ] Fields persist on the per-video `skeleton_histograms` doc.

## Integration Tests to Run (Local Verification)
- [ ] UC-91 (summary fields populated), UC-98 (detections honor `|z| > 1`).

## Dependencies
- **Blocks**: PAIML-POLA-API-012, PAIML-POLA-API-013
- **Blocked By**: PAIML-POLA-API-004, PAIML-POLA-API-008

## Estimated Effort
- [L]
