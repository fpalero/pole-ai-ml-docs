# Ticket: PAIML-POLA-API-035

## Title
[Test] `analysis` slice unit + integration tests

## Description
Write the test suite for the `analysis` slice against `analysis_db_testing` (guarded by
`scripts/guard-testing-db.sh`), covering upload, analyze job lifecycle, error isolation, and the
read endpoints (UC-A1..A5).

## What to Do (Implementation Steps)
- [ ] Unit-test schemas + validation.
- [ ] Integration-test upload (UC-A1/UC-A5) against `analysis_db_testing`.
- [ ] Integration-test analyze lifecycle + flag (UC-A2), no-skeleton (UC-A4).
- [ ] Integration-test summary/histogram/pose reads (UC-A3).
- [ ] Ensure `POLE-API.md` documents the new slice.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pixi run test-api` passes with ≥ 80% coverage on the new slice.

## Integration Tests to Run (Local Verification)
- [ ] UC-A1..A5 all pass against `_testing` DBs.

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLA-API-031, PAIML-POLA-API-032, PAIML-POLA-API-033, PAIML-POLA-API-034

## Estimated Effort
- [L]
