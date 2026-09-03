# Ticket: PAIML-KEYCLOAK-014

## Title
[Keycloak] Pixel-perfect Stitch restyle of `pole-ai-login` (Kinetic Precision light theme)

## Description
Apply the new Stitch **"Pole AI Coach"** login design
(`projects/4315784734923719370`, desktop screen `f1114f2f53b64fb3a1198b009e0303e5`
"Login - Dual Authentication", mobile screen `0aa9b4fafa3f483d89968a772752a84b`,
design system Kinetic Precision v2 `assets/5a94957f23e0414699f5396c23e524be`) pixel-perfect
to the current Keycloak `pole-ai-login` theme. Today's theme is dark indigo
(`--pole-bg-dark #0f172a`, `--pole-primary #4f46e5`, side-by-side dual panels + OR divider);
the target is the light single-card layout: sticky brand header, `max-w-[440px]` white
`rounded-2xl` card, gradient welcome header, segmented **Password / Temporary Link** tabs,
Stitch info + success boxes, `Coach & Studio Network` divider, responsive desktop (1280px) +
mobile (390px). Backend behavior is frozen — reuse `POST /api/auth/temporary-access` and
`POST /api/auth/temporary-access/activate` as-is (FE-only change, no new endpoints).

Full phase detail: [PLAN_PHASE_6.md](../plan/PLAN_PHASE_6.md).

## Repository
pole-ai-ml-infra

## What to Do (Implementation Steps)
- [x] Rewrite `infrastracture/keycloak/themes/pole-ai-login/login/login.ftl` → Stitch single-card
  structure (brand header + welcome header + tab bar + password form + magic-link form + divider),
  keeping Keycloak bindings: `action="${url.loginAction}" method="post"`, `name="username"` /
  `name="password"`, hidden `credentialId`, `messagesPerField` error spans, `rememberMe` +
  `url.loginResetCredentialsUrl` hooks (visually hidden), `url.registrationUrl` info block,
  all copy via `msg()` (no hardcoded strings)
- [x] Replace `login/resources/css/login.css` dark variables with Kinetic Precision tokens compiled
  from Stitch (no Tailwind CDN at runtime): primary `#00685f` / hover `#00524b` / active `#00433e`,
  bg `#f8f9ff` (mobile `#F6F8F9`), card `#ffffff`, inputs `bg-slate-50 border-slate-300 8px radius
  py-2.5 pl-10`, focus `ring 2px #00685f/30`, labels `12px semibold uppercase slate-600`,
  info `teal-50/70 + teal-200/80 rounded-xl`, success `emerald-50/200`, divider `slate-200`,
  Inter + system fallback; port responsive rules (compact mobile header 32px tile / 14px+10px titles,
  `max-w-md px-4 py-5` main, `min-h 48px` buttons, `tap-scale`, `aria-selected` states, eye toggle)
- [x] Extend `login/resources/js/temporary-access.js`: `switchAuthMode` tab switcher, password
  visibility toggle, magic-link `Sending… → Link Sent (emerald-600)` + success box with
  `sent-target-email`, `clientId` from `client_id` query (default `pole-fe`), `data-endpoint`
  override, locale-free strings via `data-*` from `msg()`
- [x] Add message keys to `login/messages/messages_en.properties` + `messages_es.properties`:
  tab labels, welcome title/subtitle, field labels/placeholders, 15-minute info + single-use helper,
  submit/sending/sent states, `Access Link Dispatched!` success copy, divider text, brand subtitle
- [x] Inline SVG icons only (sports_gymnastics, lock_open, password/mail_lock, person/key/visibility,
  alternate_email, info, check_circle, send, arrow_forward) — remove Material Symbols / Google Fonts
  runtime dependency; keep `theme.properties` (`parent=keycloak`, styles, scripts, `locales=en,es`)
- [x] `helm lint` + `helm upgrade --dry-run` (theme ConfigMap volume); redeploy local Keycloak and
  pixel-compare against Stitch screenshots `files/4492113200649409432` (desktop) and
  `files/17420304227306261558` (mobile) at 1280px / 390px

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] Keycloak login matches Stitch pixel-perfect (desktop + mobile): header, 440px card, tabs,
  both forms, info/success boxes, divider, tokens (`#00685f`, Inter, 8px radius) —
  fe-developer verdict PIXEL-PERFECT, no fix PR
- [x] Password submit still performs the standard Keycloak login POST; magic-link submit still
  `POST /api/auth/temporary-access {email, clientId}` → 202 + Mailpit email locally
- [x] All copy localized via `msg()` in `en` and `es`; no external CDN deps at runtime
- [x] `helm lint` + dry-run pass; new theme visible after local redeploy
- [ ] USER manual testing + manual develop→main promotion (open — ticket NOT closed until
  the user confirms)

## Integration Tests to Run (Local Verification)
- [x] Desktop 1280px + mobile 390px side-by-side vs. Stitch screenshots (visual pass)
- [x] pole-fe.local → Keycloak → password login works (standard flow, no JS breakage)
- [x] Magic-link submit → 202 + email in Mailpit UI; invalid email → inline error; 409 cooldown → error box
- [x] `es` locale renders all new keys (no missing-key fallbacks)

Evidence: `/tmp/qa014-login-desktop-1280.png`, `/tmp/qa014-login-desktop-magiclink.png`,
`/tmp/qa014-login-desktop-invalid-email.png`, `/tmp/qa014-login-mobile-390.png`.
Full detail: [PLAN_PHASE_6.md](../plan/PLAN_PHASE_6.md) ("QA gate result").

## Merge record
- Infra PR [#24](https://github.com/fpalero/pole-ai-ml-infra/pull/24) — MERGED
  (squash `b04bb69` into `develop`, 2026-09-03). `/oc review` approved, zero findings.
- Phase-end QA gate: GREEN, 4/4 (tester, local k3s rev 13). Error list empty.
- Non-blocking observations: (1) realm i18n flag off locally (es fallback, theme parity
  proven); (2) relative `/api/auth/temporary-access` fetch with `data-endpoint` override
  (pre-existing Phase 2 behavior).

## Dependencies
- **Blocks:** None
- **Blocked By:** None (overwrites PAIML-KEYCLOAK-003 theme files; reuses PAIML-KEYCLOAK-005/006 endpoints)

## Estimated Effort
- [M] (Medium 2–4h)
