# Ticket: PAIML-POLE-API-054

## Title
[Application] Reprocessing idempotente + prompt FE

## Description
Phase 19 (§2). Re-upload of an already-analyzed video → FE asks "¿Reprocesar?"; NOT reprocessed
automatically except corrupt video. Idempotent reprocess endpoint (reuses
`POST /api/analysis/videos/{id}/analyze`).

## What to Do (Implementation Steps)
- [ ] Ensure `POST /api/analysis/videos/{id}/analyze` is idempotent (re-analyze replaces results).
- [ ] Response flags whether the video was previously analyzed (for the FE prompt).
- [ ] Tests: re-analyze replaces previous results; no duplicate side-effects.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Re-analyze idempotent; previous results replaced cleanly.
- [ ] `pixi run test-api` green (guarded `_testing` DBs).

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-API-055, PAIML-POLE-ANALYST-033, PAIML-POLE-ANALYST-035
- **Blocked By**: PAIML-POLE-API-053

## Estimated Effort
- [S]