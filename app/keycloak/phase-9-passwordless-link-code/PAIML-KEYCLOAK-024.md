# Ticket: PAIML-KEYCLOAK-024

## Title
[QA] Mailpit E2E + hardening for the link→code flow (navigate, re-entry, expiry/purge, caps)

## Description
Phase-end QA gate for Phase 9: prove the full passwordless journey against the
local stack (Keycloak + Mailpit + test DBs) and pin the hardening rules —
re-entry asks a fresh code without extending the window, expiry still purges,
and the resend/attempt rate limits hold.

Why this gate (decision record):
- **Bearer-link risk is accepted only with proof.** The forwardable-link +
  inbox-code trade-off (see Phase 9 ADR) must be demonstrated, not assumed:
  link alone grants nothing, caps trigger, windows never stretch.
- **Regression on Phase 8.** The new keys (`temp:token`, `temp:code`) must not
  weaken the azp-mismatch close, the blind-sweeper fix, or the purge/disable
  path.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Full E2E per app against Mailpit: request (`POST
  /api/auth/temporary-access`) → link email → open `/?temp_token=xxx` →
  Validate (`send-code`) → code email → `verify-code` → session → in-app
  navigate (no re-ask) → re-entry via link (fresh code, same `ts_end`) →
  window lapse → 403 + purge (user disabled, owned data deleted, `temp:*`
  cleared, 14d `temp:req` kept).
- [ ] Hardening matrix: resend <60s → 429; 5 wrong codes → 429 until fresh
  send; expired code (10min+) → 410; cross-app token → 403; pending link past
  24h → 410.
- [ ] Phase 8 regression: azp-mismatch matrix (UC-06), empty-index sweep
  (UC-07), disable-failure visibility (UC-08).
- [ ] Record evidence (Mailpit captures, Redis key dumps, screenshots of FE
  states from 023) on the release ticket; `pixi run test` stays ≥80% coverage.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] E2E GREEN 4/4 per app: (1) request→link→code→session→entry; (2) in-app
  navigation never re-asks; (3) re-entry needs a fresh code with `ts_end`
  unchanged; (4) expiry purges + disables with evidence.
- [ ] Rate-limit/attempt tests GREEN: 60s resend 429, 5-attempt 429, expired
  code 410, cross-app 403, stale link 410.
- [ ] Phase 8 UC-06/07/08 + UC-04 still GREEN (no regression).
- [ ] Evidence bundle attached to the release ticket.

## Integration Tests to Run (Local Verification)
- [ ] Mailpit-backed E2E script (both hosts) asserting every hop above.
- [ ] Negative matrix (cooldown 429, mismatch 403, caps 429, expiries 410).
- [ ] Full `pixi run test` green with ≥80% coverage.

## Dependencies
- **Blocks:** None (phase-end gate)
- **Blocked By:** PAIML-KEYCLOAK-022, PAIML-KEYCLOAK-023

> 📌 **Scope note — this gate runs LOCALLY.** The local stack is provisioned with
> the OTP pepper, the per-app host map and the Brevo key, so a Mailpit pass here
> is valid *in the local environment* and verifies the **code path**. It does
> **not** verify any deployed environment: as of 2026-09-26 those values are
> wired in **no** environment, so dev/staging/prod answer 503 on the OTP
> endpoints. That gap is owned by
> [**Phase 10** — OTP Deploy Prerequisites](../phase-10-otp-deploy-prerequisites/)
> (tickets **026**–**029**, infra repo `pole-ai-ml-infra`); its gate ticket
> **029** is what closes it. **Do not report a green 024 run as "Phase 9
> works"** — it is "Phase 9 code works locally".

## Estimated Effort
- [M] (Medium 3–5h)
