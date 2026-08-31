# Plan Phase 1 — Keycloak Realm, SMTP & Custom Login Theme

> **Parent plan:** [PLAN.md](../PLAN.md)
> **Status:** 📋 PLANNED

## Scope

Prepare the Keycloak realm (`pole-ai`) so temporary-access works: configure SMTP so Keycloak can send the verify-email magic link, add a dedicated confidential admin client that `pole_api` uses to create/disable temp users, ship a custom login theme that offers **Login** or **Get temporary access**, and cap the FE client sessions/tokens to 2 hours.

## Context

Today the realm has only public clients (`pole-fe`, `pole-analyst`, `mcp-server`), roles `fe-user`/`analyst-user`, and no SMTP. Both FEs redirect to the standard Keycloak login page (`onLoad: 'login-required'`). This phase is the foundation for the backend orchestration (Phase 2) and the data purge (Phase 3).

## Tasks

### Realm SMTP (verify-email / magic-link delivery)
- [ ] [Infrastructure] Add `smtpServer` block to the realm (`realm-pole-ai.json` + Helm `configmap.yaml`) driven by values: host, port, ssl, auth (`user`/`password`), `from`.
- [ ] [Infrastructure] Add `smtp.*` values to `helm/pole-ai/charts/keycloak/values.yaml`; keep credentials in a Secret (not the realm JSON).
- [ ] [Infrastructure] Add a **`mailpit` SMTP sandbox** to the infra repo (namespace `pole-ai`): a `mailpit` Deployment + Service whose SMTP endpoint (default port `1025`) is the realm `smtpServer` host in the dev stack. UI (port `8025`) for inspecting delivered verify-emails.
- [ ] [Infrastructure] Point the realm `smtpServer` host/port at the Mailpit Service and confirm Keycloak can send email end-to-end (verify delivered in the Mailpit UI).

### Confidential admin client for pole_api
- [ ] [Infrastructure] Add client `pole-api-admin` (confidential, service-account enabled, direct access grants off) to the realm.
- [ ] [Infrastructure] Grant the service account `realm-management` client roles: `manage-users`, `view-users` (create users, set required actions, disable users, execute-actions-email).
- [ ] [Infrastructure] Persist the client secret as a Helm Secret; expose `KEYCLOAK_ADMIN_CLIENT_ID`/`KEYCLOAK_ADMIN_CLIENT_SECRET` to the `pole-api` pod.

### Custom login theme `pole-ai-login`
- [ ] [Infrastructure] Create `infrastracture/keycloak/themes/pole-ai-login/` (extends the `keycloak` base theme): `theme.properties`, `messages/messages_en.properties` + `es`.
- [ ] [Infrastructure] Override `login/login.ftl`: render the standard username/password **Login** form plus a **Get temporary access** panel (email input).
- [ ] [Infrastructure] Theme JS reads the `client` login context and POSTs `{email, clientId}` to `pole_api /api/auth/temporary-access` (CORS already `*`).
- [ ] [Infrastructure] Set realm `loginTheme: pole-ai-login`; mount the theme into the Keycloak pod via a ConfigMap volume (`keycloak/templates/deployment.yaml`).

### Client session/token lifespan (2h cap)
- [ ] [Infrastructure] Set `access.token.lifespan = 7200` and SSO session `max`/`idle` = `7200` on `pole-fe` and `pole-analyst` (client attributes) so access tokens expire 2h after login.

## Dependencies

- Keycloak 26.7 deployment (`helm/pole-ai/charts/keycloak`).
- Existing `realm-pole-ai.json` and the Helm realm `configmap.yaml`.
- `pole-api` deployment env wiring (configmap/secret) — consumed by Phase 2.

## Acceptance Criteria

- [ ] Keycloak sends verify-email emails via SMTP.
- [ ] `pole-api-admin` client exists; its service account can create/disable users and trigger execute-actions-email.
- [ ] Custom login theme shows both Login and Get temporary access; theme present in the running pod.
- [ ] `pole-fe`/`pole-analyst` access tokens expire after 2h.
- [ ] `helm upgrade` applies cleanly (`helm lint` + dry-run pass).