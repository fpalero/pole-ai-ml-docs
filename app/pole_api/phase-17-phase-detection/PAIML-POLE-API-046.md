# Ticket: PAIML-POLE-API-046

## Title
[Domain] `PhaseDetector` (Bhattacharyya + ventana deslizante + K=5)

## Description
Phase 17 (§1). Automatic detection of ENTRADA / EJECUCIÓN / SALIDA phases from normalized landmarks
using reference histograms + Bhattacharyya distance + sliding window + temporal consensus (K=5).
Input: landmarks + `skeleton_trick_histograms` references for the target `trick_label`. For each of
the 5 metrics compute the sliding-window histogram and Bhattacharyya distance against each phase
reference. Window classified as max-similarity phase; temporal consensus `required_matches(K)=5` with
`window_size=20` and `stride=5`. 300 sequence points = 100 ENTRANCE + 100 EXECUTION + 100 EXIT
(orientation for boundary estimation). If max similarity < 0.7 → `DESCONOCIDO`.

## What to Do (Implementation Steps)
- [ ] `PhaseDetector.detect(landmarks, trick_label, references) → PhaseBoundaries`.
- [ ] Sliding window (window_size=20, stride=5) → per-metric histogram → Bhattacharyya vs each phase reference.
- [ ] Temporal consensus `required_matches(K)=5`; classify windows into the 3 phases.
- [ ] Compute start/end frames; if max similarity < 0.7 → `DESCONOCIDO` (no boundaries).
- [ ] Unit tests over fake landmark sequences + seeded references (detected + unknown).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Detection with K=5 + Bhattacharyya tested on fake test landmarks.
- [ ] Low-threshold (< 0.7) → `DESCONOCIDO`.
- [ ] `pixi run test-api` green (guarded `_testing` DBs).

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-API-047, PAIML-POLE-API-048
- **Blocked By**: PAIML-POLE-API-041, PAIML-POLE-API-043, PAIML-POLE-API-045

## Estimated Effort
- [L]