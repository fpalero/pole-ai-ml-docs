# Ticket: PAIML-KEYCLOAK-016

## Title
[Keycloak] Rollout + live SMTP verify + magic-link e2e gate

## Description
Roll out the Phase 7 theme fix and prove the live state matches the repo: live theme bytes equal repo files, live realm SMTP (via Admin API) is **Brevo** (live was Mailpit while ConfigMap had Brevo; Brevo 525 seen 22:11), and the end-to-end magic-link flow returns **202 + inbox delivery + success toast** via both FE hosts.

## Repository
pole-ai-ml-infra

## What to Do (Implementation Steps)
- [ ] Rollout restart Keycloak and wait for rollout complete (checksum annotation from PAIML-KEYCLOAK-015 forces it on theme/realm change).
- [ ] Verify live served theme bytes match repo (`login.ftl`, `temporary-access.js` sizes/hashes) — no stale pod.
- [ ] Verify live realm SMTP via Keycloak Admin API equals Brevo (`smtp-relay.brevo.com:587`, auth, from `no-reply@fpalero.cc`); resolve the Mailpit-vs-Brevo drift and confirm no Brevo 525 on send.
- [ ] E2E gate via **both** FE hosts: magic-link submit to `fpalero1986@gmail.com` → HTTP `202`, real inbox delivery, success toast rendered; invalid email → inline error.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Keycloak rollout complete on the fixed revision.
- [ ] Live theme bytes match repo files (stale-theme check green).
- [ ] Live SMTP via Admin API = Brevo; test send delivers with no 525.
- [ ] E2E via both FE hosts to `fpalero1986@gmail.com`: `202` + inbox + success toast.

## Integration Tests to Run (Local Verification)
- [ ] Live-vs-repo byte/hash comparison for theme assets (record both sizes).
- [ ] Admin API `GET realm smtpServer` dump matches Brevo expectation (secret redacted).
- [ ] E2E POST evidence per FE host (status code + inbox + toast screenshot/note).

## Dependencies
- **Blocks:** None
- **Blocked By:** PAIML-KEYCLOAK-015

## Estimated Effort
- [S] (Small 1–2h)
