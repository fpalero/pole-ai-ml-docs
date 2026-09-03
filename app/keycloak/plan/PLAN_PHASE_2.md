# Plan Phase 2 — pole_api Temporary-Access Orchestration

> **Parent plan:** [PLAN.md](../PLAN.md)
> **Status:** ✅ DONE

## Scope

Implement the backend that powers temporary access: a Keycloak admin client, a Redis-backed repository for cooldown/activation state, a public endpoint that creates the temp user and triggers the magic-link email, lazy activation, and app→role mapping.

## Context

The custom login theme (Phase 1) POSTs `{email, clientId}` to pole_api. This phase turns that into a full magic-link flow: create a Keycloak user (random password, `VERIFY_EMAIL` required action, per-app role), have Keycloak email a verify link that logs the user in, track the 2-week cooldown and the 2-hour activated window in Redis.

## Redis keys

| Key | Value | TTL | Purpose |
| :-- | :-- | :-- | :-- |
| `temp:req:{email}` | `1` | 14 days | Cooldown — blocks re-request until it expires ("email persisted 2 weeks") |
| `temp:token:{hash}` | `{email, app, state: pending}` | 24h | Magic-link token state until first use |
| `temp:active:{email}` | `{app, ts}` | 2 hours | Set on first activation — starts the 2h window |

## Tasks

### Settings & Keycloak admin client
- [ ] [Application] Add settings to `core/config.py`: Keycloak admin client id/secret/issuer, `TEMP_ACCESS_COOLDOWN_S` (14d), `TEMP_ACCESS_WINDOW_S` (2h), `TEMP_ACCESS_TOKEN_TTL_S` (24h), app→role map (`pole-fe`→`fe-user`, `pole-analyst`→`analyst-user`), FE base URLs.
- [ ] [Infrastructure] `core/temp_access.py` — `KeycloakAdminClient`: obtain an admin token via service-account (client-credentials) grant; `create_or_find_user(email)` (random password, `emailVerified=false`, `VERIFY_EMAIL` required action, assign role); `send_verify_email(user_id, client_id)` (execute-actions-email); `disable_user(user_id)`.

### Redis repository
- [ ] [Infrastructure] `core/temp_access.py` — `TempAccessRepository` (async Redis): `request(email, app)` (SETNX `temp:req`, TTL 14d), `issue_token(token, email, app)` (pending), `activate(token)` (mark active + set `temp:active` TTL 2h), `is_active(email)`, `clear()`.

### Endpoints
- [ ] [Presentation] Router `auth/controllers/temporary_access.py`:
  - `POST /api/auth/temporary-access` — body `{email, clientId}`. **Public** (no `require_*`). Validates email; 409 if cooldown active; else creates user, issues token, triggers email, returns `202 {message}`.
  - `POST /api/auth/temporary-access/activate` — body `{token}`. Validates the pending token in Redis, marks active (starts 2h).
- [ ] [Presentation] Wire the router in `main.py` **outside** the `require_*`-guarded includes so it is unauthenticated.

### Lazy activation + enforcement hook
- [ ] [Application] In `core/auth.py` validation: on the first authenticated request whose token has `email_verified` and a matching pending/active temp record, set `temp:active:{email}` (TTL 2h). This starts the window on first use without an FE change.
- [ ] [Application] Enforce the per-app role from the token `azp` (`pole-fe`→`fe-user`, `pole-analyst`→`analyst-user`).

## Dependencies

- Phase 1: `pole-api-admin` client, realm SMTP, theme POST target.
- **`mailpit` SMTP sandbox** (Phase 1 / infra repo, namespace `pole-ai`): a `mailpit` Deployment + Service in `infrastracture/` that is the realm SMTP target for Keycloak verify-email delivery in the dev stack (no external SMTP required). The `/api/auth/temporary-access` 202 path depends on Keycloak being able to deliver the magic-link email through Mailpit.
- `settings.redis_url` (already present) and the in-cluster Redis.

## Acceptance Criteria

- [ ] Submitting an email returns 202 and Keycloak emails a verify link.
- [ ] Re-submitting the same email within 14 days returns 409.
- [ ] Clicking the link logs the user in; first verified API call sets the 2h active window.
- [ ] Tokens carry the app-mapped role; `pole_api` enforces it per slice.
- [ ] Unit tests cover cooldown, activation, role mapping, invalid email.