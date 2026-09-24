# Ticket: PAIML-INFRA-037

## Title
[Helm/Keycloak] realm-sync must also apply declarative user realm-roles

## Description
The realm-sync hook Job (PAIML-INFRA-036) applies clients + realm roles via `partialImport` (OVERWRITE) but deliberately EXCLUDES users, so the `dev` / `fernando` realm-role grants declared in the ConfigMap (`realmRoles: ["fe-user", "analyst-user"]`) never reach the live DB. Consequence seen live 2026-09-24: the `dev` user had **zero** realm roles → every `/api/*` returned 403 `Requires role 'analyst-user'` (fixed manually via admin API, but not durable). Fix: extend the realm-sync script to also reconcile realm-role mappings for the declarative users WITHOUT resetting passwords or touching credentials (grant/revoke the exact `realmRoles` list from the realm JSON for `dev`/`fernando`/service-accounts; leave passwords and other user fields untouched).

## Repository
`pole-ai-ml-infra`

## Affected
- `helm/pole-ai/charts/keycloak/templates/realm-sync-script-configmap.yaml` (realm_sync.py logic)
- `helm/pole-ai/charts/keycloak/templates/realm-sync-job.yaml` (if env/payload changes)

## What to Do (Implementation Steps)
- [ ] Step 1: Extend `realm_sync.py` to, after the clients/roles partialImport, iterate the declarative `users[]` and PUT each user's realm-role mappings to exactly match `realmRoles` (add missing, revoke extra realm roles) — do NOT create users that don't exist and do NOT modify credentials/attributes
- [ ] Step 2: Keep it idempotent (re-running converges; no error if a user is missing)
- [ ] Step 3: No secrets committed
- [ ] Step 4: Extend the realm-sync stdlib regression test to cover the role-mapping reconcile (dev gets fe-user+analyst-user)

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] After a deploy, `dev` has `fe-user` + `analyst-user` (and `fernando` keeps its roles) without any manual admin-API step
- [ ] Realm-sync job remains idempotent (second deploy = no-op)
- [ ] `helm lint` clean; no secrets committed
- [ ] `dev` token → `/api/*` 200 (not 403) after re-deploy

## Dependencies
- **Blocks:** None
- **Blocked By:** None
- **Related:** PAIML-INFRA-036