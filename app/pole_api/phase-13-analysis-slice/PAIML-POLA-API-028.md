# Ticket: PAIML-POLA-API-028

## Title
[Infrastructure] `analysis` jobs router

## Description
Expose the analysis job-status surface by reusing `make_jobs_router`:
`GET /api/analysis/jobs`, `GET /api/analysis/jobs/{job_id}`, `POST /api/analysis/jobs/{job_id}/cancel`
(slice `analysis`), so the FE can poll the analyze/upload jobs.

## What to Do (Implementation Steps)
- [ ] Register `make_jobs_router(prefix="/analysis", slice_name="analysis")`.
- [ ] Confirm job docs use `slice="analysis"` and the standard status machine.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pixi run test-api` passes; jobs list/get/cancel covered.

## Integration Tests to Run (Local Verification)
- [ ] UC-A2: poll `GET /api/analysis/jobs/{job_id}` observes `pending → running → done`.

## Dependencies
- **Blocks**: PAIML-POLA-API-029
- **Blocked By**: PAIML-POLA-API-025

## Estimated Effort
- [S]
