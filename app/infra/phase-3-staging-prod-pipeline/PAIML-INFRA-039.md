# Ticket: PAIML-INFRA-039

## Title
[Infra] Add checksum/env annotation to pole-api deployment so env ConfigMap changes roll the pod

## Description
The `pole-api` Deployment reads its env via `envFrom.configMapRef` (`pole-ai-pole-api-env`). Unlike `pole-fe` and `pole-analyst` (which got a `checksum/env` pod-template annotation in PAIML-INFRA-035), `pole-api` has NO such annotation, so a change to its env ConfigMap does NOT restart the pod — it keeps serving stale env until manually `rollout restart`ed. This bit us in PAIML-INFRA-038: after the DuckDNS→fpalero.cc `FE_BASE_URL`/`ANALYST_BASE_URL` fix landed in the ConfigMap, the 16-day-old `pole-api` pod kept the old values until it was manually restarted.

## Repository
`pole-ai-ml-infra`

## Affected
- `infrastracture/helm/pole-ai/charts/pole-api/templates/deployment.yaml` (pod template metadata)

## What to Do (Implementation Steps)
- [ ] Step 1: In `infrastracture/helm/pole-ai/charts/pole-api/templates/deployment.yaml`, add a `checksum/env` annotation to `spec.template.metadata` that hashes the pole-api env `configmap.yaml` — mirror how `charts/pole-analyst/templates/deployment.yaml` does it:
      `annotations.checksum/env: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}`
      (indent/nindent to match the existing `labels` block).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `helm template` shows the annotation on the pole-api pod template
- [ ] After an env ConfigMap change the Deployment pod-template hash changes (rollout triggered).

## Dependencies
- **Blocks:** —
- **Blocked By:** —
- **Related:** PAIML-INFRA-035, PAIML-INFRA-038