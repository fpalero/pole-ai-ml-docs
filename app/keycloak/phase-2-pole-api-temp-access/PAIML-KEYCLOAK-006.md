# Ticket: PAIML-KEYCLOAK-006

## Title
[pole_api] Public temporary-access endpoints + lazy activation hook

## Description
Expose unauthenticated endpoints that the login theme calls, and start the 2h window on first use. `POST /api/auth/temporary-access` validates the email, checks the 14-day cooldown, creates the Keycloak user, issues a token, triggers the magic-link email, and returns 202. `POST /api/auth/temporary-access/activate` validates a pending token and starts the window. A lazy hook in `core/auth.py` sets `temp:active:{email}` on the first verified request.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Router `auth/controllers/temporary_access.py`:
  - `POST /api/auth/temporary-access` — body `{email, clientId}`; 422 invalid email; 409 cooldown; 202 on success
  - `POST /api/auth/temporary-access/activate` — body `{token}`; 200 activates window; 404/410 invalid/expired token
- [ ] Wire the router in `main.py` **outside** the `require_*`-guarded includes (public)
- [ ] In `core/auth.py` validation: on first authenticated request with `email_verified` and a matching pending/active temp record, set `temp:active:{email}` (TTL 2h)
- [ ] Enforce per-app role from the token `azp` (`pole-fe`→`fe-user`, `pole-analyst`→`analyst-user`)

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Submitting an email returns 202 and Keycloak emails a verify link
- [ ] Same email within 14 days returns 409
- [ ] Activation returns 200 and sets `temp:active` (2h TTL)
- [ ] Tokens carry the app-mapped role

## Integration Tests to Run (Local Verification)
- [ ] POST the endpoint → Mailpit receives email → click link → API call carries the role

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-008, PAIML-KEYCLOAK-009
- **Blocked By:** PAIML-KEYCLOAK-003, PAIML-KEYCLOAK-005

## Estimated Effort
- [L] (Large 2–4h)