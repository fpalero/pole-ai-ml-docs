# Ticket: PAIML-POLE-ANALYST-025

## Title
[Infrastructure] Playwright E2E suite setup

## Description
Set up the Playwright E2E harness for the FE+BE flow, mirroring `pole_fe`. Configure the web
server + backend with the `_testing` DBs (`pole_api_testing`, `skeleton_data_testing`,
`analysis_ai_testing`) and `E2E_FAKES=1`, guarded by `scripts/guard-testing-db.sh`.

## What to Do (Implementation Steps)
- [ ] Add Playwright config with webServer (ng serve + backend env).
- [ ] Wire `POLA_API_DB`/`SKELETON_DB`/`ANALYSIS_DB` `_testing` env + `E2E_FAKES=1`.
- [ ] Add the `pixi run pole-analyst-e2e` task (mirroring `fe-e2e`).
- [ ] Add seed/fixture helpers (upload a fake `.mp4`, fake analysis job).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `npx playwright test` boots the FE + backend and runs a smoke spec.
- [ ] Tests run only against `_testing` DBs (guard passes).

## Integration Tests to Run (Local Verification)
- [ ] Smoke: app loads, chat pane + library pane render against the test backend.

## Dependencies
- **Blocks**: PAIML-POLE-ANALYST-026
- **Blocked By**: PAIML-POLE-ANALYST-001..024 (feature code complete)

## Estimated Effort
- [M]
