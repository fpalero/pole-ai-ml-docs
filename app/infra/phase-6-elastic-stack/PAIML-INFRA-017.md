# Ticket: PAIML-INFRA-017

## Title
[Infrastructure] Configure Index Lifecycle Management (ILM) for 7-day retention

## Description
Create an Elasticsearch Index Lifecycle Management policy that enforces a 7-day retention period for pole-ai indices. The policy should use the `hot` phase for the first 24 hours (with 1 primary shard), followed by a `warm` phase that reduces replicas to 0 and eventually a `delete` phase that removes the index after 7 days. Configure an index template with proper mappings (`@timestamp`, `message`, `level`, `logger_name`, `service_name`, `kubernetes` fields). On a single-node cluster, the warm phase will effectively just reduce replica count, and the delete phase will remove the index after the age threshold.

## What to Do (Implementation Steps)
- [ ] Step 1: Create an ILM policy via the Elasticsearch `_ilm` API named `pole-ai-7d-retention` with hot phase (duration: 1d, min_shards: 1) followed by delete phase (duration: 6d).
- [ ] Step 2: Create an index template `pole-ai-*` with the ILM policy applied, including mapping for `@timestamp` (date), `level` (keyword), `logger_name` (keyword), `service_name` (keyword), and `service.namespace` (keyword).
- [ ] Step 3: Apply the template to Elasticsearch and verify `GET _index_template/pole-ai-*` returns the correct configuration.
- [ ] Step 4: Push a test index with a document having `@timestamp` in the past and verify it is auto-deleted after 7 days (use `_delete_by_query` or wait for ILM execution; alternatively trigger ILM via `_POST`).
- [ ] Step 5: Confirm indices older than 7 days are automatically removed from `_cat/indices`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] ILM policy `pole-ai-7d-retention` is created and active (`GET _ilm/policy`).
- [ ] Index template `pole-ai-*` is created with the correct mappings and lifecycle policy.
- [ ] Test index is auto-deleted after approximately 7 days (or manually verified via ILM execution).
- [ ] Indices older than 7 days no longer appear in `_cat/indices`.

## Integration Tests to Run (Local Verification)
- [ ] `kubectl exec -n pole-ai <elasticsearch-pod> -- curl -s http://localhost:9200/_ilm/policy/pole-ai-7d-retention | python3 -m json.tool`
- [ ] `kubectl exec -n pole-ai <elasticsearch-pod> -- curl -s http://localhost:9200/_index_template/pole-ai-* | python3 -m json.tool`
- [ ] Verify `_cat/indices` shows no indices older than 7 days after ILM processing.

## Dependencies
- **Blocks:** PAIML-INFRA-018 (ingress + Kibana needs ILM configured)
- **Blocked By:** PAIML-INFRA-016 (ILM needs Elasticsearch running first)

## Estimated Effort
- [M] (Medium < 4h)