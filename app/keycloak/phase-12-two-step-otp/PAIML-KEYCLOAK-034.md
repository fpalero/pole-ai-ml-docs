# Ticket: PAIML-KEYCLOAK-034

## Title
[pole_analyst] Analyst app verification UI with 6-digit input, status notice, and resend cooldown

## Description
Build the client-side second-factor OTP verification interface in `pole_analyst` (Analyst Angular application).
When an analyst opens the temporary access activation route (`/activate` or `/verify-otp`) via their magic link, the page should present a 6-digit numeric input styled to match the Analyst UI theme, show an active 10-minute validity countdown, handle paste actions, display status notices, and offer a 60-second cooldown on the resend code button.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Create/update the activation component in `pole_analyst` (e.g. `src/app/auth/temp-access-verify/` or `/activate`):
  - 6-digit input boxes styled according to the Analyst design tokens with numeric input mode (`inputmode="numeric"`).
  - Handle keyboard navigation (auto-focus next, backspace) and clipboard paste event parsing.
- [ ] Render a 10-minute expiration countdown timer.
- [ ] Implement a "Resend Code" action with 60-second cooldown timer disabling repeated clicks.
- [ ] Handle submission to `POST /api/auth/temporary-access/verify-otp` with loading feedback.
- [ ] Render user feedback for expired OTPs, incorrect codes, or failed attempts.
- [ ] On successful verification, store tokens, navigate to the analyst dashboard (`/analyst` / `/dashboard`), and display temporary session banner (2h remaining).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] 6-digit input component works with keyboard entry, auto-focus, and clipboard paste.
- [ ] 10-minute timer correctly warns users as expiration approaches.
- [ ] 60-second resend cooldown prevents repeated submissions and coordinates with backend cooldown.
- [ ] Verification response successfully starts analyst session and navigates to the app.
- [ ] Unit tests for the component pass with ≥80% coverage.

## Integration Tests to Run (Local Verification)
- [ ] End-to-end component test for user input, error display, and form submit.
- [ ] Verify resend cooldown timer and button enable/disable state transitions.
- [ ] Verify routing transition on successful session initiation.

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-035
- **Blocked By:** PAIML-KEYCLOAK-032

## Estimated Effort
- [M] (Medium 3–5h)
