# Ticket: PAIML-INFRA-030

## Title
[CI] Point ipsf-server deploy to demo-* DuckDNS hosts via deploy-dev.yml

## Description
Old DuckDNS hosts (`pole-ml`, `pole-coach`, `pole-keycloack.duckdns.org`) are dead (NXDOMAIN as of 2026-09-23). New hosts `demo-ml-agent`, `demo-ai-agent`, `demo-ai-keycloak.duckdns.org` all resolve to 9.246.41.207 (presumed ipsf-server). Scope is `deploy-dev.yml` ONLY per user decision — `values-prod.yaml` stays frozen.

## Repository
`pole-ai-ml-infra`

## Affected
- `infrastracture/.github/workflows/deploy-dev.yml` — health-check URL `pole-ml` → `demo-ml-agent`; add/adjust `--set` overrides for `global.poleFeHost=demo-ml-agent.duckdns.org`, `global.poleAnalystHost=demo-ai-agent.duckdns.org`, `global.keycloakHost=demo-ai-keycloak.duckdns.org` IF the implementer confirms `values-prod.yml` is frozen — otherwise health-check only. **Decision point:** verify host value keys in `helm/pole-ai/values*.yaml` before adding overrides; if keys differ, health-check-only change wins.

## What to Do (Implementation Steps)
- [ ] Step 1: Confirm host value keys via `helm template` against current chart (`values-prod.yaml` read-only)
- [ ] Step 2: Update health-check `curl -sf https://pole-ml.duckdns.org` → `https://demo-ml-agent.duckdns.org`
- [ ] Step 3: Add `--set` host overrides only if keys confirmed (see Affected); remove all old domains from this file
- [ ] Step 4: `actionlint` on workflow file; `helm template` renders new hosts (or health-check-only diff)

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `helm template` renders new hosts OR health-check passes on `https://demo-ml-agent.duckdns.org`
- [ ] No secrets committed (workflow uses `${{ secrets.* }}` only)
- [ ] Old domains fully removed from `deploy-dev.yml`

## Integration Tests to Run (Local Verification)
- [ ] `helm template` with same `--set` overrides shows `demo-*` hosts; no `pole-ml`/`pole-coach`/`pole-keycloack` strings remain (`rg "pole-ml|pole-coach|pole-keycloack" infrastracture/.github/workflows/deploy-dev.yml` empty)

## Dependencies
- **Blocks:** None
- **Blocked By:** None

## Integration Notes
- DNS already points correctly — no DuckDNS API call needed.

> **NOTE:** DuckDNS token/email are NOT in scope — never commit them to docs or git. No token is needed for this ticket.
