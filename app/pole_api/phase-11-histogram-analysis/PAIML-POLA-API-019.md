# Ticket: PAIML-POLA-API-019

## Title
[Infrastructure] Add `test_histograms_api.py` (analysis/GET/PATCH integration)

## Description
Phase 11 (§8.3.5 bullet 2). Add the histogram API integration test covering the full contract:
POST analysis (202→poll→done, processed vs skipped, per-video error isolation), GET full doc, PATCH
phases (200) + PATCH metrics (422) + missing video (404). Targets `pole_api_testing` /
`skeleton_data_testing`.

## What to Do (Implementation Steps)
- [ ] Step 1: Create `app/pola_api/tests/tools/test_histograms_api.py`.
- [ ] Step 2: UC-91 happy path (submit → poll → done → GET full doc; signal_histograms + summary fields).
- [ ] Step 3: UC-94 one-video error isolation (job `done`, per-video reason in description).
- [ ] Step 4: UC-92 PATCH metrics → 422; UC-93 GET/PATCH missing → 404.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Test passes under `pixi run test-api`; coverage ≥80%.
- [ ] Uses guarded `_testing` DB names only.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` — `test_histograms_api.py`.

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLA-API-013, PAIML-POLA-API-014, PAIML-POLA-API-015, PAIML-POLA-API-017

## Estimated Effort
- [M]
