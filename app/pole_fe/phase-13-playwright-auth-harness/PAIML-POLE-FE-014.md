# Ticket: PAIML-POLE-FE-014

## Title
Add AUTH_ENABLED=0 to pole_fe Playwright backend harness

## Description
Gate-hygiene (pre-existing on `develop`, touches no `pole_coach` code).
`app/pole_fe/playwright.config.ts` boots a local FastAPI backend in its
`webServer` stanza WITHOUT `AUTH_ENABLED=0`, while
`app/pole_analyst/playwright.config.ts` (line 55) sets it.
`app/pole_api/src/core/auth.py:56` defaults `AUTH_ENABLED` to `"1"`, so
the FE e2e backend demands Keycloak tokens and every FE e2e API call 401s:
0/21 specs pass as committed (6/15 pass with a manual override).

## What to Do (Implementation Steps)
- [ ] (1) In `app/pole_fe/playwright.config.ts`, add `AUTH_ENABLED=0` to
  the backend `env` in the `webServer` command, mirroring
  `app/pole_analyst/playwright.config.ts` (line 55).
- [ ] (2) Test-harness only — no production-code changes.
- [ ] (3) Re-run the FE e2e suite and confirm no auth/401 failures.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] (1) `pixi run fe-e2e` (from repo root) no longer fails with
  auth/401 errors.
- [ ] (2) Suite count/behavior matches the analyst harness behavior
  (backend starts unauthenticated as intended for e2e).
- [ ] (3) Only the Playwright harness touched (no production code).

## Out of Scope
- Any production-code change under `app/pole_fe/src/` or
  `app/pole_api/src/` (including `core/auth.py` defaults).
- Real authenticated e2e coverage (future work; this ticket restores the
  intended unauthenticated harness parity with pole_analyst).

## Integration Tests to Run (Local Verification)
- [ ] `pixi run fe-e2e` from repo root (must not fail with auth/401 errors).
- [ ] Diff `app/pole_fe/playwright.config.ts` vs
  `app/pole_analyst/playwright.config.ts` backend env to confirm parity
  on `AUTH_ENABLED`.

## Dependencies
- **Blocks**: None (infra/gate-hygiene).
- **Blocked By**: None.
- Note: unblocks the `pole_coach` phase gates that depend on a green
  `fe-e2e` signal (parity with the analyst harness).

## Estimated Effort
- [XS]
