# Ticket: PAIML-KEYCLOAK-015

## Title
[Keycloak] Fix `pole-ai-login` theme: submit button, absolute endpoint, error parser, rollout hash

## Description
Live diagnosis shows the Keycloak pod serves a **stale theme** (live `login.ftl` 7883 bytes vs repo 14931; live JS 3746 vs repo 7286): the magic-link button renders `type="button"` so it never fires the submit handler, and a missing `data-endpoint` makes the JS POST a **relative `/api/...` URL against the Keycloak host** (404) instead of the pole_api FE host.

Why this phase (decision record):
- **Stale pod:** theme/realm ConfigMap changes do not force a Keycloak rollout, so the pod keeps serving the old theme. Fix with a checksum/config-hash annotation on the Keycloak Deployment.
- **Relative endpoint:** `fetch("/api/...")` resolves against the Keycloak origin. Fix with an **absolute `data-endpoint` per env** (FE host from `values-local` + `values-prod`).
- **Import-realm semantics:** realm/theme source of truth is the repo (`infrastracture/keycloak/` + helm chart); the live pod is derived state. Verification must compare live served bytes against repo files, never assume the deploy applied.

## Repository
pole-ai-ml-infra

## What to Do (Implementation Steps)
- [ ] Verify/fix magic-link button as `type="submit"` in `infrastracture/keycloak/themes/pole-ai-login/login/login.ftl` (keep `url.loginAction`, `username`/`password`, `credentialId`, `messagesPerField`, `msg()` keys).
- [ ] Set absolute `data-endpoint` per env to the pole_api FE host: `values-local.yaml` → local FE host, `values-prod.yaml` → prod FE host (keep `data-endpoint` override support in `temporary-access.js`).
- [ ] Extend `temporary-access.js` error parser to also surface backend `data.error` (besides existing message shapes); keep strings locale-free via `data-*` from `msg()`.
- [ ] Add checksum/config-hash annotation (theme + realm ConfigMap hash) to the Keycloak Deployment template so theme/realm changes force a rollout.
- [ ] `helm lint` + `helm upgrade --dry-run` (local + prod values).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Repo `login.ftl` button is `type="submit"`; magic-link submit fires the JS handler.
- [ ] Rendered page carries an absolute `data-endpoint` per env (no relative `/api` POST to the Keycloak host).
- [ ] JS error box renders backend `data.error` text.
- [ ] Theme/realm content change alters the Deployment annotation (rollout forced).
- [ ] `helm lint` + dry-run pass for local and prod values.

## Integration Tests to Run (Local Verification)
- [ ] `helm template` with `values-local.yaml` renders absolute local endpoint + checksum annotation; same with `values-prod.yaml` for prod host.
- [ ] Unit check on JS error parser: payload with `data.error` surfaces the message.

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-016, PAIML-KEYCLOAK-017
- **Blocked By:** None (root)

## Estimated Effort
- [S] (Small 1–2h)
