# Ticket: PAIML-KEYCLOAK-021

## Title
[Keycloak] Passwordless temp-user creation + pole_api direct-link email (no temporary flag, no Keycloak email)

## Description
`POST /api/auth/temporary-access` still creates temp users with
`temporary: True` and fires Keycloak's `execute-actions-email` verify link.
That couples temp onboarding to the password-setup UX and to realm SMTP. This
ticket cuts both: create the user **without** the temporary flag (passwordless
UX — the user never sets or sees a password; permanent users keep password
login unchanged) and have **pole_api send the per-app direct link via Brevo**
instead of Keycloak sending anything.

Why passwordless + pole_api-owned delivery (decision record):
- **Kill password-setup friction.** `temporary: True` forces a password action
  on first login; temp users should never see a password screen.
- **One sender.** Brevo (`no-reply@fpalero.cc`, EN+ES) already ships Phase 5
  templates; Keycloak sends NOTHING on the temp path after this ticket.
- **Token stays app-bound.** The link carries `?temp_token=xxx` for exactly one
  host (`pole-fe` → `https://demo-ml-agent.duckdns.org`, `pole-analyst` →
  `https://demo-ai-agent.duckdns.org`); cross-app presentation is rejected.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Remove `temporary: True` from temp-user creation in
  `app/pole_api/src/core/temp_access.py` (`KeycloakAdminClient`): create with a
  hidden random password (server-side only, never emailed/returned/logged),
  `emailVerified=false`, no required actions; assign the per-app role
  (`pole-fe`→`fe-user`, `pole-analyst`→`analyst-user`).
- [ ] Delete the `execute-actions-email` / `send_verify_email` call on the temp
  path (Keycloak sends nothing); keep realm SMTP for non-temp flows.
- [ ] Build the per-app direct link at request time from the host map
  (`pole-fe` → `https://demo-ml-agent.duckdns.org/?temp_token=xxx`,
  `pole-analyst` → `https://demo-ai-agent.duckdns.org/?temp_token=xxx`) and
  send it via Brevo (sender `no-reply@fpalero.cc`, EN+ES templates by locale).
- [ ] Persist `temp:req:{email}:{app}` (14d) + `temp:token:{hash}` =
  `{email, app, state: pending}` (24h) exactly as today; keep 409 cooldown and
  422 validation behavior.
- [ ] On any failure after partial writes (Brevo send failure, admin error),
  roll back via `repo.clear` so no orphaned `temp:*` keys or half-created
  users remain.
- [ ] Add/extend unit + integration tests: creation payload has no temporary
  flag and no required actions; Brevo link email asserted per app/host;
  Keycloak email API never called; rollback clears partial state.
- [ ] `pixi run test` stays ≥80% coverage.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Temp users are created without `temporary: True`, with a hidden random
  password that is never emailed, shown, or logged.
- [ ] Permanent-user password login is unchanged.
- [ ] The temp path triggers zero Keycloak emails; the Brevo link email arrives
  from `no-reply@fpalero.cc` (EN+ES) with the correct per-app host.
- [ ] `temp:token:{hash}` is bound to one app; presenting it for the other app
  is rejected.
- [ ] Brevo/admin failure leaves no orphaned `temp:*` keys (rollback via
  `repo.clear` verified).

## Integration Tests to Run (Local Verification)
- [ ] Request matrix (`pole-fe` / `pole-analyst`): 202 + Mailpit/Brevo-sandbox
  link email with the right host; Keycloak email endpoint call count = 0.
- [ ] Cooldown regression: re-request within 14d → 409, no new token/email.
- [ ] Failure injection (Brevo 500): partial `temp:*` keys rolled back.
- [ ] Full `pixi run test` green with ≥80% coverage.

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-022
- **Blocked By:** None (root of Phase 9; builds on merged phases 1–8 + Phase 5 Brevo)

## Estimated Effort
- [M] (Medium 3–5h)
