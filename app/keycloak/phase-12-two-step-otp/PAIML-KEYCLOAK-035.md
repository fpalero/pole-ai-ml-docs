# Ticket: PAIML-KEYCLOAK-035

## Title
[QA / Integration] Integration tests & QA gate for two-step OTP workflow

## Description
Execute end-to-end integration tests and establish the QA verification gate for the complete Two-Step Temporary Access workflow (Magic Link + Second-Factor Email OTP) across `pole_api`, `pole_fe`, and `pole_analyst`.
Validate that initial magic link requests, OTP generation, Brevo mock delivery, 10-minute TTL expiry, atomic single-use deletion, prior OTP invalidation upon resend, attempt exhaustion, and 2-hour temporary session activation all execute without flaws.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Implement automated integration test suite in `pole_api` (`test_two_step_otp_workflow.py`):
  - Request temp access -> dispatch magic link -> trigger OTP dispatch.
  - Assert 10-minute TTL on `temp:otp:{email}:{app}` key in Redis.
  - Assert prior OTP key is deleted/replaced when a resend is triggered.
  - Verify OTP code consumption (single-use): verify code once returns 200, immediate second verify returns 400/404.
  - Verify attempt threshold: 5 wrong guesses lock/delete the OTP.
  - Verify successful verification activates `temp:active:{email}` with 2h TTL and returns Direct Access Grant token.
- [ ] Validate FE verification flow in both `pole_fe` and `pole_analyst` (using Cypress/Playwright or Angular test harness).
- [ ] Run full test suite (`pixi run test`) across modified packages to verify ≥80% test coverage.
- [ ] Produce QA evidence report documenting all test cases, timings, and verification results.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] All automated integration tests covering the complete 2-step flow pass.
- [ ] Verified that 10-minute TTL, single-use, prior code invalidation, and 2-hour window constraints hold under all conditions.
- [ ] Both `pole_fe` and `pole_analyst` seamlessly guide the user through the verification flow.
- [ ] `pixi run test` passes with ≥80% coverage.
- [ ] QA verification report produced and signed off.

## Integration Tests to Run (Local Verification)
- [ ] `test_two_step_e2e_full_flow`: End-to-end temporary access creation through OTP verification and session issuance.
- [ ] `test_otp_ttl_and_invalidation`: Verification of 10-minute expiry and instant replacement on resend.
- [ ] `test_otp_single_use_enforcement`: Ensure consumed code cannot be replayed.
- [ ] `test_otp_attempt_lockout`: Ensure 5 failed attempts delete the OTP.

## Dependencies
- **Blocks:** None
- **Blocked By:** PAIML-KEYCLOAK-032, PAIML-KEYCLOAK-033, PAIML-KEYCLOAK-034

## Estimated Effort
- [M] (Medium 3–5h)
