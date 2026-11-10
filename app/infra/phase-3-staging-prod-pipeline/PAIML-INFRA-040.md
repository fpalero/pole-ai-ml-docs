# Ticket: PAIML-INFRA-040

## Title
[Infra] Scope every subchart Service selector to the Helm release instance

## Description
All umbrella subchart Services (`keycloak`, `keycloak-mailpit` already has instance, `mongodb`, `redis`, `pole-api`, `pole-fe`, `pole-analyst`) select pods with `app.kubernetes.io/name: <app>` only. Any second release installed into the same namespace silently doubles every backend (two Keycloak identity stores, two MongoDB databases, two Redis) behind one Service/host. Observed root cause of the 2026-11-09 `agent.fpalero.cc` post-login outage.

## Repository
`pole-ai-ml-infra`

## Affected
- `infrastracture/helm/pole-ai/charts/*/templates/service.yaml` (keycloak, mongodb, redis, pole-api, pole-fe, pole-analyst) and the corresponding `deployment.yaml` pod labels if `app.kubernetes.io/instance` is missing.

## What to Do (Implementation Steps)
- [x] Step 1: Add `app.kubernetes.io/instance: {{ .Release.Name }}` to every Service selector in `infrastracture/helm/pole-ai/charts/*/templates/service.yaml` (keycloak, mongodb, redis, pole-api, pole-fe, pole-analyst).
- [x] Step 2: Add `app.kubernetes.io/instance: {{ .Release.Name }}` to pod template labels in corresponding `deployment.yaml` files if missing, mirroring `charts/keycloak/templates/mailpit-service.yaml` which already scopes by instance.
- [x] Step 3: Add a `helm-unittest` (or `helm template | yq` assertion) proving two releases in one namespace produce disjoint selector sets.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] `helm template` with two different release names yields selectors containing the release name.
- [x] Two releases in the same namespace produce disjoint endpoints.
- [x] Existing single-release deploy still resolves all Services.
- [x] Unit test added.

## Outcome
PR #58 (squash bc217c7) merged on 2026-11-10. All umbrella subchart Service selectors now scope by `app.kubernetes.io/instance: {{ .Release.Name }}`, eliminating the silent service doubling that caused the 2026-11-09 `agent.fpalero.cc` outage. During merge, 7 stale committed `helm/pole-ai/charts/*.tgz` archives were discovered and deleted (they're gitignored) because Helm randomly picked between local `.tgz` files and chart directory, causing render inconsistency. The new `scripts/test-chart-selectors.sh` validates that two releases in one namespace produce disjoint selectors. Cluster remediation: deleted the leftover empty namespace `pole-ai-fixed` (2026-11-09 duplicate install) and resolved PVC `pole-ai-keycloak` stuck in Terminating after 3d12h (pvc-protection finalizer released when Keycloak scaled to 0, PVC recreated, realm re-imported, users restored).

## Dependencies
- **Blocks:** —
- **Blocked By:** —
- **Related:** PAIML-INFRA-041