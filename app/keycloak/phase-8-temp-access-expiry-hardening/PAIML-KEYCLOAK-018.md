# Ticket: PAIML-KEYCLOAK-018

## Title
[Keycloak] Email/owner-scoped temp identity: close the azp-mismatch enforcement bypass

## Description
Staging evidence (`ipsf-server` + staging Redis): temp user
`fpalero1986@gmail.com` enrolled via `pole-fe`
(`temp:req:fpalero1986@gmail.com:pole-fe` exists) but authenticates with a JWT
whose `azp=pole-analyst`. `_enforce_temp_access_window`
(`app/pole_api/src/core/auth.py`) calls `is_temp_user(email, app)` with the
azp-derived app, and `is_temp_user` (`app/pole_api/src/core/temp_access.py`)
only checks the exact per-app keys `temp:req/active:{email}:pole-analyst` —
both absent — so it returns `False` and the 2h window check is bypassed
entirely. The user passes on both slices even after the window expired.

Why email-scoped identity (decision record):
- **`azp` identifies the presenting client, not the enrollment.** Keying temp
  identity on the exact azp-derived app re-opens this bypass for every future
  client/enrollment combination. The temp marker must follow the owner (email)
  across all apps.
- **Role mapping stays per-app.** Only the *temp identity* lookup widens; the
  `azp`→role check (`pole-fe`→`fe-user`, `pole-analyst`→`analyst-user`) is
  unchanged, so slice isolation is preserved.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Widen `TempAccessRepository.is_temp_user` to scan `temp:req:{email}:*`
  and `temp:active:{email}:*` across ALL apps (use `SCAN`, never blocking
  `KEYS`); return `True` when any marker exists for the email.
- [ ] Apply the same email-scoped lookup in `_enforce_temp_access_window` and
  the lazy purge path (`purge_email`), so an azp↔enrollment-app mismatch
  cannot skip the 2h check or strand the lazy disable on the wrong app key.
- [ ] Keep the `email_verified` gate and the ordinary-user pass-through: an
  email with no temp markers under any app must never be rejected here.
- [ ] Keep per-app role enforcement from `azp` exactly as today.
- [ ] Add/extend unit + integration tests: enroll via `pole-fe`, present a
  verified JWT with `azp=pole-analyst` — window live → pass with
  `analyst-user`; window lapsed → 403 `TEMP_ACCESS_EXPIRED` + lazy purge fired.
  Ordinary verified non-temp user → pass.
- [ ] `pixi run test` stays ≥80% coverage; existing `test_temp_access*.py`,
  `test_auth_window_enforcement.py`, `test_temp_access_repository.py` green.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Expired temp user presenting a mismatched-`azp` JWT gets 403
  `TEMP_ACCESS_EXPIRED` (no bypass on either slice).
- [ ] Live-window temp user passes on every slice with the correct per-app role.
- [ ] Ordinary (non-temp) verified users are never rejected by this check.
- [ ] No `KEYS` usage; enumeration is `SCAN`-based.

## Integration Tests to Run (Local Verification)
- [ ] UC-06 mismatch matrix: enroll `pole-fe` × present `azp=pole-analyst`
  (and the mirror) × window live/lapsed → pass/403 as specified.
- [ ] Lazy purge fires on the 403 path and targets the email (not the
  azp-derived app key alone).
- [ ] Full `pixi run test` green with ≥80% coverage.

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-019, PAIML-KEYCLOAK-020
- **Blocked By:** None (root; builds on merged phases 1–6 enforcement)

## Estimated Effort
- [M] (Medium 3–5h)
