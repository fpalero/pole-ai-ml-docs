# Plan Phase 9 — Passwordless Direct-Link + Activation-Code Flow

> **Parent plan:** [PLAN.md](../PLAN.md)
> **Status:** 🟡 PARTIAL — tickets 021 (BE root) ✅ DONE and 022 (OTP send/verify) ✅ DONE; 023–025 outstanding (025 FUTURE)
> **Class:** BE (`pole_api`, repo `pole-ai-ml`) + FE (`pole_fe`/`pole_analyst` activation pages) + QA. No Keycloak realm/theme or Helm changes (theme keeps its self-service entry point; Keycloak sends no email in this phase).

## Scope

Replace the Keycloak `execute-actions-email` magic-link flow (phases 1–8) with a
**passwordless direct-link + activation-code flow owned entirely by `pole_api`**:

1. Temp user creation has **no `temporary: True` flag** (passwordless UX — no
   password-setup friction). Temp users get a **hidden random password known
   only to `pole_api`** (never emailed, never shown). Permanent users keep
   password login unchanged.
2. `pole_api` sends **both emails via Brevo** (sender `no-reply@fpalero.cc`,
   EN+ES templates). **Keycloak sends NOTHING** (no `execute-actions-email`,
   no verify-email action).
3. Self-service entry stays on the login theme (**Get temporary access → email**),
   but the delivered link is a **per-app direct link**
   `https://<host>/?temp_token=xxx` bound to one host, leading to a per-app
   `/activate?temp_token=xxx` page with a **Validate button → 6-digit code →
   verify** handshake that opens the 2-hour window.
4. OTP hardening: 6-digit code, **10-minute TTL, max 5 attempts, 60-second
   resend cooldown**. Re-entry via the link inside the live window still asks a
   fresh code but **never extends the window past its original end**
   (e.g. 10:00→12:00 stays 12:00).
5. In-app navigation with a live session does **NOT** re-ask for a code.
6. Everything else is kept: pending link **24h**, **14-day** `temp:req`
   cooldown, per-app roles (`pole-fe`→`fe-user`,
   `pole-analyst`→`analyst-user`), purge + disable on expiry, token `exp` 2h.
7. First step ships **hidden-password + Direct Access Grant** to fetch the
   Keycloak session after `verify-code`. The proper
   **token-exchange impersonation via `pole-api-admin`** (removing the hidden
   password) is deferred to ticket 025 (FUTURE, not scheduled now).

## Context

Phases 1–8 proved the temp-access model (cooldown, 2h window, purge) but the
delivery mechanism — Keycloak's built-in verify-email action link — couples
temp onboarding to Keycloak SMTP, the `temporary` flag password-setup UX, and
the `email_verified` gate. Users hit password-setup friction; ops owns two
email paths (Keycloak realm SMTP + Brevo). Phase 9 moves delivery fully into
`pole_api`: one sender (Brevo), one UX (link → validate → code), Keycloak
reduced to identity store + session issuer.

The login theme keeps only its self-service trigger (email capture → `POST
/api/auth/temporary-access`); the response is now a Brevo-sent direct link
instead of a Keycloak action email.

## Per-app host map (link target + token binding)

| `clientId` | Host | Link shape |
| :--- | :--- | :--- |
| `pole-fe` | `https://demo-ml-agent.duckdns.org` | `https://demo-ml-agent.duckdns.org/?temp_token=xxx` |
| `pole-analyst` | `https://demo-ai-agent.duckdns.org` | `https://demo-ai-agent.duckdns.org/?temp_token=xxx` |

The `temp_token` is **bound to exactly one host/app** at issue time
(`temp:token:{hash}` stores `{email, app}`). Presenting it on the other app's
`/activate` page is rejected (403 `TEMP_TOKEN_APP_MISMATCH`).

## Endpoints

All under the existing public router
`app/pole_api/src/auth/controllers/temporary_access.py` (no `require_*` guard):

| Endpoint | Body | Success | Errors |
| :--- | :--- | :--- | :--- |
| `POST /api/auth/temporary-access` (existing, behavior changed) | `{email, clientId}` | `202 {message}` + Brevo link email; sets `temp:req` (14d) + `temp:token` (24h pending) | `409` cooldown; `422` invalid email/clientId |
| `POST /api/auth/temporary-access/send-code` (new) | `{temp_token}` | `200 {message}` + Brevo code email; sets `temp:code` (10min) | `404/410` unknown/expired token; `403` app mismatch; `429` resend cooldown (60s) |
| `POST /api/auth/temporary-access/verify-code` (new) | `{temp_token, code}` | `200 {access_token, token_type, expires_in}` + starts/confirms `temp:active` 2h window; sets `emailVerified=true` via Admin API | `404/410` unknown/expired token or code; `403` app mismatch; `429` attempt cap (5) |

`POST .../activate` (`{token}`) from Phase 2 is **superseded** by
`send-code`/`verify-code` and is removed or kept as a deprecated shim only if
the Developer finds live callers (decision at implementation time, documented
in the ticket close-out).

## Redis keys

| Key | Value | TTL | Purpose |
| :--- | :--- | :--- | :--- |
| `temp:req:{email}:{app}` | `1` | 14 days | Cooldown marker (unchanged, Phase 8 semantics) |
| `temp:token:{hash}` | `{email, app, state: pending}` | 24h | Pending direct-link token until first successful `verify-code` |
| `temp:code:{token_hash}` | `{code_hash, attempts, email, app}` | 10 minutes | Hashed 6-digit OTP + attempt counter for one send |
| `temp:code-resend:{email}:{app}` | `1` | 60 seconds | Resend-cooldown marker |
| `temp:active:{email}:{app}` | `{app, ts_start, ts_end}` | 2 hours (from FIRST success only) | Activated window — expiry signal; re-entry never extends `ts_end` |
| `temp:active-index` | SET of `"{email}:{app}"` | — | Fast-path sweep discovery (Phase 8 semantics kept) |

Rules: OTP stored **hashed only** (SHA-256 + pepper, never plaintext); attempt
counter increments on every wrong code and caps at 5 → further tries 429 until
a fresh `send-code`; resend sets a new code + resets attempts but does NOT
touch `temp:active`; first `verify-code` success sets `temp:active` with
`ts_end = ts_start + 2h`; later successes (re-entry) only confirm, never move
`ts_end`.

## Flow (happy path)

1. Anonymous user → login theme **Get temporary access** → submits email →
   `POST /api/auth/temporary-access {email, clientId}` → 202.
2. `pole_api` creates/finds the Keycloak user (**no temporary flag**, hidden
   random password, `emailVerified=false`, per-app role), stores
   `temp:req` + `temp:token` (24h), and emails via Brevo the per-app link
   `https://<host>/?temp_token=xxx` (EN/ES by locale).
3. User opens the link → app routes to `/activate?temp_token=xxx` → presses
   **Validate** → `POST .../send-code {temp_token}` → 200 + Brevo 6-digit code
   email.
4. User enters the code → `POST .../verify-code {temp_token, code}` → 200 with
   the Keycloak session (Direct Access Grant with the hidden password);
   `pole_api` sets `emailVerified=true` via Admin API and starts `temp:active`
   (2h).
5. In-app navigation with the live session never re-asks. Re-entry via the link
   inside the window asks a fresh code (new `send-code`/`verify-code` round)
   but the window end is unchanged.

## Tasks

### Ticket 021 — Passwordless creation + link email (BE root) — ✅ DONE

- [x] [Application] Remove `temporary: True` from temp-user creation; generate
  a hidden random password stored server-side only (never emailed/shown);
  keep `emailVerified=false` at creation, per-app role assignment, and the
  14d `temp:req` + 24h `temp:token` writes.
- [x] [Application] Replace `execute-actions-email` with a Brevo-sent per-app
  direct link (`https://<host>/?temp_token=xxx`, EN+ES templates, sender
  `no-reply@fpalero.cc`); Keycloak sends nothing on this path.
- [x] [Application] Bind the token to one host/app; failure rollback via
  `repo.clear` (no orphaned `temp:*` keys or half-created users on Brevo
  failure). Full details and the implementation record (incl. the
  deprecated-`activate` decision and the `repo.clear` token-leak fix) in
  `phase-9-passwordless-link-code/PAIML-KEYCLOAK-021.md`.

> **Note.** The host map is `FE_BASE_URL` / `ANALYST_BASE_URL` in
> `core/config.py` (defaults: `https://demo-ml-agent.duckdns.org` for
> `pole-fe`, `https://demo-ai-agent.duckdns.org` for `pole-analyst`), and
> `POST .../activate` is kept as a **deprecated** shim. **022 confirmed it stays**
> a deprecated shim (not removed this phase); removal is deferred until the
> Phase 2 FE flow is confirmed migrated.

### Ticket 022 — OTP send/verify + hidden-password grant + 2h window (BE) — ✅ DONE

- [x] [Application] `send-code`: validate pending token + app binding, hash and
  store the 6-digit OTP (10min TTL), enforce the 60s resend cooldown, Brevo-send
  the code (EN+ES).
- [x] [Application] `verify-code`: check code hash, cap attempts at 5, fetch
  the Keycloak session via hidden-password Direct Access Grant, set
  `emailVerified=true` via Admin API, start `temp:active` 2h on FIRST success
  only (re-entry never extends `ts_end`).
- [x] [Tests] OTP hash/attempt/resend/window matrix. Full details in
  `phase-9-passwordless-link-code/PAIML-KEYCLOAK-022.md`.

> **Implementation record (022).** Merged in `pole-ai-ml` via
> [`PR #356`](https://github.com/fpalero/pole-ai-ml/pull/356) (merge commit
> `814596f`, 2026-09-26). Four deltas from the plan above, all recorded in the
> ticket close-out:
>
> 1. **The hidden password is never stored.** 021 generated it inline in the
>    Keycloak create POST and discarded it, so there was nothing to grant with.
>    `verify-code` now **rotates** the nobody-held password and logs in with it
>    **inside a single call** — nothing is persisted (stronger than the plan;
>    025 removes the mechanism entirely).
> 2. **`temp:active` holds `{app, ts_start, ts_end}` (as documented) and is
>    written with SETNX** — this is the re-entry window-extension fix.
>    `get_active_token` keeps its existence-probe contract; `get_window` is the
>    new typed read.
> 3. **App binding is derived from the request `Origin` header** (the OTP bodies
>    carry no `clientId`). A missing/unrecognised `Origin` is **not** a
>    mismatch, so local verification still works — which means the `403` is a
>    **guardrail/UX boundary, not a security boundary**. The real second factor
>    is the inbox OTP plus the non-extendable 2h window (ADR Decision 3).
> 4. **TOCTOU between the app-binding read and the OTP write is knowingly left**
>    (fail-closed); a Redis Lua script was rejected because `fakeredis` cannot
>    execute it in tests. Accepted risk.
>
> Two review-round blocking fixes shipped with it: `emailVerified` is now set
> **before** the session is minted (it was after, so the JWT carried
> `email_verified:false` and opted out of the 2h enforcement), and the attempt
> cap moved from a non-atomic read-modify-write to **`HINCRBY`**.
> `POST .../activate` remains a **deprecated shim** (021+022 decision).
>
> 🔴 **Rollout blockers (infra repo `pole-ai-ml-infra`, not code):**
> `TEMP_ACCESS_OTP_PEPPER` must be provisioned per environment or both OTP
> endpoints answer 503; **Direct Access Grants must be enabled on the `pole-fe`
> and `pole-analyst` clients**; and the 021 carry-overs `FE_BASE_URL` /
> `ANALYST_BASE_URL` / `BREVO_API_KEY` must be set per environment.

### Ticket 023 — Activation pages x2 (FE)

- [ ] [FE] Per-app `/activate?temp_token=xxx` pages (`pole_fe`,
  `pole_analyst`): Validate button, code input, expired/invalid states,
  per-app branding; deep-link `/?temp_token=xxx` → `/activate` routing. Full
  details in `phase-9-passwordless-link-code/PAIML-KEYCLOAK-023.md`.

### Ticket 024 — Mailpit E2E + hardening (QA)

- [ ] [QA] End-to-end against Mailpit: request → link email → validate → code
  email → navigate → re-entry (fresh code, same window end) → expiry/purge;
  rate-limit (60s resend) and attempt-cap (5) tests. Full details in
  `phase-9-passwordless-link-code/PAIML-KEYCLOAK-024.md`.

### Ticket 025 — Token-exchange impersonation (FUTURE, not scheduled)

- [ ] [Future] Replace the hidden-password grant with proper token exchange via
  the `pole-api-admin` service account; remove the stored password; realm
  config changes (infra repo). Marked FUTURE, no implementation now. Full
  details in `phase-9-passwordless-link-code/PAIML-KEYCLOAK-025.md`.

## Dependencies

- Phases 1–8 enforcement kept: Phase 8 email/owner-scoped identity, `SCAN`
  enumeration, purge + disable (tickets 018/019/020) apply to the new keys
  unchanged.
- Phase 5 Brevo SMTP (sender, credentials, templates) — reused for both new
  emails; realm SMTP is no longer on this path.
- Ticket order: 021 blocks 022; 022 blocks 023/024/025; 023 blocks 024
  (024 needs the pages); 025 is FUTURE (blocked by 022, never scheduled now).
- Keycloak `pole-api-admin` service account (for `emailVerified` update +
  Direct Access Grant lookup) and in-cluster Redis; `settings` additions for
  host map, OTP TTL/attempts, resend cooldown, Brevo templates.

## Acceptance Criteria

- [ ] Temp users are created without `temporary: True` and without any
  password ever emailed/shown; permanent-user password login is untouched.
- [ ] Keycloak sends zero emails on the temp path; both emails arrive from
  `no-reply@fpalero.cc` via Brevo in EN+ES.
- [ ] Link is per-app and token-bound: cross-app presentation is rejected.
- [ ] OTP: 6 digits, 10min TTL, max 5 attempts (then 429), 60s resend cooldown;
  codes stored hashed only.
- [ ] `verify-code` success returns a usable session, sets `emailVerified=true`,
  and starts a 2h `temp:active` window; re-entry asks a fresh code but never
  moves the window end (10:00→12:00 example holds).
- [ ] Live-session in-app navigation never re-asks for a code.
- [ ] Pending link 24h, 14d cooldown, per-app roles, purge + disable on expiry,
  token `exp` 2h — all preserved; `pixi run test` stays ≥80% coverage.
- [ ] Ticket 025 stays FUTURE (no hidden-password removal in this phase).

## Risks and Mitigations

- **Risk:** Hidden password stored server-side leaks or is mishandled.
  **Mitigation:** random per-user secret, never logged/emailed/returned; scoped
  to the temp flow only; removed entirely by ticket 025 (token exchange).
- **Risk:** Forwardable bearer link (`?temp_token=xxx` can be shared).
  **Mitigation (accepted trade-off):** the link alone grants nothing — a fresh
  inbox-bound 6-digit OTP (10min, 5 attempts, 60s resend) is always required;
  token is single-app-bound and pending only 24h; see ADR below.
- **Risk:** Brevo outage blocks both emails. **Mitigation:** failure rollback
  via `repo.clear` (no half-state); 429/5xx surfaced distinctly so the FE can
  show retry states; existing Brevo Phase 5 alerting reused.
- **Risk:** Window-extension bug on re-entry. **Mitigation:** `ts_end` written
  once (SETNX semantics); regression test pins the 10:00→12:00 case.
- **Risk:** OTP brute force. **Mitigation:** hash storage, 5-attempt cap,
  10min TTL, per-email rate limits; Mailpit E2E covers the caps.

## ADR — Why this shape (decision record)

**Context.** The Phase 1–8 magic link reuses Keycloak's verify-email action:
temp onboarding inherits the `temporary`-flag password-setup UX and a second
email path (realm SMTP). Goal: kill the password-setup friction, unify sending
on Brevo, and keep the 2h-window/cooldown/purge guarantees.

**Decision 1 — pole_api sends both emails; Keycloak sends nothing.**
`execute-actions-email` is dropped. Rationale: one sender, one template set
(EN+ES), no realm-SMTP coupling on the temp path; `emailVerified` is set by
`pole_api` via Admin API after the inbox proof (OTP success) instead of by a
Keycloak action. Consequence: realm SMTP stays for non-temp flows only.

**Decision 2 — hidden-password + Direct Access Grant first, token-exchange
later (ticket 025).** After `verify-code`, the user needs a real Keycloak
session without ever knowing a password. Options: (a) hidden random password +
Direct Access Grant now; (b) proper token exchange impersonating the user via
`pole-api-admin` now. Chosen: (a) first — it needs no realm/config change and
unblocks the UX; (b) is the correct end state (no stored secret) but requires
exchange permissions + client policy work, so it ships as FUTURE ticket 025.
The hidden secret is per-user random, server-side only, never exposed.

**Decision 3 — bearer-link + inbox-code trade-off; forwardable-link risk
accepted with mitigations.** The `?temp_token=xxx` URL is forwardable by
construction (like any magic link). Accepted because the link alone is
insufficient: every entry requires a fresh 6-digit inbox code (10min TTL, 5
attempts, 60s resend), the token is bound to one app/host, pending only 24h,
and the 2h window never extends. An attacker holding only the link still faces
the victim's inbox.

**Alternatives considered.** Keep `temporary: True` + Keycloak email (rejected:
keeps password-setup friction and dual email paths). OTP-only without link
(rejected: no per-app deep-link entry from the login theme). Long-lived link
without OTP (rejected: forwardable bearer with no second factor).
