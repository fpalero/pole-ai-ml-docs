# Plan Phase 12 — Two-Step Temporary Access: Auto-Send Hardening

> **Parent plan:** [PLAN.md](../PLAN.md)
> **Status:** 📋 PLANNED
> **Class:** Full-stack UX hardening (BE `pole_api`, FE `pole_fe` & `pole_analyst`).
> **Tickets:** PAIML-KEYCLOAK-032, PAIML-KEYCLOAK-033.

## ⚠️ Scope correction — Phase 12 is hardening, not a build

**The two-step OTP handshake is already implemented and working (~85% of the
originally drafted scope).** Verified 2026-09-28 by reading the code. The
following **already exist and are NOT in scope for this phase**:

| Capability | Where it lives today | Origin |
| :--- | :--- | :--- |
| `POST /api/auth/temporary-access/send-code` | `app/pole_api/src/auth/controllers/temporary_access.py` | PAIML-KEYCLOAK-022 |
| `POST /api/auth/temporary-access/verify-code` | same file | PAIML-KEYCLOAK-022 |
| 10-minute code TTL (`TEMP_ACCESS_OTP_TTL_S`) | `app/pole_api/src/core/temp_access.py`, `app/pole_api/src/core/otp.py` | PAIML-KEYCLOAK-022 |
| Single-use enforcement (`repo.delete_code`) | `app/pole_api/src/core/temp_access.py` | PAIML-KEYCLOAK-022 |
| Prior-code invalidation (same `temp:code:{token}` key) | `store_code` (`DELETE` + `HSET` + `EXPIRE`, atomic) | PAIML-KEYCLOAK-022 |
| 5-attempt cap (atomic `HINCRBY`) | `record_failed_attempt` | PAIML-KEYCLOAK-022 |
| 60s resend cooldown (`SETNX`) | `claim_resend_slot` | PAIML-KEYCLOAK-022 |
| Brevo code delivery, EN + ES | `BrevoEmailSender.send_code` | PAIML-KEYCLOAK-022 |
| `/activate` page, `ActivationFlow` state machine | `app/pole_fe/src/app/core/activation/`, `app/pole_analyst/src/app/core/activation/` | PAIML-KEYCLOAK-023 |
| EN/ES copy for every state (`activation-core.ts`) | same two dirs, **byte-identical by design** | PAIML-KEYCLOAK-023 |
| 6-digit input, TTL hint, resend cooldown UI | `activate.page.ts` (both apps) | PAIML-KEYCLOAK-023 |
| Test coverage | `pole_fe`: **371 tests passing**; `pole_analyst` mirrored | PAIML-KEYCLOAK-023 |

The original draft of this phase (tickets 032–035) proposed building all of the
above, plus a per-app Analyst UI and a dedicated integration/QA gate. That was
**wrong** — it described shipped work as new work. Those tickets were replaced
on 2026-09-28: **034 and 035 were deleted** (not renumbered) and 032/033 were
rewritten around the three real gaps below. The ticket counter for `keycloak`
therefore ends at **33**.

## The three real gaps (the entire scope of this phase)

1. **No auto-send.** The user must click a "Validate" button for the code to be
   emailed. The code must be emailed **automatically** the moment the
   verification page loads with a valid `temp_token`.
2. **No "code sent" notice on landing.** The page shows a "Validate your
   access link" pre-step instead of "A verification code has been sent to your
   email. It should arrive in a few seconds."
3. **Cooldown UX (decision B2).** Auto-send must **not** punish a page refresh.
   A refresh inside the 60s resend cooldown must return **200
   `{already_sent: true}`** — not 429 — so the page shows the code entry
   instead of a "wait before requesting another code" error while a perfectly
   valid code is already in their inbox. The 429 path stays for explicit
   "Resend code" clicks.

## Scope

1. **Backend (`pole_api`, ticket 032).** Make `send_access_code` idempotent
   *inside* the resend cooldown: when the slot cannot be claimed but a live code
   is still armed for the token, answer `200` with `already_sent: true` and the
   code's **remaining** lifetime. 429 is preserved for the case where there is
   nothing live to fall back on.
2. **Frontend (`pole_fe` + `pole_analyst`, ticket 033).** Fire `sendCode` from
   the `ActivationFlow` constructor once a non-null `temp_token` is read, land
   directly on the code step, delete the "Validate" pre-step, replace its copy
   with the "code sent" notice, and consume the `already_sent` flag so a refresh
   renders the code step rather than an error.

---

## Tickets Overview

| Ticket | Module | Title | Description |
| :--- | :--- | :--- | :--- |
| `PAIML-KEYCLOAK-032` | `pole_api` (BE) | Make `send-code` idempotent inside the 60s resend cooldown | Add `already_sent` to `SendCodeResponse`; add a `code_remaining_ttl(token)` repository helper; on a failed `claim_resend_slot` with a live armed code, return `200 {already_sent: true, expires_in: <remaining>}` with no Brevo call. Keep 429 + `Retry-After` for the no-live-code case. |
| `PAIML-KEYCLOAK-033` | `pole_fe` + `pole_analyst` (FE ×2) | Auto-send the verification code on page load, drop the "Validate" gate, show the "code sent" notice | Auto-fire `sendCode` from the constructor when `temp_token` is non-null; remove the `validate` view; replace the `validate*` copy with the "code sent" notice in EN/ES; surface `already_sent`; update `activate.page.ts` and the mirrored specs in both apps, keeping the shared files byte-identical. |

> **No ticket 034 / 035.** They previously covered an Analyst-specific
> verification UI (already delivered by PAIML-KEYCLOAK-023 as a byte-identical
> mirror of `pole_fe`) and a phase-wide integration/QA gate. The per-app UI does
> not need a second ticket, and the Phase 9 QA gate (PAIML-KEYCLOAK-024, with
> its Phase 11 fixes 030/031) is the gate that owns the flow's end-to-end
> verification.

---

## Technical Specifications

### Backend (`pole_api`)

- **Response shape.** `SendCodeResponse` gains `already_sent: bool = False`
  (additive and backward compatible: existing callers ignore it).
  `expires_in` continues to be resolved per request from settings
  (`TEMP_ACCESS_OTP_TTL_S`) so a deployment that tunes the TTL is not told a
  hardcoded number.
- **New repository helper.** `TempAccessRepository.code_remaining_ttl(token)`
  returns the `temp:code:{token}` key's **remaining TTL** in seconds — `None`
  when no record exists. It reads the key's TTL, never reconstructing one from
  settings, and follows the same "unreadable is indistinguishable from absent"
  posture as `get_code` so it cannot be used to enumerate valid links.
- **Why only the TTL is readable.** The stored value is a **peppered SHA-256
  digest**; the plaintext exists only in the email body. The fallback response
  therefore reports *that* a code is live and *for how long*, never *which*
  code. This must not be relaxed.
- **Branch behaviour in `send_access_code`:**

  | `claim_resend_slot` | live code armed? | Response |
  | :--- | :--- | :--- |
  | won | — | `200 {already_sent: false, expires_in: <TTL>}` + Brevo send (today's path, unchanged) |
  | lost | **yes** | `200 {already_sent: true, expires_in: <remaining>}` — **no** Brevo call, no `store_code`, no attempt-counter reset |
  | lost | no | `429` + `Retry-After` (today's path, unchanged) |

  The `already_sent` path must not build a `BrevoEmailSender`, must not mint a
  code, and must log distinctly so a 200 that sent nothing stays diagnosable.
  Endpoint ordering (404 / 410 / 403 / 503 gates) must not change.
- **Redis keys — unchanged by this phase.** `temp:code:{token}` (hash, `EX` =
  600), `temp:code-resend:{email}:{app}` (`SETNX`, `EX` = 60),
  `temp:active:{email}:{app}` (2h, non-extendable).

### Frontend (`pole_fe` & `pole_analyst`)

- **`activation-flow.ts` (both copies byte-identical).** The constructor fires
  `sendCode` once a non-null `temp_token` is read from the route snapshot and
  lands on the code step. A null/blank token still short-circuits to the
  `missing` state with **no** request. The public `validate()` method is
  **kept** — it is the shared send path behind `resendCode()` and `retry()`,
  and "Resend code" must keep working.
- **`activation-core.ts` (both copies byte-identical).** `validateTitle` /
  `validateBody` / `validateCta` / `validatePending` are replaced by the "code
  sent" notice in **both** `en` and `es`; `SendCodeResponse` gains
  `already_sent?: boolean` mirroring the backend field.
- **`already_sent` handling.** An `already_sent: true` 200 renders the code step
  (not an error) and arms the TTL hint from the **reported remaining**
  `expires_in`, never a hardcoded 600. The resend countdown still arms on that
  path, because the backend slot is still claimed.
- **`activate.page.ts` (both apps, intentionally not identical).** The
  `data-state="validate"` branch and its CTA button are removed; the notice
  becomes the code step's leading text. Every other state (`loading`, `missing`,
  `success`, per-kind error views) and both buttons stay.
- **Duplication discipline.** `activation-core.ts`, `activation-flow.ts` and
  the mirrored `*.spec.ts` are compared **byte-for-byte** by
  `activation-parity.spec.ts` in each app. Every edit must land in both apps in
  the same change or the parity guard goes RED. The per-app `activate.page.ts`
  files stay per-app (branding, markup, home route).

---

## Acceptance Criteria

- [ ] `/activate?temp_token=…` fires `send-code` automatically and renders the
  code entry with **no click**.
- [ ] The landing copy is the "a verification code has been sent to your email"
  notice, in EN and ES; the "Validate your access link" pre-step is gone.
- [ ] A refresh inside the 60s cooldown returns `200 {already_sent: true}` and
  renders the code step — not a 429 error screen — and sends no second email.
- [ ] `send-code` inside the cooldown with **no** live code still returns 429
  with `Retry-After`, so the explicit "Resend code" path is unchanged.
- [ ] The response never exposes the code or anything that makes the stored
  digest recoverable.
- [ ] A missing `temp_token` still fires no request (both apps).
- [ ] The shared activation files remain byte-identical between `pole_fe` and
  `pole_analyst`; `pole_fe` stays at its 371-test baseline **plus** the new
  cases, `pole_analyst` matches.
- [ ] New tests **fail against the pre-change code**; `pixi run test` green with
  ≥80% coverage.

## Risks and Mitigations

- **Risk: auto-send turns every page refresh into an email.** A user reloading
  twice inside 60s must not receive two codes and must not be shown an error.
  - **Mitigation:** decision **B2** — the `already_sent` 200 answers the second
    and later calls within the cooldown, the frontend renders the code step, and
    the resend countdown still gates the button. The one email per 60s ceiling
    (`SETNX`) is unchanged.
- **Risk: an `already_sent: true` with no code behind it** (a Brevo failure
  rolled the record back but left the slot claimed, or the code's 10 minutes
  lapsed under a surviving resend key) would strand the user on a code screen
  that can never be satisfied.
  - **Mitigation:** the `already_sent` 200 is only reachable when a live code
    record is actually present; otherwise the 429 branch answers, unchanged.
    Covered by a dedicated test.
- **Risk: drift between the two hand-duplicated frontend copies.** A fix applied
    to one app only would make the two `/activate` pages render different states
    for the same backend answer.
  - **Mitigation:** `activation-parity.spec.ts` fails the build on divergence;
    both copies must change in the same commit.
- **Risk: relaxing the hash-only storage to make the fallback easier.** A
    6-digit code is a 10^6 space — a bare digest is crackable from a Redis dump.
  - **Mitigation:** the helper returns the **TTL only**; the plaintext is never
    stored, returned or logged. Called out explicitly in ticket 032.
- **Risk: overstating the code's life after a fallback.** Hardcoding 600 on the
  `already_sent` path would promise minutes the user does not have.
  - **Mitigation:** `expires_in` is the record's actual remaining TTL, and the
    frontend renders the hint from the reported value.

## Decisions

- **Decision B1 — auto-send, no gate.** The code is emailed automatically when
  the verification page loads with a valid `temp_token`; the "Validate your
  access link" pre-step is removed rather than re-worded, because there is
  nothing left to validate.
- **Decision B2 — idempotent cooldown (user-confirmed).** A `send-code` inside
  the 60s resend cooldown that has a live code armed returns **200
  `{already_sent: true}`** with the remaining `expires_in` instead of 429; the
  frontend shows the code step without re-sending. The 429 rate-limit path is
  preserved for explicit "Resend code" clicks and for the no-live-code case.
