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
- [x] Remove `temporary: True` from temp-user creation in
  `app/pole_api/src/core/temp_access.py` (`KeycloakAdminClient`): create with a
  hidden random password (server-side only, never emailed/returned/logged),
  `emailVerified=false`, no required actions; assign the per-app role
  (`pole-fe`→`fe-user`, `pole-analyst`→`analyst-user`).
- [x] Delete the `execute-actions-email` / `send_verify_email` call on the temp
  path (Keycloak sends nothing); keep realm SMTP for non-temp flows.
- [x] Build the per-app direct link at request time from the host map
  (`pole-fe` → `https://demo-ml-agent.duckdns.org/?temp_token=xxx`,
  `pole-analyst` → `https://demo-ai-agent.duckdns.org/?temp_token=xxx`) and
  send it via Brevo (sender `no-reply@fpalero.cc`, EN+ES templates by locale).
- [x] Persist `temp:req:{email}:{app}` (14d) + `temp:token:{hash}` =
  `{email, app, state: pending}` (24h) exactly as today; keep 409 cooldown and
  422 validation behavior.
- [x] On any failure after partial writes (Brevo send failure, admin error),
  roll back via `repo.clear` so no orphaned `temp:*` keys or half-created
  users remain.
- [x] Add/extend unit + integration tests: creation payload has no temporary
  flag and no required actions; Brevo link email asserted per app/host;
  Keycloak email API never called; rollback clears partial state.
- [x] `pixi run test` stays ≥80% coverage.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] Temp users are created without `temporary: True`, with a hidden random
  password that is never emailed, shown, or logged.
- [x] Permanent-user password login is unchanged.
- [x] The temp path triggers zero Keycloak emails; the Brevo link email arrives
  from `no-reply@fpalero.cc` (EN+ES) with the correct per-app host.
- [x] `temp:token:{hash}` is bound to one app; presenting it for the other app
  is rejected.
- [x] Brevo/admin failure leaves no orphaned `temp:*` keys (rollback via
  `repo.clear` verified).

## Integration Tests to Run (Local Verification)
- [x] Request matrix (`pole-fe` / `pole-analyst`): 202 + Mailpit/Brevo-sandbox
  link email with the right host; Keycloak email endpoint call count = 0.
- [x] Cooldown regression: re-request within 14d → 409, no new token/email.
- [x] Failure injection (Brevo 500): partial `temp:*` keys rolled back.
- [x] Full `pixi run test` green with ≥80% coverage.

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-022
- **Blocked By:** None (root of Phase 9; builds on merged phases 1–8 + Phase 5 Brevo)

## Estimated Effort
- [M] (Medium 3–5h)

---

## Close-Out Note (implementation record)

**Status:** ✅ DONE — implemented in `pole-ai-ml` on
`feature/PAIML-KEYCLOAK-021-passwordless-link-creation` (base `develop`).

### What shipped

| Area | Change |
|---|---|
| `core/temp_access.py` | `create_or_find_user` no longer sends `temporary: True` and no longer sends `requiredActions`. The random password stays a **write-only secret** (never returned, logged, emailed or shown). `send_verify_email` is **kept** and marked deprecated — realm SMTP still serves non-temp self-service flows. |
| `core/email/link_templates.py` (new) | Per-app host map + EN/ES template rendering. Host map reads the pre-existing `fe_base_url` / `analyst_base_url` settings, so the sandbox can override it. |
| `core/email/brevo_email.py` (new) | Brevo `/v3/smtp/email` transport; sender `no-reply@fpalero.cc`; never logs the API key, the payload or the token. |
| `auth/controllers/temporary_access.py` | Request path creates the user, issues the token, then emails the per-app link via Brevo. **Keycloak email API is never called.** 503 when `BREVO_API_KEY` is unset (never a 202 for an unsent email). |
| `core/temp_access.py` → `TempAccessRepository.clear` | **Bug fix:** `clear` built a `temp:token:*` pattern and never used it, so a rollback stranded a 24h-pending token. Now `_delete_tokens_for(email, app)` deletes the pending token for that email+app, shared with `clear_email`. |

### Decisions taken at implementation time

1. **Host map (confirmed with the user).** `pole-fe` →
   `https://demo-ml-agent.duckdns.org`, `pole-analyst` →
   `https://demo-ai-agent.duckdns.org`. These are the **deployment** values of
   `FE_BASE_URL` / `ANALYST_BASE_URL`. The **code defaults stay on the local
   sandbox origins** (`https://pole-fe.local` / `https://pole-analyst.local`):
   these settings are the temp-token *app binding*, so an environment that
   forgets to set them must fail closed rather than silently mint links to a
   public host. Every environment (dev/staging/prod) must set both explicitly;
   the helm chart does not yet, which is a prerequisite tracked below.
2. **`POST /api/auth/temporary-access/activate` is KEPT as a deprecated shim**
   (confirmed with the user), not deleted this phase. It is flagged
   `deprecated=True` in OpenAPI so clients see the warning. Phase 9 ticket 022
   supersedes it with `send-code` / `verify-code`; the endpoint must be removed
   in 022 (or when the Phase 2 FE flow is confirmed migrated).
3. **Brevo is an HTTP API, not SMTP.** The Phase 5 work pointed the *Keycloak
   realm SMTP* at Brevo; there was no `pole_api` mail code to reuse, so this
   ticket introduces the first one. Consequently the old
   `test_temp_access_integration_mailpit.py` (which asserted a Keycloak realm-SMTP
   email) was **replaced** by `test_temp_access_integration_brevo.py`, which
   drives the real controller + real Brevo transport against a local HTTP stub
   and real Redis. Mailpit is no longer on this path.
4. **503 (not 500) when `BREVO_API_KEY` is missing**, and **not** a silent 202.
5. The `locale` body field was added (optional, `en`/`es`, defaults to
   `DEFAULT_EMAIL_LOCALE`) so the FE/login theme can pick a language; unknown
   locales fall back to English.

### Acceptance criteria — verified

- [x] Temp users created **without** `temporary: True` and **without** required
      actions; hidden random password never emailed, returned or logged
      (asserted against the real create payload and `caplog`).
- [x] Permanent-user password login unchanged — an existing account is reused
      with no credential write at all.
- [x] Zero Keycloak emails on the temp path; Brevo link email from
      `no-reply@fpalero.cc` in EN + ES with the correct per-app host
      (parametrised over both apps, and the other app's host is asserted absent).
- [x] `temp:token:{hash}` bound to one app; cross-app presentation rejected.
- [x] Brevo/admin failure leaves no orphaned `temp:*` keys (rollback via
      `repo.clear` verified, including the cooldown being released for retry).
- [x] 409 cooldown and 422 validation preserved.

### Test evidence

| Suite | Result |
|---|---|
| `pixi run test-api` (CI scope) | **1783 passed**, 0 failed |
| New/changed temp-access suites | 240 passed |
| Integration (`test_temp_access_integration_brevo.py`) | 7 passed against real Redis + real HTTP Brevo stub |
| Coverage of the changed modules (`core.email`, `core.temp_access`, `auth.controllers.temporary_access`) | **90%** total; `core/email` package **94%** |
| Review follow-ups (closer guards, dead template API, fail-closed host map) | 10 further regression tests |
| `pixi run test` (ML package) | 677 passed, **82.42%** (≥80% gate) |
| `ruff check` on every touched file | clean |

### Follow-ups for PAIML-KEYCLOAK-022

- Remove the deprecated `POST .../activate` once the FE no longer calls it.
- `BREVO_API_KEY` must be provisioned from a Helm Secret in
  `pole-ai-ml-infra` before this path is live (an unset key answers 503).
- **Infra (blocking for rollout):** the `pole-api` ConfigMap sets
  `TEMP_ACCESS_*` but **not** `FE_BASE_URL` / `ANALYST_BASE_URL` /
  `BREVO_API_KEY`. All three must be added per environment
  (`pole-ai-ml-infra`) or the endpoint will answer 503 / link to the sandbox
  hosts. `app/pole_api/.env.example` now documents the whole block.
- `emailVerified` is still created `false` and nothing flips it yet; ticket 022
  owns that at `verify-code`.
- The stored `app` in `temp:token:{hash}` is what 022 must compare against the
  presenting app to answer `403 TEMP_TOKEN_APP_MISMATCH`.
