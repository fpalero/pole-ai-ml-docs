# Ticket: PAIML-KEYCLOAK-003

## Title
[Keycloak] Custom login theme `pole-ai-login` with "Get temporary access"

## Description
Create a custom Keycloak login theme that extends the `keycloak` base theme and adds a **Get temporary access** panel (email input) alongside the standard **Login** form. Theme JS reads the `client` login context and POSTs `{email, clientId}` to `pole_api /api/auth/temporary-access`. Set realm `loginTheme: pole-ai-login` and mount the theme into the Keycloak pod via a ConfigMap volume.

## What to Do (Implementation Steps)
- [ ] Create `infrastracture/keycloak/themes/pole-ai-login/` extending `keycloak` base theme
- [ ] Add `theme.properties` and `messages` (en + es) with the temp-access copy
- [ ] Override `login/login.ftl`: standard Login form + Get temporary access panel (email input)
- [ ] Add theme JS that reads `client` and POSTs `{email, clientId}` to `/api/auth/temporary-access` (CORS already `*`)
- [ ] Set realm `loginTheme: pole-ai-login` in the realm JSON/configmap
- [ ] Mount the theme into the Keycloak pod (`keycloak/templates/deployment.yaml`) via a ConfigMap volume
- [ ] Add `loginTheme` value to `helm/pole-ai/charts/keycloak/values.yaml`

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Keycloak login page shows both Login and Get temporary access
- [ ] Submitting an email posts to the pole_api endpoint with the correct `clientId`
- [ ] Theme files are present in the running Keycloak pod
- [ ] `helm lint` + dry-run pass

## Integration Tests to Run (Local Verification)
- [ ] Navigate to pole-fe.local → redirected to Keycloak → see both options → submit email → request hits pole_api

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-006
- **Blocked By:** None

## Estimated Effort
- [L] (Large 2–4h)