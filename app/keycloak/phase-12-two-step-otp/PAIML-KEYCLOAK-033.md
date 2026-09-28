# Ticket: PAIML-KEYCLOAK-033

## Title
[Keycloak / pole_fe + pole_analyst] Auto-send the verification code on page load, drop the "Validate" gate, and show the "code sent" notice

## Description
**Phase 12 is a UX-hardening phase, not a build phase.** The `/activate` page,
the `ActivationFlow` state machine and the shared `activation-core.ts`
(EN/ES copy) already exist and are covered by a green suite in **both** apps —
PAIML-KEYCLOAK-023 shipped `/activate` in `pole_fe` and `pole_analyst` with the
`activation/` directory duplicated **byte-identically** by design (a
`activation-parity.spec.ts` in each app fails if the two copies diverge).
`pole_fe` is at **371 tests passing**; `pole_analyst` mirrors it. **None of that
is in scope here** — do not rebuild the page, the state machine or the code
input.

**The gap: the user must still click "Validate".** `ActivationFlow.validate()`
is fired only by a button click on the `data-state="validate"` view, so the
code is **not** emailed until the user acts. Two concrete consequences:

1. **The flow does not start itself.** A guest following the emailed link
   arrives on a page whose only job is to ask them to confirm the link — an
   extra, meaningless step ("validate" what? the link is the credential), and a
   dead end for anyone who does not understand what the button does.
2. **The landing copy is wrong.** The page's first impression is
   "Validate your access link" instead of the fact that matters — **"a
   verification code has been sent to your email, it should arrive in a few
   seconds."**

**Required behaviour.** The code must be emailed **automatically** the moment
the verification page loads with a valid `temp_token`, and the page must land
**directly on the code step**. The `validate*` pre-step view and its CTA button
are removed, not re-worded: there is nothing left to validate.

**Refreshing must not be punished (decision B2, user-confirmed).** Auto-send
turns every accidental page refresh into another `send-code` call, and most of
those land inside the backend's 60s resend cooldown. The backend therefore
answers such a call with `200 {already_sent: true}` plus the code's remaining
`expires_in` (PAIML-KEYCLOAK-032), and this ticket must **consume that flag**:
show the code entry step, arm the countdown from the **remaining** lifetime
reported, and do **not** treat it as an error. The 429 path stays live for the
explicit "Resend code" click, and the existing `resend-cooldown` error state
must keep working exactly as today.

**Duplication discipline (load-bearing, not stylistic).** `activation-flow.ts`
and `activation-core.ts` are hand-duplicated into both apps. The
`activation-parity.spec.ts` files compare the two copies **byte-for-byte**, so
any edit must be applied to **both** `app/pole_fe/src/app/core/activation/` and
`app/pole_analyst/src/app/core/activation/` in the same change — otherwise the
parity guard goes RED and the two `/activate` pages can render different states
for the same backend answer, which is the exact drift the guard exists to
prevent. The mirrored `*.spec.ts` files are covered by the same rule.

**One behaviour change, two apps, no divergence:** the per-app
`activate.page.ts` files are **not** byte-identical by design (each owns its own
branding, markup and home route) — only the shared helper files are. Update
both pages; do not try to unify them.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [ ] **`activation-flow.ts` (BOTH copies, byte-identical).** In the
  constructor, after the token is read from the route snapshot and `loading` is
  cleared, fire `sendCode` automatically **only when `tempToken()` is non-null**,
  and land directly on the code step. An absent/blank token must still short
  circuit to the `missing` state without ever firing a request that must 404 —
  keep that guarantee and cover it with a test. Use the existing busy/error
  plumbing and the same single in-flight `Subscription` discipline already in
  place (no second concurrent request; `unsubscribe()` the previous one first).
  - **Keep the public `validate()` method.** It is the reusable send path that
    `resendCode()` and `retry()` both call, and the "Resend code" button must
    keep working — just re-point those callers if the auto-send makes a
    separate call site redundant. Do not delete it, and do not leave two code
    paths that can drift.
- [ ] **`activation-core.ts` (BOTH copies, byte-identical).**
  - **Copy:** replace the `validateTitle` / `validateBody` / `validateCta` /
    `validatePending` "Validate your access link" strings with an explicit
    **"A verification code has been sent to your email. It should arrive in a
    few seconds."** notice, in **both** `en` and `es` (ship both locales — a
    missing translation is a type error by design, and the ES app is a
    first-class target). Prefer reusing/renaming the existing `code*` fields
    over growing a parallel set of near-duplicate strings.
  - **Types:** add the `already_sent` flag to the `SendCodeResponse` interface
    (mirroring the backend field added by PAIML-KEYCLOAK-032). The interface
    must not claim a field the backend does not send.
- [ ] **Response handling.** In the `sendCode` success path, surface
  `already_sent`: an `already_sent: true` response must still land on the code
  step and must **not** be surfaced as an error or a resend prompt. Arm the
  code-TTL hint from the **reported** `expires_in` (the remaining lifetime),
  not from a hardcoded 600, so a refresh that fell back inside the cooldown
  shows the truth. Decide and document whether the resend countdown arms on
  the `already_sent` path too — the honest answer is yes, because the backend
  slot is still claimed, so "Resend code" stays disabled for the remainder of
  the real cooldown. Keep the existing `resend-cooldown` error view for the
  genuine 429.
- [ ] **`activate.page.ts` in BOTH apps** so the code-entry state renders
  directly on load: drop the `data-state="validate"` branch and its
  `data-testid="validate-button"` CTA, and render the new "code sent" notice as
  the code step's leading text. Keep every other state (`loading`, `missing`,
  `success`, and the per-kind error views) and both buttons (`verify-button`,
  `resend-button`) exactly as they are — the six-digit input, the TTL hint and
  the resend countdown are already built and correct.
- [ ] **Specs, mirrored in both apps.** Update the affected
  `activate.page.spec.ts` cases (several currently click `validate-button`
  first — they must be rewritten, not deleted, so the happy path stays
  covered) and add:
  - `sendCode` is called **automatically on construction** with the token from
    the URL, with **no click at all**;
  - the code step renders with no click required;
  - a `200 {already_sent: true}` response still renders the code step (and does
    not render an error state);
  - a **missing** token still fires **no** request;
  - the 429 `resend-cooldown` path still renders its own view (regression guard
    for the flag handling above).
  - Keep the `activation-parity.spec.ts` guard green in both apps.
- [ ] Run the suites in **both** apps; `pole_fe` must stay at its current
  371-passing baseline **plus** the new cases, and `pole_analyst` must match.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Loading `/activate?temp_token=…` fires `send-code` automatically and the
  code-entry state renders with **no user interaction**.
- [ ] The page's first impression is the "a verification code has been sent to
  your email" notice, in EN and ES — the "Validate your access link" pre-step
  and its button are gone.
- [ ] `already_sent: true` renders the code step (not an error), and the TTL
  hint reflects the **remaining** lifetime the backend reported.
- [ ] A page refresh inside the cooldown does **not** produce an error screen,
  and sends no second email.
- [ ] The explicit "Resend code" button still re-sends, still honours the 60s
  cooldown countdown, and the 429 `resend-cooldown` view still renders.
- [ ] A missing `temp_token` still fires no request and still shows the
  "incomplete link" state.
- [ ] `activation-flow.ts` and `activation-core.ts` are **byte-identical**
  between `pole_fe` and `pole_analyst` (parity guard green in both), and both
  `activate.page.ts` files render the new first impression.
- [ ] `pole_fe` and `pole_analyst` suites green (≥371 + new cases), ≥80%
  coverage.

## Integration Tests to Run (Local Verification)
- [ ] Open `/activate?temp_token=…`: assert exactly **one** `send-code` request
  on load, the code input visible, and the new notice text rendered.
- [ ] Reload the same URL within 60s: assert **one** `send-code` request, the
  code step still visible, **no** error state, and still exactly one email in
  the Brevo/Mailpit capture.
- [ ] Wait out the 60s and reload: assert a genuinely fresh send
  (`already_sent: false`) and a second email.
- [ ] Kill Brevo / stub `send-code` to fail: assert a readable error state, not
  a blank card.
- [ ] Open `/activate` with no `temp_token`: assert zero network requests and
  the "incomplete link" state.
- [ ] Full `pole_fe` + `pole_analyst` suites green.

## Dependencies
- **Blocks:** None
- **Blocked By:** PAIML-KEYCLOAK-032 (the `already_sent` 200 this consumes —
  without it, an auto-send inside the cooldown renders a 429 error screen)

## Estimated Effort
- [M] (Medium 3–5h)

> **Cross-reference:** PAIML-KEYCLOAK-021 / -022 (the backend handshake whose
> 10-min TTL, single-use, attempt cap and 60s cooldown already exist),
> PAIML-KEYCLOAK-023 (the `/activate` pages, `ActivationFlow`, `activation-core`
> and the byte-identical duplication rule this ticket edits),
> PAIML-KEYCLOAK-032 (the `already_sent` idempotent-cooldown response), and
> [PLAN_PHASE_12.md](../../plan/PLAN_PHASE_12.md) (decision **B2**).
