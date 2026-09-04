# Implementation Plan — `keycloak` (Temporary Magic-Link Access)

> **Status:** Phase 1–6 ✅ DONE (PAIML-KEYCLOAK-001..014 implemented, merged into `develop`,
> QA-verified on the local cluster). Phase 6 awaits USER manual testing + manual
> develop→main promotion — NOT closed until the user confirms.

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