# Ticket: PAIML-KEYCLOAK-007

## Title
[pole_api] Enforce 2h window + cooldown at request time

## Description
Enforce the temporary-access lifecycle at request time: a temp user whose `temp:active:{email}` key has expired is treated as expired (defense in depth alongside the 2h token `exp`), and the 14-day `temp:req` cooldown blocks re-request. Wire env for the new settings into the `pole-api` configmap/secret.

## What to Do (Implementation Steps)
- [ ] Add a request-time check that a verified temp email is within its `temp:active` window (else trigger the expiry path)
- [ ] Confirm `temp:req` (14d) blocks re-request and surfaces a "try again in X" message
- [ ] Add `KEYCLOAK_ADMIN_*` and `TEMP_ACCESS_*` env to `helm/pole-ai/charts/pole-api/templates/configmap.yaml` + `secret.yaml`

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Expired window → temp user rejected/expired at request time
- [ ] Cooldown blocks re-request with a clear message
- [ ] New env wired into the `pole-api` pod

## Integration Tests to Run (Local Verification)
- [ ] Force an expired window and confirm rejection; confirm re-request within 14d is blocked

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-010
- **Blocked By:** PAIML-KEYCLOAK-004, PAIML-KEYCLOAK-006

## Estimated Effort
- [M] (Medium 1–2h)