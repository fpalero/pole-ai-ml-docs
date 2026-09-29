# Plan Phase 12 — Two-Step Temporary Access: Auto-Send Hardening, Cooldown UX & Audit Retention

> **Parent plan:** [PLAN.md](../PLAN.md)
> **Status:** 🟡 PARTIAL — PAIML-KEYCLOAK-035 ✅ SHIPPED ([pole-ai-ml#363](https://github.com/fpalero/pole-ai-ml/pull/363)); 032/033/034 remain 📋 PLANNED
> **Class:** Full-stack UX hardening (BE `pole_api`, FE `pole_fe` & `pole_analyst`).
> **Tickets:** PAIML-KEYCLOAK-032, PAIML-KEYCLOAK-033, PAIML-KEYCLOAK-034, PAIML-KEYCLOAK-035.
> **Decisions:** [ADR-007](../../decisions/ADR-007-temp-access-link-reuse-and-audit-retention.md)
> (Q1 link re-use, Q2 cooldown UX, Q3 data lifecycle + audit retention).

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
**wrong** — it described shipped work as new work. It was corrected on
2026-09-28: the per-app Analyst UI (the former 034) and the phase-wide QA gate
(the former 035) were **deleted, not renumbered**, and 032/033 were rewritten
around the three real gaps below. Later the same day, **034 and 035 were
re-issued as new, different tickets** covering the two gaps found in the
product-decision review recorded in
[ADR-007](../../decisions/ADR-007-temp-access-link-reuse-and-audit-retention.md)
— the cooldown UX (Q2) and the durable audit ledger (Q3). The ticket counter for
`keycloak` therefore ends at **35**.

## Product decisions recorded in ADR-007 (2026-09-27, user-confirmed)

Three questions came out of a review of the temp-access flow. They are
recorded in
[ADR-007](../../decisions/ADR-007-temp-access-link-reuse-and-audit-retention.md)
so the current behaviour is not misread as a bug:

| Q | Decision | Code impact |
| :--- | :--- | :--- |
| **Q1 — link re-use** | The magic link **may** be re-used, but **only while the 2h window is live**. Once the 2h lapses the link is dead: the user must wait out the 14-day cooldown and request a **brand-new** link. | **NONE — no code change.** This is the already-shipped behaviour (`temp:token` TTL 24h; `start_window` pins `ts_end = ts_start + 2h` and never extends; request-time `_enforce_temp_access_window` rejects after lapse and lazily purges). Recorded **as a decision record only**, so a future reader does not "fix" it. |
| **Q2 — cooldown UX** | The 14-day cooldown stays **hard** (the user waits it out), but the application **must show an explanatory message** instead of a bare number. | **Ticket 034** (FE ×2). Today the cooldown surfaces only as a bare `409 {"detail":"Email in cooldown — try again in 336 hours"}` and the `/activate` page has **no cooldown state at all**. |
| **Q3 — data lifecycle & audit** | Owned data (videos, DB rows, Chroma vectors) is **physically deleted** on purge — unchanged. What must be **retained** is a durable per-user audit trail: the email, `link_issued_at`, `window_started_at`, a use counter, and the expired/consumed **token identifiers** so a spent token is recognisable and never re-used. **Retention: forever for now** (low-traffic demo). | **Ticket 035** (BE). Unbounded growth is **accepted for now**; a retention job would be required before production. See "Deferred" in ADR-007. |

## The gaps this phase closes (the entire scope)

1. **No auto-send.** The user must click a "Validate" button for the code to be
   emailed. The code must be emailed **automatically** the moment the
   verification page loads with a valid `temp_token`. → **032 (BE) + 033 (FE)**
2. **No "code sent" notice on landing.** The page shows a "Validate your
   access link" pre-step instead of "A verification code has been sent to your
   email. It should arrive in a few seconds." → **033 (FE)**
3. **Auto-send must not punish a page refresh (decision B2).** A refresh inside
   the 60s resend cooldown must return **200 `{already_sent: true}`** — not
   429 — so the page shows the code entry instead of a "wait before requesting
   another code" error while a perfectly valid code is already in their inbox.
   The 429 path stays for explicit "Resend code" clicks. → **032 (BE) + 033 (FE)**
4. **The 14-day cooldown is unexplained (Q2).** The `/activate` page has no
   cooldown state, and the only surface that mentions it returns a bare hours
   number. It must render an explanatory message (EN + ES). → **034 (FE ×2)**
5. **There is no durable record that a user existed (Q3).** The purge removes
   owned data and clears Redis, leaving no answer to "who used temp access,
   when, how often, and is this token already spent?". → **035 (BE)**

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
3. **Frontend (`pole_fe` + `pole_analyst`, ticket 034).** Add a distinct
   cooldown state to the activation flow and give it explanatory EN + ES copy.
   **Presentation only — no backend change is spec'd** (the 409 + `Retry-After`
   already exists).
4. **Backend (`pole_api`, ticket 035).** Add a durable `temp_access_audit`
   ledger in MongoDB, written at link-issue and window-start, **never** deleted
   by the purge, and **never** used as the cooldown's source of truth.

---

## Tickets Overview

| Ticket | Module | Title | Description |
| :--- | :--- | :--- | :--- |
| `PAIML-KEYCLOAK-032` | `pole_api` (BE) | Make `send-code` idempotent inside the 60s resend cooldown | Add `already_sent` to `SendCodeResponse`; add a `code_remaining_ttl(token)` repository helper; on a failed `claim_resend_slot` with a live armed code, return `200 {already_sent: true, expires_in: <remaining>}` with no Brevo call. Keep 429 + `Retry-After` for the no-live-code case. |
| `PAIML-KEYCLOAK-033` | `pole_fe` + `pole_analyst` (FE ×2) | Auto-send the verification code on page load, drop the "Validate" gate, show the "code sent" notice | Auto-fire `sendCode` from the constructor when `temp_token` is non-null; remove the `validate` view; replace the `validate*` copy with the "code sent" notice in EN/ES; surface `already_sent`; update `activate.page.ts` and the mirrored specs in both apps, keeping the shared files byte-identical. |
| `PAIML-KEYCLOAK-034` | `pole_fe` + `pole_analyst` (FE ×2) | Cooldown-expiry message on the activation flow (Q2) | Map the existing backend answers to distinct copy states — `409` cooldown (explanatory message, ideally the re-request date, **not** a bare hours number), plus the existing `410 expired-link` / `404 invalid-link`. EN + ES copy in `activation-core.ts`, **both copies byte-identical**. **FE presentation only: do not spec backend changes.** |
| ✅ `PAIML-KEYCLOAK-035` | `pole_api` (BE) | Durable `temp_access_audit` ledger (Q3) | MongoDB ledger written at link-issue and window-start, **never** deleted by the purge. Fields: `email`, `app`, `link_issued_at`, `window_started_at`, `use_count`, `consumed_tokens`. Idempotent on re-entry. **Additive only** — must not reintroduce the PAIML-KEYCLOAK-031 bug (the 14-day `temp:req` marker stays the cooldown's source of truth). Retention/pruning **out of scope** (deferred). |

## Ticket dependency graph

```
PAIML-KEYCLOAK-032 (BE, idempotent 60s cooldown)
   ├──▶ PAIML-KEYCLOAK-033 (FE ×2, auto-send + code-sent notice)
   │       └──▶ PAIML-KEYCLOAK-034 (FE ×2, cooldown-expiry message)
   └──▶ PAIML-KEYCLOAK-035 (BE, durable audit ledger)
```

Acyclic. Every `Blocked By` is symmetric with the other ticket's `Blocks`:

| Ticket | Blocks | Blocked By |
| :--- | :--- | :--- |
| `PAIML-KEYCLOAK-032` | 033, 035 | 030, 031 |
| `PAIML-KEYCLOAK-033` | 034 | 032 |
| `PAIML-KEYCLOAK-034` | None | 033 |
| `PAIML-KEYCLOAK-035` | None | 032 |

**Why 034 hangs off 033** rather than off 032: 034 adds a *new* state to the
same `/activate` flow that 033 reshapes, and the 409/429 classifier cases sit
directly next to the `already_sent` handling 033 introduces — editing both at
once would be a guaranteed parity conflict. **Why 035 hangs off 032:** it writes
into the same request/verify surface 032 branches on, so the two must not be
implemented concurrently against that code.

> **The former 034 / 035 are not these tickets.** The original 034 covered an
> Analyst-specific verification UI (already delivered by PAIML-KEYCLOAK-023 as a
> byte-identical mirror of `pole_fe`) and the original 035 a phase-wide
> integration/QA gate (owned by the Phase 9 gate PAIML-KEYCLOAK-024, with its
> Phase 11 fixes 030/031). Both were **deleted, not renumbered**, and the
> numbers were re-issued on 2026-09-28 for the Q2/Q3 work above.

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

### Cooldown UX (ticket 034)

- [ ] A `409` cooldown answer renders a **distinct, explanatory** state on
  `/activate` in both apps — not the generic "Something went wrong" view, and
  not a bare hours number. The copy explains **why** (this email already had a
  temporary-access session) and **what to do next** (request again after the
  cooldown), in **EN and ES**.
- [ ] The re-request **date** (or day count) is shown when `Retry-After` is
  present; when the header is absent the explanation still renders without
  inventing a number.
- [ ] The `429 → resend-cooldown / attempt-cap` split is untouched, and the new
  state carries no misleading action button.
- [ ] **No file under `app/pole_api/` is modified** — the 409 + `Retry-After`
  already exists and the work is presentation only.

### Audit ledger (ticket 035)

- [ ] A `temp_access_audit` record is written at **link-issue** and updated at
  **window-start**, carrying `email`, `app`, `link_issued_at`,
  `window_started_at`, `use_count` and `consumed_tokens`.
- [ ] Re-entry is idempotent: one document per user+app, `use_count`
  increments, and `link_issued_at` / `window_started_at` are first-write-wins
  (a second `start_window` does **not** move `window_started_at`).
- [ ] A spent or expired token's identifier is recorded exactly once in a form
  that is **not** a usable credential, and is never honoured again.
- [ ] The purge deletes the user's owned data and leaves the ledger row
  **intact**; after a purge a re-request is **still refused** by the `temp:req`
  cooldown, with no code path consulting the ledger (the PAIML-KEYCLOAK-031
  invariant holds).
- [ ] No TTL, prune job or retention policy was added — ADR-007 defers it.

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
- **Risk: the new 409 cooldown state (034) collides with the 60s resend
  cooldown (032/033).** They are different clocks with different remedies, and
  a classifier that merges them would tell a user to "resend" a code when the
  real answer is "come back in 14 days".
  - **Mitigation:** a distinct `ActivationErrorKind` with a docstring stating
    the distinction, a regression test pinning the untouched
    `429 → resend-cooldown / attempt-cap` split, and an explicit Do-Not-Enter
  in both `RESEND_KINDS` and `NEW_LINK_KINDS` in `activation-flow.ts`.
- **Risk: the audit ledger (035) becomes the cooldown's second source of truth
  and reintroduces the PAIML-KEYCLOAK-031 defect** — a permanent Mongo entry
  would make the 14-day cooldown unbounded, and a purge that touched the
  ledger would lose the only record that the user existed.
  - **Mitigation:** the ledger is strictly **additive**; `repo.request`'s Redis
    `SETNX` remains the single arbiter, ledger writes are best-effort and never
    on the decision path, and two regression tests pin the behaviour (purge
    leaves the row; post-purge re-request is still refused without consulting
    it).
- **Risk: storing token identifiers durably turns the ledger into a permanent
  credential store.** A `temp_token` that survives the purge is a replayable
  secret.
  - **Mitigation:** store a one-way digest, following the existing
    store-a-digest-never-the-plaintext precedent in `core/otp.py`. The
    property that matters — "recognise this token, never honour it" — survives
    a digest, and the identifier can never open or extend a window.

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
- **Decision B3 — link re-use is bounded by the 2h window
  ([ADR-007](../../decisions/ADR-007-temp-access-link-reuse-and-audit-retention.md)
  Q1, user-confirmed 2026-09-27).** The magic link **may** be re-used, but
  **only while the 2h window is live**; once the 2h lapses the link is dead and
  the user must wait out the 14-day cooldown and request a **brand-new** one.
  **This required NO code change** — it is the already-shipped behaviour
  (`temp:token` TTL 24h, `start_window` pinning `ts_end = ts_start + 2h` and
  never extending, request-time `_enforce_temp_access_window` rejecting after
  lapse and lazily purging). It is recorded **as a decision record only** so a
  future reader or agent does not "fix" it into a sliding window or a
  single-use token.
- **Decision B4 — the 14-day cooldown stays hard, the message is the
  deliverable ([ADR-007](../../decisions/ADR-007-temp-access-link-reuse-and-audit-retention.md)
  Q2).** The user waits the cooldown out; the application must **explain** it
  (EN + ES) rather than show a bare hours number. Presentation-only: the backend
  already returns `409` + `Retry-After`. A pre-flight "check my cooldown" GET
  was considered and **rejected** — it would be an account-enumeration oracle
  on an unauthenticated endpoint.
- **Decision B5 — owned data is physically deleted, the audit trail is retained
  forever ([ADR-007](../../decisions/ADR-007-temp-access-link-reuse-and-audit-retention.md)
  Q3, user-confirmed 2026-09-27).** The purge keeps removing what the user
  *produced*; a durable per-user `temp_access_audit` ledger keeps the record
  that the user *existed* (email, `link_issued_at`, `window_started_at`,
  `use_count`, `consumed_tokens`). **Retention is "forever, for now"** —
  unbounded growth is **accepted** at demo traffic, and a retention job would
  be required before production. The ledger is **additive only** and must
  never be consulted as the cooldown's source of truth.
