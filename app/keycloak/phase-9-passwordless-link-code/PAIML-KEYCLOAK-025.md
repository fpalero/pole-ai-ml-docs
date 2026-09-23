# Ticket: PAIML-KEYCLOAK-025

## Title
[FUTURE] Proper token-exchange impersonation via pole-api-admin (remove hidden password)

## Description
Ticket 022 ships the first-step session fetch with a **hidden random password
+ Direct Access Grant**. That leaves one server-side secret per temp user. The
correct end state is **token exchange impersonation**: `pole_api` exchanges
its `pole-api-admin` service-account token for the temp user's session with no
stored password at all.

Why deferred, not now (decision record):
- **Unblocks the UX first.** The hidden-password grant needs no realm or client
  policy change; exchange needs token-exchange permissions + client policy
  work (infra repo) that must not gate Phase 9.
- **Contained risk until then.** The secret is per-user random, server-side
  only, never logged/emailed/returned — acceptable as an interim with this
  ticket tracking its removal.

> **Status: FUTURE — do NOT schedule for implementation now.** Implement only
> after Phase 9 (021–024) is DONE and QA-verified.

## Repository
pole-ai-ml + infra (realm/client config in `pole-ai-ml-infra`)

## What to Do (Implementation Steps)
- [ ] Enable token exchange for the `pole-api-admin` service account (realm +
  client policy in the infra repo): allow exchanging for temp users, scoped to
  the temp flow.
- [ ] Replace the hidden-password Direct Access Grant in `verify-code` with a
  token-exchange call; delete the hidden-password generation/storage path.
- [ ] Rotate/remove any stored hidden passwords from existing temp users (or
  document why remaining ones are safe to age out via the 2h purge).
- [ ] Add/extend unit + integration tests: exchange success, exchange-denied
  surfaces cleanly, no password material anywhere in logs/DB/Redis.
- [ ] `helm lint` + `helm upgrade --dry-run` for the realm/client changes;
  `pixi run test` stays ≥80% coverage.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `verify-code` issues sessions with zero stored password material for temp
  users (no secret in Redis/DB/logs).
- [ ] Exchange permissions are least-privilege (temp flow only).
- [ ] Realm/client changes pass `helm lint` + dry-run; E2E (024 matrix) still
  GREEN on the exchanged sessions.

## Integration Tests to Run (Local Verification)
- [ ] Exchange E2E: token → send-code → verify-code → session with no password
  artifact; grep Redis/DB/logs for secret leakage (none).
- [ ] Denied-exchange negative (policy off) → clean error, no session.
- [ ] Full `pixi run test` green with ≥80% coverage.

## Dependencies
- **Blocks:** None (terminal future work)
- **Blocked By:** PAIML-KEYCLOAK-022

## Estimated Effort
- [M] (Medium 3–5h)
