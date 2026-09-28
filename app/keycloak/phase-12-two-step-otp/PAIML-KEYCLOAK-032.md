# Ticket: PAIML-KEYCLOAK-032

## Title
[Keycloak / pole_api] Make `send-code` idempotent inside the 60s resend cooldown: `already_sent` 200 instead of 429 when a live code is armed

## Description
**Phase 12 is a UX-hardening phase, not a build phase.** The two-step OTP
handshake is already implemented and green (Phase 9): `POST
/api/auth/temporary-access/send-code` and `/verify-code` exist in
`app/pole_api/src/auth/controllers/temporary_access.py`; the 10-minute code TTL
(`TEMP_ACCESS_OTP_TTL_S`), single-use consumption (`repo.delete_code`),
prior-code invalidation (same `temp:code:{token}` key), the 5-attempt cap and
the 60s resend cooldown (`SETNX` on `temp:code-resend:{email}:{app}`) all live
in `app/pole_api/src/core/temp_access.py` and `app/pole_api/src/core/otp.py`
(PAIML-KEYCLOAK-021/-022). **None of that is in scope here** — it must not be
re-implemented, re-planned or re-tested as new work.

**The single gap this ticket closes is the backend half of the auto-send
requirement (decision B2, user-confirmed).** Phase 12 makes the code email
itself the moment the verification page loads, which turns an ordinary
accidental page refresh into a `send-code` call. Today that refresh is
punished: `claim_resend_slot` returns `False` inside the 60s window, so
`send_access_code` answers **429**, and the auto-send frontend
(PAIML-KEYCLOAK-033) would land the user on a "please wait before requesting
another code" error screen instead of the code entry they are supposed to see
— on a flow where **a perfectly valid code is already sitting in their inbox**.

That answer is also wrong on its own terms. A 429 tells the user "no code is
out there", when in fact one is armed, delivered and valid for up to 10 more
minutes. The state the client actually needs to render is "a code was already
sent and it is still good for N more seconds".

**Required behaviour (decision B2).** When the resend slot cannot be claimed
BUT a valid armed code already exists for that `temp_token` (the
`temp:code:{token}` key is present and has not passed its 10-minute TTL), return
**200** with `already_sent: true` and the code's **remaining** lifetime in
`expires_in`. No second email, no Brevo call, no new code minted, no attempt
counter touched. The client then simply shows the code step.

**The 429 must survive.** It is the correct answer for two distinct callers and
this ticket must not weaken either:

1. **The explicit "Resend code" click**, where no live code is armed (the user
   already burned theirs, it lapsed, or the attempts cap locked it) — there is
   genuinely nothing to fall back on and the user asked for a new email.
2. **The fall-back case for the auto-send path** — inside the cooldown with *no*
   live code (e.g. a Brevo failure rolled the record back but the slot claim
   was not released, or the code's own 10 minutes lapsed while a stale
   resend key survived). Silently answering `already_sent: true` with no code
   behind it would send the user to a code screen that can never be satisfied.

**Security note — why only the TTL is readable.** `store_code` persists a
**peppered SHA-256 digest**, never the plaintext, so the repository can report
"a live code exists and has N seconds left" but can never report the code
itself. The fallback response therefore leaks exactly one bit of information
that the caller already had (they possess the `temp_token` and therefore could
have triggered a send anyway) — the code itself remains unreachable. **Do not
relax this to make the implementation easier**; there is no need to, and a
recoverable code from a Redis dump is precisely what `core.otp` exists to
prevent.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Add `already_sent: bool = False` to `SendCodeResponse` in
  `app/pole_api/src/auth/controllers/temporary_access.py`. Default `False`
  keeps the field additive and backward compatible: any caller that ignores it
  (including the current `pole_fe` / `pole_analyst` builds) is unaffected.
- [ ] Add a repository helper in `app/pole_api/src/core/temp_access.py`, next
  to `get_code` / `delete_code` and following the same conventions (typed
  accessor, `temp:code:{token}` layout encapsulated, docstring stating what is
  and is not readable), that returns the live code record's **remaining TTL** in
  seconds — e.g. `code_remaining_ttl(token) -> int | None`:
  - `None` when no `temp:code:{token}` record exists (never sent, consumed, or
    the 10-minute TTL already lapsed and Redis removed the key);
  - `0` or a non-positive/None-equivalent when the record exists but its
    remaining lifetime is spent — the endpoint must treat "expired" and
    "absent" identically, so decide one representation and pin it in a test;
  - the positive remaining seconds otherwise. It must read the key's TTL, never
    reconstruct one from `settings.otp_code_ttl_s` (a re-`store_code` resets the
    clock; the TTL is the only honest source). Keep the same "unreadable state
    is indistinguishable from absent" posture as `get_code`, so a probe cannot
    use this helper to enumerate links.
- [ ] In `send_access_code`, restructure the resend-slot branch: when
  `claim_resend_slot(email, app)` returns `False`, consult
  `code_remaining_ttl(body.temp_token)` **before** raising. If a live code is
  found, return `200` with `already_sent=True` and `expires_in` set to that
  remaining lifetime (override the `default_factory` value — the fresh-code TTL
  would overstate what the user actually has). **Do not** build a
  `BrevoEmailSender`, do not mint a code, do not call `store_code`, and do not
  touch the attempts counter. Log the reuse distinctly (a `logger.info` on the
  `already_sent` path) so a 200 that sent nothing is still diagnosable.
- [ ] Keep the **429 branch intact and reachable**: no live code ⇒ raise
  `HTTPException(429)` with the existing `Retry-After` from
  `repo.resend_remaining`, exactly as today. The explicit resend path must be
  unchanged.
- [ ] Update the endpoint docstring to state the new contract (200
  `already_sent: true` for a page refresh inside the cooldown; 429 only when
  there is nothing live to fall back on), so the OpenAPI-facing description and
  the behaviour cannot drift.
- [ ] Unit tests in `app/pole_api/tests/` (extend the existing temp-access /
  OTP endpoint suite — do **not** start a new parallel test module):
  - fresh send ⇒ `already_sent: false`, Brevo called once, a code record stored;
  - repeat inside 60s **with** a live code ⇒ `200`, `already_sent: true`,
    `expires_in` == the record's remaining TTL, and **no** Brevo call and no
    second `store_code` (assert the sender/`send_code` was not invoked — that
    assertion is the real regression guard);
  - repeat inside 60s **without** a live code (record deleted / TTL lapsed) ⇒
    `429` with `Retry-After` still present, and `already_sent` never leaked;
  - Brevo failure still rolls back the code record **and** releases the resend
    slot (the pre-existing rollback must not regress);
  - the 404 / 410 / 403 link gates and the missing-pepper 503 are unaffected by
    the new branch (cheap guards against a reordered precondition).
- [ ] Keep `pixi run test` green with ≥80% coverage on the modified files.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `send-code` returns `200` with `already_sent: true` and the **remaining**
  `expires_in` when a valid armed code exists for the token and the 60s slot is
  taken.
- [ ] That path sends **no** email, mints no new code, and does not reset the
  attempt counter (proved by an assertion on the Brevo sender, not by comment).
- [ ] `send-code` still returns `429` with `Retry-After` when the slot is taken
  and there is no live code — i.e. the explicit "Resend code" button behaves
  exactly as before.
- [ ] The response never contains the code, a token, or anything that makes the
  stored digest recoverable.
- [ ] `code_remaining_ttl` is covered directly (absent / expired / live) in the
  repository's own test file.
- [ ] The new tests **fail against the pre-change code** (verified by reverting
  the change locally — the `already_sent` test must go RED).
- [ ] `pixi run test` green, ≥80% coverage.

## Integration Tests to Run (Local Verification)
- [ ] Send → wait ~5s → send again on the same `temp_token`: expect
  `200 {already_sent: true, expires_in: <≈595>}` and exactly **one** email in
  the Brevo/Mailpit capture.
- [ ] Send → delete `temp:code:{token}` (simulating a consumed code) → send
  again inside 60s: expect `429` + `Retry-After`.
- [ ] Send → wait out the 10-minute TTL (or re-seed the key with a spent TTL) →
  send again inside the resend window: expect `429`, not a false
  `already_sent: true`.
- [ ] Send → wait out the 60s → send again: expect a genuinely fresh
  `200 {already_sent: false}` and a second email (the normal resend still works).
- [ ] Full `pixi run test` green with ≥80% coverage.

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-033, PAIML-KEYCLOAK-035
- **Blocked By:** PAIML-KEYCLOAK-030, PAIML-KEYCLOAK-031

## Estimated Effort
- [S] (Small 2–3h)

> **Cross-reference:** PAIML-KEYCLOAK-021 / -022 (the `send-code` / `verify-code`
> endpoints, the 10-min TTL, single-use, attempt cap and 60s cooldown this
> ticket *adjusts* — all already implemented), PAIML-KEYCLOAK-023 (the
> `/activate` pages and `ActivationFlow` this ticket serves), PAIML-KEYCLOAK-030
> / -031 (Phase 11 QA-gate fixes on the same temp-access surface),
> [ADR-007](../../decisions/ADR-007-temp-access-link-reuse-and-audit-retention.md)
> (Decision 3 — the 60s resend cooldown is the *short* clock; the 14-day
> re-request cooldown is a different one), and
> [PLAN_PHASE_12.md](../../plan/PLAN_PHASE_12.md) (decision **B2**).
