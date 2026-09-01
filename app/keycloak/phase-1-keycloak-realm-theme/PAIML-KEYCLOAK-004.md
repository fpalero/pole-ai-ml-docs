# Ticket: PAIML-KEYCLOAK-004

## Title
[Keycloak] Cap `pole-fe`/`pole-analyst` sessions and access tokens to 2 hours

## Description
Set client-level `access.token.lifespan = 7200` and SSO session `max`/`idle` = `7200` on the `pole-fe` and `pole-analyst` clients so access tokens expire 2h after login (defense in depth alongside the Redis window). Note: this also caps existing `dev`/`fernando` sessions to 2h (accepted).

## Repository
pole-ai-ml-infra

## What to Do (Implementation Steps)
- [ ] Add `access.token.lifespan: 7200`, `sso.session.max.lifespan: 7200`, `sso.session.idle.timeout: 7200` to `pole-fe` and `pole-analyst` client attributes in `realm-pole-ai.json` and the Helm realm `configmap.yaml`
- [ ] Add corresponding values to `helm/pole-ai/charts/keycloak/values.yaml` (e.g. `feAccessTokenLifespan`, `feSsoMaxLifespan`)

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Access tokens for `pole-fe`/`pole-analyst` expire after 2h
- [ ] SSO session max/idle = 2h
- [ ] `helm lint` + dry-run pass

## Integration Tests to Run (Local Verification)
- [ ] Log in via pole-fe, decode the access token `exp` ≈ now + 7200s

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-007
- **Blocked By:** None

## Estimated Effort
- [S] (Small < 1h)