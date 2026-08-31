# Ticket: PAIML-POLA-API-025

## Title
[Infrastructure] `analysis` slice settings + Mongo client for `analysis-db`

## Description
Add the configuration and DB wiring for the new `analysis` slice: the `analysis-db` Mongo
connection (collections `videos`, `skeleton-landmarks`, `video_histograms`) and the dedicated
analysis upload folder env. Mirrors the existing slice wiring so the new slice can be split into
its own service later.

## What to Do (Implementation Steps)
- [ ] Add `ANALYSIS_DB` + upload-folder settings (and `_testing` guard support).
- [ ] Add a Mongo client/provider for `analysis-db`.
- [ ] Add `ANALYSIS_DB` to `.env.example` and the testing-DB guard script.
- [ ] Add `app/pola_api/src/analysis/` package skeleton + `APIRouter(prefix="/analysis")`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pixi run test-api` passes (existing tests unaffected).
- [ ] The router mounts under `/api/analysis` without errors.

## Integration Tests to Run (Local Verification)
- [ ] UC-A1: boot the app; `/api/analysis` is reachable with a test DB.

## Dependencies
- **Blocks**: PAIML-POLA-API-026, PAIML-POLA-API-027, PAIML-POLA-API-028
- **Blocked By**: —

## Estimated Effort
- [M]
