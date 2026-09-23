# Ticket: PAIML-INFRA-035

## Title
[Helm] Trigger FE/analyst rollout on env configmap change (checksum annotation)

## Description
`pole-fe` and `pole-analyst` mount their `env.js` via `subPath` (`volumeMounts[].mountPath: /usr/share/nginx/html/assets/env.js`, `subPath: env.js`). Kubernetes does NOT hot-reload `subPath` mounts, so when the `*-env` ConfigMap changes but the Deployment spec does not (image tag stays `develop`), `helm upgrade` leaves the pods running the STALE `env.js`. Seen live 2026-09-23: after `deploy-dev` updated the env ConfigMaps to `demo-ai-keycloak`, the analyst/FE pods (created 09-21) kept serving `pole-keycloack.duckdns.org`, breaking the OIDC login redirect. Manual `kubectl rollout restart` fixed it once, but the problem recurs on every future env change. Fix: add a `checksum/env` pod-template annotation over the env ConfigMap so Helm regenerates the pod spec hash and triggers a rollout whenever the ConfigMap content changes.

## Repository
`pole-ai-ml-infra`

## Affected
- `helm/pole-ai/charts/pole-fe/templates/deployment.yaml` (pod template metadata)
- `helm/pole-ai/charts/pole-analyst/templates/deployment.yaml` (pod template metadata)

## What to Do (Implementation Steps)
- [ ] Step 1: In each deployment's `spec.template.metadata`, add `annotations: checksum/env: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}` (indent/nindent to match existing `labels` block)
- [ ] Step 2: Keep the existing `subPath: env.js` volume mount as-is (do NOT remove it — the nginx serves a single file at that path)
- [ ] Step 3: No secrets committed; no other template logic changed
- [ ] Step 4: `helm lint` + `helm template` render clean on the parent chart with `-f helm/pole-ai/values-dev.yaml`

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `helm template ./helm/pole-ai -f helm/pole-ai/values-dev.yaml` shows the `checksum/env` annotation on both deployments
- [ ] Changing `keycloakUrl` in values-dev.yaml changes the rendered annotation hash (proves rollout trigger)
- [ ] `helm lint` clean
- [ ] No secrets committed

## Dependencies
- **Blocks:** None
- **Blocked By:** None
- **Related:** PAIML-INFRA-031, PAIML-INFRA-034