# Plan Phase 4 — Tests, Docs & Verification

> **Parent plan:** [PLAN.md](../PLAN.md)
> **Status:** ✅ DONE

## Scope

Add automated coverage for the temporary-access flow, integration test harness against a mail sandbox, and update the operational documentation (`docs/ENV_VARS.md`, Keycloak README, this project's docs).

## Tasks

### Unit tests
- [ ] [Testing] `core/temp_access.py` — cooldown (SETNX 14d), token issue/activate, window TTL, role mapping, disable_user, purge idempotency. Mock the Keycloak admin client and Redis.
- [ ] [Testing] Endpoints — `POST /api/auth/temporary-access` (202 / 409 / 422) and `POST /api/auth/temporary-access/activate`.
- [ ] [Testing] Lazy activation hook and expiry enforcement in `core/auth.py`.

### Integration harness
- [ ] [Testing] Configure Keycloak with the **`mailpit` SMTP sandbox** (Deployment + Service in the infra repo, namespace `pole-ai`; SMTP port `1025`, UI `8025`) as the realm SMTP target in the dev stack, so verify-email can be exercised end-to-end without a real SMTP.
- [ ] [Testing] Integration test: request temp access → verify the email arrives in Mailpit's UI → open the magic link → land authenticated → API call carries app role → after expiry, user disabled and owned data purged. Assert the delivered email body/link against the Mailpit REST API.

### Documentation
- [ ] [Documentation] `infrastracture/keycloak/README.md` — document SMTP, `pole-api-admin` client, custom theme, 2h lifespan, and the temp-access flow.
- [ ] [Documentation] `docs/ENV_VARS.md` — new `pole_api` variables (`KEYCLOAK_ADMIN_CLIENT_ID/SECRET`, `KEYCLOAK_ADMIN_ISSUER`, `TEMP_ACCESS_*`).
- [ ] [Documentation] Update this project's `PLAN.md` phase table + `PROJECT_VARS.md`.

## Dependencies

- Phases 1–3 complete and deployed in the dev stack.

## Acceptance Criteria

- [ ] `pixi run test` passes with ≥80% coverage.
- [ ] Integration flow verified end-to-end against Keycloak + Mailpit + Mongo test DBs.
- [ ] `docs/ENV_VARS.md` and `infrastracture/keycloak/README.md` reflect the new configuration.