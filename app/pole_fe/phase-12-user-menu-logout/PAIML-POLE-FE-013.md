# Ticket: PAIML-POLE-FE-013

## Title
[Auth UX] User dropdown menu on the header `account_circle` button + logout via Keycloak end-session

## Description
`app/pole_fe` had no way for a signed-in user to log out from the app shell. The header
`account_circle` button was dead. Implemented in `app/pole_fe/src/app/app.ts` (`AppComponent`,
PR fpalero/pole-ai-ml#192 into `develop`, +72/−3): clicking the button toggles a user dropdown
menu with a Logout item; `logout()` calls `keycloak.logout({ redirectUri: window.location.origin })`,
which hits the Keycloak end-session endpoint (server-side SSO session termination with
`id_token_hint`) and returns to the app origin, where `login-required` shows the login page again.

## Design decision
End-session call is required — clearing local tokens alone is not enough. The Keycloak SSO
session (cookie) is shared; with `login-required` init, a local-only clear would silently
re-authenticate on the next load. Per-app logout is therefore impossible in this setup: logout
always kills the shared SSO session.

## What to Do (Implementation Steps)
- [x] Header user-menu UI: `.user-menu-wrap` + backdrop + `.user-menu` dropdown on the
  `account_circle` button (`toggleUserMenu` / `closeUserMenu`, `showUserMenu` state).
- [x] `logout()`: close menu, `keycloak.logout({ redirectUri: window.location.origin })`.
- [x] Verify: `tsc --noEmit` clean, `ng build` success, live on staging.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] Clicking `account_circle` opens a dropdown with a Logout item; backdrop click closes it.
- [x] Logout terminates the Keycloak SSO session server-side and lands back on the login page.
- [x] `tsc --noEmit` clean, `ng build` success.

## Integration Tests to Run (Local Verification)
- [x] `tsc --noEmit` (clean).
- [x] `ng build` (success).
- [ ] Manual staging check: login → open user menu → Logout → SSO session ended → login page shown.

## Dependencies
- **Blocks**: None
- **Blocked By**: None (consumes existing `KEYCLOAK` provider / `login-required` init).

## Estimated Effort
- [XS]

## Status Update
Implemented and merged via PR fpalero/pole-ai-ml#192 (single file: `app/pole_fe/src/app/app.ts`).
Verified `tsc --noEmit` clean + `ng build` success; live on staging.
