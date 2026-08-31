# Ticket: PAIML-POLE-FE-008

## Title
[Tests] Unit + Playwright E2E for the extraction → process (biometric + histogram) flow

## Description
Add integration coverage for the new Phase 9 flow end to end: extract landmarks → annotate phase
frames → biomech (process) → histo (histogram analysis + summary), reusing the existing Playwright
harness (`app/pole_fe/e2e/`, `playwright.config.ts`, `E2E_FAKES=1`, `_testing` DBs, temp Chroma).

## What to Do (Implementation Steps)
- [ ] `e2e/biomech-flow.spec.ts` — create class → upload/cut clips → Extract (poll job) → open
      Biomechanical Signal Analysis before Histo → assert the panel shows **nothing** (empty state,
      Q2 resolution) → capture Start/Execution/Exit/End → Histo (poll) → reopen the panel → assert the
      chart renders and `GET /api/tools/histograms/summary/{video_id}` returns a summary.
- [ ] Extend `e2e/helpers.ts` with the new API calls (`extract`, `phase-frames`, `histograms/analysis`,
      `histograms/summary`) + job-poll helper reuse.
- [ ] Update `docs/app/pole_fe/e2e-test-plan.md` with the new scenarios (E2E-21..23) mapping to the
      flow's happy path, missing-phase-frames skip, and the pre-Histo empty-state / post-Histo chart.
- [ ] Ensure unit specs from FE-005/006/007 remain green in the aggregate (`npx ng test --watch=false`).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `npx playwright test e2e/biomech-flow.spec.ts` passes against `_testing` DBs + `E2E_FAKES=1`.
- [ ] No console errors in the new flow; `aria-live` job announcements present on Extract/Biomech/Histo.

## Integration Tests to Run (Local Verification)
- [ ] `npx playwright test e2e/biomech-flow.spec.ts`.
- [ ] `pixi run fe-e2e` (full suite, includes the new spec).

## Dependencies
- **Blocks**: None.
- **Blocked By**: `PAIML-POLE-FE-006`, `PAIML-POLE-FE-007`.

## Estimated Effort
- [M]
