# Ticket: PAIML-KEYCLOAK-010

## Title
[pole_api] Expiry sweeper + lazy expiry trigger

## Description
Schedule the purge and trigger it lazily. A periodic sweeper finds expired `temp:active:{email}` keys and runs `TempAccessPurgeService` + disables the user. A lazy check on the next authenticated request for an expired temp email triggers the purge as defense in depth.

## What to Do (Implementation Steps)
- [ ] Periodic sweeper (interval < 2h window) that scans expired `temp:active` keys and runs the purge
- [ ] Lazy expiry: on an authenticated request for a temp email whose `temp:active` key has expired, trigger the purge
- [ ] Align sweeper interval, `temp:active` TTL, and token `exp` to avoid mid-session races

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Expired windows are purged automatically by the sweeper
- [ ] Lazy path also triggers the purge if the sweeper has not yet run
- [ ] No race disables a user mid-session within the window

## Integration Tests to Run (Local Verification)
- [ ] Shorten the window in test, wait past expiry, confirm the purge runs and the user is disabled

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-011
- **Blocked By:** PAIML-KEYCLOAK-007, PAIML-KEYCLOAK-009

## Estimated Effort
- [M] (Medium 1–2h)