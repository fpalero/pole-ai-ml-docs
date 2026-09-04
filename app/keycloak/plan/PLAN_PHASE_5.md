# Plan Phase 5 — Brevo SMTP

> **Parent plan:** [PLAN.md](../PLAN.md)
> **Status:** ✅ DONE

> **Note:** no Phase 5 doc existed in the docs repo; this file is a minimal
> merge record reconstructed from the team-lead handover (infra PR #22).
> Scope below states only handover facts — nothing invented.

## Scope

Point the Keycloak realm SMTP (`smtpServer`) at Brevo so verify-email
magic links are delivered in real environments (replacing the Mailpit-only
dev sandbox from Phase 1).

## Merge record

- Infra PR #22 — MERGED (commit `1e9f381` line).
- Ticket: `phase-5-brevo-smtp/PAIML-KEYCLOAK-013.md`.

## Dependencies

- Phase 1: realm `smtpServer` block + `pole-api-admin` client.

## Acceptance Criteria

- [x] Realm sends verify-email via Brevo SMTP (merged as infra PR #22).
