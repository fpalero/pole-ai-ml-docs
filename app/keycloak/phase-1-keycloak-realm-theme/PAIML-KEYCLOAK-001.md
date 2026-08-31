# Ticket: PAIML-KEYCLOAK-001

## Title
[Keycloak] Configure realm SMTP for magic-link (verify-email) delivery

## Description
Add the `smtpServer` block to the `pole-ai` realm so Keycloak can send the verify-email magic-link. Wire it through Helm values (host, port, ssl, auth user/password, `from`) and keep credentials in a Secret, not the realm JSON. Local dev uses a mail sandbox (Mailpit).

## What to Do (Implementation Steps)
- [ ] Add `smtpServer` (host, port, ssl, auth `user`/`password`, `from`) to `infrastracture/keycloak/realm-pole-ai.json`
- [ ] Add the same `smtpServer` block to `helm/pole-ai/charts/keycloak/templates/configmap.yaml` driven by `Values.smtp.*`
- [ ] Add `smtp.*` values to `helm/pole-ai/charts/keycloak/values.yaml`; keep credentials in the admin Secret
- [ ] Add a `mailpit` SMTP sandbox Deployment + Service to the infra repo (namespace `pole-ai`; SMTP port `1025`, UI `8025`) as the realm SMTP target in the dev stack
- [ ] Point the realm `smtpServer` host/port at the Mailpit Service and confirm a test verify-email is delivered and the link works

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Keycloak sends verify-email emails via SMTP (delivered to Mailpit in dev)
- [ ] Credentials live in Helm values/Secret, not hardcoded in the realm JSON
- [ ] `helm lint` + `helm upgrade --dry-run` pass
- [ ] `mailpit` Deployment + Service present in the infra repo and reachable from the Keycloak pod

## Integration Tests to Run (Local Verification)
- [ ] Deploy, trigger execute-actions-email on the `dev` user, confirm Mailpit receives it

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-006
- **Blocked By:** None

## Estimated Effort
- [S] (Small < 1h)