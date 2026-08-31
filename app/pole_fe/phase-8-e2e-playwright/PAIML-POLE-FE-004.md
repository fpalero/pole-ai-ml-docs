# Ticket: PAIML-POLE-FE-004

## Title
[Tests] E2E Jobs (E2E-16..17) + Model registry (E2E-18) + Error states (E2E-19) + Responsive (E2E-20)

## Description
Implement the remaining scenarios from `docs/app/pole_fe/e2e-test-plan.md`: jobs dashboard
poll/cancel, model registry list/activate/reject, error states (409 duplicate + job failure toast),
and responsive viewport smoke.

## What to Do (Implementation Steps)
- [ ] `e2e/jobs.spec.ts` — E2E-16 (dashboard polls to done + history), E2E-17 (cancel → stopped + rollback).
- [ ] `e2e/model-registry.spec.ts` — E2E-18 (list runs, activate one, reject another).
- [ ] `e2e/errors.spec.ts` — E2E-19 (duplicate class → 409 inline; failing crawl → failed card/toast).
- [ ] `e2e/responsive.spec.ts` — E2E-20 (768px + 375px viewports across Tricks/Jobs/Registry; assert
      no console errors).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] All five scenarios pass; responsive spec asserts zero console errors.

## Integration Tests to Run (Local Verification)
- [ ] `npx playwright test e2e/jobs.spec.ts e2e/model-registry.spec.ts e2e/errors.spec.ts e2e/responsive.spec.ts`.

## Dependencies
- **Blocks**: None.
- **Blocked By**: `PAIML-POLE-FE-001`.

## Estimated Effort
- [M]
