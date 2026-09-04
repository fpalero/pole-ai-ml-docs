# Ticket: PAIML-KEYCLOAK-019

## Title
[Keycloak] Index-independent sweeper: enumerate expiries from durable markers + repair index maintenance

## Description
Staging evidence: `purge_expired()` (`app/pole_api/src/core/temp_access_purge.py`)
discovers expired windows ONLY via the Redis `temp:active-index` SET
(`TempAccessRepository.list_active_keys` → `SMEMBERS temp:active-index`), which
is EMPTY (`SCARD = 0`) on staging. The sweeper iterates over nothing, so it
never disables the Keycloak user — and because the user stays `enabled`,
Keycloak keeps issuing fresh tokens on every login. Several stale probe temp
users are also un-purged in Redis, confirming the sweep is broken generally.
The index is write-path derived state: whatever prevented its population (or
lost it) silently degrades expiry discovery to zero.

Why enumerate from durable markers (decision record):
- **The index is a cache, not the source of truth.** The durable enrollment
  record is `temp:req:{email}:{app}` (14d TTL); an expiry candidate is
  `temp:req` present + no live `temp:active:{email}:*` window + no valid
  pending `temp:token:*`. Deriving candidates from durable keys makes the sweep
  self-healing.
- **Keep the index as the fast path, but repair it.** Fix population on
  activation (and audit `clear()` removal) so the cheap `SMEMBERS` discovery
  works again — while never trusting it alone.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Extend `purge_expired()` (or the sweeper candidate discovery in
  `app/pole_api/src/core/temp_access_purge.py` /
  `app/pole_api/src/core/temp_access_sweeper.py`) to also enumerate candidates
  from `temp:req:{email}:*` (via `SCAN`): purge when no live
  `temp:active:{email}:*` window exists for the email and no valid pending
  `temp:token:*` remains. Union with (not replacement of) the index fast path.
- [ ] Fix `temp:active-index` maintenance: ensure activation adds the
  `"{email}:{app}"` member and `clear()`/purge removes it; cover the
  last-colon `rpartition` parsing with a unit test (emails may contain `:`).
- [ ] Keep the purge idempotent and per-user-failure isolated (one failing user
  never aborts the sweep — existing behavior, add a regression test).
- [ ] Add/extend unit + integration tests: expired window + EMPTY index →
  user disabled + owned data purged + residual `temp:*` cleared; activation
  re-populates the index. Existing `test_temp_access_purge.py` green.
- [ ] `pixi run test` stays ≥80% coverage.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `purge_expired()` disables expired temp users with `temp:active-index`
  empty (index no longer a single point of failure).
- [ ] Activation populates the index; purge/clear removes the member (fast
  path works again).
- [ ] One user's purge failure does not abort the sweep (regression-tested).
- [ ] Enumeration uses `SCAN`, never blocking `KEYS`.

## Integration Tests to Run (Local Verification)
- [ ] UC-07: seed expired window, flush the index (`DEL temp:active-index`),
  run `purge_expired()` → user disabled, data purged, keys cleared.
- [ ] Index round-trip: activate → `SISMEMBER temp:active-index` true; purge →
  member gone.
- [ ] Full `pixi run test` green with ≥80% coverage.

## Dependencies
- **Blocks:** None
- **Blocked By:** PAIML-KEYCLOAK-018

## Estimated Effort
- [M] (Medium 3–5h)
