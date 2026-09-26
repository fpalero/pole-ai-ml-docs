# Ticket: PAIML-KEYCLOAK-026

## Title
[Infra][Secret] Provision `TEMP_ACCESS_OTP_PEPPER` per environment as a Helm Secret (never hardcoded)

## Description
`TEMP_ACCESS_OTP_PEPPER` is the server-side secret mixed into the 6-digit OTP hash
(peppered SHA-256). `pole_api` **fails closed** without it: `send-code` and
`verify-code` answer **503**. This is deliberate — a code hashed with no pepper
would be brute-forceable offline from a Redis dump.

The pepper is a Phase 9 (022) code requirement, but provisioning is **not** code:
it is a `pole-ai-ml-infra` concern. As of this ticket the variable is wired in
**neither** the `pole-api` ConfigMap nor the `pole-api` Secret, so **every**
deployed environment — local sandbox, dev/staging, and prod — answers 503 on the
OTP endpoints. Only the local QA run of `PAIML-KEYCLOAK-024` (in which the
pepper is injected out-of-band) can pass today.

**Decision record (Secret vs ConfigMap).** Secrets in this chart are rendered
into the `pole-api` Secret as `stringData` and injected at deploy time via
`--set pole-api.<key>=${{ secrets.<NAME> }}` (the same pattern as
`openrouterApiKey` / `keycloakAdminClientSecret` in
`.github/workflows/deploy-{dev,prod}.yml`). The pepper follows it:
- **Secret, not ConfigMap.** A ConfigMap is world-readable to anything that can
  read pod specs in the namespace and is committed in plain sight in
  `values.yaml`; the pepper's entire purpose is to make an offline OTP
  brute-force infeasible, so it must never be one of those.
- **Never hardcoded, never a committed default.** `values.yaml` may only carry a
  non-functional placeholder (mirroring the existing
  `keycloakAdminClientSecret: "admin-secret-placeholder"`), so a missing
  `--set` fails closed at the app (503) instead of silently hashing with a
  publicly-known pepper. **A committed pepper is a broken pepper.**
- **Per environment, not shared.** A pepper reused across environments lets a
  code captured in one environment be validated against another's `temp:code`
  hash; the random value is generated per environment and stored in that
  environment's secret store.

## Repository
pole-ai-ml-infra

## What to Do (Implementation Steps)
- [ ] Add `tempAccessOtpPepper` to `helm/pole-ai/values.yaml` under the
  `pole-api` block as an **empty/placeholder** default (no real secret), with a
  comment stating it is a fail-closed placeholder and must be injected per
  environment.
- [ ] Add `TEMP_ACCESS_OTP_PEPPER: {{ .Values.tempAccessOtpPepper | quote }}`
  to `helm/pole-ai/charts/pole-api/templates/secret.yaml` `stringData` (the
  existing Secret, which is already mounted by the Deployment) — **not** to
  `configmap.yaml`.
- [ ] Wire `--set pole-api.tempAccessOtpPepper=${{ secrets.TEMP_ACCESS_OTP_PEPPER }}`
  into `.github/workflows/deploy-dev.yml` and `deploy-prod.yml`, next to the
  existing `pole-api.openrouterApiKey` / `keycloakAdminClientSecret` `--set`
  lines, so the value is never committed and only reaches the cluster through
  the Actions secret store.
- [ ] Add the `TEMP_ACCESS_OTP_PEPPER` repository secret in the GitHub Actions
  secret store (32+ random bytes per environment, e.g. `openssl rand -base64 32`).
  Document where each environment's value lives.
- [ ] Verify the local sandbox path: if local is provisioned via
  `values-local.yaml`, inject a locally-generated pepper there **as an ignored
  local override** (or an explicit `--set`) — never a committed real value.
- [ ] Confirm the Deployment restart picks the new Secret env up (Secret env
  changes do **not** trigger a rollout the way a ConfigMap checksum-annotation
  does — confirm the pod was actually recreated/restarted, or add the same
  rollout trigger already used for the FE/analyst env ConfigMap).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `TEMP_ACCESS_OTP_PEPPER` is present in the `pole-api` **Secret** in each
  target environment, and absent from every ConfigMap.
- [ ] No real pepper value is committed anywhere: `values.yaml` carries only a
  placeholder (repo-wide secret scan on the diff is clean).
- [ ] Deploy workflows pass the pepper from the Actions secret store; the value
  never appears in workflow logs.
- [ ] `POST /api/auth/temporary-access/send-code` on a **valid pending token**
  no longer answers 503 in that environment (it may still answer 429/404/403 —
  those are the other tickets' concerns).
- [ ] The pod is confirmed running with the pepper in its environment.

## Integration Tests to Run (Local Verification)
- [ ] `helm lint helm/pole-ai` and `helm upgrade --dry-run` render the Secret
  with the key present and no `TEMP_ACCESS_OTP_PEPPER` in the ConfigMap.
- [ ] `kubectl -n pole-ai get secret pole-ai-pole-api-secret` lists
  `TEMP_ACCESS_OTP_PEPPER`; the ConfigMap does **not**.
- [ ] Negative check: with the pepper unset, `send-code` answers **503**
  (confirms the fail-closed contract still holds and was not bypassed).
- [ ] With the pepper set, `send-code` advances past 503 (real delivery is
  `PAIML-KEYCLOAK-024`'s scope).

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-024 (QA gate), PAIML-KEYCLOAK-028
- **Blocked By:** None (independent of 027/029; 027 is the sibling that makes the
  reachability check meaningful)

## Estimated Effort
- [S] (Small 1–2h)
