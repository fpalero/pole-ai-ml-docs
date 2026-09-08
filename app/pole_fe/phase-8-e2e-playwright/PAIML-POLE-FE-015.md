# Ticket: PAIML-POLE-FE-015

## Title
Fix staging-gate harness failure: `fe-e2e` UI-shell suite blocks on Keycloak `login-required` with no IdP reachable (no FE auth bypass)

## Description
Staging-gate follow-up (pre-existing on `develop`, touches no `pole_coach` code).
Leg `fe-e2e` (`pixi run fe-e2e`, specs in `app/pole_fe/e2e/`): **6 passed / 15 failed**.
Even the E2E-00 smoke fails — the app shell never renders.

What fails today (exact errors):

```text
getByText('TRICK_REGISTRY') element not found
```

→ failure screenshot shows a **blank page** → every UI-shell assertion fails.
API-level specs pass (backend `/health` 200 under the harness).

Provenance (why this is NOT a 001 regression): `git diff origin/develop...HEAD -- app/`
is EMPTY for the 001 branch — 001 touches only `packages/pole_coach/*`. This failure is
pre-existing on `develop` and blocked legs 5–6 of the 001 staging gate; it is extracted
here to its own ticket. Same harness-drift class as PAIML-POLE-API-105 (leg 2 waiver).

## Root Cause
Both apps now boot with a BLOCKING Keycloak initializer before any route activates:

- `app/pole_fe/src/app/app.config.ts:24` → `provideAuth(keycloak)`
- `app/pole_fe/src/app/core/auth/keycloak.factory.ts:31` → `onLoad: 'login-required'`,
  default IdP `https://keycloak.pole.local`

The `fe-e2e` harness (`app/pole_fe/playwright.config.ts`) boots the backend with
`AUTH_ENABLED=0` (backend auth bypassed) but serves the FE via plain
`npx ng serve --configuration development` — **no FE-side bypass exists**.
With no IdP reachable during e2e, `keycloak.init(...)` never resolves, the shell never
renders, and every UI assertion fails. The suite predates the `login-required` change.
(Sister leg `pole-analyst-e2e` shares the root cause but has its own harness starting
point — a real-IdP `setup` project — and is tracked separately in
PAIML-POLE-ANALYST-077.)

## What to Do (Implementation Steps)
- [ ] (1) **Recommended: add an FE-side E2E auth bypass seam keyed off env** (extend the
  existing `AUTH_ENABLED=0` the harness already exports into the `ng serve` leg, or a
  dedicated `E2E_AUTH_BYPASS=1`): when set, `provideAuth`/factory skips `keycloak.init`
  and installs a stub adapter so routes activate unauthenticated. Justification: the
  backend leg already runs hermetic (`AUTH_ENABLED=0` + `E2E_FAKES=1`); these specs test
  the UI shell, not auth; a local stub keeps the suite hermetic/fast with zero IdP
  dependency. Reject making the live-IdP login the default path — it couples every gate
  run to a reachable Keycloak, which is exactly today's failure mode. (Note: FE-014 is
  reserved in-flight — see PROJECT_VARS — if its seam has landed, reuse it instead of
  building a second one.)
- [ ] (2) Wire the flag through `app/pole_fe/playwright.config.ts` (`ng serve` webServer
  entry) so `pixi run fe-e2e` is green with no IdP reachable and no code change per run.
- [ ] (3) Keep real-login coverage possible (opt-in override pointing at a live IdP),
  not the default.
- [ ] (4) Test-only + harness-config change; no production auth-behavior change when the
  flag is unset (default `login-required` path byte-identical).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] (1) `pixi run fe-e2e` smoke + UI-shell suites GREEN with **no reachable IdP**
  (no `keycloak.pole.local` resolvable).
- [ ] (2) Default (flag unset) boot path unchanged: `login-required` against the
  configured IdP.
- [ ] (3) No production-code changes outside the bypass seam + harness config.

## Out of Scope
- Any change to the production login/logout behavior (incl. FE-013 end-session flow).
- `pole_analyst` harness (tracked in PAIML-POLE-ANALYST-077).
- `pole_coach` phase work itself (this ticket only unblocks its gate).

## Integration Tests to Run (Local Verification)
- [ ] `pixi run fe-e2e` (full leg — must be GREEN with no IdP reachable).
- [ ] Targeted: E2E-00 smoke spec alone under the fixed harness.

## Unit-Test Requirement
- [ ] The bypass seam ships with unit specs: flag set → `keycloak.init` skipped / stub
  installed and routes activate; flag unset → `login-required` init unchanged; ≥ 80%
  coverage for any new helper.

## Dependencies
- **Blocks**: Re-running legs 5–6 of the PAIML-POLE-COACH-001 staging gate (waived
  pending this fix + PAIML-POLE-ANALYST-077).
- **Blocked By**: None (pre-existing harness bug, independent of 001). Coordinate with
  reserved FE-014 if its seam lands first.
- Note: same harness-drift class as PAIML-POLE-API-105 (leg 2 waiver).

## Estimated Effort
- [S]
