# Ticket: PAIML-INFRA-024

## Title
[Infrastructure] Add Filebeat DaemonSet for log shipping to Elasticsearch

## Description
Deploy a Filebeat DaemonSet into the `pole-ai` k3s namespace that ships container logs (stdout/stderr) from all pods in the namespace to the Elasticsearch cluster. Configure Filebeat autodiscovery to automatically detect pod labels (`app.kubernetes.io/name`, `kubernetes.namespace`) and add custom fields `service_name` based on the container name pattern (pole-api, pole-jobs, pole-crawler, pole-ml). Set the output to write directly to `http://elasticsearch:9200` with TLS disabled (intra-cluster). After deployment, verify that indices appear in ES with the expected naming pattern (`pole-api-*`, `pole-jobs-*`, etc.) and that log entries include the structured JSON fields.

## What to Do (Implementation Steps)
- [ ] Step 1: Create a Filebeat ConfigMap with output.es.hosts: `["http://elasticsearch:9200"]`, `ssl.enabled: false`, and `processors` to add `service_name` based on container name (using `add_host_metadata` and custom `processors` if needed).
- [ ] Step 2: Create a Filebeat DaemonSet YAML that mounts the ConfigMap, adds the `kubernetes` autodiscovery labels, and sets the image to `docker.elastic.co/beats/filebeat:8.15.x` (or latest available).
- [ ] Step 3: Apply the ConfigMap and DaemonSet into the `pole-ai` namespace: `kubectl apply -f filebeat-configmap.yaml -f filebeat-daemonset.yaml`.
- [ ] Step 4: Wait for Filebeat pods to become `Running` and verify they can reach Elasticsearch: `kubectl exec -n pole-ai <filebeat-pod> -- curl -s http://elasticsearch:9200/_cluster/health`.
- [ ] Step 5: Generate some log entries (e.g., `kubectl logs -n pole-ai <pole-api-pod> | head -1`) and verify indices appear: `curl -s http://elasticsearch:9200/_cat/indices` showing `pole-api-*`.
- [ ] Step 6: Confirm that a log entry from a pole_jobs worker pod also appears in the ES indices.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Filebeat DaemonSet pod is `Running` in `pole-ai` namespace.
- [ ] Filebeat can reach Elasticsearch (`_cluster/health` returns `green` or `yellow`).
- [ ] Indices `pole-api-*`, `pole-jobs-*`, `pole-crawler-*`, `pole-ml-*` appear in `_cat/indices` after log generation.
- [ ] Log entries in Kibana (or via `_search`) contain the structured JSON fields (`time`, `level`, `name`, `service_name`, `message`).

## Integration Tests to Run (Local Verification)
- [ ] `kubectl get daemonset -n pole-ai filebeat` and verify `READY` is `1/1`.
- [ ] `kubectl logs -n pole-ai <filebeat-pod>` shows no errors connecting to ES.
- [ ] `curl -s http://elasticsearch:9200/_cat/indices` shows expected `pole-*` indices.
- [ ] `kubectl exec -n pole-ai <pole-api-pod> -- curl -s http://localhost:9200/_search?q=*` returns recent log entries.

## Dependencies
- **Blocks:** None (can run after Phase 8 tickets 22/23 have migrated packages to JSON logger; ES+Kibana from Phase 6 should already be running).
- **Blocked By:** PAIML-INFRA-023 (all packages must use shared JSON logger first).

## Estimated Effort
- [M] (Medium < 4h)