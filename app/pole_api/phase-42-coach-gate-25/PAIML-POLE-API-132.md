# Ticket: PAIML-POLE-API-132

## Title
ensureCoachSession bootstrap flake (Class D): retry waitForURL navigation timeout without masking auth failures (TP-04)

## Status
📋 PLANNED — follow-up gate-fix ticket for phase-42 coach-gate-25, SAMPLE-5 gate
run `sample5-647d57e-20260921-205203` (**15/25, RED**).

- **Status**: 📋 PLANNED
- **Project**: pole_api (frontend lane / e2e harness)
- **Phase**: 42 coach-gate-25
- **Blocks**: —
- **Blocked By**: — independent of 129/130/131 (none of the four gate-fix
  tickets block each other).

## Context

SAMPLE-5 gate run `app/pole_analyst/test-results/coach-150q/sample5-647d57e-20260921-205203/`
(`coach-150q-judge.md` + `coach-150q-transcript.jsonl`): **COACH7-TP-04** fails
one-off with `page.waitForURL: Timeout 30000ms` during re-login / bootstrap in
`ensureCoachSession` while the app loads — "waiting for navigation until load".
Judge row: fail, empty blocks / empty reply (the turn never got asked).

### Evidence / root cause
- Location: `ensureCoachSession` in
  `app/pole_analyst/e2e/coach-150q.spec.ts:349-369`; the failing wait is the
  Keycloak round-trip `page.waitForURL((url) => url.origin.includes(KC_URL), { timeout: 30_000 })`
  at `:360` (session-expired leg).
- One-off flake — the app slug/navigation is slow on the contended gate
  runner, so the `waitForURL` 30 s budget expires while the app is still
  loading. Not a genuine auth failure (credentials / Keycloak are healthy).

## Scope

Make `ensureCoachSession` bootstrap robust:

- add **one retry** (e.g. re-attempt `waitForURL` after a short settle) and/or
  raise the wait budget,
- **WITHOUT masking genuine auth failures**: only retry on navigation timeout,
  and **assert the actual destination URL** before proceeding.

## Files Affected
- `app/pole_analyst/e2e/coach-150q.spec.ts` — `ensureCoachSession`
  (`:349-369`).

## Validation Plan
1. Flake proof — 3 consecutive runs of the full gate **or** the TP-04 case:
   ```bash
   npx playwright test coach-150q.spec.ts --workers=1 -g "COACH7-TP-04"
   ```
   ×3 must pass with no `waitForURL` timeout.
2. Full SAMPLE-5 gate **25/25** as phase acceptance (with 129/130/131).

## Acceptance Criteria
- [ ] 3 consecutive TP-04 runs (or 3 consecutive full-gate runs) pass with no
      `waitForURL` timeout.
- [ ] Genuine auth failures still fail loudly — retry applies **only** on
      navigation timeout, and the destination URL is asserted before the
      session proceeds.
- [ ] No regression to other specs using `ensureCoachSession` / the login
      bootstrap.

## Dependencies
- **Blocked By**: —.
- **Blocks**: — (independent of 129/130/131).

## Estimated Effort
- [S]