# Ticket: PAIML-KEYCLOAK-005

## Title
[pole_api] Temp-access settings + Keycloak admin client + Redis repository

## Description
Add temp-access configuration, a Keycloak admin client (service-account token grant; create/find user, random password, `VERIFY_EMAIL` required action, assign role, send verify-email, disable user), and a Redis-backed repository for cooldown/activation/token state.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Add settings to `core/config.py`: `KEYCLOAK_ADMIN_CLIENT_ID`/`KEYCLOAK_ADMIN_CLIENT_SECRET`/`KEYCLOAK_ADMIN_ISSUER`, `TEMP_ACCESS_COOLDOWN_S` (14d), `TEMP_ACCESS_WINDOW_S` (2h), `TEMP_ACCESS_TOKEN_TTL_S` (24h), app→role map (`pole-fe`→`fe-user`, `pole-analyst`→`analyst-user`), FE base URLs
- [ ] `core/temp_access.py` — `KeycloakAdminClient`: obtain admin token via client-credentials grant; `create_or_find_user(email)` (random password, `emailVerified=false`, `VERIFY_EMAIL`, assign role); `send_verify_email(user_id, client_id)`; `disable_user(user_id)`
- [ ] `core/temp_access.py` — `TempAccessRepository` (async Redis): `request(email, app)` (SETNX `temp:req`, TTL 14d), `issue_token(token, email, app)`, `activate(token)` (set `temp:active` TTL 2h), `is_active(email)`, `clear()`

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Admin client obtains a token and can create/disable users and send verify-email
- [ ] Redis repo handles cooldown (14d), token pending/active, and the 2h window
- [ ] Settings wired and unit-testable with mocks

## Integration Tests to Run (Local Verification)
- [ ] Unit-test cooldown/activation/role-map with mocked Keycloak + Redis

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-006
- **Blocked By:** PAIML-KEYCLOAK-002

## Estimated Effort
- [L] (Large 2–4h)