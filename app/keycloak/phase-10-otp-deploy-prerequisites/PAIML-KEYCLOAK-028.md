# Ticket: PAIML-KEYCLOAK-028

## Title
[Infra][ConfigMap] Wire `FE_BASE_URL` / `ANALYST_BASE_URL` per environment (temp-token app binding) + `BREVO_API_KEY` as a Secret

## Description
Phase 9 made `pole_api` the sole sender of temp-access email: it emails a
**per-app direct link** `https://<host>/?temp_token=xxx` via **Brevo**, and
Keycloak sends nothing on the temp path. Two consequences, both wired in the
`pole-api` ConfigMap (carried over from `PAIML-KEYCLOAK-021`, still open):

1. **`FE_BASE_URL` / `ANALYST_BASE_URL` are the temp-token app binding.** The
   `temp_token` is delivered to exactly one host and presenting it on the other
   app is rejected. The same host map is also what resolves the presenting app
   from the request `Origin` header on `send-code` / `verify-code` (the OTP
   bodies carry no `clientId`). So these two values are **load-bearing security
   configuration**, not cosmetic links.
2. **`BREVO_API_KEY`** is required for both emails; unset, the request endpoint
   answers **503** rather than promising an email it cannot send.

**Decision record (ConfigMap vs Secret) — the split for this ticket:**

| Value | Placement | Why |
| :--- | :--- | :--- |
| `FE_BASE_URL` | **ConfigMap** | A public origin is not a secret. It must be visible/auditable in `kubectl get cm` and editable per environment without touching a secret store. |
| `ANALYST_BASE_URL` | **ConfigMap** | Same. |
| `BREVO_API_KEY` | **Secret** | A credential. Same treatment as `OPENROUTER_API_KEY` / `KEYCLOAK_ADMIN_CLIENT_SECRET`; never in a ConfigMap, never a committed default. |

**Decision record (fail closed, and why the values differ per environment).**
The code defaults are the **local sandbox origins**
(`http://localhost:4200` / `http://localhost:4300`), not the public hosts. That
is deliberate: an environment that forgets these must *fail closed* rather than
mint a production link pointing at a developer's laptop. Documented deployment
values:

| Environment | `FE_BASE_URL` | `ANALYST_BASE_URL` |
| :--- | :--- | :--- |
| demo / staging | `https://demo-ml-agent.duckdns.org` | `https://demo-ai-agent.duckdns.org` |
| local sandbox | `http://localhost:4200` | `http://localhost:4300` |
| prod | (set explicitly — do not assume the demo hosts) | (set explicitly) |

A **wrong** value here fails *quietly* rather than loudly: a staging
`FE_BASE_URL` still pointing at the demo host sends real users a link to the
wrong app. That is why the per-environment table is part of the acceptance
criteria and not just a comment.

## Repository
pole-ai-ml-infra

## What to Do (Implementation Steps)
- [ ] Add `feBaseUrl` / `analystBaseUrl` to `helm/pole-ai/values.yaml` in the
  `pole-api` block, defaulting to the **local sandbox origins** so the shipped
  default is never a public host.
- [ ] Add `FE_BASE_URL` / `ANALYST_BASE_URL` to
  `helm/pole-ai/charts/pole-api/templates/configmap.yaml` (rendered from values,
  with a comment recording that this pair is the temp-token app binding and the
  `Origin` resolution source — not just a link template).
- [ ] Add `brevoApiKey` to `values.yaml` as an **empty/placeholder** default and
  `BREVO_API_KEY` to `charts/pole-api/templates/secret.yaml` `stringData`
  (**not** the ConfigMap).
- [ ] Wire `--set pole-api.brevoApiKey=${{ secrets.BREVO_API_KEY }}` into
  `.github/workflows/deploy-dev.yml` and `deploy-prod.yml`, mirroring the
  existing `openrouterApiKey` pattern. Add the `BREVO_API_KEY` repository secret.
- [ ] Set the per-environment overrides: the local sandbox to
  `http://localhost:4200` / `http://localhost:4300`; demo/staging to the two
  documented duckdns hosts; prod to its own explicit origins. Do **not** inherit
  the demo hosts in prod.
- [ ] Confirm the ConfigMap change actually **restarts** the `pole-api` pods.
  The FE/analyst env ConfigMaps already have a rollout trigger
  (`PAIML-INFRA-035`); confirm the same trigger covers the `pole-api` env
  ConfigMap, or the new values will be rendered but never read by a running pod.
- [ ] Re-check that the `pole-api` Deployment consumes the ConfigMap **and** the
  Secret (`envFrom` or equivalent) for these keys.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `FE_BASE_URL` / `ANALYST_BASE_URL` are present in the `pole-api` **ConfigMap**
  and match the per-environment table in every target environment.
- [ ] `BREVO_API_KEY` is present in the `pole-api` **Secret**, absent from every
  ConfigMap, and absent from git (placeholder only in `values.yaml`).
- [ ] `POST /api/auth/temporary-access` in a deployed environment no longer
  answers 503 and returns **202** with a Brevo link whose host equals that
  environment's `FE_BASE_URL` / `ANALYST_BASE_URL` (assert the host in the
  emailed link — the value being set in the CM is not the same as it being used).
- [ ] `send-code` / `verify-code` `Origin` resolution resolves against the
  deployed host map: an `Origin` matching the configured host is **not** a 403,
  and a token presented on the *other* app's origin still is.
- [ ] `pole-api` pods were observed restarted/recreated with the new values.

## Integration Tests to Run (Local Verification)
- [ ] `helm lint helm/pole-ai` + `helm upgrade --dry-run` — both URLs render in
  the ConfigMap, the Brevo key renders in the Secret, neither leaks into the
  ConfigMap.
- [ ] `kubectl -n pole-ai get cm pole-ai-pole-api-env` shows the two URLs;
  `kubectl get secret pole-ai-pole-api-secret` shows `BREVO_API_KEY` (value
  redacted in any evidence).
- [ ] Full local request against a fresh address → 202 → the Mailpit-captured
  link host matches the configured local `FE_BASE_URL` / `ANALYST_BASE_URL`.
- [ ] Cross-app negative: a `pole-fe` token presented with the `pole-analyst`
  `Origin` is still rejected (proves the binding is live, not just present).

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-024 (QA gate)
- **Blocked By:** None (independent of 026/027/029)

## Estimated Effort
- [M] (Medium 2–4h)
