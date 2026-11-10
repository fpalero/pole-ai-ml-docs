# Ticket: PAIML-INFRA-041

## Title
[Infra] Fail fast when deploying the umbrella chart to a remote cluster with local default values

## Description
`helm/pole-ai/values.yaml` ships LOCAL defaults (`global.registry: localhost:5000`, `*.pole.local` hosts). A deploy that forgets `-f values-dev.yaml` (and the `--set global.registry=ghcr.io/fpalero`) renders `localhost:5000/pole-api:main`-style images and silently produces a `failed` release with Pending pods (exactly what happened to `pole-ai-fixed` on 2026-11-09). Additionally there is no guard against installing a second release name into a namespace that already runs one, which is what triggered PAIML-INFRA-040.

## Canonical fpalero.cc hosts
| Service | Canonical host |
| :--- | :--- |
| Keycloak | `https://kc.fpalero.cc` |
| pole-analyst | `https://agent.fpalero.cc` |
| pole-fe | `https://ai.fpalero.cc` |

## values-dev.yaml drift
The committed `helm/pole-ai/values.yaml` ships LOCAL defaults that are only valid with `-f values-local.yaml` or explicit `--set global.registry=ghcr.io/fpalero`. Without the dev override, a plain `helm install` or `helm upgrade` produces `localhost:5000/...`-style image strings and a release that cannot pull its images.

## Repository
`pole-ai-ml-infra`

## Affected
- `infrastracture/helm/pole-ai/templates/_validate.tpl` (new or existing validation helper)
- `infrastracture/.github/workflows/deploy-dev.yml` (and staging/prod)
- `infrastracture/scripts/deploy.sh`

## What to Do (Implementation Steps)
- [x] Step 1: Add a chart-level validation that `fail`s when `global.registry` contains `localhost` while any ingress host does not end in `.pole.local` (i.e. a remote/public deployment with a local registry), with an explicit escape hatch value (e.g. `global.allowLocalImages: true`) for the local k3s flow.
- [x] Step 2: Add a preflight step to `infrastracture/.github/workflows/deploy-dev.yml` (and staging/prod workflows) that aborts if the target namespace already contains a Helm release whose name differs from the expected release name.
- [x] Step 3: Add a preflight check to `infrastracture/scripts/deploy.sh` that mirrors the workflow guard, ensuring local `deploy.sh` runs fail fast too.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] `helm template` with `values-dev.yaml`-style hosts + `localhost:5000` registry fails with an actionable message.
- [x] The local flow (`values-local.yaml`) renders unchanged.
- [x] Deploy workflow aborts on a pre-existing differently-named release in the namespace.
- [x] The failure message names the missing `-f values-dev.yaml` / `--set global.registry` fix.

## Outcome
PR #59 (squash 83a98e1) merged on 2026-11-10. Added `helm/pole-ai/templates/_validate.tpl` guard that fails render when `global.registry` contains `localhost` while any ingress host is not `.local` (escape hatch `global.allowLocalImages`, default false), invoked from `templates/tls.yaml`. New `scripts/preflight-release-guard.sh` (exit 0 safe / 1 foreign release / 2 usage / 3 fail-closed) wired into `deploy-dev.yml`, `deploy-staging.yml`, `deploy-prod.yml` and `scripts/deploy.sh`. Cluster remediation: the `keycloak-user-expiry` CronJob was failing every 30 min for days with `CreateContainerConfigError: secret "temp-user-expiry-secret" not found`; the operator-created secret now exists (from the realm's own `temp-user-expiry` client secret) and a manual job run completed (`scanned=2 expired_enabled=0 dry_run=True`).

## Dependencies
- **Blocks:** —
- **Blocked By:** —
- **Related:** PAIML-INFRA-040