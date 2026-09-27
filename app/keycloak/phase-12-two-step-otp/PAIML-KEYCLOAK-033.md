# Ticket: PAIML-KEYCLOAK-033

## Title
[pole_fe] Athlete app verification UI with 6-digit input, status notice, and resend cooldown

## Description
Build the client-side second-factor OTP verification interface in `pole_fe` (Athlete Angular application).
When an athlete navigates to the temporary access activation route (`/activate` or `/verify-otp`) from the magic link, the page should present a 6-digit verification input form, display a clear expiration timer (10 minutes), show informative status notices, handle clipboard paste, and offer a resend action with a 60-second cooldown timer.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Create/update the activation component in `pole_fe` (e.g. `src/app/auth/temp-access-verify/` or `/activate`):
  - 6 individual digit input boxes or masked single input formatted as `XXX-XXX` with numeric keypad support (`inputmode="numeric"`).
  - Support auto-advance on typing and auto-split on paste event.
- [ ] Display an active countdown timer reflecting the 10-minute OTP expiration window.
- [ ] Implement a "Resend Code" button bound to a 60-second cooldown timer that disables the button and shows remaining seconds.
- [ ] Handle submission to `POST /api/auth/temporary-access/verify-otp` with loading spinner and disabled state.
- [ ] Display clear error alerts for invalid codes, expired codes, and exceeded attempts with guidance to request a new code.
- [ ] On success, store received session tokens, redirect to the athlete dashboard (`/athlete` or home), and display a welcome toast with the 2-hour temporary access duration notice.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] 6-digit input component functions smoothly with typing, backspace, and paste support.
- [ ] 10-minute timer counts down accurately and indicates expiration when elapsed.
- [ ] Resend button enforces 60-second client-side cooldown and triggers OTP dispatch.
- [ ] Form submission validates OTP and navigates athlete into the app upon success.
- [ ] Unit tests for the component pass with ≥80% coverage.

## Integration Tests to Run (Local Verification)
- [ ] End-to-end component test for digit entry, paste handling, and submit payload structure.
- [ ] Verify resend cooldown timer behaviour and API dispatch.
- [ ] Verify error states rendered on 400/404/429 backend responses.

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-035
- **Blocked By:** PAIML-KEYCLOAK-032

## Estimated Effort
- [M] (Medium 3–5h)
