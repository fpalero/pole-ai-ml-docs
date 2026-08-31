# Ticket: PAIML-POLE-API-047

## Title
[Application] `DetectPhasesUseCase` + `PhaseDetectionResult` + edge cases

## Description
Phase 17 (§2). Orchestrates `PhaseDetector` per video:
`detect_phases(landmarks, trick_label) → PhaseDetectionResult` with
`{detected: bool, phases: {ENTRADA:{start,end,confidence}, EJECUCIÓN:{...}, SALIDA:{...}}, confidence, trick_label}`.
Empty reference → 422 with list of missing metrics.

## What to Do (Implementation Steps)
- [ ] `PhaseDetectionResult` pydantic model (detected, phases, confidence, trick_label).
- [ ] `DetectPhasesUseCase.detect_phases(landmarks, trick_label)`.
- [ ] Edge case: empty reference for trick → `EmptyReferenceError` → 422 `{missing_metrics:[...]}`.
- [ ] Edge case: too-short sequence / undetectable → detected=false (DESCONOCIDO).
- [ ] Unit tests: happy path, empty reference, low confidence.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `detect_phases` returns full `PhaseDetectionResult`; empty reference → 422 with missing metrics.
- [ ] `pixi run test-api` green (guarded `_testing` DBs).

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-API-048
- **Blocked By**: PAIML-POLE-API-046

## Estimated Effort
- [M]