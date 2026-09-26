# Ticket: PAIML-KEYCLOAK-023

## Title
[FE] Per-app activation pages (/activate?temp_token) with Validate + code states

## Description
The direct link (`https://<host>/?temp_token=xxx`) and the OTP endpoints
(021/022) need their UI: each app (`pole_fe`, `pole_analyst`) ships an
`/activate?temp_token=xxx` page that routes the deep link, offers a
**Validate button** (fires `send-code`), then a code-input step (fires
`verify-code`), with clear expired/invalid/rate-limited states and per-app
branding.

Why per-app pages (decision record):
- **Token is app-bound.** Each host owns its activation UX so a `pole-fe`
  token can never be redeemed inside the `pole-analyst` page (and vice versa);
  cross-app presentation shows the mismatch state.
- **Per-app branding.** The two apps keep their own look; shared logic lives in
  one activation helper used by both pages.

## Repository
FE/monorepo (pole_fe + pole_analyst)

## What to Do (Implementation Steps)
- [x] Route `/?temp_token=xxx` → `/activate?temp_token=xxx` on both apps,
  preserving the token through the redirect.
- [x] Build the `/activate` page per app: token state (loading/missing),
  **Validate button** → `POST /api/auth/temporary-access/send-code`,
  code-input step (6-digit, numeric, EN+ES copy) → `POST
  /api/auth/temporary-access/verify-code`, success → store session + enter the
  app.
- [x] Render all backend states distinctly: expired/invalid token (410/404),
  app mismatch (403), resend cooldown countdown (429/60s), attempt cap (429/5),
  expired code (410) — each with a retry/resend affordance, EN+ES copy.
- [x] Apply per-app branding (each page matches its host app's theme); share
  the API-call logic via one helper used by both pages.
- [x] No live-session re-ask: authenticated in-app navigation never routes back
  to `/activate`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] Both apps serve `/activate?temp_token=xxx`; `/?temp_token=xxx`
  deep-links into it with the token intact.
- [x] Validate button + code input work end-to-end against 022 (link → code →
  session → app entry) on both hosts.
- [x] Expired/invalid token, app mismatch, resend-cooldown, attempt-cap, and
  expired-code states each render distinctly (EN+ES).
- [x] Each page carries its own app's branding; no cross-app token redemption.

## Integration Tests to Run (Local Verification)
- [ ] Manual E2E per app (local FE + Mailpit): request → link → Validate →
  code → app entry; screenshot each state. → **deferred to
  PAIML-KEYCLOAK-024** (024's scope; not run in 023).
- [ ] Cross-app negative: `pole-fe` token on the `pole-analyst` page → mismatch
  state (and mirror). → **deferred to PAIML-KEYCLOAK-024** (the state is
  implemented and unit-covered; the live Mailpit negative is 024's).
- [ ] Cooldown/attempt visuals: resend <60s shows countdown; 5 wrong codes show
  the cap state. → **deferred to PAIML-KEYCLOAK-024** (implemented + unit-covered;
  the live visual pass is 024's).

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-024
- **Blocked By:** PAIML-KEYCLOAK-022

## Estimated Effort
- [M] (Medium 3–5h)

---

## Close-Out Note (implementation record)

**Status:** ✅ DONE — implemented in `pole-ai-ml` on
`feature/PAIML-KEYCLOAK-023-activation-pages` (base `develop`), merged via
[`pole-ai-ml` PR #357](https://github.com/fpalero/pole-ai-ml/pull/357)
(merge commit `3e2d935`, 2026-09-26; 4 commits, 38 files, +5835 / −21).

> The manual Mailpit E2E listed under "Integration Tests" was **not** run here —
> it is `PAIML-KEYCLOAK-024`'s scope and stays open.

### What shipped

| Area | Change |
|---|---|
| `/activate` page (×2 apps) | `pole_fe` and `pole_analyst` both serve `/activate?temp_token=…` and run the **Validate → 6-digit code → session** handshake against the 022 endpoints. Each page carries its own host app's branding (pole_fe dark terminal theme, pole_analyst "Pole AI Coach" light theme). |
| Deep-link routing | `/?temp_token=…` is intercepted and routed to `/activate?temp_token=…` with the token preserved. Implemented as a **function `redirectTo`**, not a `canActivate` guard — see decision 3. |
| Shared activation helper (duplicated) | `core/activation/activation-core.ts` (EN+ES copy for every state, HTTP classification, token/code parsing — framework-free, so unit-tested without `TestBed`), `activation-flow.ts` (page state machine), `activation.service.ts` (the two POSTs, via each app's own `ApiClientService` so the absolute-vs-`/api`-proxy base-URL topology stays app-native), `activation-session.service.ts` (adopts the session into the Keycloak adapter). |
| Drift guard | `activation-parity.spec.ts` pins the copies **byte-identical** in both apps; verified to fail when they are made to diverge. This is what makes the duplication safe. |
| `Retry-After` preservation | `pole_analyst`'s `apiInterceptor` / `ApiError` were updated to preserve the `Retry-After` header so the cooldown countdown is server-driven (a deployment with a tuned cooldown is not told 60s by the client). |
| Baseline repair (separate commit) | `pole_fe`'s unit suite **did not compile at `develop`** (`jobs-store.service.spec.ts` omitted `JobDto.entity_name`), so *zero* tests ran. Fixing that compile error surfaced **64** further failures it had been masking; all were fixed (missing `entity_name`; missing `KEYCLOAK` provider for the `TrickDetailPage` media-binding specs; `bulkExtract` two-step flow in `trick-detail.bulk.spec`; `localStorage` leakage of the root-singleton `ChatbotWsService` session id). A green baseline is what makes the new tests meaningful. |

### States rendered distinctly (EN + ES, each with its own affordance)

| state | backend | affordance |
| :--- | :--- | :--- |
| missing token | — | hint to open the link as emailed |
| invalid link | `404` | *request a new link* (hint only) |
| expired link | `410` | *request a new link* (hint only) |
| app mismatch | `403` | **none** — a new code cannot fix a link issued for the other app |
| resend cooldown | `429` on `send-code` | countdown from `Retry-After`, resend disabled |
| attempt cap | `429` on `verify-code` | request a new code |
| wrong code | `401` | retry |
| malformed code | `400` | re-enter |
| session failure | `502` | retry |
| unavailable | `503` | retry |

The two **dead-link** states (404/410) deliberately offer **no** button: the code
is armed per-link server-side, so re-sending against a dead token just
reproduces the same error, and the FE has no endpoint to request a fresh email —
the "request a new link" hint is the only honest affordance.

### Backend contract respected (022 follow-ups)

- `send-code` / `verify-code` bodies carry **no `clientId`** — the app binding is
  derived server-side from `Origin`, exactly as 022's close-out specified. No
  call overrides headers, so the browser `Origin` reaches the API and a
  cross-app token gets a genuine `403` → the app-mismatch state. Pinned by a spec
  asserting the POST call has exactly two arguments.
- **`429` is disambiguated by step** — resend cooldown (`send-code`) vs attempt
  cap (`verify-code`). Same status code, two different user-facing states.

### Decisions taken at implementation time

1. **`/activate` uses the `check-sso` flow, NOT `login-required`.** With
   `login-required`, Keycloak redirects before the page renders, so the emailed
   link appears broken. `check-sso` adopts an existing SSO session silently and
   does not redirect when there is none — exactly the unauthenticated case the
   page exists to serve. **A plain `/` still requires login** (see the
   review-round regression below).
2. **The deep link is a `redirectTo` function, not a guard.** Only the redirect
   function sees the partially-matched snapshot, so it — and only it — can choose
   its target from the query string. The redirect target must be **relative**:
   Angular raises `AbsoluteRedirect` against a `PartialMatchRouteSnapshot` for an
   absolute target. (The token survives the redirect because
   `Recognizer.recognize()` re-attaches `urlTree.queryParams` to the final tree —
   asserted against `router.url` in the routing spec, not via a route property.)
3. **The activation helper is DUPLICATED in both apps rather than shared**,
   because `pole_fe` and `pole_analyst` are separate npm builds with no shared
   workspace. The parity spec (`activation-parity.spec.ts`) is what makes this
   duplication safe.
4. **No new env vars.** 023 introduced **no** configuration — it consumes the
   existing 021/022 contract, so [`docs/ENV_VARS.md`](../../../ENV_VARS.md) is
   unchanged by this ticket.

### ⚠️ KNOWN GAP — documented, NOT fixed in this ticket

**`authGuard` is attached to zero routes in either app.** It is defined in
`core/auth/auth.guard.ts` and re-exported from `app.config.ts`, but
`grep canActivate|canActivateChild|canMatch` returns only its own definition —
and the sole `keycloak.login()` call site lives inside that unused guard (there
is no login button; `app.ts` only has `logout()`). The **blocking auth
initializer is therefore the apps' only working auth trigger.** The gap is
documented in `provide-auth.ts` so the dependency is not rediscovered the hard
way, but **wiring the guard onto the lazy feature routes is a separate change,
deliberately out of 023's scope** (it would change behaviour for every route in
both apps, not just the activation path).

### Reviewer-caught regression worth calling out

The `/oc review` on PR #357 requested changes: **1 blocking + 5 non-blocking**,
all fixed before merge. The blocking one is the most valuable thing this ticket
produced:

> **`isActivationPath()` classified the ROOT path as an activation path**, so
> every visit to `/` — with or without a `temp_token` — initialised with
> `check-sso` instead of `login-required`. Combined with the `authGuard` gap
> above, an unauthenticated visitor opening `/` was dropped onto an unguarded
> feature page with no auth header, every API call 401ing, and **no in-app way to
> sign in** — a regression on the **front door** of both apps. The deep link
> worked and CI was green, but the **plain-root case was never checked**. Fixed
> by treating the root as an activation path only when it actually carries a
> non-blank `temp_token`; a plain `/` keeps `login-required`. Covered by explicit
> regression specs in both apps (bare `/`, empty search, `?other=1`,
> `?temp_token=`, `?temp_token=%20`).

The 5 non-blocking fixes: restored a **deleted passing behavioural test** in
`pole_analyst`'s `app.routes.spec.ts` (the analysis-history router test from
`PAIML-POLE-ANALYST-042` had been traded for a weaker static assertion, though
023 never touched those routes); removed the **dead-end "Request a new link"
button** on `expired-link` (it re-fired `send-code` against the dead token);
removed a duplicated `KEYCLOAK` provider; merged a duplicated JSDoc block; and
corrected a comment claiming a nonexistent `queryParamsHandling: 'preserve'`
route property (+ removed the genuinely dead `buildActivateUrl()`).

### Acceptance criteria — verified

- [x] Both apps serve `/activate?temp_token=xxx`; `/?temp_token=xxx`
      deep-links into it with the token intact (routing spec asserts the token
      in `router.url`).
- [x] Validate button + code input work end-to-end against 022 (link → code →
      session → app entry) on both hosts — the session→interceptor seam is
      pinned end-to-end against the **real** adapter.
- [x] Expired/invalid token (404/410), app mismatch (403), resend-cooldown (429
      + countdown), attempt-cap (429) and expired-code (410) states each render
      distinctly (EN + ES).
- [x] Each page carries its own app's branding; no cross-app token redemption
      (the `Origin`-derived `403` is rendered as the mismatch state).
- [x] No live-session re-ask: `check-sso` silently adopts an existing session on
      an activation page load; elsewhere is unchanged.

### Test evidence

| Suite | Result |
|---|---|
| `pole_fe` unit tests | **371 passed** (24 files) — was 0 (suite did not compile); baseline repair took it 244 → 371 |
| `pole_analyst` unit tests | **1260 passed** (81 files) — was 1133 |
| `ng build` (both apps) | ✅ green |
| `ng lint` (`pole_analyst`) | ✅ clean (`pole_fe` has no lint target) |
| CI on PR #357 | **12/12 checks SUCCESS** |

### 🔴 FOLLOW-UP / POLICY ITEM — half of this diff has no CI coverage (NOT fixed here)

**`fe-checks.yml` only triggers on `app/pole_analyst/**`, so the `pole_fe` half
of this diff has NO CI coverage.** Its 371 tests — and the ~2,900 new lines
including the baseline repair — rest on a **local run only**, unverified by any
gate. The workflow's `paths` were **deliberately NOT widened** in PR #357: that
would add a `pole_fe` lint/test/build gate to every future PR touching that app,
which is a **policy change to a shared CI file** rather than part of this ticket.
It is left for a **separate PR**.

This matters more than a generic coverage note: the gap is *exactly* what hid the
`pole_fe` compile error that the baseline repair fixes — a broken `pole_fe`
suite reports success, because nothing runs it. **Half of the Phase 9 UI is
currently unguarded by CI.**

### Other follow-ups

- **024 (Mailpit E2E) remains the only open Phase 9 gate** and should now cover
  the full matrix 023's states implement: request → link email → Validate → code
  email → app entry; the `Origin`-derived 403 cross-app negative on both hosts;
  the 60s resend 429 with the `Retry-After` countdown; the 5-attempt cap; and
  the pinned-window re-entry.
- **Wiring `authGuard` onto the feature routes** (the known gap above) is a
  separate change; until it lands, the blocking initializer is the only auth
  trigger, so any change to `provide-auth.ts` is high-blast-radius.
- **Widening `fe-checks.yml` to `app/pole_fe/**`** — separate PR, policy
  decision (see the follow-up above).
- 🔴 **Rollout blockers are unchanged from 022** and live in the infra repo
  `pole-ai-ml-infra` (never `pole-ai-ml`): `TEMP_ACCESS_OTP_PEPPER` must be
  provisioned per environment or both OTP endpoints answer `503`; **Direct
  Access Grants must be enabled** on the `pole-fe` / `pole-analyst` clients; and
  `FE_BASE_URL` / `ANALYST_BASE_URL` / `BREVO_API_KEY` must be set per
  environment. See [`docs/ENV_VARS.md`](../../../ENV_VARS.md).
- The passwordless grant returns **no refresh token**, so the adopted session
  cannot self-renew; when it lapses the user re-enters through Keycloak. A real
  token exchange is tracked in `PAIML-KEYCLOAK-025` (FUTURE).
