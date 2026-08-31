# Ticket: PAIML-POLE-ANALYST-028

## Title
[Infrastructure] Keycloak OIDC auth (deferred, last phase)

## Description
Add Keycloak-based authentication/authorization in a later iteration: OIDC login, an auth
interceptor adding `Authorization: Bearer`, and per-user video library scoping. **Deferred — not
in the first iteration.**

## What to Do (Implementation Steps)
- [ ] Integrate OIDC login (Keycloak) into the shell.
- [ ] Add an auth interceptor (`Authorization: Bearer`) to `ApiClient`.
- [ ] Scope the library/list endpoints to the authenticated user.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Login flow works; authenticated requests carry the bearer token; library is per-user.

## Integration Tests to Run (Local Verification)
- [ ] Manual: login → library scoped to the user; unauthorized → redirect to login.

## Dependencies
- **Blocks**: —
- **Blocked By**: PAIML-POLE-ANALYST-001, PAIML-POLE-ANALYST-002

## Estimated Effort
- [L]
