# Ticket: PAIML-KEYCLOAK-034

## Title
[Keycloak / pole_fe + pole_analyst] Cooldown-expiry message on the activation flow: explain the 14-day wait instead of showing a bare number

## Description
**This is a frontend-presentation ticket. Do not change the backend.** The
backend already returns everything the page needs; see the "Backend contract —
already shipped, do not re-spec" section below. The gap is that the shipped
answers are never given explanatory copy.

**The gap.** The 14-day temp-access cooldown is a hard wall (ADR-007,
Decision 2): a user who already had a session cannot re-request for 14 days.
Today that wall is invisible and unexplained:

1. On the **request** side, a repeat request answers
   `409 {"detail":"Email in cooldown — try again in 336 hours"}` plus a
   `Retry-After` header. "336 hours" tells the user nothing about *why* they
   are being refused or *what to do*.
2. On the **`/activate` page** — the surface this ticket owns — there is
   **no cooldown state at all**. `ActivationErrorKind` has
   `'invalid-link' | 'expired-link' | 'app-mismatch' | 'resend-cooldown' |
   'attempt-cap' | 'invalid-code' | 'wrong-code' | 'session-failed' |
   'unavailable' | 'unknown'`, and
   `classifyActivationError` maps `409` → `unknown` (the only 409 case it knows
   is the 60s *resend* cooldown on `send-code`). A cooldown answer therefore
   lands the user on the generic "Something went wrong" view, which is worse
   than the bare number because it does not even offer the remaining time.

**What the copy must do (ADR-007 Decision 2).** Explain the *situation*, not
just the number: **this email already had a temporary-access session, and a new
link can be requested again after 14 days.** In **EN and ES**. Showing the
re-request **date** (or a day count) alongside the explanation is the correct
shape — a raw hours figure is an internal value and should not be the headline.

**Scope the work tightly.** The backend returns the status and the seconds;
the frontend owns the words, the date formatting and the state. A ticket that
"improves the cooldown message" by adding a backend field, a new endpoint or a
different status code is **out of scope** — see the exclusions below.

## Repository
pole-ai-ml

## Backend contract — already shipped, do not re-spec

Read `app/pole_api/src/auth/controllers/temporary_access.py` and
`core/temp_access.py` before starting. These answers exist today:

| Answer | Where | What it means | FE obligation |
| :--- | :--- | :--- | :--- |
| `409` + `Retry-After: <seconds>` | `request_temporary_access` (the `repo.request(...)` `SETNX` gate), `detail=_cooldown_message(remaining)` | The 14-day cooldown is live for this email+app | Render a **distinct cooldown state** with the explanatory message. Derive the re-request **date/day count** from `Retry-After`; do not show a raw hours number as the headline. |
| `410 Gone` `detail="Access link has expired — request a new one"` | the link TTL gate (24h `temp:token` TTL) | The emailed link itself is dead | Existing `expired-link` state. Keep it, but its copy must not imply the user can re-request *now* (they cannot — see the cooldown copy's cross-reference). |
| `404` | link unknown / already used / purged | No such link | Existing `invalid-link` state. Keep as-is. |

Notes that constrain the implementation:

- **`Retry-After` is in seconds** and is the only trustworthy clock. Do not
  hardcode 14 days for display even though the default is
  `TEMP_ACCESS_COOLDOWN_S = 14 * 24 * 3600` — a deployment that tunes it must
  not be told a lie. If the header is absent, fall back to explaining the
  situation **without** a number.
- The backend `detail` is **English only** and the flow ships **EN + ES**.
  `ActivationError.detail` is already documented as "for diagnostics/logging
  only — **never displayed**". Keep that rule: the page renders its own copy.
- The `409` is raised by the **request** endpoint, not `send-code`. That does
  not make the state unreachable for the page: the same
  `classifyActivationError(err, step)` helper classifies whatever
  `HttpErrorResponse` reaches it, and a `409` from any call in the activation
  chain must land on the new state. The classifier's `step` disambiguation
  (429 = resend-cooldown on `send-code`, attempt-cap on `verify-code`) is the
  existing precedent for "one status, two meanings" — extend it the same way.
- `pole_analyst` normalizes errors differently: its `apiInterceptor` rethrows
  an `ApiError` (`status` + `detail` + a preserved `retryAfter`), while
  `pole_fe` surfaces the raw `HttpErrorResponse` (`status` + `error.detail` +
  `headers`). `readDetail` / `readRetryAfter` in `activation-core.ts` already
  accept both shapes — the new state must work through the same helpers, so it
  must work in **both** apps without per-app branching.

## What to Do (Implementation Steps)

- [ ] **`activation-core.ts` (BOTH copies, byte-identical).**
  - **Add the kind.** Extend `ActivationErrorKind` with a cooldown kind
    (e.g. `'access-cooldown'`). Naming matters: it must **not** collide with
    `'resend-cooldown'`, which is the *60s* resend gate on `send-code` and must
    keep its current behaviour and copy. A reader who confuses the two will
    "fix" the wrong thing. Add a docstring on the new kind stating the
    distinction explicitly (60s resend vs 14-day re-request cooldown).
  - **Classify it.** In `classifyActivationError`, map `409` to the new kind
    **without** breaking the existing 429 semantics: keep
    `429 → step === 'send-code' ? 'resend-cooldown' : 'attempt-cap'` exactly as
    it is. A 409 has only one meaning in this flow (the 14-day cooldown), so
    no `step` disambiguation is needed — say so in a comment.
  - **Copy, in BOTH `en` and `es`.** Add `errorTitles[<kind>]` and
    `errorBodies[<kind>]` that **explain** the situation: the address already
    had a temporary-access session, so a new link cannot be requested until
    the 14-day cooldown ends, and they can request again after that. The body
    should have a place for the remaining time. Follow the existing shape —
    look at how `codeResendIn: 'Resend in {seconds}s'` and
    `codeExpiresIn: 'The code expires in {minutes} min.'` interpolate — and
    prefer **reusing that interpolation style** over inventing a second one.
    Suggested EN/ES skeletons (wording is the developer's to polish, the
    *explanation* is not negotiable):
    - EN title: "You already used temporary access"
    - EN body: "This email address already had a temporary-access session. You
      can request a new access link on {date}." (with a no-header fallback that
      drops the date clause entirely rather than inventing one)
    - ES title: "Ya has usado el acceso temporal"
    - ES body: "Esta dirección de correo ya tuvo una sesión de acceso
      temporal. Podrás solicitar un enlace nuevo el {date}."
  - **`errorActions`.** Decide and justify what the cooldown state's button
    is. The honest answer is **no action**: unlike `invalid-link` /
    `expired-link` there is no endpoint the page can call to shorten or bypass
    a cooldown, so a "Try again" button would be a lie. A missing entry in
    `errorActions` is a supported state (`Partial<Record<…>>` +
    `errorAction()` returns `null`). If you do add a label, it must be
    something the page can actually do — the `needNewLink` footer hint is the
    existing mechanism for "you'll need to come back later".
  - **Expose the remaining time.** Add whatever small helper/field the page
    needs to format the re-request date from `ActivationError.retryAfter`
    (already carried through by `readRetryAfter` for both apps' error
    shapes). Reuse the existing ceiling/formatting conventions — do not
    re-derive `Retry-After` parsing, it already exists and is covered.
- [ ] **`activation-flow.ts` (BOTH copies, byte-identical).** Make sure the
  new state renders: `errorKind()` and the per-kind affordance sets
  (`RESEND_KINDS`, `NEW_LINK_KINDS`) are the decision points. The cooldown
  state must **not** land in `RESEND_KINDS` (a re-request email is not a code
  resend) and must **not** land in `NEW_LINK_KINDS` either, because that set
  drives the "request a new link" affordance, and a new link is exactly what
  the cooldown forbids. Add a comment recording that reasoning, since the
  sets look superficially similar. Do **not** arm any countdown for this
  state — a 14-day ticking clock is noise, and the page may be long closed by
  the time it ends.
- [ ] **`activate.page.ts` in BOTH apps** (per-app files stay per-app —
  branding, markup, home route; only the shared helpers are byte-identical).
  Render the new state as its own view, consistent with the other per-kind
  error views, with a stable `data-testid` following the existing naming
  convention. Keep the `errorActions` / `retry` fallbacks behaving as they do
  for a kind with no action.
- [ ] **Review the neighbouring states for copy coherence** (do not rewrite
  them): `expired-link` currently says "Request a new link" — after this
  ticket, a dead link and a cooldown are two different situations and the
  `expired-link` copy must not imply an immediate re-request is possible.
  A one-line cross-reference to the cooldown copy is enough; changing
  `expired-link` semantics is out of scope.
- [ ] **Specs, mirrored in BOTH apps.** Extend the existing
  `activation-core.spec.ts` / `activation-flow` specs and
  `activate.page.spec.ts` (do **not** start a new parallel spec module):
  - a `409` (with and without `Retry-After`) classifies as the new cooldown
    kind — **not** `unknown`, **not** `resend-cooldown`;
  - the `429` → `resend-cooldown` / `attempt-cap` split is unchanged
    (regression guard — the 409/429 cases sit next to each other in the
    classifier and are easy to break);
  - the EN **and** ES copy for the new kind renders the explanation (assert
    the copy is non-empty and locale-distinct, following the pattern the
    existing copy tests already use);
  - the state renders in the page with no action button;
  - the same classification works when the error arrives as `pole_analyst`'s
    `ApiError` shape (with `retryAfter` already parsed) as well as the raw
    `HttpErrorResponse` shape.
  - Keep `activation-parity.spec.ts` **green in both apps** — the two copies
    of `activation-core.ts` / `activation-flow.ts` are compared byte-for-byte
    and **must** be edited in the same commit.
- [ ] Run the suites in **both** apps; `pole_fe` stays at its 371-passing
  baseline **plus** the new cases and `pole_analyst` matches.

## Explicitly OUT of scope (do not spec backend changes)

- **No backend change of any kind.** No new endpoint, no new field on an
  existing response, no new status code, no reworded `detail` string. The
  409 + `Retry-After` already exists and is sufficient.
- **No change to the cooldown rule itself.** It stays a hard 14 days
  (ADR-007 Decision 2). Nothing here shortens, softens or bypasses it.
- **No "check my cooldown" pre-flight GET.** It would be an
  account-enumeration oracle on an unauthenticated endpoint; the ADR records
  this as considered-and-rejected.
- **No change to the 60s resend cooldown** — different clock, different copy,
  owned by PAIML-KEYCLOAK-032 / -033.
- **No backend polish of `_cooldown_message`.** Leave the English-only detail
  string alone; it is a diagnostic, and the page does not display it.
- **Do not** unify the two per-app `activate.page.ts` files.

## Acceptance Criteria (Definition of Done for this Ticket)

- [ ] A cooldown answer renders a **distinct, explanatory** state on
  `/activate` in both apps — not the generic "Something went wrong" view, and
  not a bare hours number.
- [ ] The copy explains **why** (this email already had a temporary-access
  session) and **what to do next** (request again after the cooldown), in
  **EN and ES**.
- [ ] The re-request **date** (or day count) is shown when `Retry-After` is
  present; when the header is absent, the explanation still renders **without
  inventing a number**.
- [ ] The existing `410 expired-link` and `404 invalid-link` states keep
  rendering their own copy, unchanged in behaviour.
- [ ] The `429 → resend-cooldown / attempt-cap` split is untouched (proven by
  a regression test).
- [ ] The new state carries no misleading action button.
- [ ] `activation-core.ts` and `activation-flow.ts` remain **byte-identical**
  between `pole_fe` and `pole_analyst` (parity guard green in both), and both
  `activate.page.ts` files render the new view.
- [ ] **No file under `app/pole_api/` is modified by this ticket** (state this
  in the PR description so the reviewer can verify the scope claim cheaply).
- [ ] New tests **fail against the pre-change code**; both app suites green
  (≥371 + new cases), ≥80% coverage.

## Integration Tests to Run (Local Verification)

- [ ] Stub the activation chain to answer `409` with
  `Retry-After: 1209600` (14d): assert the cooldown view renders with the
  explanation and a date, in EN and in ES (`Accept-Language` / `navigator.language`).
- [ ] Answer `409` with **no** `Retry-After`: assert the view still renders the
  explanation and shows **no** fabricated time.
- [ ] Answer `410`: assert the `expired-link` view (not the cooldown view).
- [ ] Answer `404`: assert the `invalid-link` view.
- [ ] Answer `429` from `send-code`: assert `resend-cooldown` still renders
  with its countdown (the 60s gate must not be captured by the new 409 case).
- [ ] Open the same URL in `pole_fe` and `pole_analyst` and confirm the two
  pages show the **same** state for the **same** 409.
- [ ] Full `pole_fe` + `pole_analyst` suites green.

## Dependencies
- **Blocks:** None
- **Blocked By:** PAIML-KEYCLOAK-033 (auto-send lands the page directly on the
  code step; this ticket adds states to that same flow, and the 409/429
  classifier cases sit next to the `already_sent` handling 033 introduces)

## Estimated Effort
- [S] (Small 2–3h)

> **Cross-reference:** [ADR-007](../../decisions/ADR-007-temp-access-link-reuse-and-audit-retention.md)
> (Decision 2 — the cooldown stays hard, the *message* is the deliverable;
> and the recorded rejection of a pre-flight cooldown endpoint),
> PAIML-KEYCLOAK-032 (the 60s resend cooldown — a **different** clock),
> PAIML-KEYCLOAK-033 (auto-send + `already_sent` on the same page),
> PAIML-KEYCLOAK-023 (the `/activate` pages, `ActivationFlow`,
> `activation-core.ts` and the byte-identical duplication rule this ticket
> edits), and [PLAN_PHASE_12.md](../../plan/PLAN_PHASE_12.md).
