# Ticket: PAIML-KEYCLOAK-011

## Title
[Testing] Unit + integration tests for temporary access

## Description
Add automated coverage: unit tests for cooldown, activation, role mapping, disable_user, and purge idempotency (mock Keycloak admin client + Redis); endpoint tests for 202/409/422; integration harness with a mail sandbox (Mailpit) so the full flow is exercised end-to-end against `pole_api_test` / `skeleton_data_test`.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Unit tests: `core/temp_access.py` (cooldown SETNX 14d, token issue/activate, window TTL, role map, disable_user, purge idempotency) with mocks
- [ ] Unit tests: `POST /api/auth/temporary-access` (202 / 409 / 422) and `POST /api/auth/temporary-access/activate`
- [ ] Unit tests: lazy activation hook + expiry enforcement in `core/auth.py`
- [ ] Integration: point Keycloak's realm SMTP at the `mailpit` sandbox (infra repo Deployment + Service, namespace `pole-ai`, SMTP `1025`, UI `8025`); request temp access → Mailpit receives email → open link → authenticated → API call carries role → after expiry, user disabled + data purged

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pixi run test` passes with ≥80% coverage
- [ ] End-to-end temp-access flow verified against Keycloak + Mailpit + Mongo test DBs

## Integration Tests to Run (Local Verification)
- [ ] Full happy path + expiry purge with shortened window

## Dependencies
- **Blocks:** None
- **Blocked By:** PAIML-KEYCLOAK-006, PAIML-KEYCLOAK-010

## Estimated Effort
- [L] (Large 2–4h)