# Ticket: PAIML-INFRA-016

## Title
[Infrastructure] Deploy Elasticsearch single-node via Helm into k3s

## Description
Add an Elasticsearch subchart to the umbrella Helm chart (`infrastracture/helm/pole-ai/`) for single-node deployment into the `pole-ai` k3s namespace. Configure resource limits (heap ~1GB), PVC for data persistence, and health probes. Evaluate using the official Elastic Helm chart with `node.auto.expand:false` and `node.store.allow_mmap: false` for small-node compatibility.

## What to Do (Implementation Steps)
- [ ] Step 1: Add Elasticsearch subchart to umbrella `values.yaml` with `enabled: true`, `node.count: 1`, resource requests/limits (memory: 1Gi, cpu: 250m), PVC size (20Gi), and `node.store.allow_mmap: false`.
- [ ] Step 2: Configure Elasticsearch pod disruption budget and anti-affinity for single-node placement.
- [ ] Step 3: Add Elasticsearch service type `ClusterIP` and health probes (readiness/liveness).
- [ ] Step 4: Run `helm upgrade --install` into the `pole-ai` namespace and verify pod is `Running`.
- [ ] Step 5: Confirm `_cluster/health` endpoint returns green/yellow status.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Elasticsearch Helm chart is merged into umbrella chart and renders without errors (`helm lint`).
- [ ] Elasticsearch pod is `Running` in `pole-ai` namespace with allocated resources.
- [ ] PVC is bound and data directory persists across restarts.
- [ ] `_cluster/health` API returns `green` or `yellow`.
- [ ] `helm template` produces valid YAML with no warnings about deprecated fields.

## Integration Tests to Run (Local Verification)
- [ ] Run `helm upgrade --install pole-ai ./helm/pole-ai -n pole-ai --wait` and `kubectl get pods -n pole-ai | grep elasticsearch`
- [ ] Curl `_cluster/health` and assert `"status":"green"` or `"status":"yellow"`.
- [ ] Run `helm lint` on the umbrella chart.

## Dependencies
- **Blocks:** PAIML-INFRA-017 (ILM policy needs ES running)
- **Blocked By:** None (can start immediately, depends only on k3s cluster access)

## Estimated Effort
- [M] (Medium < 4h)