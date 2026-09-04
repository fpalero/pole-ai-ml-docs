# Plan Phase 8 — Temp-Access Expiry Hardening (azp-mismatch + blind-sweeper fix)

> **Parent plan:** [PLAN.md](../PLAN.md)
> **Status:** 📋 PLANNED
> **Class:** BE-only (`pole_api`, repo `pole-ai-ml`). No Keycloak realm/theme,
> Helm, or FE changes. Plus one ops runbook step (no code).

## Scope

Harden the already-merged temp-access enforcement (phases 1–6,
PAIML-KEYCLOAK-005/006/007/009/010) against two compounding gaps found live on
staging (`ipsf-server`): a per-app key-scoping bypass that lets an expired temp
user keep access when the JWT `azp` differs from the enrollment app, and a
sweeper that can only see expiries via a Redis index that is empty in practice.
Defense in depth across three code tickets (018/019/020) plus an operational
cleanup step after deploy. No new endpoints, no contract changes.

## Context

The temp user `fpalero1986@gmail.com` on staging keeps access to
pole-fe/pole-analyst after the 2h window expired. Verified against staging
Redis/`ipsf-server`:

- **GAP 1 — per-app key scoping vs `azp` mismatch (enforcement bypass).** The
  user enrolled via `pole-fe` (Redis `temp:req:fpalero1986@gmail.com:pole-fe`
  exists), but authenticates with a JWT whose `azp=pole-analyst`. Enforcement
  `_enforce_temp_access_window` in `app/pole_api/src/core/auth.py` calls
  `is_temp_user(email, app)` with the azp-derived app, and `is_temp_user`
  (`core/temp_access.py`) only checks the exact per-app keys
  `temp:req/active:{email}:pole-analyst` — both absent — so it returns `False`
  and the 2h window check is bypassed entirely. The user passes on both slices.
- **GAP 2 — sweeper is blind (user never disabled).** `purge_expired()` in
  `core/temp_access_purge.py` discovers expired windows ONLY via the Redis
  `temp:active-index` SET, which is EMPTY (`SCARD = 0`) on staging. The sweeper
  iterates over nothing and never disables the Keycloak user. Because the user
  stays `enabled`, Keycloak keeps issuing fresh tokens on every login. Several
  stale probe temp users are also un-purged in Redis, confirming the sweep is
  broken generally, not just for this one user.

Why email/owner-scoped identity plus index-independent enumeration (decision
record):

- **Identity must follow the owner, not the presenting slice.** `azp` tells
  which client the token was minted for, not which app enrolled the email. Any
  check keyed on the exact azp-derived app re-opens the bypass for every
  future client/enrollment combination. Scanning `temp:{req,active}:{email}:*`
  across all apps closes the whole class.
- **The sweeper must not trust a single derived index.** The index is
  write-path state: if activation never populated it (or it was lost), expiry
  discovery silently degrades to zero. Enumerating from the durable
  `temp:req:{email}:*` markers (present + no live window + no valid pending
  token) makes the sweep self-healing; repairing index maintenance removes the
  original hole.
- **Silent purge failures are data-loss-adjacent.** The lazy path in
  `_enforce_temp_access_window` swallows purge errors with a bare `pass`, and
  sweeper logging drowns in the health-check flood — so Gap 2 stayed invisible.
  Reliable disable + survivable diagnostics are part of the fix, not garnish.

## Redis keys

| Key | Value | TTL | Purpose |
| :-- | :-- | :-- | :-- |
| `temp:req:{email}:{app}` | `1` | 14 days | Cooldown marker — also the durable enrollment record the hardened sweeper enumerates from |
| `temp:token:{hash}` | `{email, app, state: pending}` | 24h | Magic-link token state until first use |
| `temp:active:{email}:{app}` | `{app, ts}` | 2 hours | Activated window — expiry signal |
| `temp:active-index` | SET of `"{email}:{app}"` | — | Fast-path sweep discovery (repaired maintenance; NO LONGER the sole source) |

New behavior scans `temp:req:{email}:*` / `temp:active:{email}:*` (all apps for
the email) instead of only the exact azp-derived app key.

## Tasks

### Ticket 018 — Gap A: email/owner-scoped enforcement identity (root)

- [ ] [Application] Make `is_temp_user`, window enforcement
  (`_enforce_temp_access_window`), and the lazy purge key off the email across
  ALL apps (scan `temp:{req,active}:{email}:*`), not just the exact
  azp-derived app key, so an azp↔enrollment-app mismatch cannot bypass the 2h
  check. Non-temp users (no markers for the email under any app) must still
  pass untouched.
- [ ] [Application] Keep per-app role mapping (`pole-fe`→`fe-user`,
  `pole-analyst`→`analyst-user`) enforced from `azp` as today — only the
  *temp identity* lookup widens, not the role check.
- [ ] [Tests] azp-mismatch regression: enroll via `pole-fe`, present a verified
  JWT with `azp=pole-analyst` after window expiry → 403 `TEMP_ACCESS_EXPIRED`;
  while window live → pass. Full details in `phase-8-temp-access-expiry-hardening/PAIML-KEYCLOAK-018.md`.

### Ticket 019 — Gap B: robust sweeper enumeration + index maintenance

- [ ] [Application] Stop relying solely on `temp:active-index`: enumerate
  expiry candidates from `temp:req:{email}:*` present + no live
  `temp:active:{email}:*` window + no valid pending `temp:token:*`, and purge
  those. Repair index population/maintenance so the fast path works again.
- [ ] [Tests] Sweeper purges an expired window with the index EMPTY; index
  membership is re-populated on activation. Full details in
  `phase-8-temp-access-expiry-hardening/PAIML-KEYCLOAK-019.md`.

### Ticket 020 — Gap C: reliable Keycloak disable + diagnostics

- [ ] [Application] Ensure the purge reliably disables the Keycloak user and
  surfaces errors instead of silently swallowing them (the lazy path's bare
  `pass` on purge failure goes away in favor of logged, observable failure).
- [ ] [Application] Add sweeper/purge logging that survives the health-check
  log flood (distinct logger/prefix, failure always logged with email+app).
- [ ] [Tests] Disable-failure and logging assertions. Full details in
  `phase-8-temp-access-expiry-hardening/PAIML-KEYCLOAK-020.md`.

### Ops step D — staging cleanup (runbook, no code-in-repo)

- [ ] [Ops] After deploy to staging: purge the currently-affected temp user
  (`fpalero1986@gmail.com`) plus the stale probe temp users, then verify: user
  `enabled=false` via Keycloak Admin API, `temp:active:*` keys gone, fresh
  login issues no usable session past the window, and `temp:active-index`
  re-populated on the next activation. Record evidence on the release ticket.

## Integration test use cases

- **UC-06 (new): azp↔enrollment mismatch is rejected after expiry.** Given
  `temp:req:{email}:pole-fe` present and window lapsed, when a verified request
  arrives with `azp=pole-analyst`, then `pole_api` returns 403
  `TEMP_ACCESS_EXPIRED` (and fires the lazy purge). While the window is live,
  the same request passes with the `analyst-user` role.
- **UC-07 (new): sweeper purges with an empty index.** Given an expired window
  and `SCARD temp:active-index = 0`, when `purge_expired()` runs, then the
  Keycloak user is disabled, owned data purged, and residual `temp:*` keys
  cleared.
- **UC-08 (new): purge failure is visible and retried.** Given Keycloak admin
  disable fails (e.g. simulated 500), when the purge runs, then the failure is
  logged with email+app (not swallowed) and the next sweep/lazy trigger
  completes the disable.
- **UC-04 (regression):** expiry still purges owned data and disables the user
  on the enrollment app path; 14-day `temp:req` cooldown preserved.

## Dependencies

- Phases 1–6 enforcement (PAIML-KEYCLOAK-005/006/007/009/010): `core/auth.py`
  hook, `TempAccessRepository`, `TempAccessPurgeService`, sweeper loop.
- Ticket order inside this phase: 018 is the root fix and blocks 019 and 020;
  019 and 020 are independent of each other.
- `settings.redis_url` and the in-cluster Redis; Keycloak `pole-api-admin`
  service account (unchanged).

## Acceptance Criteria

- [ ] An expired temp user is rejected (403) regardless of which app's `azp`
  the presented JWT carries; a live window still passes on every slice.
- [ ] `purge_expired()` disables expired users even when `temp:active-index`
  is empty; the index is re-populated on activation.
- [ ] Purge/disable failures are logged with email+app (no bare-`pass`
  swallowing); sweeper diagnostics are findable despite health-check noise.
- [ ] Unit + integration tests cover UC-06/07/08; `pixi run test` stays ≥80%
  coverage; existing suites (`test_temp_access*.py`,
  `test_auth_window_enforcement.py`, `test_temp_access_purge.py`,
  `test_temp_access_repository.py`) stay green.
- [ ] Ops step D verified on staging with recorded evidence.

## Risks and Mitigations

- **Risk:** Widening the identity lookup falsely flags ordinary users as temp
  (403 for real users). **Mitigation:** markers only exist when the email went
  through the temp flow; keep the `email_verified` gate; regression-test that
  ordinary verified users pass.
- **Risk:** `KEYS`/`SCAN` enumeration is heavy on a big Redis. **Mitigation:**
  enumerate via `SCAN` with a narrow `temp:req:*` match (bounded temp-user
  population), not `KEYS`; keep the index as the fast path.
- **Risk:** Emails contain `:` rarely — index member split must stay
  last-colon split. **Mitigation:** reuse the existing `rpartition` parsing;
  cover with a unit test.
- **Risk:** Louder purge logging re-floods logs. **Mitigation:** log successes
  at debug, failures at error with a distinct prefix; no per-request info spam.
