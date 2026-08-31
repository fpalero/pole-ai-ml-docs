# Ticket: PAIML-POLA-API-015

## Title
[Presentation] Delete `/reference/*`, `/analyze`, `/attempts` endpoints in `tools.py`

## Description
Phase 11 (§8.3.4 bullet 1). Remove the legacy reference/threshold/attempt/analyze REST surface from the
tools controller, keeping only `crop/shift/correct/health` (the histogram endpoints live in the new
`histograms` controller).

## What to Do (Implementation Steps)
- [ ] Step 1: In `app/pola_api/src/tools/controllers/tools.py`, delete `POST/GET /reference/metrics`.
- [ ] Step 2: Delete `POST/GET /reference/thresholds` and `POST /reference/thresholds/discover`.
- [ ] Step 3: Delete `POST /analyze` and `GET /attempts/{attempt_id}`.
- [ ] Step 4: Keep `crop`, `shift`, `correct`, `health`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] The legacy routes are gone; no imports reference them.
- [ ] `crop/shift/correct/health` still pass their existing tests.

## Integration Tests to Run (Local Verification)
- [ ] Regression on `test_tools_api.py` (crop/shift/correct) after rewrite in PAIML-POLA-API-018.

## Dependencies
- **Blocks**: PAIML-POLA-API-016, PAIML-POLA-API-018
- **Blocked By**: PAIML-POLA-API-009

## Estimated Effort
- [S]
