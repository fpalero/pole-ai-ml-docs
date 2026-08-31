# Ticket: PAIML-POLA-API-018

## Title
[Infrastructure] Rewrite tools tests (remove threshold/reference; cover crop/shift/correct/histogram)

## Description
Phase 11 (§8.3.5 bullet 1). Delete the threshold/reference test files and rewrite the tools test suite
to cover the retained surface (`crop/shift/correct/histogram/similarity`) plus the new endpoints, after
the removals in PAIML-POLA-API-015/016/017.

## What to Do (Implementation Steps)
- [ ] Step 1: Delete `tests/tools/test_threshold_discovery.py` and `tests/tools/test_seed_reference.py`.
- [ ] Step 2: Rewrite `test_tools_api.py`, `test_tools_service.py`, `test_hardening_api.py` for crop/shift/correct/histogram/similarity.
- [ ] Step 3: Remove any reference/attempt/analyze assertions.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Tools tests pass under `pixi run test-api`; ≥80% coverage.
- [ ] No test references threshold discovery / reference / attempts / analyze.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (real Mongo on `pole_api_testing` / `skeleton_data_testing`).

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLA-API-013, PAIML-POLA-API-015, PAIML-POLA-API-016, PAIML-POLA-API-017

## Estimated Effort
- [L]
