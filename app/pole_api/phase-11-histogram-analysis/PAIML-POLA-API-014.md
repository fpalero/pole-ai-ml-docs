# Ticket: PAIML-POLA-API-014

## Title
[Presentation] Add tools jobs router + mount histograms in `main.py`

## Description
Phase 11 (§8.3.3 bullets 2-3). Add the `tools` jobs router (`GET/POST /api/tools/jobs{/id,/id/cancel}`)
and mount the `histograms` router + jobs router under `/api`, registering `tools` in the jobs slice set.

## What to Do (Implementation Steps)
- [ ] Step 1: Create `app/pola_api/src/tools/controllers/jobs.py` = `make_jobs_router(prefix="/tools", tags=["tools"], slice_name="tools")`.
- [ ] Step 2: In `main.py`, include the `histograms` router and the `tools` jobs router under `/api`.
- [ ] Step 3: Register `tools` in the jobs slice set (so jobs are discoverable/pollable).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `GET /api/tools/jobs/{id}` polls histogram-analysis jobs; cancel works.
- [ ] `/api/tools/histograms/*` is mounted and reachable.
- [ ] No cross-slice import violations.

## Integration Tests to Run (Local Verification)
- [ ] UC-91 (poll `GET /api/tools/jobs/{id}`).

## Dependencies
- **Blocks**: PAIML-POLA-API-019
- **Blocked By**: PAIML-POLA-API-013

## Estimated Effort
- [S]
