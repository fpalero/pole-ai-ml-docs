# Ticket: PAIML-KEYCLOAK-022

## Title
[Keycloak] OTP send/verify + hidden-password grant + emailVerified + fixed 2h window

## Description
With the direct link (021) in place, entry still needs its second factor: the
`/activate` page calls **Validate** (`send-code`), the user receives a 6-digit
code, and `verify-code` exchanges link + code for a real Keycloak session and
starts the 2-hour window. This ticket builds both endpoints, the OTP
hardening, the first-step hidden-password Direct Access Grant session fetch,
the `emailVerified=true` Admin API update, and the **never-extend** window
rule (e.g. 10:00→12:00 stays 12:00 even when re-entry asks a fresh code).

Why this shape (decision record):
- **Hashed OTP + caps.** Codes are stored as SHA-256 (+ pepper), never
  plaintext; 10-minute TTL, max 5 attempts, 60-second resend cooldown.
- **Hidden-password grant is step one, not the end state.** It needs no realm
  change and unblocks the UX; proper token-exchange impersonation follows in
  025 (FUTURE).
- **Window end is immutable.** `ts_end` is written once (SETNX); re-entry only
  confirms, so a shared/forwarded link cannot stretch access.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] `POST /api/auth/temporary-access/send-code {temp_token}` (public):
  validate the pending `temp:token:{hash}` (404/410 on unknown/expired, 403 on
  app mismatch); enforce the 60s `temp:code-resend:{email}:{app}` cooldown
  (429); generate a 6-digit code, store ONLY its hash in
  `temp:code:{token_hash}` = `{code_hash, attempts: 0, email, app}` (10min
  TTL); Brevo-send the code (EN+ES, `no-reply@fpalero.cc`); reset attempts on
  every fresh send without touching `temp:active`.
- [ ] `POST /api/auth/temporary-access/verify-code {temp_token, code}`
  (public): validate token + app binding; compare code hashes (constant-time);
  increment attempts on mismatch and 429 after 5; on success fetch the Keycloak
  session via hidden-password Direct Access Grant, set `emailVerified=true`
  via the Admin API, and start `temp:active:{email}:{app}` = `{app, ts_start,
  ts_end}` (2h) ONLY if absent (re-entry never moves `ts_end`); return
  `200 {access_token, token_type, expires_in}`.
- [ ] Keep Phase 8 semantics: email/owner-scoped identity, `SCAN` enumeration,
  `temp:active-index` maintenance, purge + disable on expiry.
- [ ] Add/extend unit + integration tests (OTP hash/attempt/resend/window
  matrix below); `pixi run test` stays ≥80% coverage.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `send-code` enforces token validity, app binding, and the 60s resend
  cooldown; codes are stored hashed only.
- [ ] `verify-code` caps attempts at 5 (then 429), validates app binding, and
  returns a usable session on success.
- [ ] Success sets `emailVerified=true` via Admin API.
- [ ] FIRST success starts the 2h `temp:active` window; re-entry (fresh code
  required) never extends `ts_end` (10:00→12:00 pinned).
- [ ] Live-session in-app navigation never re-asks for a code.

## Integration Tests to Run (Local Verification)
- [ ] Happy path: token → send-code (code email) → verify-code → 200 session +
  `emailVerified=true` + `temp:active` TTL 2h.
- [ ] Wrong-code × 5 → 429; 6th try blocked until fresh `send-code`.
- [ ] Resend within 60s → 429; after cooldown → new code, attempts reset.
- [ ] Re-entry inside the window: fresh code required, `ts_end` unchanged
  (assert original end, e.g. start+2h exact).
- [ ] Expired code (10min+) → 410; cross-app token → 403.
- [ ] Full `pixi run test` green with ≥80% coverage.

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-023, PAIML-KEYCLOAK-024, PAIML-KEYCLOAK-025
- **Blocked By:** PAIML-KEYCLOAK-021

## Estimated Effort
- [L] (Large 5–8h)
