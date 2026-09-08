# Ticket: PAIML-POLE-API-104

## Title
Fix duplicate pytest basename blocking test-api collection

## Description
Gate-hygiene (pre-existing on `develop`, touches no `pole_coach` code).
While implementing PAIML-POLE-COACH-001 (`docs/app/packages/pole-coach/`
phase 1), the pre-PR integration gate is blocked before any test runs:
two files with the same basename exist from PAIML-KEYCLOAK-010 PR #188:

- `app/pole_api/tests/test_temp_access_purge.py` (21KB, from commit 84d0c42)
- `app/pole_api/tests/auth/test_temp_access_purge.py` (10.6KB, from f7278c7/33cab04)

pytest aborts collection with a duplicate-basename ERROR, so
`pixi run test-api` exits before running any test. This blocks the entire
pre-PR integration gate for ALL pole_coach phase tickets (phase 1..5),
not just the coach work.

## What to Do (Implementation Steps)
- [ ] (1) Read both files and compare coverage (fixtures, cases, imports).
- [ ] (2) Resolve the basename collision with a test-only change — either:
  (a) rename the colliding file to a unique basename (recommended:
  `tests/auth/test_temp_access_purge_auth.py`), or (b) if content analysis
  shows the `auth/` version supersedes the root one, delete the stale root
  copy. Implementer decides after reading both; keep full test coverage
  either way.
- [ ] (3) No production-code changes (tests/ only).
- [ ] (4) Re-run collection + the affected test files to confirm green.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] (1) `cd app/pole_api && PYTHONPATH=src pixi run python -m pytest --collect-only -q`
  succeeds with no duplicate-basename error.
- [ ] (2) The full `test-api` suite starts (collection passes; no import
  errors introduced by the rename/delete).
- [ ] (3) Full test coverage preserved (no test case lost in the
  rename/delete); only test files touched.

## Out of Scope
- Any production-code change under `app/pole_api/src/`.
- `pole_coach` phase work itself (this ticket only unblocks its gate).

## Integration Tests to Run (Local Verification)
- [ ] `cd app/pole_api && PYTHONPATH=src pixi run python -m pytest --collect-only -q`
  (must pass with no duplicate-basename error).
- [ ] `pixi run test-api` starts and the purge suites pass
  (`tests/auth/` + any renamed file).

## Dependencies
- **Blocks**: None (infra/gate-hygiene).
- **Blocked By**: None.
- Note: unblocks the `pole_coach` phase-1..5 pre-PR integration gates
  (and every later phase gate that runs `test-api`).

## Estimated Effort
- [XS]
