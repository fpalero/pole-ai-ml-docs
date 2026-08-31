# Plan Phase 1 — Helm Charts & Local Deploy (Foundation)

> **Parent plan:** [PLAN.md](../PLAN.md)
> **Status:** ✅ DONE

## Scope

Set up the Helm umbrella chart and local deployment scripts for the full pole-ai stack on k3s. This phase establishes the deployment foundation that all subsequent CI/CD phases build upon.

## What Was Implemented

### Helm Umbrella Chart (`infrastracture/helm/pole-ai/`)

- **Chart.yaml** — umbrella chart with 6 subchart dependencies
- **values.yaml** — default values with YAML anchors for credentials
- **values-local.yaml** — local k3s overlay (localhost:5000 registry)

### Subcharts

| Subchart | Templates | Purpose |
| :--- | :--- | :--- |
| `mongodb` | deployment, service, pvc | MongoDB 7 data store |
| `redis` | deployment, service | Redis 7 cache/sessions |
| `keycloak` | deployment, service, ingress, configmap, secret, pvc | OIDC (realm `pole-ai`) |
| `pole-api` | deployment, service, ingress, configmap, secret, pvc | FastAPI backend |
| `pole-fe` | deployment, service, ingress, configmap | Angular 22 SPA |
| `pole-analyst` | deployment, service, ingress, configmap | Angular 22 analyst SPA |

### Scripts

- **build-push.sh** — builds Docker images from app Dockerfiles, pushes to localhost:5000
- **deploy.sh** — `helm upgrade --install` with values-local.yaml overlay
- **teardown.sh** — `helm uninstall` + optional PVC cleanup

### Configuration

- **k3s/registries.yaml** — containerd mirror for insecure local Docker registry
- **Health probes** — readiness + liveness on all deployments (pole-api: `/health`)
- **Ingress** — Traefik routing for pole-fe.local, pole-analyst.local, api.pole.local, keycloak.pole.local

## Dependencies

- k3s running locally (Traefik bundled)
- Helm + kubectl + Docker installed
- ML models (pose_landmarker_heavy.task, lstm_model_normal_final.keras) baked into pole-api image

## Acceptance Criteria

- [x] `helm install pole-ai ./helm/pole-ai -n pole-ai --create-namespace` succeeds
- [x] All 6 pods start and pass readiness probes
- [x] Ingress routes work: pole-fe.local, pole-analyst.local, api.pole.local, keycloak.pole.local
- [x] `curl http://api.pole.local/health` returns 200
- [x] `./scripts/teardown.sh` cleanly removes the release
