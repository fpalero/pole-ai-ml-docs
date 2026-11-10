# ADR-040: Duplicate Release / Chart Source Ambiguity

## Status
Accepted

## Date
2026-11-10

## Context
During Phase 3 (staging-prod-pipeline) merges PAIML-INFRA-040 and PAIML-INFRA-041, two umbrella subchart Services (keycloak, mongodb, redis, pole-api, pole-fe, pole-analyst) were being deployed twice into the same namespace `pole-ai`, producing 7 stale committed `helm/pole-ai/charts/*.tgz` archives that were deleted because Helm randomly selected between the directory chart and its `-0.1.0.tgz` variant. This led to:
- Silent service duplication (two Keycloak identity stores, two MongoDB DBs, two Redis instances behind a single Kubernetes Service/host).
- Render inconsistency: 8 identical k3s renders produced endpoint counts {4,5,5,5,5,6,6,7} out of 7 expected scoped services.
- A live staging login redirect pointing at a dead DuckDNS host (`demo-ai-keycloak.duckdns.org`), traced to values-dev.yaml still hardcoding the old URL.

The root cause was that both `infrastracture/helm/pole-ai/charts/<subchart>/` and `infrastracture/helm/pole-ai/charts/<subchart>-0.1.0.tgz` existed as separate chart artifacts. With both present, Helm's default behavior picks either source at random, making chart changes silently ignored on some renders.

## Decision
Scope every umbrella subchart Service selector to the Helm release instance using `app.kubernetes.io/instance: {{ .Release.Name }}` in all `service.yaml` templates and pod template labels. Add a preflight validation (`_validate.tpl`) that fails render when `global.registry` contains `localhost:5000` while any ingress host is not ending in `.pole.local`, with escape hatch `global.allowLocalImages: true` for local k3s flow. Wired preflight check into `deploy-dev.yml`, `deploy-staging.yml`, `deploy-prod.yml`, and `scripts/deploy.sh`.

## Alternatives Considered
### Kustomize over Helm
- Pros: Declarative, layer-based.
- Cons: PO explicitly confirmed Helm (`helm upgrade --wait`) as the chosen tool; Kustomize would require rewriting all deployment manifests and workflows.
- Rejected.

### Relying on a single chart artifact (`.tgz`)
- Pros: Simpler manifest.
- Cons: Caused exactly this ambiguity — Helm could pick either the directory or the tgz file, leading to random selection and silent failures. 7 stale archives found during PR #58/#59 merge.
- Rejected.

### Keeping both chart directories AND tgz files
- Pros: Maximum compatibility with older Helm versions.
- Cons: Same random-selection problem; also triggered the duplicate-service issue.
- Rejected.

## Consequences
- Every subchart Service now resolves uniquely per release via `app.kubernetes.io/instance: <release-name>`.
- Disjoint endpoints across releases within the same namespace (verified by `scripts/test-chart-selectors.sh`).
- Local k3s flow continues to work via `values-local.yaml` (no `global.registry: localhost:5000` needed); remote/public deployments must set `--set global.registry=ghcr.io/fpalero` or rely on `global.allowLocalImages: true`.
- Cluster cleanup: removed leftover empty namespace `pole-ai-fixed` (2026-11-09 duplicate install) and resolved PVC `pole-ai-keycloak` stuck in Terminating after 3 days (pvc-protection finalizer released once Keycloak scaled to 0; realm re-imported from ConfigMap; users restored).
- Resolved keycloak-user-expiry CronJob failure (`CreateContainerConfigError: secret "temp-user-expiry-secret" not found`); operator-created secret now exists from realm's own client secret; manual job run completed (`scanned=2 expired_enabled=0 dry_run=True`).

## Related
- PAIML-INFRA-040 (scope selectors)
- PAIML-INFRA-041 (preflight guard)
- PR #58 (bc217c7) / PR #59 (83a98e1)

## Verification
- `pixi run docs-rag-read "PAIML-INFRA-040 instance scoped service selectors stale tgz" --k 3 --rag pole_docs`
- `pixi run docs-rag-read "PAIML-INFRA-041 deploy fail fast local registry" --k 3 --rag pole_docs`
