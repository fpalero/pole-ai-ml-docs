# Ticket: PAIML-POLE-API-049

## Title
[Application] `ClassifyTrickUseCase` LSTM stub (trick_label null → flujo manual)

## Description
Phase 17 (§3). LSTM stub classification: if the model does not classify (low confidence) →
`trick_label=null` → the FE asks the athlete for the trick name (manual flow).

## What to Do (Implementation Steps)
- [x] `ClassifyTrickUseCase.classify(landmarks, phases) → trick_label | null`.
- [x] Stub returns `trick_label` when confidence high, `null` when low (configurable threshold).
- [x] Wire into AnalyzeWorker Classification & analysis stage.
- [x] Unit tests: classified + null (manual flow) cases.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] `trick_label` set on high confidence, `null` on low; worker survives both.
- [x] `pixi run test-api` green (guarded `_testing` DBs).

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-API-053, PAIML-POLE-ANALYST-035
- **Blocked By**: PAIML-POLE-API-047, PAIML-POLE-API-048

## Estimated Effort
- [S]