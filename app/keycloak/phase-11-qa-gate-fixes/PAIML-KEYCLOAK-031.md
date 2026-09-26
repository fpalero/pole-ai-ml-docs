# Ticket: PAIML-KEYCLOAK-031

## Title
[Keycloak] Purge semantics: preserve `temp:req` cooldown, clear all OTP keys

## Description
The window-lapse purge destroys the **14-day cooldown marker**, contradicting the
phase's own specification. This is the inverse of the OTP-key leak the gate
originally suspected: the purge is not under-clearing, it is **over-clearing the
one durable key it must keep**, and (separately) it may not clear the OTP keys
it should.

**Confirmed behaviour (live `k3s-local`, `PAIML-KEYCLOAK-024` gate).** After the
lapse purge, `temp_keys_for(email)` returns `[]` — `temp:req:{email}:{app}` is
**gone**.

**Why (mechanism).** The purge calls **both** `clear(email, app)` **and**
`clear_email(email)`:
- `clear()` explicitly deletes `temp:req:{email}:{app}`
  (`app/pole_api/src/core/temp_access.py`, ~lines 1011–1015).
- `clear_email()` `SCAN`s `temp:req:{email}:*`.

So the durable cooldown marker is destroyed by the design of those two helpers.

**Why that is a defect, not a doc bug.** Plan **UC-04** and ticket 024's
acceptance criterion both require the **14-day `temp:req` cooldown to be KEPT**
after purge — a temp user must be able to re-request after the cooldown lapses,
and `temp:req` is also the sweeper's self-healing enumeration path
(PAIML-KEYCLOAK-019). Deleting it silently removes the cooldown guarantee the
whole temp-access model rests on.

**Open question this ticket must close (verify, then fix).** The tester could
not finish reading `_clear_redis_state` before the run was cut off, so the OTP
half is **strongly indicated but not code-conclusive**: confirm whether the sweep
covers the post-022 key families `temp:code:*` and `temp:code-resend:*`. The
current sweep is understood to cover `temp:active*` / `temp:token*` /
`temp:req*` / `temp:session*`. If `temp:code*` is not covered, an inbox-bound
credential hash survives expiry — add it.

**Net required semantics:** preserve `temp:req` (14d) · clear all
`temp:code:*` / `temp:code-resend:*` · clear `temp:active` / `temp:token` /
`temp:session` · disable the user · purge owned data.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Read `_clear_redis_state` in
  `app/pole_api/src/core/temp_access_purge.py` and `clear` / `clear_email` in
  `app/pole_api/src/core/temp_access.py`; confirm the exact key families each
  touches **before** editing.
- [ ] Make the lapse purge **preserve** `temp:req:{email}:{app}` with its
  **remaining** 14-day TTL (do not re-set it to a fresh 14d — preserve the
  residual).
- [ ] Ensure **all** `temp:code:*` and `temp:code-resend:*` for the email are
  **removed** on purge (confirm the sweep covers them; add them if not).
- [ ] Keep `temp:active` / `temp:token` / `temp:session` clearing, user disable,
  and owned-data purge **unchanged**.
- [ ] Add a regression test that pins **`temp:req` survival** (with residual
  TTL) **and** OTP-key removal.
- [ ] Keep `pixi run test` at ≥80% coverage.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] After a lapse purge, `temp:req:{email}:{app}` **still exists** with its
  remaining 14-day TTL.
- [ ] All `temp:code:*` and `temp:code-resend:*` for the email are **removed**.
- [ ] `temp:active` / `temp:token` / `temp:session` are cleared; the Keycloak
  user is disabled; owned data is purged.
- [ ] A regression test pins `temp:req` survival **and** OTP-key removal, and
  **fails against the pre-fix code**.
- [ ] `pixi run test` green, ≥80% coverage.

## Integration Tests to Run (Local Verification)
- [ ] Purge a temp user whose `temp:req` has, say, 9 days left; assert the key
  survives with ~9 days TTL (not reset to 14).
- [ ] Seed `temp:code:{hash}` + `temp:code-resend:{email}:{app}`; purge; assert
  both are gone.
- [ ] Assert `temp:active` / `temp:token` / `temp:session` are gone and the
  user is disabled.
- [ ] Pre-fix bite check: revert the preserve-`temp:req` change, confirm the new
  regression test goes RED.
- [ ] Full `pixi run test` green with ≥80% coverage.

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-024 (its re-run)
- **Blocked By:** None (independent of 030; different call site, same purge/gate surface)

## Estimated Effort
- [S] (Small 2–3h)

> **Cross-reference:** PAIML-KEYCLOAK-019 (sweeper self-healing enumeration path),
> PAIML-KEYCLOAK-024 (the QA gate that surfaced this), and PLAN.md **UC-04**
> ("the 14-day `temp:req` cooldown remains").
