# Ticket: PAIML-INFRA-038

## Title
[Infra] Migrate DuckDNS hosts → fpalero.cc across values-dev.yaml, live staging env, and docs

## Description
The live k3s cluster (context `ipsf-server`, namespace `pole-ai-staging`) was partially
migrated from DuckDNS hosts to the user's real `fpalero.cc` domain. Keycloak
(`KC_HOSTNAME=https://kc.fpalero.cc`), the API `KEYCLOAK_ISSUER`, and the realm client
redirect URIs are already correct. **But** the committed Helm source of truth
`infrastracture/helm/pole-ai/values-dev.yaml` still hardcodes DuckDNS everywhere, and four
runtime env values in the live cluster were never migrated — which is why the login redirect at
`https://agent.fpalero.cc` points to the dead `https://demo-ai-keycloak.duckdns.org`.

## Canonical fpalero.cc hosts
| Service | Canonical host |
| :--- | :--- |
| Keycloak | `https://kc.fpalero.cc` |
| pole-analyst | `https://agent.fpalero.cc` |
| pole-fe | `https://ai.fpalero.cc` |

## Stale live values (to be corrected)
Four runtime env values in the live cluster were never migrated off the DuckDNS hosts:

1. `pole-ai-pole-analyst-env` ConfigMap `env.js` → `window.keycloakUrl` =
   `https://demo-ai-keycloak.duckdns.org` (should be `https://kc.fpalero.cc`).
2. `pole-ai-pole-fe-env` ConfigMap `env.js` → `window.keycloakUrl` =
   `https://demo-ai-keycloak.duckdns.org` (should be `https://kc.fpalero.cc`).
3. `pole-ai-pole-api-env` ConfigMap → `FE_BASE_URL` =
   `https://demo-ml-agent.duckdns.org` (should be `https://ai.fpalero.cc`).
4. `pole-ai-pole-api-env` ConfigMap → `ANALYST_BASE_URL` =
   `https://demo-ai-agent.duckdns.org` (should be `https://agent.fpalero.cc`).

## values-dev.yaml drift
The uncommitted `--set` overrides migrated the global/keycloak hosts (which is why
`KEYCLOAK_ISSUER` / `KC_HOSTNAME` / realm redirect URIs turned out correct) but never the
FE/analyst `keycloakUrl` or the API base URLs (`FE_BASE_URL` / `ANALYST_BASE_URL`) — so the
live `*-env` ConfigMaps kept serving / minting the dead DuckDNS origins. The committed
`values-dev.yaml` source of truth still hardcodes DuckDNS everywhere.

## Repository
`pole-ai-ml-infra`

## Affected
- `infrastracture/helm/pole-ai/values-dev.yaml` (DuckDNS → fpalero.cc everywhere: `global.*`, `keycloak.*`, `pole-fe` / `pole-analyst` `keycloakUrl`, `pole-api` `feBaseUrl` / `analystBaseUrl`)
- `infrastracture/helm/pole-ai/charts/keycloak/tests/test_realm_sync.py` (if it pins DuckDNS hosts)

## What to Do (Implementation Steps)
- [ ] Step 1: Infra code fix — in `infrastracture/helm/pole-ai/values-dev.yaml`, replace every
      DuckDNS host with the canonical fpalero.cc host (incl. `global.poleFeHost=https://ai.fpalero.cc`,
      `global.poleAnalystHost=https://agent.fpalero.cc`, `global.keycloakHost=https://kc.fpalero.cc`,
      `keycloak.hostnameUrl=https://kc.fpalero.cc`, `keycloak.magicLinkEndpoint=https://ai.fpalero.cc/api/auth/temporary-access`,
      `keycloak.feClientRedirect*` / `keycloak.feWebOrigins` → `https://ai.fpalero.cc`,
      `keycloak.analystClientRedirect*` / `keycloak.analystWebOrigins` → `https://agent.fpalero.cc`,
      `pole-fe.keycloakUrl=https://kc.fpalero.cc`, `pole-analyst.keycloakUrl=https://kc.fpalero.cc`,
      `pole-api.feBaseUrl=https://ai.fpalero.cc`, `pole-api.analystBaseUrl=https://agent.fpalero.cc`).
- [ ] Step 2: App comment fix — update the `FE_BASE_URL` / `ANALYST_BASE_URL` comment in
      `app/pole_api/src/core/config.py` (demo DuckDNS hosts → fpalero.cc).
- [ ] Step 3: Docs fix — update `docs/ENV_VARS.md` (this repo) `FE_BASE_URL` / `ANALYST_BASE_URL` /
      `window.keycloakUrl` examples (demo DuckDNS → fpalero.cc).
- [ ] Step 4: Live redeploy — apply the corrected values through the staging deploy so the live
      `*-env` ConfigMaps pick up the new origins and the rollout restarts pick up the new `env.js`
      (checksum annotation), then verify the login redirect at `https://agent.fpalero.cc` →
      `https://kc.fpalero.cc` is green.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `helm template -f helm/pole-ai/values-dev.yaml` renders the fpalero.cc hosts (no DuckDNS).
- [ ] Live `pole-ai-pole-analyst-env` / `pole-ai-pole-fe-env` ConfigMaps `env.js` →
      `window.keycloakUrl = https://kc.fpalero.cc`; live `pole-ai-pole-api-env` ConfigMap →
      `FE_BASE_URL=https://ai.fpalero.cc`, `ANALYST_BASE_URL=https://agent.fpalero.cc`.
- [ ] Live login redirect at `https://agent.fpalero.cc` → Keycloak `https://kc.fpalero.cc` no
      longer points at the dead DuckDNS host.
- [ ] `helm lint` clean; no secrets committed.

## Dependencies
- **Blocks:** —
- **Blocked By:** —
- **Related:** PAIML-INFRA-031, PAIML-INFRA-035, PAIML-KEYCLOAK-028
