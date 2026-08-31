# Ticket: PAIML-KEYCLOAK-012

## Title
[Documentation] Temp-access docs: Keycloak README, ENV_VARS, project docs

## Description
Document the temporary-access feature and configuration so the stack is operable and auditable.

## What to Do (Implementation Steps)
- [ ] Update `infrastracture/keycloak/README.md` — SMTP, `pole-api-admin` client, custom theme, 2h lifespan, temp-access flow
- [ ] Update `docs/ENV_VARS.md` — new `pole_api` variables: `KEYCLOAK_ADMIN_CLIENT_ID`, `KEYCLOAK_ADMIN_CLIENT_SECRET`, `KEYCLOAK_ADMIN_ISSUER`, `TEMP_ACCESS_*`
- [ ] Update this project's `PLAN.md` phase table + `PROJECT_VARS.md` (ticket counter)

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Keycloak README documents SMTP, admin client, theme, and temp-access flow
- [ ] `docs/ENV_VARS.md` lists all new variables
- [ ] `PROJECT_VARS.md` reflects the latest ticket number

## Integration Tests to Run (Local Verification)
- [ ] N/A (documentation)

## Dependencies
- **Blocks:** None
- **Blocked By:** PAIML-KEYCLOAK-001 .. PAIML-KEYCLOAK-011

## Estimated Effort
- [S] (Small < 1h)