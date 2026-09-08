# Ticket: PAIML-POLE-ANALYST-077

## Title
Fix staging-gate harness failure: `pole-analyst-e2e` setup project requires a live Keycloak (`login-required` blocks shell with no IdP reachable)

## Description
Staging-gate follow-up (pre-existing on `develop`, touches no `pole_coach` code).
Leg `pole-analyst-e2e` (`pixi run pole-analyst-e2e`, specs in `app/pole_analyst/e2e/`):
**20 passed / 13 failed**. The smoke fails — the app shell never renders.

What fails today (exact errors):

```text
`Coach` heading resolves but is `hidden`
```

→ the Angular shell never activates past the auth initializer, so UI-shell assertions
fail. API-level specs pass (20 green, backend `/health` 200 under the harness).

Provenance (why this is NOT a 001 regression): `git diff origin/develop...HEAD -- app/`
is EMPTY for the 001 branch — 001 touches only `packages/pole_coach/*`. This failure is
pre-existing on `develop` and blocked legs 5–6 of the 001 staging gate; it is extracted
here to its own ticket. Same harness-drift class as PAIML-POLE-API-105 (leg 2 waiver).

## Root Cause
Same shared root cause as PAIML-POLE-FE-015 (FE leg tracked separately there):

- `app/pole_analyst/src/app/app.config.ts:31` → `provideAuth(keycloak)` (blocking init
  before any route activates), `keycloak.factory.ts` → `onLoad: 'login-required'`,
  default IdP `https://keycloak.pole.local`

The analyst harness differs in starting point: instead of no auth handling, it has a
real-IdP `setup` project (`app/pole_analyst/e2e/auth.setup.ts`) that performs the
Authorization-Code+PKCE round-trip once against `E2E_KEYCLOAK_URL` (default
`https://keycloak.pole.local`) and fans the `storageState` to the `chromium` project
(`playwright.config.ts` `dependencies: ['setup']`). With no IdP reachable during e2e,
the setup login never completes, so the shell never renders. The backend leg is already
hermetic (`AUTH_ENABLED=0` + `E2E_FAKES=1`); only the FE shell blocks.

## What to Do (Implementation Steps)
- [ ] (1) **Recommended: make the harness bypass-aware, mirroring the FE-015 seam.**
  Add the same FE-side E2E auth bypass (env flag skipping `keycloak.init` with a stub
  adapter) to `app/pole_analyst`, and gate `auth.setup.ts` on it: when the bypass flag
  is set, skip the real login round-trip (specs run with the stub); when unset, keep
  today's real-IdP `setup` project as the opt-in path for staging runs with a live
  IdP. Justification: one shared bypass pattern across both FE harnesses (single mental
  model, mirrors the backend `AUTH_ENABLED=0` hermetic pattern); the UI-shell specs test
  workflows, not auth. Reject live-IdP-only — it keeps the gate coupled to Keycloak
  availability, which is exactly today's failure.
- [ ] (2) Wire the flag through `app/pole_analyst/playwright.config.ts` (both the
  `ng serve` leg and the `setup` project gating) so `pixi run pole-analyst-e2e` is green
  with no IdP reachable.
- [ ] (3) Test-only + harness-config change; no production auth-behavior change when the
  flag is unset.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] (1) `pixi run pole-analyst-e2e` smoke + UI-shell suites GREEN with **no reachable
  IdP** (bypass path; `E2E_KEYCLOAK_URL` unreachable).
- [ ] (2) Real-IdP path still works opt-in (flag unset + live IdP → `setup` login green).
- [ ] (3) Default (flag unset) boot path unchanged: `login-required` against the
  configured IdP.
- [ ] (4) No production-code changes outside the bypass seam + harness config.

## Out of Scope
- Any change to the production login/logout behavior.
- `pole_fe` harness (tracked in PAIML-POLE-FE-015).
- `pole_coach` phase work itself (this ticket only unblocks its gate).

## Integration Tests to Run (Local Verification)
- [ ] `pixi run pole-analyst-e2e` (full leg — must be GREEN with no IdP reachable).
- [ ] Targeted: smoke spec alone under the fixed harness.
- [ ] Opt-in check (only where a live IdP exists): flag unset → `setup` login green.

## Unit-Test Requirement
- [ ] The bypass seam + setup-gating ship with unit specs: flag set → init skipped /
  setup skipped; flag unset → `login-required` init and real setup unchanged; ≥ 80%
  coverage for any new helper. Reuse the FE-015 helper/spec shape where applicable —
  no duplicated logic without justification.

## Dependencies
- **Blocks**: Re-running legs 5–6 of the PAIML-POLE-COACH-001 staging gate (waived
  pending this fix + PAIML-POLE-FE-015).
- **Blocked By**: None (pre-existing harness bug, independent of 001). Implement after
  (or in parallel with, same pattern as) PAIML-POLE-FE-015.
- Note: same harness-drift class as PAIML-POLE-API-105 (leg 2 waiver).

## Estimated Effort
- [S]
