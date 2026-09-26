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
- **Blocked By:** PAIML-KEYCLOAK-022, PAIML-KEYCLOAK-023, PAIML-KEYCLOAK-030, PAIML-KEYCLOAK-031

> 🔴 **GATE RAN 2026-09-26 — VERDICT: RED.** Two P1 defects blocked the pass, both
> now ticketed in **Phase 11** (`phase-11-qa-gate-fixes/`) and both blocking this
> gate's re-run:
> - **PAIML-KEYCLOAK-030** (BLOCKER) — `verify-code` Direct Access Grant returns
>   `400 invalid_grant "Account is not fully set up"` on a clean environment
>   because the realm-required `firstName`/`lastName` are not set at creation;
>   the endpoint answers `502` on both apps. Also: reused disabled accounts.
> - **PAIML-KEYCLOAK-031** — the lapse purge deletes the durable 14-day
>   `temp:req` cooldown marker, contradicting this ticket's own acceptance
>   criterion and PLAN.md UC-04.
>
> **Gate matrix at RED:**
> | Gate | Result |
> | :--- | :--- |
> | 1a E2E request→link→code→session→window (per app) | ✅ PASS *(only behind a local shim for DEFECT-01)* |
> | 1b in-app navigation never re-asks | ✅ PASS |
> | 1c re-entry fresh code, `ts_end` unchanged | ✅ PASS (18/18) |
> | 1d window lapse → 403 + purge | ⚠️ PARTIAL (`temp:req` deleted — 031) |
> | 2 rate-limit / attempt matrix | ⛔ NOT RUN |
> | 3 Phase 8 no-regression UC-06/07/08 + UC-04 | ⛔ NOT RUN (UC-04 failing — 031) |
> | 4 `pixi run test` ≥80% | ⛔ NOT RUN |
> | 5 evidence bundle | ⚠️ PARTIAL (no FE screenshots) |
>
> **Evidence root:** `/tmp/opencode/qa-024/evidence/`
> (`DEFECT-01-direct-access-grant-400.md`, `brevo-captures-*.json`,
> `redis-gate1*-*.txt`, `gate1a-state.json`, `gate1c-pinned.json`, `403-body.json`).
> **QA harness (not committed):** `/tmp/opencode/qa-024/` + `QA_SECRETS.txt`.
>
> ⚠️ **Interim-report caveat.** An earlier, truncated QA output claimed re-entry
> *extended* the 2h window. The final run did **not** reproduce it — `ts_end`
> was byte-identical and the pinned case passed 18/18. That claim is **not** an
> open defect.

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
