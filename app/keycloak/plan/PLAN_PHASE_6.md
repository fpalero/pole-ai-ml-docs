# Plan Phase 6 — Stitch Pixel-Perfect Login Restyle (`pole-ai-login` theme)

> **Parent plan:** [PLAN.md](../PLAN.md)
> **Status:** ✅ DONE (implementation merged + QA GREEN; awaiting USER manual
> develop→main promotion — NOT closed until the user confirms)
> **Design source:** Stitch project **"Pole AI Coach"** (`projects/4315784734923719370`)
> - Desktop screen: **"Login - Dual Authentication (Password & Temporal Access)"**
>   (`screens/f1114f2f53b64fb3a1198b009e0303e5`, 1280×800)
> - Mobile screen: **"Login - Mobile Responsive"** (`screens/0aa9b4fafa3f483d89968a772752a84b`, 390px)
> - Design system: **Kinetic Precision v2** (`assets/5a94957f23e0414699f5396c23e524be`) —
>   LIGHT, Inter, ROUND_EIGHT, primary `#00685f` / hover `#00524b`, surfaces
>   `#f8f9ff` / `#eff4ff` / `#ffffff`
> **Class:** FE-only (Keycloak login-theme restyle). No new or changed backend endpoints.

## Scope

Restyle the existing custom Keycloak login theme `pole-ai-login` (shipped in Phase 1,
tickets PAIML-KEYCLOAK-001..004) from its current **dark indigo** look
(`--pole-bg-dark: #0f172a`, `--pole-primary: #4f46e5`, side-by-side dual panels with OR
divider) to the new Stitch design **pixel-perfect**: light **Kinetic Precision** theme,
single centered card (`max-w-[440px]`), brand header bar, welcome header, segmented
Password / Temporary-Link tab switcher, and fully responsive desktop + mobile rendering.
Behavior (standard Keycloak password POST + `fetch POST /api/auth/temporary-access`
magic-link flow from Phase 2) is **unchanged** — only markup, tokens, and styles move.

## Context

- Current theme files (repo `pole-ai-ml-infra`, on disk `infrastracture/keycloak/themes/pole-ai-login/`):
  `login/login.ftl` (dual `.pole-dual-panel-container` row layout), `login/resources/css/login.css`
  (dark variables), `login/resources/js/temporary-access.js` (submit handler posting
  `{email, clientId}`), `login/messages/messages_{en,es}.properties`, `login/theme.properties`
  (`parent=keycloak`, `styles=css/login.css`, `scripts=js/temporary-access.js`, `locales=en,es`).
- Stitch desktop HTML (Tailwind CDN, Inter via Google Fonts, Material Symbols) and mobile HTML
  (Tailwind v3 + forms plugin, inline SVG icons, `role=tablist`/`tabpanel`, 48px touch targets)
  were fetched 2026-09-04 and are the pixel reference. Keycloak cannot rely on CDN Tailwind /
  Google Fonts / Material Symbols at runtime — the theme must **hand-compile** the Stitch
  utilities into vanilla `login.css` and inline SVGs (see ticket for the full token table).
- Backend contract is frozen: `POST /api/auth/temporary-access` (`{email, clientId}` → 202/409/422)
  and `POST /api/auth/temporary-access/activate` (`{token}` → 200) in
  `app/pole_api/src/auth/controllers/temporary_access.py`, plus the lazy-activation hook in
  `core/auth.py`. Every field the design renders (username/email, password, magic-link email)
  is already covered — **no BE change**.

## Tasks

### FTL restructure (single card + tabs, Keycloak bindings preserved)
- [x] [Infra theme] Rewrite `login/login.ftl`: sticky brand header (40px `sports_gymnastics`
  tile + "Pole AI Coach" 18px bold `#00685f` + 11px subtitle), centered card `max-w 440px`
  `rounded-2xl` with gradient welcome header (`lock_open` badge, "Welcome Back" 24px bold,
  "Sign in to review your routines"), segmented tab bar (`switchAuthMode`), password form +
  magic-link form (one hidden at a time), `Coach & Studio Network` divider.
- [x] [Infra theme] Keep all Keycloak bindings: form `action="${url.loginAction}" method="post"`,
  inputs `name="username"` / `name="password"`, hidden `credentialId`, `messagesPerField`
  error spans, `rememberMe` + `url.loginResetCredentialsUrl` hooks (visually hidden — the
  Stitch cards render empty placeholders there), `url.registrationUrl` info section, `msg()`
  keys only (zero hardcoded English — add new keys to both `messages_en/es.properties`).

### Token + CSS port (Tailwind → vanilla, pixel values)
- [x] [Infra theme] Replace dark variables in `login.css` with Kinetic Precision tokens:
  primary `#00685f` / hover `#00524b` / active `#00433e`, bg `#f8f9ff` (mobile `#F6F8F9`),
  card `#ffffff`, inputs `bg-slate-50 border-slate-300 rounded-lg(8px) py-2.5 pl-10`,
  focus `ring 2px #00685f/30`, labels `12px semibold uppercase tracking-wider slate-600`,
  info box `teal-50/70 + teal-200/80 rounded-xl 12px`, success `emerald-50/200`, divider
  `slate-200 / 12px uppercase slate-400`, Inter stack with system fallback (no webfont CDN).
- [x] [Infra theme] Port desktop + mobile responsive rules: `≥768px` centered card, `<768px`
  compact header (`px-4 py-3`, 32px brand tile, 14px/10px titles), `max-w-md px-4 py-5` main,
  `min-h-[48px]` buttons, `tap-scale .985`, `-webkit-tap-highlight transparent`,
  `aria-selected` tab states, password-visibility eye toggle (keep `tracking-widest` detail).

### JS + i18n (behavior unchanged, Stitch interactions adopted)
- [x] [Infra theme] Extend `temporary-access.js`: tab switcher (`switchAuthMode`, active =
  white + `shadow-sm`), password-visibility toggle (eye/eye-off swap), magic-link submit with
  `Sending Link… → Link Sent (emerald-600)` + success box showing the target email
  (`sent-target-email` span), `clientId` from `client_id` query (default `pole-fe`),
  endpoint override via `data-endpoint`, `data-invalid-email` message — all strings via
  `data-*` attributes fed from `msg()` (JS stays locale-free).
- [x] [Infra theme] Add message keys (en + es): tab labels, welcome title/subtitle, field labels,
  placeholders (`athlete@domain.com or coach_sarah`, `••••••••••••`, `athlete@polecoach.com`),
  info/helper copy (incl. "valid for 15 minutes" / "Single-use access token"),
  `Send Temporal Access Link` / `Sending…` / `Link Sent`, `Access Link Dispatched!` success copy,
  `Coach & Studio Network` divider, brand subtitle.

### Verification
- [x] [Infra] `helm lint` + `helm upgrade --dry-run` for the theme ConfigMap volume change
  (no chart value changes expected — theme files only).
- [x] [Manual] Side-by-side pixel check: Stitch screenshots (`files/4492113200649409432`
  desktop, `files/17420304227306261558` mobile) vs. rendered Keycloak page at desktop 1280px
  and mobile 390px (header, card width, tab states, focus rings, info/success boxes, divider).
- [x] [Manual] Functional regression: password login POST still hits `url.loginAction`;
  magic-link submit still `POST /api/auth/temporary-access` → 202 + Mailpit email (local);
  invalid email → inline error; 409 cooldown → error box (no new endpoints).

## Dependencies

- Phase 1 theme (PAIML-KEYCLOAK-001..004) — this phase overwrites its FTL/CSS/JS/messages.
- Phase 2 endpoints (`POST /api/auth/temporary-access`, `POST /api/auth/temporary-access/activate`) — reused as-is.
- Phase 5 SMTP (Mailpit local / Brevo staging) — email delivery path unchanged.
- No `pole_api`, `pole_fe`, or `pole_analyst` code changes (auth in `pole_analyst` stays deferred, PAIML-POLE-ANALYST-028).

## Acceptance Criteria

- [x] Keycloak login renders the Stitch design pixel-perfect on desktop (1280px) and mobile
  (390px): brand header, 440px card, tabs, both forms, info/success states, divider —
  matching the token table (primary `#00685f`, Inter, 8px radius, 8px grid) —
  fe-developer verdict PIXEL-PERFECT, no fix PR.
- [x] Password submit performs a standard Keycloak login POST (no JS interception breaking auth);
  magic-link submit posts `{email, clientId}` and shows Stitch success/error states.
- [x] All user-visible copy resolves via `msg()` in both `en` and `es` locales.
- [x] No external runtime deps (no Tailwind CDN, no Google Fonts, no Material Symbols font —
  inline SVG only).
- [x] `helm lint` + dry-run pass; local Keycloak redeploy shows the new theme.
- [ ] USER manual testing + manual develop→main promotion (open — phase NOT closed until
  the user confirms).

## Merge record

- Ticket: `phase-6-stitch-login-restyle/PAIML-KEYCLOAK-014.md`.
- Infra PR [#24](https://github.com/fpalero/pole-ai-ml-infra/pull/24) — MERGED
  (squash `b04bb69` into `develop`, 2026-09-03). `/oc review` approved, zero findings.
- fe-developer conformance verdict: PIXEL-PERFECT, no fix PR, no files changed.

## QA gate result

- **Verdict:** GREEN, 4/4 (tester phase-end gate, local k3s rev 13, commit `b04bb69`). Error list empty.
- **Checks:** (1) visual desktop 1280px + mobile 390px vs Stitch; (2) password POST
  failure-path (standard `Invalid username or password`, zero JS errors); (3) magic-link
  202 + Mailpit delivery, invalid-email inline error, 422 backend validation, 409 cooldown
  error-box path; (4) en full render + es key parity (24/24 keys identical).
- **Evidence:** `/tmp/qa014-login-desktop-1280.png`, `/tmp/qa014-login-desktop-magiclink.png`,
  `/tmp/qa014-login-desktop-invalid-email.png`, `/tmp/qa014-login-mobile-390.png`,
  served-asset captures + Keycloak/API log tails.
- **Non-blocking observations:**
  1. Realm `internationalizationEnabled` is off locally → live `kc_locale=es` falls back
     to English; theme-side es parity proven, no theme change needed.
  2. Theme JS uses relative `/api/auth/temporary-access` with `data-endpoint` override
     (pre-existing Phase 2 behavior, unchanged by this FE-only restyle) — confirm the
     origin/proxy story before staging promotion.
- **Promotion pending:** USER manual testing + manual develop→main promotion.
