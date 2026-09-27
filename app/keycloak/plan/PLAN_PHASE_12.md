# Plan Phase 12 — Two-Step Temporary Access: Magic Link + Second-Factor Email OTP

> **Parent plan:** [PLAN.md](../PLAN.md)
> **Status:** 📋 PLANNED
> **Class:** Full-stack (BE `pole_api`, FE `pole_fe` & `pole_analyst`, Integration Tests/QA gate).

## Scope

Phase 12 establishes a hardened **two-step authentication workflow** for temporary guest access across the Pole AI platform (`pole_fe` Athlete app and `pole_analyst` Analyst app):

1. **Step 1 (Magic Link Validation):** The guest user initiates temporary access by providing their email. An initial magic link is delivered via Brevo pointing to the application's `/activate?token=...` endpoint.
2. **Step 2 (Second-Factor Email OTP):** When the user visits the activation page or clicks the magic link, a dedicated OTP dispatch endpoint generates a single-use, 6-digit numeric OTP with a **10-minute TTL**, immediately invalidates any prior unconsumed OTPs for that user session, and dispatches the code to the user's email address via Brevo transactional email.
3. **Frontend Verification Experience:** Both `pole_fe` and `pole_analyst` provide a refined 6-digit input component, clear state/status feedback, a 10-minute expiration countdown, and a resend cooldown control (60s).
4. **Session Activation & Security:** Successful submission of the 6-digit OTP completes verification, provisions the Direct Access Grant session, activates the fixed 2-hour window (`temp:active:{email}` in Redis), and cleans up all temporary OTP keys.
5. **Quality Assurance & Verification:** Comprehensive unit and integration test suites validating TTL enforcement, single-use consumption, prior code invalidation, Brevo mock delivery, rate-limiting, and end-to-end guest access journeys in both frontends.

---

## Tickets Overview

| Ticket | Module | Title | Description |
| :--- | :--- | :--- | :--- |
| `PAIML-KEYCLOAK-032` | `pole_api` (BE) | Backend OTP dispatch endpoint, 10-minute TTL, single-use, prior OTP invalidation, email delivery via Brevo | Implement `POST /api/auth/temporary-access/send-otp` / `verify-otp` with secure hashing (peppered SHA-256), 10m TTL in Redis, atomic prior-code invalidation, rate-limiting, and Brevo transactional email dispatch. |
| `PAIML-KEYCLOAK-033` | `pole_fe` (FE) | Athlete app verification UI with 6-digit input, status notice, and resend cooldown | Angular activation component in `pole_fe` supporting 6-digit PIN input, clipboard paste, loading indicators, countdown timer (10m), error messaging, and 60-second resend cooldown. |
| `PAIML-KEYCLOAK-034` | `pole_analyst` (FE) | Analyst app verification UI with 6-digit input, status notice, and resend cooldown | Angular activation component in `pole_analyst` matching Analyst UI theme/design tokens, 6-digit input, timer, resend button with cooldown, and deep-link query parameter parsing. |
| `PAIML-KEYCLOAK-035` | Testing / QA | Integration tests & QA gate for two-step OTP workflow | Full integration test coverage in `pole_api` and end-to-end verification across `pole_fe` & `pole_analyst`, verifying single-use semantics, 10m expiry, invalidation of prior codes, and 2h session grant. |

---

## Technical Specifications & Architecture

### Backend (`pole_api`) Flow & Redis Key Schema
- **Key Pattern:**
  - `temp:otp:{email}:{app}`: Hashed OTP payload (`{"hash": "...", "attempts": 0, "created_at": ...}`) with `EX = 600` (10 minutes).
  - `temp:otp-resend:{email}:{app}`: Cooldown marker with `EX = 60` (60 seconds).
- **Security & Integrity:**
  - OTP generation using cryptographically secure PRNG (`secrets.randbelow(1_000_000)` padded to 6 digits).
  - OTPs are stored exclusively as peppered SHA-256 hashes (`TEMP_ACCESS_OTP_PEPPER`).
  - Requesting a new OTP immediately deletes/overwrites existing `temp:otp:{email}:{app}` keys, ensuring only the most recent OTP is valid.
  - Maximum 5 failed verification attempts before the OTP is permanently invalidated.

### Email Delivery (Brevo)
- Dedicated transactional email template or styled HTML body containing the 6-digit code, clear expiration warning (10 minutes), and security notice.
- Fallback handling for Brevo API rate limits and connection retries.

### Frontend (`pole_fe` & `pole_analyst`)
- Standalone Angular component route `/activate` / `/verify-otp`.
- Input fields with auto-focus, paste auto-fill, and numeric keypad hint on mobile devices (`inputmode="numeric"`).
- Resend button disabled until 60-second cooldown expires.
- Clear error alerts for expired OTPs, incorrect codes, and attempt exhaustion.

---

## Acceptance Criteria

- [ ] `POST /api/auth/temporary-access/send-otp` dispatches 6-digit OTP via Brevo with 10-minute TTL.
- [ ] Generating a new OTP immediately invalidates any previously issued OTP for that email and client.
- [ ] OTP verification enforces single-use (deleted upon successful verification or 5 failed attempts).
- [ ] `pole_fe` and `pole_analyst` provide responsive 6-digit OTP verification interfaces with 60s resend cooldown.
- [ ] Successfully verifying the OTP logs the guest in and starts the 2-hour non-extendable session.
- [ ] All unit and integration tests pass with ≥80% code coverage.

---

## Risks and Mitigations

- **Risk:** Email delivery latency could cause users to submit verification after OTP expiration.
  - **Mitigation:** 10-minute TTL provides ample buffer; clear UI countdown timer informs user of remaining validity.
- **Risk:** Brute-force guessing of 6-digit numeric OTP.
  - **Mitigation:** Rate-limit to 5 max verification attempts per OTP; 60-second resend cooldown; peppered SHA-256 storage.
- **Risk:** Resending OTP could create confusion if multiple valid codes exist.
  - **Mitigation:** Atomic invalidation of prior codes ensures only the latest code is valid.
