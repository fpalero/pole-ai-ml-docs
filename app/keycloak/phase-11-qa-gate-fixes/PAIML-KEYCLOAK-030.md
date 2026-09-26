# Ticket: PAIML-KEYCLOAK-030

## Title
[Keycloak] Fix `verify-code` Direct Access Grant: required `firstName`/`lastName` + reuse of disabled temp accounts

## Description
`POST /api/auth/temporary-access/verify-code` fails on a **clean** environment.
After the 6-digit code is verified, `pole_api` fetches the Keycloak session via
the hidden-password **Direct Access Grant**. That grant is refused with
`400 invalid_grant "Account is not fully set up"`, so the endpoint returns
`502 {"detail":"Could not start a session — please try again"}` — **100% of the
time, on both apps, on a freshly provisioned realm**. The failure happens
**after** the single-use code has already been consumed, so the user cannot even
retry with the same link.

**Root cause (confirmed on live `k3s-local`).** The realm's user-profile policy
marks `firstName` and `lastName` as **required**
(`required: {"roles":["user"]}`). `KeycloakAdminClient.create_or_find_user`
(`app/pole_api/src/core/temp_access.py`) posts only
`username`/`email`/`emailVerified`/`enabled`/`credentials` — no name fields. With
the profile policy unsatisfied, Keycloak refuses the password grant even though
`requiredActions` is `[]`.

**Isolation (single variable).** Same user, same password: adding **only**
`firstName` + `lastName` flips the grant from `400 "Account is not fully set up"`
to `200 + access_token`. The name fields are the whole defect.

**Secondary defect at the same call site.** A purged temp user is **disabled**.
A subsequent request for the same email reuses that disabled account as-is, so
the grant fails again. The fix must decide — and justify — whether a re-request
**re-enables** the existing account or **rotates** it.

**Why 022's suite missed it (decision record).**
`test_temp_access_session_grant.py` and the OTP suites assert the *call
sequence* with the Keycloak client **stubbed**. No test performs a **real**
password grant against a **live** realm, so a realm-policy mismatch was
invisible to a green suite. This ticket must close that class of gap, not just
the one field: a stubbed sequence test cannot prove a grant works.

**Evidence.** `/tmp/opencode/qa-024/evidence/DEFECT-01-direct-access-grant-400.md`
(full repro + isolation), produced by the `PAIML-KEYCLOAK-024` QA gate run on
2026-09-26.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Add `firstName` / `lastName` to the create payload in
  `KeycloakAdminClient.create_or_find_user`. Derive them from the email
  local-part (a display value only — temp users are never shown a name form),
  so every created user satisfies the realm profile policy.
- [ ] Preserve `firstName` / `lastName` on the `set_email_verified` `PUT` (a
  representation update that omits required fields can itself trip the profile
  policy).
- [ ] Handle the **reused disabled account** case on re-request: choose
  re-enable-vs-rotate, implement it, and record the choice in the close-out
  with its trade-off (a re-enabled account is cheaper; a rotated account avoids
  inheriting a stale credential — either is defensible, but it must be decided
  and tested, not left implicit).
- [ ] Replace the stubbed-only grant coverage with a **live-realm** Direct
  Access Grant integration test: create a temp user through the real admin
  client against a real realm, then perform a real password grant and assert
  `200 + access_token`. The test must **fail against the pre-fix code**.
- [ ] Keep `pixi run test` at ≥80% coverage.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `verify-code` returns `200` with a usable session on a **fresh clean
  environment with no local shim**.
- [ ] `firstName` / `lastName` are present in the create payload and preserved
  by `set_email_verified`.
- [ ] The reused-disabled-account case is handled and covered by a test, with
  the re-enable-vs-rotate decision recorded.
- [ ] A **real** Direct Access Grant integration test exists and **fails
  against the pre-fix code** (verified by reverting the fix locally).
- [ ] `pixi run test` green, ≥80% coverage.

## Integration Tests to Run (Local Verification)
- [ ] Live-realm grant: create temp user via the real admin client → real
  password grant → `200 + access_token` (no shim, fresh realm state).
- [ ] Fresh-user regression: `verify-code` end-to-end returns `200` on a clean
  environment.
- [ ] Reused-disabled-account: purge/disable a temp user, re-request the same
  email, assert the grant succeeds per the chosen strategy.
- [ ] Pre-fix bite check: revert the name-field change, confirm the new live
  grant test goes RED (proves the test is not vacuous).
- [ ] Full `pixi run test` green with ≥80% coverage.

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-024 (its re-run)
- **Blocked By:** None (a fix on the merged 022 call site; no in-flight blockers)

## Estimated Effort
- [M] (Medium 3–5h)
