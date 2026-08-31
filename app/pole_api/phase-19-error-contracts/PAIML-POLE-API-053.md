# Ticket: PAIML-POLE-API-053

## Title
[Infrastructure] Error contracts unificados + tests por escenario

## Description
Phase 19 (§1). Consolidate error contracts of the analysis pipeline (upload → extraction → processing →
phase detection → classification → feedback):
- Empty reference → `422` `{"detail":"no reference histograms for trick X","missing_metrics":[…]}`.
- Corrupt/undecodable video → job `failed` `{"error":"video_unreadable","reason":"…"}`.
- No detectable skeleton → job `done` + `skipped` (`result_json.failed="low_quality"`, card stays "Not analyzed").
- Phase confidence < 0.7 → job `done` + `DESCONOCIDO` (FE opens manual modal).
- LSTM no classification → job `done` + `trick_label=null` (FE asks trick name).

## What to Do (Implementation Steps)
- [ ] Define exception → response/result mapping for each row of the matrix.
- [ ] Ensure job `failed` only for corrupt video; other cases `done` + `skipped`/`DESCONOCIDO`/`null`.
- [ ] Tests per scenario (fake landmarks + seeded references + LSTM stub).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Error matrix fully implemented and tested per scenario.
- [ ] `pixi run test-api` green (guarded `_testing` DBs).

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-API-054
- **Blocked By**: PAIML-POLE-API-048, PAIML-POLE-API-049

## Estimated Effort
- [M]