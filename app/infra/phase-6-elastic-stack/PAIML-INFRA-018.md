# Ticket: PAIML-INFRA-018

## Title
[Infrastructure] Configure Kibana ingress with DuckDNS + Keycloak SSO

## Description
Configure Kibana to be accessible via `pole-kibana.duckdns.org` with TLS certificates managed by cert-manager. Add Keycloak-based SSO using oauth2-proxy (or Kibana's built-in Elasticsearch auth) so that authenticated users from the `pole-ai` Keycloak realm can log in. Update the umbrella Helm chart values to expose Kibana service type `NodePort` (or `LoadBalancer` if cloud) and add an Ingress resource with the DuckDNS hostname, cert-manager issuer/cluster issuer, and oauth2-proxy configuration.

## What to Do (Implementation Steps)
- [ ] Step 1: Add Kibana subchart configuration to umbrella `values.yaml` (image, resources, nodeCount: 1, service.type: NodePort, env: SERVER_NAME=kibana, ELASTICSEARCH_HOSTS).
- [ ] Step 2: Create/Update cert-manager ClusterIssuer (or use existing `letsencrypt-prod` issuer) for `pole-kibana.duckdns.org`.
- [ ] Step 3: Add an Ingress resource to the umbrella chart with host `pole-kibana.duckdns.org`, TLS annotation, and `oauth2-proxy` as the ingress auth backend (or configure Kibana basic auth with Keycloak users).
- [ ] Step 4: Configure oauth2-proxy settings: `provider: keycloak`, `client-id`, `client-secret`, `redirect-url`, `scope: openid email profile`, and Keycloak realm URL.
- [ ] Step 5: Deploy with `helm upgrade --install` and verify access via `https://pole-kibana.duckdns.org` with Keycloak login.
- [ ] Step 6: Test that unauthenticated access is redirected to Keycloak and successful login opens Kibana.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Kibana is reachable at `https://pole-kibana.duckdns.org` with a valid TLS certificate.
- [ ] Login with Keycloak credentials (any valid user in the `pole-ai` realm) grants access to Kibana.
- [ ] Unauthenticated requests are redirected to Keycloak login page.
- [ ] `helm template` produces valid Ingress with TLS and oauth2-proxy config.
- [ ] `kubectl get ingress -n pole-ai` shows the Kibana ingress is `READY`.

## Integration Tests to Run (Local Verification)
- [ ] `curl -k https://pole-kibana.duckdns.org` and verify Keycloak redirect or Kibana dashboard appears.
- [ ] `kubectl get ingress -n pole-ai pole-kibana --template '{{.status.loadBalancer.ingress}}'`
- [ ] `kubectl describe ingress -n pole-ai pole-kibana | grep -E 'TLS|Annotations: .*oauth2'`

## Dependencies
- **Blocks:** None (can start after PAIML-INFRA-016 ES pod is Running; ILM configured recommended but not strictly required for Kibana UI access)
- **Blocked By:** PAIML-INFRA-017 (ILM policy recommended for log retention governance, but Kibana access is independent)

## Estimated Effort
- [M] (Medium < 4h)