# Ticket: PAIML-KEYCLOAK-002

## Title
[Keycloak] Add confidential `pole-api-admin` client (service account) for user management

## Description
Create a confidential `pole-api-admin` client whose service account can create/disable users, set the `VERIFY_EMAIL` required action, and trigger execute-actions-email — so `pole_api` never stores the `fernando` admin password. Grant the service account `realm-management` client roles `manage-users` and `view-users`. Expose the client id/secret to the `pole-api` pod as env/Secret.

## What to Do (Implementation Steps)
- [ ] Add client `pole-api-admin` (confidential, service-account enabled, direct access grants off) to `realm-pole-ai.json` and the Helm realm `configmap.yaml`
- [ ] Grant the service account `realm-management` client roles: `manage-users`, `view-users`
- [ ] Persist the client secret in a Helm Secret (keycloak/pole-api)
- [ ] Add `KEYCLOAK_ADMIN_CLIENT_ID` / `KEYCLOAK_ADMIN_CLIENT_SECRET` env to the `pole-api` configmap/secret
- [ ] Add `keycloakAdminClientId`/`keycloakAdminClientSecret` values to `helm/pole-ai/charts/pole-api/values.yaml`

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pole-api-admin` exists and its service account can create/disable users and trigger execute-actions-email
- [ ] Secret stored via Helm, not in the realm JSON
- [ ] `pole-api` pod receives the client id/secret via env

## Integration Tests to Run (Local Verification)
- [ ] With an admin token from the service account, create a user and send a verify-email

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-005, PAIML-KEYCLOAK-008
- **Blocked By:** None

## Estimated Effort
- [M] (Medium 1–2h)