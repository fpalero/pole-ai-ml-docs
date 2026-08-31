# Ticket: PAIML-POLA-API-023

## Title
[Infrastructure] Add `test_summary_service.py` + `test_histograms_summary_api.py`

## Description
Phase 12 (§9.3.3). Add unit + integration tests for the read-only summary path: stored-fields →
`VideoSummary` mapping, absent-summary → `404`, read-only + idempotency (GET does not mutate, repeated
GETs identical). Targets `pole_api_testing` / `skeleton_data_testing`.

## What to Do (Implementation Steps)
- [ ] Step 1: Create `app/pola_api/tests/tools/test_summary_service.py` (mapping + absence path).
- [ ] Step 2: Create `app/pola_api/tests/tools/test_histograms_summary_api.py` (GET happy path; missing summary → 404; unknown video → 404; idempotent; no mutation of `skeleton_histograms`/`signal_histograms`).
- [ ] Step 3: Cover UC-95..98.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Tests pass under `pixi run test-api`; coverage ≥80%.
- [ ] Asserts `summary` never mutates/recomputes.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` — summary service + API tests.

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLA-API-021, PAIML-POLA-API-022

## Estimated Effort
- [M]
