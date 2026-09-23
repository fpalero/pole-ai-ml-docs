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
- [ ] Route `/?temp_token=xxx` → `/activate?temp_token=xxx` on both apps,
  preserving the token through the redirect.
- [ ] Build the `/activate` page per app: token state (loading/missing),
  **Validate button** → `POST /api/auth/temporary-access/send-code`,
  code-input step (6-digit, numeric, EN+ES copy) → `POST
  /api/auth/temporary-access/verify-code`, success → store session + enter the
  app.
- [ ] Render all backend states distinctly: expired/invalid token (410/404),
  app mismatch (403), resend cooldown countdown (429/60s), attempt cap (429/5),
  expired code (410) — each with a retry/resend affordance, EN+ES copy.
- [ ] Apply per-app branding (each page matches its host app's theme); share
  the API-call logic via one helper used by both pages.
- [ ] No live-session re-ask: authenticated in-app navigation never routes back
  to `/activate`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Both apps serve `/activate?temp_token=xxx`; `/?temp_token=xxx`
  deep-links into it with the token intact.
- [ ] Validate button + code input work end-to-end against 022 (link → code →
  session → app entry) on both hosts.
- [ ] Expired/invalid token, app mismatch, resend-cooldown, attempt-cap, and
  expired-code states each render distinctly (EN+ES).
- [ ] Each page carries its own app's branding; no cross-app token redemption.

## Integration Tests to Run (Local Verification)
- [ ] Manual E2E per app (local FE + Mailpit): request → link → Validate →
  code → app entry; screenshot each state.
- [ ] Cross-app negative: `pole-fe` token on the `pole-analyst` page → mismatch
  state (and mirror).
- [ ] Cooldown/attempt visuals: resend <60s shows countdown; 5 wrong codes show
  the cap state.

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-024
- **Blocked By:** PAIML-KEYCLOAK-022

## Estimated Effort
- [M] (Medium 3–5h)
