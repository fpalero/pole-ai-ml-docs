# Ticket: PAIML-INFRA-031

## Title
[CI] Replace values-prod.yaml with values-dev.yaml (demo-* hosts), repoint deploy-dev.yml, delete values-prod

## Description
`values-prod.yaml` is a historical/misleading name (per PLAN.md + ENV_VARS.md — there is no prod, only local + staging/pre-prod on ipsf-server) and carries dead hosts (`pole-ml` / `pole-coach` / `pole-keycloack.duckdns.org`, NXDOMAIN as of 2026-09-23). Standardize on local/dev only: delete `values-prod.yaml`, introduce `values-dev.yaml` with verified `demo-ml-agent` / `demo-ai-agent` / `demo-ai-keycloak.duckdns.org` hosts (all → 9.246.41.207), and repoint `deploy-dev.yml` at it. **Supersedes PAIML-INFRA-030** (030 stays CLOSED/superseded, do not delete it).

## Repository
`pole-ai-ml-infra`

## Affected
- `infrastracture/helm/pole-ai/values-dev.yaml` (NEW — content = current `values-prod.yaml` with `demo-ml-agent` / `demo-ai-agent` / `demo-ai-keycloak.duckdns.org` replacing `pole-ml` / `pole-coach` / `pole-keycloack` everywhere incl. `hostnameUrl`, `magicLinkEndpoint`, redirects, `keycloakUrl`)
- `infrastracture/helm/pole-ai/values-prod.yaml` (DELETE)
- `infrastracture/.github/workflows/deploy-dev.yml` (`-f helm/pole-ai/values-prod.yaml` → `-f helm/pole-ai/values-dev.yaml`; health-check `curl https://pole-ml.duckdns.org` → `https://demo-ml-agent.duckdns.org`)
- In-repo reference updates: `infrastracture/helm/pole-ai/values.yaml` comment (line ~70 prod override), `charts/keycloak/values.yaml` comments (2x `values-prod.yaml`), `README.md`, `charts/keycloak-user-expiry/README` if needed

## What to Do (Implementation Steps)
- [ ] Step 1: Create `values-dev.yaml` with new hosts (copy of `values-prod.yaml`, all old domains replaced)
- [ ] Step 2: Repoint `deploy-dev.yml` (`-f values-dev.yaml`, health-check → `https://demo-ml-agent.duckdns.org`)
- [ ] Step 3: Delete `values-prod.yaml`
- [ ] Step 4: Update comments/docs refs (`values.yaml`, `charts/keycloak/values.yaml`, READMEs)
- [ ] Step 5: `helm lint` + `helm template` (local + dev) + `actionlint` + `rg` checks

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `values-prod.yaml` absent; only `values-local.yaml` + `values-dev.yaml` exist
- [ ] `helm template -f values-dev.yaml` renders `demo-*` hosts, no old strings
- [ ] `rg "values-prod"` empty in `infrastracture/`
- [ ] `deploy-dev.yml` uses `values-dev.yaml`
- [ ] No secrets committed

## Integration Tests to Run (Local Verification)
- [ ] `helm template ./helm/pole-ai -f helm/pole-ai/values-dev.yaml | rg "demo-ml-agent|demo-ai-agent|demo-ai-keycloak"` matches; `rg "pole-ml|pole-coach|pole-keycloack" infrastracture/helm/pole-ai/values-dev.yaml` empty
- [ ] `rg "values-prod" infrastracture/` empty; `actionlint infrastracture/.github/workflows/deploy-dev.yml` clean

## Dependencies
- **Blocks:** None
- **Blocked By:** None
- **Supersedes:** PAIML-INFRA-030 (030 stays CLOSED/superseded, do not delete it)

## Integration Notes
- DNS already points correctly — no DuckDNS API call needed.

> **NOTE:** DuckDNS token/email are NOT in scope — never commit them to docs or git. No token is needed for this ticket.
