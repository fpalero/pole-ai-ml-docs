# Ticket: PAIML-POLE-FE-001

## Title
[Infrastructure] Playwright setup — `@playwright/test`, `playwright.config.ts`, `e2e/`, browser install

## Description
`app/pole_fe` has no Playwright yet. Add it and wire the FE+BE driver so the E2E-1..20 suite
(`docs/app/pole_fe/e2e-test-plan.md`) can run against a real backend on `_testing` DBs.

## What to Do (Implementation Steps)
- [ ] `npm install -D @playwright/test` in `app/pole_fe`; add `test:e2e` script to `package.json`.
- [ ] `npx playwright install` (Chromium at minimum; `--with-deps` if needed).
- [ ] Create `app/pole_fe/playwright.config.ts`: `baseURL: http://localhost:4200`,
      `testDir: ./e2e`, and a `webServer` array that starts the backend
      (`uvicorn main:app --port 8000` in `app/pola_api` with `POLA_API_DB=pole_api_testing`,
      `SKELETON_DB=skeleton_data_testing`, temp `CHROMA_PERSIST_DIR`, `E2E_FAKES=1`) and
      `ng serve --port 4200`, or documents explicit startup (record the choice in the config comment).
- [ ] Add `e2e/` fixtures + helpers: `e2e/helpers/api.ts` (Playwright `request` wrapper), DB-state
      helpers, and a small seed/cleanup util (create class, poll job, drop `_testing` data).
- [ ] Verify `environment.ts` (`apiBaseUrl: http://localhost:8000`) is adequate for E2E; add an
      environment override if needed.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `npx playwright test` discovers and runs specs in `e2e/`.
- [ ] Browsers installed; config starts (or documents) backend + FE.
- [ ] Backend always runs with `_testing` DBs + temp Chroma + `E2E_FAKES=1` (never prod).

## Integration Tests to Run (Local Verification)
- [ ] A smoke spec `e2e/health.spec.ts` passes (load `/`, assert no console error, `GET /health` 200).

## Dependencies
- **Blocks**: `PAIML-POLE-FE-002`, `PAIML-POLE-FE-003`, `PAIML-POLE-FE-004`.
- **Blocked By**: `PAIML-POLA-API-001` (env contract + `fe-e2e`/`test-integration` tasks).

## Estimated Effort
- [M]
