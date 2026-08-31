# Ticket: PAIML-POLE-FE-012

## Title
[Tests] Unit + E2E del flujo de generación/visualización de histogramas de clase

## Description
Phase 11 (§4). Cover the reference-histogram generation and visualization flow end-to-end in
`pole_fe` (unit + Playwright E2E).

## What to Do (Implementation Steps)
- [ ] Unit: services (generate/getClassHistogramStats/classes) with mocked HTTP.
- [ ] Unit: presentation components (action, job progress, class stats panel, empty-state).
- [ ] E2E (Playwright, `_testing` guarded): select videos → generate → job done → panel shows curves; empty reference → empty-state.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Coverage ≥ 80% on the new modules.
- [ ] `npx ng test --watch=false` and `pixi run fe-e2e` green (guarded `_testing` DBs).

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`.
- [ ] `pixi run fe-e2e`.

## Dependencies
- **Blocks**: None
- **Blocked By**: PAIML-POLE-FE-010, PAIML-POLE-FE-011

## Estimated Effort
- [M]

## Status Update (Phase 19 completion)
Backend `POST/GET /api/tools/histograms/references` contract implemented (PAIML-POLE-API-043).
The two Playwright E2E tests in `e2e/histograms.spec.ts` are un-skipped: `test.skip` probes replaced
with hard availability assertions so a contract regression fails the suite rather than silently skipping.
E2E run deferred (per deferred-full-test convention); verify via `pixi run test-integration`.
