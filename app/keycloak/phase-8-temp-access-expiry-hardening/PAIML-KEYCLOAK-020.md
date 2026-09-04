# Ticket: PAIML-KEYCLOAK-020

## Title
[Keycloak] Reliable Keycloak disable + purge diagnostics that survive the log flood

## Description
Staging evidence: even where the purge is reached, failures are invisible. The
lazy path in `_enforce_temp_access_window`
(`app/pole_api/src/core/auth.py`) wraps `purge.purge_email(email, app)` in a
bare `except Exception: pass` ("never block the request on purge failures"),
so a failed Keycloak disable leaves the user `enabled` with zero trace — and
Keycloak then keeps issuing fresh tokens on every login. Sweeper-side logging
exists but drowns in the health-check log flood, which is how Gap 2 (empty
`temp:active-index`, stale probe users never purged) stayed undetected.

Why observable disable (decision record):
- **Best-effort must still be observable.** Never blocking the request is
  correct; swallowing the failure is not. A logged, email+app-tagged error
  turns the next sweep/lazy trigger into a retry with a trail.
- **Diagnostics must be findable under noise.** A distinct logger/prefix for
  temp-access purge events (success at debug, failure at error) keeps the
  signal retrievable without re-flooding the logs.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Replace the bare `pass` on lazy-purge failure in
  `_enforce_temp_access_window` with an error log carrying email+app (request
  still returns the 403 `TEMP_ACCESS_EXPIRED` — behavior unchanged, now
  observable).
- [ ] Ensure `_purge_one`/`purge_email` in
  `app/pole_api/src/core/temp_access_purge.py` reliably disables the Keycloak
  user via the `pole-api-admin` service account and propagates/reports a
  failed disable (no silent success); keep per-user isolation in
  `purge_expired()`.
- [ ] Give sweeper/purge events a distinct logger/prefix so they survive the
  health-check flood: success at debug, failure at error with email+app (and
  the Keycloak admin error where available). No per-request info spam.
- [ ] Add/extend unit + integration tests: simulated admin-disable 500 →
  error logged with email+app, request still 403s, next sweep/lazy trigger
  completes the disable. Existing `test_temp_access_purge.py`,
  `test_auth_window_enforcement.py` green.
- [ ] `pixi run test` stays ≥80% coverage.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] No bare-`pass` swallowing on the lazy purge path; every disable failure
  is logged with email+app.
- [ ] A failed disable is retried to completion by the next sweep/lazy trigger
  (no permanently half-purged user).
- [ ] Purge/sweeper log lines are greppable under health-check noise (distinct
  prefix; failures at error level).

## Integration Tests to Run (Local Verification)
- [ ] UC-08: inject Keycloak admin 500 on disable → error log with email+app
  asserted; clear the fault → next sweep disables the user.
- [ ] Log inspections: success path emits debug only; failure path emits error
  with the distinct prefix.
- [ ] Full `pixi run test` green with ≥80% coverage.

## Dependencies
- **Blocks:** None
- **Blocked By:** PAIML-KEYCLOAK-018

## Estimated Effort
- [S] (Small 1–2h)
