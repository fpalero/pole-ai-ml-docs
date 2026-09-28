# Implementation Plan — `keycloak` (Temporary Magic-Link Access)

> **Status:** Phase 1–7 ✅ DONE (PAIML-KEYCLOAK-001..017 implemented, merged into `develop`,
> QA-verified on the local cluster). Phase 6 awaits USER manual testing + manual
> develop→main promotion — NOT closed until the user confirms. Phase 8 🟡 PARTIAL
> (code+docs merged, staging QA gate BLOCKED on rollout). Phase 9 🟡 PARTIAL — 021 ✅ DONE + 022 ✅ DONE
> + 023 ✅ DONE; **024 QA gate 🔴 RED (2026-09-26)** — blocked on the Phase 11 fixes 030+031; 025 FUTURE
> (PAIML-KEYCLOAK-021..025 passwordless direct-link + activation-code flow).
> **Phase 10 📋 PLANNED** (PAIML-KEYCLOAK-026..029) — the **DEPLOY prerequisite** for Phase 9, in the
> **infra** repo `pole-ai-ml-infra`: the deployed environments are still unprovisioned, so the Phase 9
> OTP flow is **unreachable outside local** and no deployed-environment claim is valid yet.
> **Phase 11 📋 PLANNED** (PAIML-KEYCLOAK-030..031) — the **QA-gate fixes** for the two P1 defects
> that made the 024 gate RED: the `verify-code` Direct Access Grant (**030**, BLOCKER — realm-required
> `firstName`/`lastName` missing at creation) and the lapse purge destroying the 14-day `temp:req`
> cooldown (**031**). Both block the **024 re-run**.
> **Phase 12 🟡 PARTIAL** (PAIML-KEYCLOAK-032..035) — **auto-send hardening + the
> temp-access product decisions** for the two-step OTP flow, **not** a build phase. The
> `send-code` / `verify-code` endpoints, the 10-min code TTL, single-use consumption,
> prior-code invalidation, the 5-attempt cap, the 60s resend cooldown, Brevo delivery and
> the per-app `/activate` pages (`pole_fe` + `pole_analyst`, shared `activation-core.ts`
> shipped byte-identically) **all already exist** from Phase 9
> (PAIML-KEYCLOAK-021..023; `pole_fe` at 371 tests passing). Phase 12 adds only what is
> missing: **automatic send on page load** (032 BE + 033 FE), the **"a verification code
> has been sent"** notice replacing the "Validate your access link" gate, the
> **idempotent 60s cooldown** (`200 {already_sent: true}` instead of 429 when a live code
> is armed, so a page refresh is not punished), the **cooldown-expiry message** on the
> activation flow (034 FE ×2), and a **durable `temp_access_audit` ledger** (035 BE).
> The original 032–035 draft described shipped work as new work; its 034/035 (Analyst
> verification UI, phase-wide QA gate) were **deleted, not renumbered**, and 032/033 were
> rewritten (2026-09-28) — the numbers were then **re-issued the same day** for the Q2/Q3
> work above, hence the `keycloak` counter ending at **35**.
>
> **Progress:** ✅ **PAIML-KEYCLOAK-035** (durable `temp_access_audit` ledger) **SHIPPED**
> — `pole-ai-ml` PR [#363](https://github.com/fpalero/pole-ai-ml/pull/363), merged into
> `develop`. 📋 032 / 033 / 034 remain planned. The `temp_access_audit` collection is
> written at link-issue, window-start and token consumption, is **never** deleted by the
> purge, and is **additive only** — the 14-day `temp:req` Redis marker remains the
> cooldown's sole arbiter. **Retention is still deferred** and is required before
> production.
>
> **Q1 (link re-use) required no code change.** Per
> [ADR-007](../decisions/ADR-007-temp-access-link-reuse-and-audit-retention.md)
> (user-confirmed 2026-09-27): the magic link **may** be re-used, but **only while the
> 2h window is live**; once the 2h lapses the link is dead and the user must wait out the
> 14-day cooldown and request a brand-new one. That **is** the shipped behaviour
> (`temp:token` TTL 24h, `start_window` pins `ts_end = ts_start + 2h` and never extends,
> request-time `_enforce_temp_access_window` rejects after lapse and lazily purges) — it is
> recorded **as a decision record only**, so a future reader does not "fix" it.

---

## 1. Feature Context & Objective

- **Goal:** Allow anonymous users to get **temporary access** to `pole_fe` / `pole_analyst`. Landing on either app redirects to Keycloak, whose login page offers **Login** or **Get temporary access**. Temp access asks only for an email; Keycloak emails a magic link (its built-in verify-email action link) that logs the user in. Access is capped at **2 hours**; the **same email cannot re-request for 2 weeks**; on expiry the temp user is disabled and **all data they created is deleted** (temp users must not leave shared data that could corrupt the app).
- **Non-Functional Constraints:**
  - Auth via Keycloak realm `pole-ai` (roles `fe-user` / `analyst-user`), validated by `pole_api` (`core/auth.py`).
  - Magic-link email sent by **Keycloak** via realm SMTP.
  - **Redis** is the source of truth for the 2-week cooldown and the 2-hour activated window.
  - Access token `exp` = 2h (defense in depth); temp user disabled after the window.
  - Per-app role assignment: `pole-fe` → `fe-user`, `pole-analyst` → `analyst-user`.
  - ≥80% test coverage; `pixi run test`.
- **Affected Components:**
  - `infrastracture/keycloak/realm-pole-ai.json` + `helm/pole-ai/charts/keycloak/templates/configmap.yaml` — realm SMTP, `pole-api-admin` client, `loginTheme`.
  - `infrastracture/keycloak/themes/pole-ai-login/` — custom login theme (new).
  - `helm/pole-ai/charts/keycloak/templates/deployment.yaml` — mount theme volume.
  - `helm/pole-ai/charts/pole-api/templates/configmap.yaml` + `secret.yaml` — new env.
  - `app/pole_api/src/core/temp_access.py` — Keycloak admin client + Redis repo + purge service (new).
  - `app/pole_api/src/auth/controllers/temporary_access.py` — public endpoints (new).
  - `app/pole_api/src/core/auth.py` — lazy activation hook.
  - `app/pole_api/src/core/config.py` — temp-access settings.
  - `app/pole_api/src/main.py` — router wiring.
  - Existing deletion services reused for the purge: `video/services/video_deletion_service.py`, analysis cascade deletes.
- **Assumptions:**
  - A dedicated confidential `pole-api-admin` client (service account) is used instead of storing the `fernando` admin password in pole_api.
  - The 2h token/session cap applies to `pole-fe`/`pole-analyst` clients (also caps existing `dev`/`fernando` sessions to 2h — accepted).
  - SMTP credentials are supplied via Helm values/Secrets (not hardcoded).
  - `pole_fe`/`pole_analyst` need **no** FE code change (redirect flow + login theme handle temp access).

## 2. Architectural Layering (The "Where")

- **Domain:** Temporary-access model — email cooldown (14d), magic-link token (pending→active), 2h activated window, per-app role mapping, owned-resource purge.
- **Application:** `TempAccessService` (request/activate/enforce), `TempAccessPurgeService` (expiry purge), `KeycloakAdminClient` (create/disable user, send verify email), `TempAccessRepository` (Redis).
- **Infrastructure:** Keycloak realm (SMTP, `pole-api-admin` client, custom theme, 2h lifespan), Redis (cooldown/activation), MongoDB + PVC + Chroma (owned data to purge).
- **Presentation:** Custom Keycloak login theme panel; `POST /api/auth/temporary-access`, `POST /api/auth/temporary-access/activate` (public); lazy activation inside `core/auth.py`.

## 3. Implementation Roadmap (Atomic Steps)

| Fase | Nombre | Estado | Detalle |
| :--- | :--- | :--- | :--- |
| 1 | Keycloak Realm, SMTP & Custom Login Theme | ✅ DONE | [PLAN_PHASE_1.md](plan/PLAN_PHASE_1.md) |
| 2 | pole_api Temporary-Access Orchestration | ✅ DONE | [PLAN_PHASE_2.md](plan/PLAN_PHASE_2.md) |
| 3 | Temp-User Data Isolation & Expiry Purge | ✅ DONE | [PLAN_PHASE_3.md](plan/PLAN_PHASE_3.md) |
| 4 | Tests, Docs & Verification | ✅ DONE | [PLAN_PHASE_4.md](plan/PLAN_PHASE_4.md) |
| 5 | Brevo SMTP | ✅ DONE | [PLAN_PHASE_5.md](plan/PLAN_PHASE_5.md) |
| 6 | Stitch pixel-perfect login restyle | ✅ DONE (impl + QA GREEN; awaiting user manual develop→main promotion) | [PLAN_PHASE_6.md](plan/PLAN_PHASE_6.md) |
| 7 | Magic-link fix (stale theme, endpoint, SMTP verify) | ✅ DONE | [phase-7-magic-link-fix](phase-7-magic-link-fix/) (015, 016, 017 emergency probe fix) |
| 8 | Temp-access expiry hardening (azp-mismatch + blind-sweeper fix) | 🟡 PARTIAL — code+docs merged (pole-ai-ml#220 pole-ai-ml-docs#9), staging QA gate BLOCKED on rollout | [PLAN_PHASE_8.md](plan/PLAN_PHASE_8.md) |
| 9 | Passwordless direct-link + activation-code flow (Brevo link + 6-digit OTP, hidden-password grant first, token-exchange FUTURE) | 🟡 PARTIAL — **021 ✅ DONE** (passwordless creation + Brevo link) + **022 ✅ DONE** (OTP send/verify, hidden-password grant, `emailVerified`, fixed non-extendable 2h window) + **023 ✅ DONE** (per-app `/activate` pages x2, Validate + code states, deep-link routing); **024 QA gate 🔴 RED** (2026-09-26 — blocked on 030+031), 025 FUTURE | [PLAN_PHASE_9.md](plan/PLAN_PHASE_9.md) |
| 10 | OTP deploy prerequisites (infra: pepper Secret, Direct Access Grants, host map, Brevo key) | 📋 PLANNED — 026–029 authored in the docs repo; **no infra code yet**. Owns the DEPLOY prerequisite for Phase 9, which is currently provisioned **only in the local stack** | [PLAN_PHASE_10.md](plan/PLAN_PHASE_10.md) |
| 11 | Phase 9 QA-gate fixes (verify-code grant + purge semantics) | 📋 PLANNED — **030** (BLOCKER: `verify-code` Direct Access Grant, realm-required `firstName`/`lastName`; reused disabled accounts) + **031** (lapse purge destroys the 14-day `temp:req` cooldown, may not clear `temp:code:*`); both **block the 024 re-run** | [PLAN_PHASE_11.md](plan/PLAN_PHASE_11.md) |
| 12 | Two-Step Temporary Access — auto-send hardening, cooldown UX & audit retention (auto-send on page load, "code sent" notice, idempotent 60s cooldown, 14-day cooldown message, durable audit ledger) | 📋 PLANNED — **032** (BE: `send-code` idempotent inside the resend cooldown → `200 {already_sent: true}` when a live code is armed; 429 preserved) + **033** (FE `pole_fe` **and** `pole_analyst`: auto-send on load, drop the "Validate" gate, "code sent" notice, consume `already_sent`) + **034** (FE `pole_fe` **and** `pole_analyst`: explain the 14-day cooldown in EN/ES on `/activate`; **presentation only, no backend change**) + **035** (BE: durable MongoDB `temp_access_audit` ledger — `email`, `link_issued_at`, `window_started_at`, `use_count`, `consumed_tokens` — written at link-issue/window-start, never deleted by the purge, **additive only** so the `temp:req` cooldown stays the source of truth). **Q1 (link re-use bounded by the 2h window) required NO code change** — recorded in [ADR-007](../decisions/ADR-007-temp-access-link-reuse-and-audit-retention.md) as a decision record only. **Hardening only** — the BE endpoints, 10-min TTL, single-use, prior-code invalidation, 5-attempt cap and the `/activate` pages **already exist** from Phase 9 (PAIML-KEYCLOAK-021..023); see the scope-correction note in PLAN_PHASE_12.md | [PLAN_PHASE_12.md](plan/PLAN_PHASE_12.md) |

> **Phase 9 ⇄ Phase 10 (read this before claiming Phase 9 works).** Phase 9's code
> is done and is being exercised by the `PAIML-KEYCLOAK-024` QA gate **locally**.
> The values that flow needs in a **deployed** environment —
> `TEMP_ACCESS_OTP_PEPPER` (Secret), `FE_BASE_URL` / `ANALYST_BASE_URL`
> (ConfigMap), `BREVO_API_KEY` (Secret) — are wired in **no** environment today,
> so `send-code` / `verify-code` and the request endpoint answer **503** in
> dev/staging/prod. Phase 10 owns closing that; **ticket 029** owns proving it.
> A green local `024` run is evidence about the **code**, not about any
> deployment. Verified 2026-09-26 against the live local cluster + both realm
> sources — see [PLAN_PHASE_10.md](plan/PLAN_PHASE_10.md#verified-starting-state-read-2026-09-26-local-cluster-k3s-local).

## 4. Quality Gates & Testing Commands (DoD)

- **Unit Tests:** `pixi run test` (≥80% coverage)
- **Integration Tests:** end-to-end temp-access against Keycloak + Mailpit + Mongo test DBs (`pole_api_test`, `skeleton_data_test`)
- **Automation:** `helm lint` + `helm upgrade --dry-run` for infra changes; existing CI checks
- **Database Target:** `pole_api_test` and `skeleton_data_test`
- **Coverage Requirement:** ≥80%
- **Additional Checks:** lint/typecheck for `pole_api` (`ruff`); `helm lint` for charts; `shellcheck`/`bash -n` on scripts

## 5. Defined Use Cases (Gherkin + Technical Matrix)

### UC-01: Request temporary access (happy path)
- **Given** an anonymous user lands on pole_fe and is redirected to the Keycloak login page
- **When** the user submits `POST /api/auth/temporary-access` with payload `{"email": "guest@example.com", "clientId": "pole-fe"}`
- **Then** the system returns HTTP `202` and Keycloak emails a verify-email magic link
- **And** Redis `temp:req:guest@example.com` is set with a 14-day TTL

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/auth/temporary-access` |
| Request Method | POST |
| Required Headers | `Content-Type: application/json` |
| Payload Example | `{"email": "guest@example.com", "clientId": "pole-fe"}` |
| DB State (Before) | no `temp:req` key for the email |
| DB State (After) | `temp:req:guest@example.com` TTL=14d; Keycloak user created with `VERIFY_EMAIL`, role `fe-user` |

### UC-02: Cooldown blocks a re-request within 2 weeks
- **Given** a temp user requested access less than 14 days ago (`temp:req:{email}` present)
- **When** the user submits `POST /api/auth/temporary-access` with the same email
- **Then** the system returns HTTP `409` with a "try again in X" message
- **And** no new token/email is issued

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/auth/temporary-access` |
| Request Method | POST |
| Required Headers | `Content-Type: application/json` |
| Payload Example | `{"email": "guest@example.com", "clientId": "pole-fe"}` |
| DB State (Before) | `temp:req:guest@example.com` exists |
| DB State (After) | unchanged (no new token issued) |

### UC-03: Activate the window via the magic link
- **Given** a pending token `temp:token:{hash}` exists for the user's email
- **When** the user clicks the email link (Keycloak verifies email and logs in), then `POST /api/auth/temporary-access/activate` with payload `{"token": "<token>"}` fires
- **Then** the system returns HTTP `200` and Redis `temp:active:{email}` is set with a 2-hour TTL
- **And** the first authenticated API request carries the app-mapped role and a 2h `exp`

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/auth/temporary-access/activate` |
| Request Method | POST |
| Required Headers | `Content-Type: application/json` |
| Payload Example | `{"token": "<jwt-or-token>"}` |
| DB State (Before) | `temp:token:{hash}` state=pending |
| DB State (After) | `temp:active:{email}` TTL=2h |

### UC-04: Expiry purges all owned data and disables the user
- **Given** the 2-hour `temp:active:{email}` window has expired
- **When** the sweeper (or a lazy check on the next request) runs the purge for that `owner_id`
- **Then** all Mongo docs, PVC files, Chroma embeddings, and Redis sessions owned by the user are deleted, the Keycloak user is disabled, and Redis `temp:*` keys for the email are cleared
- **And** the 14-day `temp:req` cooldown remains so the email can re-request after it lapses

| Technical Check | Expected Value |
| :--- | :--- |
| Trigger | sweeper / lazy expiry |
| DB State (Before) | owned resources present for `owner_id` |
| DB State (After) | owned resources removed; `temp:active` cleared; user disabled |

### UC-05: Invalid email rejected
- **Given** a malformed email address
- **When** the user submits `POST /api/auth/temporary-access` with `{"email": "not-an-email", "clientId": "pole-fe"}`
- **Then** the system returns HTTP `422` (validation error)
- **And** no Redis key, Keycloak user, or email is created

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `/api/auth/temporary-access` |
| Request Method | POST |
| Required Headers | `Content-Type: application/json` |
| Payload Example | `{"email": "not-an-email", "clientId": "pole-fe"}` |
| DB State (Before) | no temp state |
| DB State (After) | unchanged (no Redis/Keycloak writes) |

## 6. Risks and Mitigations

- **Risk:** Custom Keycloak login theme is complex to package/mount. **Mitigation:** theme extends the `keycloak` base theme; mount via ConfigMap volume; validate with `helm lint`/dry-run and a Mailpit-backed e2e.
- **Risk:** Keycloak verify-email requires SMTP; misconfig blocks delivery. **Mitigation:** realm `smtpServer` from values + Mailpit sandbox in dev; document the `from`/auth contract.
- **Risk:** A temp user could be auto-disabled mid-session if the sweeper races the 2h window. **Mitigation:** idempotent purge; window TTL and token `exp` aligned; sweeper interval < window.
- **Risk:** Deleting shared resources (option 2) could remove data another (non-temp) user relies on. **Mitigation:** scope deletion to resources the temp user actually created (by `owner_id`); document the trade-off; reuse existing cascade-deletion services.
- **Risk:** Admin client secret exposure. **Mitigation:** store in a Helm Secret, not the realm JSON; service account scoped to `manage-users`/`view-users` only.

## 7. Open Questions and Decisions

- **Decision:** Project stored under `docs/app/keycloak/`.
- **Decision:** Custom Keycloak login theme for the two-option entry (Login / Get temporary access).
- **Decision:** Magic link = Keycloak's built-in verify-email action link (reuse, minimal custom code).
- **Decision:** Per-app role mapping (`pole-fe`→`fe-user`, `pole-analyst`→`analyst-user`).
- **Decision:** Keycloak sends the email via realm SMTP (reuse existing SMTP creds).
- **Decision:** On expiry, disable the user and keep the account for audit; 14-day Redis cooldown.
- **Decision:** Data purge is **option 2** — delete all resources the temp user created, including shared/global ones.
- **Decision:** Dedicated confidential `pole-api-admin` client (service account) instead of the `fernando` admin password.
- **Open:** Actual SMTP host/port/creds/from — supply via Helm values/Secret at deploy time.
- **Open:** 2h token/session cap on `pole-fe`/`pole-analyst` also caps existing `dev`/`fernando` sessions to 2h — confirm acceptable.
- **Decision (Phase 10):** `TEMP_ACCESS_OTP_PEPPER` and `BREVO_API_KEY` are **Helm Secrets** (injected per environment from the Actions secret store, placeholder-only in `values.yaml`); `FE_BASE_URL` / `ANALYST_BASE_URL` are **ConfigMap** values. The pepper must never be hardcoded or shared across environments — a committed pepper is a broken pepper, and the fail-closed 503 is deliberate.
- **Decision (Phase 10):** the **deployed environment is unproven** until the Phase 10 prerequisites are observed live in dev/staging/prod. The Phase 9 QA gate runs locally and proves the code path only; ticket 029 is the artifact that changes that.
- **Decision (Phase 10):** Direct Access Grants stay enabled on `pole-fe` / `pole-analyst` until ticket 025 replaces the hidden-password grant with token exchange — at which point the grant can be turned back off.
- **Open (infra, `pole-ai-ml-infra`):** the four provisioning gaps are ticketed as 026–029; the code-side infra PRs are scheduled by the team lead, **never** a `develop` → `main` PR.
- **Decision (Phase 12):** Phase 12 is **UX hardening of an already-shipped flow**, re-scoped on 2026-09-28 after reading the code. What exists (from PAIML-KEYCLOAK-021..023): the `send-code` / `verify-code` endpoints, the 10-min code TTL (`TEMP_ACCESS_OTP_TTL_S`), single-use consumption, prior-code invalidation, the 5-attempt cap, the 60s resend cooldown, Brevo delivery, and the `/activate` pages with the byte-identical `activation-core.ts` in **both** `pole_fe` and `pole_analyst`. What Phase 12 adds:
  - **Decision (B1) — auto-send, no gate:** the code is emailed **automatically** when the verification page loads with a valid `temp_token`. The "Validate your access link" pre-step is **removed**, not re-worded — there is nothing left to validate — and the landing copy becomes "A verification code has been sent to your email. It should arrive in a few seconds." (EN + ES).
  - **Decision (B2) — idempotent cooldown (user-confirmed):** auto-send turns every page refresh into a `send-code` call, and most land inside the 60s cooldown. Answering 429 there would show the user "please wait before requesting another code" while a **valid code is already in their inbox** — wrong on its own terms, since a 429 says "no code is out there". Therefore a `send-code` inside the cooldown **with a live armed code** returns **200 `{already_sent: true}`** plus the code's **remaining** `expires_in`; the frontend renders the code step without re-sending. The **429 rate-limit path is preserved** for explicit "Resend code" clicks and for the case where there is **no** live code to fall back on.
  - **Constraint:** the stored value stays a peppered SHA-256 digest; the fallback reports only the record's remaining TTL (a 6-digit code is a 10^6 space — a recoverable digest defeats the whole point of `core.otp`).
  - **Constraint:** `activation-core.ts` / `activation-flow.ts` and their specs are hand-duplicated into both apps and compared byte-for-byte by `activation-parity.spec.ts`; any FE edit must land in both apps in the same change.
  - **Decision (B3) — link re-use is bounded by the 2h window (user-confirmed 2026-09-27, ADR-007 Q1; NO code change).** The magic link **may** be re-used, but **only while the 2h window is live**; once the 2h lapses the link is dead and the user must wait out the 14-day cooldown and request a **brand-new** one. This **is** the shipped behaviour (`temp:token` TTL 24h, `start_window` pins `ts_end = ts_start + 2h` and never extends, request-time `_enforce_temp_access_window` rejects after lapse and lazily purges). It is recorded **as a decision record only** so a future reader or agent does not "fix" it into a sliding window or a single-use token. A sliding window was explicitly considered and **rejected** — it turns a forwarded link into indefinite access.
  - **Decision (B4) — the 14-day cooldown stays hard; the *message* is the deliverable (user-confirmed 2026-09-27, ADR-007 Q2).** The user waits the cooldown out, but the application **must** show an explanatory message (EN + ES) rather than a bare hours number: today the cooldown surfaces only as `409 {"detail":"Email in cooldown — try again in 336 hours"}` and the `/activate` page has **no cooldown state at all**. **Ticket 034** (FE ×2) adds a distinct cooldown state and copy, ideally showing the re-request **date** derived from `Retry-After`. This is **presentation only** — the backend already returns `409` + `Retry-After`, so **no backend change is spec'd**. A pre-flight "check my cooldown" GET was considered and **rejected**: on an unauthenticated endpoint it is an account-enumeration oracle.
  - **Decision (B5) — owned data is physically deleted; the audit trail is retained forever (user-confirmed 2026-09-27, ADR-007 Q3). ✅ SHIPPED by PAIML-KEYCLOAK-035** (`pole-ai-ml` PR #363). The purge keeps removing what the user *produced* (videos, DB rows, Chroma vectors) — unchanged, and **no soft-delete of owned data** is in scope. **Ticket 035** (BE) added a durable MongoDB `temp_access_audit` ledger recording the email, `link_issued_at`, `window_started_at`, a `use_count`, and the expired/consumed **token identifiers** (`consumed_tokens`) so a spent or expired token is recognisable and never re-used. The ledger is written at link-issue, window-start and token consumption, is **idempotent on re-entry**, is **never deleted by the purge**, and is strictly **additive**: the 14-day `temp:req` Redis marker stays the cooldown's source of truth, so the ledger is never consulted as the cooldown's arbiter (that would reintroduce the PAIML-KEYCLOAK-031 defect) — pinned by a test that strips the Redis marker and shows the request is accepted again despite the permanent audit row. Token identifiers are stored as a **peppered SHA-256 digest**, following the `core/otp.py` store-a-digest-never-the-plaintext precedent, so a permanent ledger never becomes a permanent credential store. **Retention remains "forever, for now"**: unbounded growth is **accepted** at demo traffic and a retention job is **required before production** (still deferred). One further bound *was* added here: `consumed_tokens` is capped at **100 per document** (FIFO) so an array inside a single row cannot grow without limit — distinct from the deferred collection-level retention.
  - **Ticket numbering:** the original 034 (Analyst verification UI — already delivered by 023 as a byte-identical mirror) and 035 (phase-wide integration/QA gate — owned by the Phase 9 gate 024 with its Phase 11 fixes 030/031) were **deleted, not renumbered**, on 2026-09-28. The numbers were **re-issued the same day** for the Q2 cooldown message (034) and the Q3 audit ledger (035). The `keycloak` counter therefore ends at **35**. Graph: `032 → 033 → 034` and `032 → 035` (acyclic, every `Blocked By` symmetric).
