# Ticket: PAIML-INFRA-036

## Title
[Helm/Keycloak] Fix feClientRedirects leak + realm re-import on deploy

## Description
Two chained bugs broke the demo-* Keycloak login (found 2026-09-23/24):

1. **`feClientRedirects` leak:** `helm/pole-ai/values-dev.yaml` sets `keycloak.feClientRedirect: https://demo-ml-agent.duckdns.org/*` (single) but NOT `keycloak.feClientRedirects` (the list). Helm merges `values-dev.yaml` over the parent `values.yaml`, so the default `feClientRedirects` from `values.yaml` (`https://pole-fe.local/*`, `http://pole-fe.local/*`, `http://localhost:4200/*`) leaks through. The realm ConfigMap template (`keycloak/templates/configmap.yaml` line 39) prefers `.Values.feClientRedirects` over the single value, so the rendered `pole-fe` client keeps stale `.local`/localhost redirect URIs. (The analyst client is unaffected because `values-dev.yaml` DOES set `analystClientRedirects`.)

2. **Realm never re-imports:** the Keycloak deployment runs `--import-realm` (keycloak/templates/deployment.yaml line 35), but Keycloak only imports realms that do NOT already exist in the persistent store (dev-file PVC). The `pole-ai` realm was imported once (very early) with the ORIGINAL hosts (`pole-ml`/`pole-coach.duckdns.org`) and has NEVER been re-applied since — every later realm change (checksum/rollout restarts the pod, but the existing realm is skipped) is silently ignored in the live DB. The `checksum/realm` annotation triggers a rollout, but the re-import is a no-op for existing realms.

**Immediate fix already applied manually** (live realm clients updated to demo-* redirectUris/webOrigins via admin API). This ticket makes the fix durable so the next deploy does not regress.

## Repository
`pole-ai-ml-infra`

## Affected
- `helm/pole-ai/values-dev.yaml` (add `keycloak.feClientRedirects` list)
- `helm/pole-ai/charts/keycloak/templates/deployment.yaml` (realm re-import strategy)

## What to Do (Implementation Steps)
- [ ] Step 1: In `values-dev.yaml`, add `feClientRedirects:` under `keycloak:` with `- https://demo-ml-agent.duckdns.org/*` and `- http://localhost:4200/*` (keep localhost:4200 for local Playwright e2e). Align `feWebOrigins` to `https://demo-ml-agent.duckdns.org` + `http://localhost:4200`.
- [ ] Step 2: Establish a durable realm re-import so the declarative ConfigMap realm is authoritative on every deploy. Options (pick one, document the decision): (a) a post-deploy Kubernetes Job that applies the realm via the Keycloak admin API (idempotent partial import), or (b) a Keycloak startup option/strategy that overwrites the existing realm. Do NOT lose existing users/sessions unless explicitly documented as acceptable for the dev realm.
- [ ] Step 3: No secrets committed; Brevo SMTP password still injected via `--set` at deploy.
- [ ] Step 4: `helm template` shows `pole-fe` redirectUris = demo-ml-agent (not `.local`); `helm lint` clean.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `helm template ./helm/pole-ai -f helm/pole-ai/values-dev.yaml` renders `pole-fe` `redirectUris` containing `https://demo-ml-agent.duckdns.org/*` (no `pole-fe.local`)
- [ ] A deploy re-applies realm changes (verify: change a realm field, deploy, confirm live realm reflects it)
- [ ] `helm lint` clean; no secrets committed
- [ ] Login flow on demo-* still green after re-deploy

## Dependencies
- **Blocks:** None
- **Blocked By:** None
- **Related:** PAIML-INFRA-031, PAIML-INFRA-035