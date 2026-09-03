# Ticket: PAIML-KEYCLOAK-013

## Title
[Infrastructure] Realm SMTP via Brevo (verify-email magic-link delivery)

## Description
Point the Keycloak realm SMTP at Brevo so verify-email magic links are
delivered in real environments.

<!-- Cross-repo note: primary delivery is the infra repo (realm + chart);
     this file is the docs-repo merge record. No prior ticket body existed;
     reconstructed from the team-lead handover — scope states only those facts. -->
## Repository
pole-ai-ml-infra (delivery) / pole-ai-ml-docs (this record)

## What to Do (Implementation Steps)
- [x] Configure realm `smtpServer` for Brevo (host/port/auth/from via values/Secret)
- [x] Verify verify-email delivery end-to-end

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] Keycloak sends verify-email emails via Brevo SMTP

## Merge record
- Infra PR #22 — MERGED (commit `1e9f381` line)

## Integration Tests to Run (Local Verification)
- [ ] N/A (merge record; delivery verified in the infra repo)

## Dependencies
- **Blocks:** None
- **Blocked By:** PAIML-KEYCLOAK-001 (realm SMTP block)

## Estimated Effort
- [S] (Small < 1h)
