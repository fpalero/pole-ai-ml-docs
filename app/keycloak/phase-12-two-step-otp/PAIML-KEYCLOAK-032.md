# Ticket: PAIML-KEYCLOAK-032

## Title
[Keycloak / pole_api] Backend OTP dispatch endpoint, 10-minute TTL, single-use, prior OTP invalidation, email delivery via Brevo

## Description
Implement the second-factor OTP backend logic for the two-step temporary access workflow in `pole_api`.
The system must generate a 6-digit numeric OTP, invalidate any prior unconsumed OTPs for the user/client pair, store the peppered hash in Redis with a strict 10-minute (600s) TTL, enforce single-use upon successful verification (or invalidation after 5 failed attempts), and deliver the code via transactional email using the Brevo API.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] Add/update endpoint `POST /api/auth/temporary-access/send-otp` (or integrate into the step-2 dispatch flow):
  - Generate a secure 6-digit numeric code (`secrets.randbelow(1_000_000)` formatted to 6 digits).
  - Compute peppered hash using `TEMP_ACCESS_OTP_PEPPER` + SHA-256.
  - Invalidate/delete any existing `temp:otp:{email}:{app}` and set the new payload with a 10-minute TTL (600 seconds).
  - Set resend cooldown `temp:otp-resend:{email}:{app}` with 60s TTL to prevent spam.
  - Send email via Brevo transactional email client with clear 10-minute expiry copy.
- [ ] Add/update endpoint `POST /api/auth/temporary-access/verify-otp`:
  - Validate email, client ID, and 6-digit code format.
  - Look up `temp:otp:{email}:{app}` in Redis. If expired or missing, return `400/404` with appropriate code.
  - Track verification attempts (max 5); delete key and fail if exceeded.
  - On match, atomically delete OTP key (single-use), initiate Direct Access Grant / Keycloak session, and activate 2h temp window (`temp:active:{email}`).
- [ ] Implement unit tests covering TTL expiration, single-use deletion, attempt exhaustion, invalid code rejections, and prior OTP invalidation.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `send-otp` issues a 6-digit code, sets a 10-minute TTL in Redis, and sends email via Brevo.
- [ ] Requesting a new OTP overwrites and invalidates any previous unconsumed OTP.
- [ ] `verify-otp` successfully validates the code, consumes it immediately (single-use), and grants access.
- [ ] 5 incorrect attempts invalidate the OTP immediately.
- [ ] `pixi run test` passes with ≥80% coverage on new and modified files.

## Integration Tests to Run (Local Verification)
- [ ] `test_temp_access_otp_dispatch_ttl`: Verify 10-minute TTL in Redis.
- [ ] `test_temp_access_otp_invalidation_on_resend`: Verify prior code becomes invalid after new code is requested.
- [ ] `test_temp_access_otp_single_use`: Verify code cannot be used twice.
- [ ] `test_temp_access_otp_attempt_exhaustion`: Verify key deleted after 5 failed attempts.

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-033, PAIML-KEYCLOAK-034, PAIML-KEYCLOAK-035
- **Blocked By:** PAIML-KEYCLOAK-030, PAIML-KEYCLOAK-031

## Estimated Effort
- [M] (Medium 3–5h)
