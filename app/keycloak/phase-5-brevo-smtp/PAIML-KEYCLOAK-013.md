# Ticket: PAIML-KEYCLOAK-013

## Title
[Keycloak] Send temp-access emails via Brevo SMTP relay (staging/prod)

## Description
Keycloak realm SMTP currently points at the in-cluster Mailpit sandbox (dev only). Production/real email should go through the Brevo relay so temp-access magic links are actually delivered:

- **Host:** `smtp-relay.brevo.com`
- **Port:** `587` (STARTTLS)
- **Login (username):** `b7c0c6001@smtp-brevo.com`
- **Password (SMTP key):** secret — referenced via Helm Secret + GitHub Actions secret, NEVER committed.
- **From:** `no-reply@fpalero.cc` (display name "Pole AI")
- **Mailpit stays the local default** (`values-local.yaml` unchanged); Brevo is the staging/prod override (`values-prod.yaml` + CI `--set`).

## What to Do (Implementation Steps)
- [x] Step 1: Make the SMTP `host` a chart value in `infrastracture/helm/pole-ai/charts/keycloak/templates/configmap.yaml` (currently hardcoded to the Mailpit service name) — default resolves to the Mailpit service for local.
- [x] Step 2: Verify the chart renders `host/port/from/fromDisplayName/auth/starttls/ssl/user/password` from `.Values.smtp.*` (template already supports auth/starttls).
- [x] Step 3: Add a Brevo SMTP block to `infrastracture/helm/pole-ai/values-prod.yaml` (host `smtp-relay.brevo.com`, port `587`, from `no-reply@fpalero.cc`, auth enabled, username `b7c0c6001@smtp-brevo.com`, password via Secret reference placeholder) and to the realm source `infrastracture/keycloak/realm-pole-ai.json` if it carries SMTP.
- [x] Step 4: Wire the SMTP key as a GitHub Actions secret (e.g. `BREVO_SMTP_KEY`) and pass it via `--set keycloak.smtp.auth.password=${{ secrets.BREVO_SMTP_KEY }}` in the deploy workflow, mirroring how `openrouterApiKey` is handled.
- [x] Step 5: Deploy local k3s first (Mailpit still works), then staging; verify a real email arrives via Brevo on a temp-access request.
- [x] Step 6: Update docs: `infrastracture/keycloak/README.md` (SMTP section) + `docs/ENV_VARS.md` if relevant.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] Local deploy still sends to Mailpit (`values-local.yaml` unchanged).
- [x] Staging Keycloak realm `smtpServer` points at `smtp-relay.brevo.com:587` with auth; a temp-access request produces a real delivered email from `no-reply@fpalero.cc`.
- [x] The SMTP key value is NOT committed anywhere in git (only referenced as a secret).

## Integration Tests to Run (Local Verification)
- [x] Local k3s: `POST /api/auth/temporary-access` with a fresh email → 202 + email in Mailpit (unchanged).
- [x] Staging: same request → 202 + email actually delivered via Brevo (not Mailpit).

## Merge record
- Infra PR #22 — MERGED (commit `1e9f381` line).

## Dependencies
- **Blocks:** None
- **Blocked By:** None (extends the Phase 1 realm SMTP block, PAIML-KEYCLOAK-001)

## Estimated Effort
- [M] (Medium 2–4h)
