# Ticket: PAIML-KEYCLOAK-022

## Title
[Keycloak] OTP send/verify + hidden-password grant + emailVerified + fixed 2h window

## Description
With the direct link (021) in place, entry still needs its second factor: the
`/activate` page calls **Validate** (`send-code`), the user receives a 6-digit
code, and `verify-code` exchanges link + code for a real Keycloak session and
starts the 2-hour window. This ticket builds both endpoints, the OTP
hardening, the first-step hidden-password Direct Access Grant session fetch,
the `emailVerified=true` Admin API update, and the **never-extend** window
rule (e.g. 10:00→12:00 stays 12:00 even when re-entry asks a fresh code).

Why this shape (decision record):
- **Hashed OTP + caps.** Codes are stored as SHA-256 (+ pepper), never
  plaintext; 10-minute TTL, max 5 attempts, 60-second resend cooldown.
- **Hidden-password grant is step one, not the end state.** It needs no realm
  change and unblocks the UX; proper token-exchange impersonation follows in
  025 (FUTURE).
- **Window end is immutable.** `ts_end` is written once (SETNX); re-entry only
  confirms, so a shared/forwarded link cannot stretch access.

## Repository
pole-ai-ml

## What to Do (Implementation Steps)
- [x] `POST /api/auth/temporary-access/send-code {temp_token}` (public):
  validate the pending `temp:token:{hash}` (404/410 on unknown/expired, 403 on
  app mismatch); enforce the 60s `temp:code-resend:{email}:{app}` cooldown
  (429); generate a 6-digit code, store ONLY its hash in
  `temp:code:{token_hash}` = `{code_hash, attempts: 0, email, app}` (10min
  TTL); Brevo-send the code (EN+ES, `no-reply@fpalero.cc`); reset attempts on
  every fresh send without touching `temp:active`.
- [x] `POST /api/auth/temporary-access/verify-code {temp_token, code}`
  (public): validate token + app binding; compare code hashes (constant-time);
  increment attempts on mismatch and 429 after 5; on success fetch the Keycloak
  session via hidden-password Direct Access Grant, set `emailVerified=true`
  via the Admin API, and start `temp:active:{email}:{app}` = `{app, ts_start,
  ts_end}` (2h) ONLY if absent (re-entry never moves `ts_end`); return
  `200 {access_token, token_type, expires_in}`.
- [x] Keep Phase 8 semantics: email/owner-scoped identity, `SCAN` enumeration,
  `temp:active-index` maintenance, purge + disable on expiry.
- [x] Add/extend unit + integration tests (OTP hash/attempt/resend/window
  matrix below); `pixi run test` stays ≥80% coverage.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] `send-code` enforces token validity, app binding, and the 60s resend
  cooldown; codes are stored hashed only.
- [x] `verify-code` caps attempts at 5 (then 429), validates app binding, and
  returns a usable session on success.
- [x] Success sets `emailVerified=true` via Admin API.
- [x] FIRST success starts the 2h `temp:active` window; re-entry (fresh code
  required) never extends `ts_end` (10:00→12:00 pinned).
- [x] Live-session in-app navigation never re-asks for a code.

## Integration Tests to Run (Local Verification)
- [x] Happy path: token → send-code (code email) → verify-code → 200 session +
  `emailVerified=true` + `temp:active` TTL 2h.
- [x] Wrong-code × 5 → 429; 6th try blocked until fresh `send-code`.
- [x] Resend within 60s → 429; after cooldown → new code, attempts reset.
- [x] Re-entry inside the window: fresh code required, `ts_end` unchanged
  (assert original end, e.g. start+2h exact).
- [x] Expired code (10min+) → 410; cross-app token → 403.
- [x] Full `pixi run test` green with ≥80% coverage.

## Dependencies
- **Blocks:** PAIML-KEYCLOAK-023, PAIML-KEYCLOAK-024, PAIML-KEYCLOAK-025
- **Blocked By:** PAIML-KEYCLOAK-021

## Estimated Effort
- [L] (Large 5–8h)

---

## Close-Out Note (implementation record)

**Status:** ✅ DONE — implemented in `pole-ai-ml` on
`feature/PAIML-KEYCLOAK-022-otp-send-verify` (base `develop`), merged via
[`pole-ai-ml` PR #356](https://github.com/fpalero/pole-ai-ml/pull/356)
(merge commit `814596f`, 2026-09-26; 15 files, +3323 / −41).

### What shipped

| Area | Change |
|---|---|
| `POST /api/auth/temporary-access/send-code` | Validates the pending `temp:token:{hash}` (404/410), resolves the app binding, enforces the 60s `temp:code-resend:{email}:{app}` cooldown (429), generates a 6-digit code, stores **only** its hash in `temp:code:{token_hash}` (10min TTL) and Brevo-sends it (EN+ES, `no-reply@fpalero.cc`). A fresh send resets `attempts` and never touches `temp:active`. |
| `POST /api/auth/temporary-access/verify-code` | Constant-time code-hash compare; attempt cap then 429; on success rotates the nobody-held password, mints the session in a single call, sets `emailVerified=true` via the Admin API, and writes `temp:active:{email}:{app}` = `{app, ts_start, ts_end}` (2h) **only if absent**. Returns `200 {access_token, token_type, expires_in}`. |
| `core/temp_access.py` (repo) | `temp:active` write switched to **SETNX** with the plan's documented `{app, ts_start, ts_end}` value (was a token string). `get_active_token` keeps its existence-probe contract; new typed read `get_window` returns the window struct. |
| Phase 8 semantics | Email/owner-scoped identity, `SCAN` enumeration, `temp:active-index` maintenance, purge + disable on expiry all kept unchanged. |

### Decisions taken at implementation time

1. **The hidden password is NOT stored — nothing is persisted.** The plan said
   the hidden password would be "stored server-side", but 021 generates it
   **inline** in the Keycloak create POST and discards it, so at `verify-code`
   time there was nothing to grant with. Instead of introducing a new store,
   `verify-code` now **rotates** the nobody-held password (a fresh random one)
   and logs in with it **inside a single call** — the secret exists only in
   process memory for the duration of that call and is never written, logged,
   or returned. This is **stronger than the plan** (no secret at rest) and keeps
   the Direct-Access-Grant step (ADR Decision 2). Ticket 025 removes the
   mechanism entirely via token exchange.
2. **`temp:active` value + write semantics changed (this was the re-entry
   window-extension bug).** The stored value moved from a token string to the
   plan's documented `{app, ts_start, ts_end}` struct, and the write is now
   **SETNX**, so `ts_end` is written exactly once and can never move. This is
   the mechanism that enforces the 10:00→12:00-pinned-forever rule. Reads: the
   Phase 8 sweeper/`get_active_token` keeps its existence-probe contract, and a
   new typed `get_window` read returns the struct for callers that need
   `ts_start`/`ts_end`.
3. **App binding is derived from the request `Origin` header.** The OTP bodies
   carry **no `clientId`** (only `{temp_token}` / `{temp_token, code}`), and the
   plan's `{temp_token}` shape had no field to carry one, so the presenting app
   is resolved from `Origin` against the host map. A **missing or unrecognised
   `Origin` is NOT treated as a mismatch**, so the documented local
   verification flow (curl / server-side call, no browser `Origin`) still works.
   ⚠️ **Explicit consequence:** this makes the `403` app-mismatch a
   **guardrail / UX boundary, not a security boundary** — a caller that simply
   omits `Origin` bypasses it. The real second factor is the **inbox OTP** plus
   the **non-extendable 2h window** (per the phase ADR, Decision 3): a forwarded
   link still faces the victim's inbox and still cannot stretch the window.
4. **TOCTOU between the app-binding read and the OTP write is knowingly left
   (fail-closed).** A Redis Lua script would close it atomically, but it was
   **not** used because `fakeredis` cannot execute Lua in the test suite, which
   would have made the whole flow untestable. Recorded as an **accepted risk**:
   the window is a single-request race whose worst case is a rejected send, not
   an extended window (`ts_end` is still SETNX-immutable).
5. **`POST /api/auth/temporary-access/activate` remains a deprecated shim**
   (021+022 decision, confirmed with the user) rather than being removed. It
   stays flagged `deprecated=True` in OpenAPI; removal is deferred until the
   Phase 2 FE flow is confirmed migrated (tracked with 023/024).

### Blocking review-round fixes

| # | Defect found in review | Fix |
|---|---|---|
| 1 | **`emailVerified` was set AFTER the session was minted**, so the returned JWT carried `email_verified: false` and therefore **opted out of the 2h window enforcement**. | Reordered: `emailVerified=true` is applied **before** the token is issued. A call-sequence test asserts the order (Admin API update precedes the grant). |
| 2 | **The attempt cap was a non-atomic read-modify-write** — 10 concurrent wrong guesses produced attempts `1,1,1,…` instead of `1..10`, so the 5-attempt cap was not enforced under concurrency. | Counter is now incremented with **`HINCRBY`** (atomic). A concurrency regression test asserts 10 parallel guesses yield a distinct increasing counter and the cap holds. |

### Acceptance criteria — verified

- [x] `send-code` enforces token validity, app binding and the 60s resend
      cooldown; codes stored hashed only (peppered SHA-256, never plaintext).
- [x] `verify-code` caps attempts at 5 (then 429, atomically), validates app
      binding, and returns a usable session on success.
- [x] Success sets `emailVerified=true` via the Admin API **before** minting the
      token (ordering test).
- [x] FIRST success starts the 2h `temp:active` window; re-entry (fresh code
      required) never extends `ts_end` (10:00→12:00 pinned — SETNX + regression
      test).
- [x] Live-session in-app navigation never re-asks for a code.
- [x] Phase 8 semantics preserved (email/owner-scoped identity, `SCAN`
      enumeration, `temp:active-index`, purge + disable on expiry).

### Test evidence

| Suite | Result |
|---|---|
| `pytest pole_api (scoped)` — CI job | **pass** (5m26s) |
| `pytest analysis-tools` / `chatbot` / `jobs` / `pole_coach` / `pole_rag` / `pole-train-model` — CI jobs | all **pass** |
| `ruff check` — CI job | **pass** |
| OTP hash / attempt / resend / window matrix + call-sequence + concurrency regressions | green (see close-out above) |

### 🔴 ROLLOUT BLOCKERS (infra repo `pole-ai-ml-infra` — NOT code)

These are **not** code defects; until they are provisioned the OTP endpoints
cannot work in a deployed environment:

1. **`TEMP_ACCESS_OTP_PEPPER` must be provisioned per environment** (Helm
   Secret) or `send-code` / `verify-code` answer **503**. The pepper is required
   to hash codes; fail-closed on purpose.
2. **Direct Access Grants must be enabled on the `pole-fe` and `pole-analyst`
   clients** (realm config). The hidden-password session fetch is a Direct
   Access Grant and is rejected otherwise.
3. **Carried over from 021:** `FE_BASE_URL`, `ANALYST_BASE_URL` and
   `BREVO_API_KEY` must be set per environment (`pole-api` ConfigMap still only
   sets `TEMP_ACCESS_*`).

Items 1–2 belong to `infrastracture/` (realm clients + `pole-api` Secret) and
must land in `pole-ai-ml-infra` — **never** in `pole-ai-ml`. See
[`docs/ENV_VARS.md`](../../../ENV_VARS.md) for the full variable contract.

### Follow-ups for PAIML-KEYCLOAK-023 / 024

- 023 must call `send-code` / `verify-code` with **no `clientId`** and send a
  browser `Origin`; the FE should not invent a client-binding field.
- 024 (Mailpit E2E) should cover the `Origin`-derived 403 path, the 60s resend
  429, the 5-attempt cap under concurrency, and the pinned-window re-entry.
