# OmniRoute Management API — Runtime Provisioning Reference (CI use)

> **Type:** Reference (how-to hooks for a future follow-up).
> **Status:** Investigative — **NOT** currently wired into the `/oc` GitHub Action.
> **Accepted CI config today:** `opencode/big-pickle` via the `OPENCODE_API_KEY` secret in
> the self-contained `.github/workflows/opencode.yml` (see ACD `ADR-003`).
> **Source:** [OmniRoute API Reference wiki](https://github.com/diegosouzapw/OmniRoute/wiki/API-Reference).
> **Date:** 2026-08-31.

This document captures how an OmniRoute instance could be **provisioned at runtime inside a
CI job** — create an API key, add an upstream provider connection, and then call the
OpenAI-compatible `/v1/chat/completions` through it. It exists so that the OmniRoute routing
path can be re-enabled later (or used in a sandbox) without re-deriving the API surface from
scratch.

---

## 1. Two authentication tiers (important distinction)

| Tier | Mechanism | Used by |
|------|-----------|---------|
| **Management auth** | `auth_token` cookie (dashboard session) **or** a management-scoped API key (`requireManagementAuth`) | all `/api/*` management endpoints (providers, keys, settings, combos, webhooks, skills, …) |
| **Runtime Bearer key** | `Authorization: Bearer <api-key>` | all `/v1/*` runtime endpoints (chat/completions, embeddings, …) |

Authentication section (verbatim from the wiki):

- Dashboard routes (`/dashboard/*`) use `auth_token` cookie.
- Login uses saved password hash; fallback to `INITIAL_PASSWORD`.
- `requireLogin` toggleable via `/api/settings/require-login`.
- `/v1/*` routes optionally require a Bearer API key when `REQUIRE_API_KEY=true`.

> **Breaking change (v3.8.0):** `/api/v1/agents/tasks/*` and cooldown endpoints now require
> **management auth** (dashboard `auth_token` cookie or a management-scoped API key).

### `REQUIRE_API_KEY` (keyless mode)

- When `REQUIRE_API_KEY=true`: `/v1/*` routes **require** a Bearer API key.
- When `REQUIRE_API_KEY=false`: `/v1/*` routes accept **any** Bearer key (or none) — ideal for
  an ephemeral CI instance where you only need auto-routing.
- There is **no** `AUTH_ENABLED` variable documented in the API Reference page; the keyless
  toggle is `REQUIRE_API_KEY`.

Alternative key delivery for clients that cannot set headers: `?token=…`, `?apiKey=…`,
`?api_key=…`, `?key=…`, or the URL-embedded form `POST /api/v1/vscode/{token}/chat/completions`.

### Auth endpoints

```
POST /api/auth/login
POST /api/auth/logout
GET|PUT /api/settings/require-login     # toggle login required
```

---

## 2. Registered Keys (auto-management) — runtime API-key issuance

The most relevant API for **creating a key at runtime**. Auth: Bearer API key.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/registered-keys` | List registered keys (masked prefix only) |
| `POST` | `/api/v1/registered-keys` | **Issue a new registered key** |
| `GET` | `/api/v1/registered-keys/[id]` | Retrieve metadata (no raw key) |
| `DELETE` | `/api/v1/registered-keys/[id]` | Revoke |
| `POST` | `/api/v1/registered-keys/[id]/revoke` | Explicit revoke (same as DELETE) |

**POST body (verbatim):**

```json
{
  "name": "...",
  "provider": "?",
  "accountId": "?",
  "idempotencyKey": "?",
  "expiresAt": "?",
  "dailyBudget": "?",
  "hourlyBudget": "?"
}
```

**Response behavior:**

- Returns the **raw key once** in the response; afterwards only the masked prefix is visible.
- Returns **`429 Too Many Requests`** on quota refusal.

Companion endpoints:

```
GET  /v1/quotas/check            # Pre-validate quota for a provider + accountId before issuing a registered key
POST /v1/issues/report           # Report a quota/key issuance failure to GitHub (requires GITHUB_ISSUES_REPO + token)
```

> Wiki verbatim: "Issue a new registered key — body `{name, provider?, accountId?, idempotencyKey?,
> expiresAt?, dailyBudget?, hourlyBudget?}`. Returns the raw key **once**. Returns `429` on quota refusal."

---

## 3. Provider management (add an upstream connection)

Auth on all provider routes: management session (`auth_token` cookie) or management-scoped API key.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/providers` | `GET/POST` | List / create providers |
| `/api/providers/[id]` | `GET/PUT/DELETE` | Manage a provider |
| `/api/providers/[id]/test` | `POST` | Test provider connection |
| `/api/providers/[id]/models` | `GET` | List provider models |
| `/api/providers/validate` | `POST` | Validate provider config |
| `/api/provider-nodes*` | Various | Provider node management |
| `/api/provider-models` | `GET/POST/PATCH/DELETE` | Custom models (add / update / hide / delete) |

**Provider POST body shape is NOT expanded in the API Reference page.** The provider type used is
`"apikey"` (the doc references `providerBreaker.apikey`). To author a valid body, inspect the
OmniRoute source (`src/shared/validation/schemas.ts`) or run `GET /api/providers` against a live
instance to copy an existing provider object as a template.

**Provider `test` example (verbatim pattern):**

```bash
curl -X POST http://localhost:20128/api/providers/<id>/test \
  -H "Cookie: auth_token=..." \
  -H "Content-Type: application/json"
```

**OAuth env repair (v3.6.1+):**

```
POST /api/system/env/repair
Content-Type: application/json

{ "provider": "claude-code" }
```

---

## 4. Env-var pre-seeding at container startup

The API Reference page does **not** enumerate `OPENROUTER_API_KEY` / `ANTHROPIC_API_KEY` /
`OPENAI_API_KEY` names — those live on the separate
[Environment Variables](https://github.com/diegosouzapw/OmniRoute/wiki/Environment) wiki page.

Known explicit reference: **`OMNIROUTE_API_KEY`**:

```bash
wscat -c "ws://localhost:20128/v1/responses?api_key=<OMNIROUTE_API_KEY>"
# or: -H "Authorization: Bearer <OMNIROUTE_API_KEY>"
```

Practical inference for CI: pre-seed a provider by either (a) setting the provider `*_API_KEY`
env vars read at startup, or (b) `POST /api/providers` to create an `"apikey"`-type provider with
the upstream key in the body.

---

## 5. Runtime chat completions

```
POST /v1/chat/completions
Authorization: Bearer your-api-key
Content-Type: application/json
```

**Request body (verbatim):**

```json
{
  "model": "cc/claude-opus-4-6",
  "messages": [
    { "role": "user", "content": "Write a function to..." }
  ],
  "stream": true
}
```

**Model naming observations:**

- Provider-prefixed: `cc/claude-opus-4-6`, `openai/gpt-4o-mini`, `deepgram/nova-3`,
  `cohere/rerank-3`, `openai/tts-1`.
- Combo/model mappings: `POST /api/model-combo-mappings` maps a `pattern` → `comboId` for
  transparent redirection of OpenAI-style model IDs.
- **`"auto"`** model is accepted (used in the VS Code alias example):
  `{"model":"auto","messages":[{"role":"user","content":"hello"}]}`.
- "The provider prefix is auto-added if missing. Mismatched models return `400`." (line 551)
- Quota-share routing: `qtSd/<group>/codex/<model>`.

**Custom request headers:**

| Header | Direction | Description |
|--------|-----------|-------------|
| `X-OmniRoute-No-Cache` | Request | `true` to bypass cache |
| `X-OmniRoute-Progress` | Request | `true` for progress events |
| `X-Session-Id` | Request | Sticky session key |
| `Idempotency-Key` | Request | Dedup key (5s window) |

**Auto model resolution order:** direct provider/model → alias (`/api/models/alias`) → combo
(`/api/combos*`, `/api/model-combo-mappings`) → auto-routing strategy (rules / cost / latency /
sla-aware / lkgp). Note: **`auto/coding` is not documented** in the API Reference page; only
`auto` appears (in a curl example). The `coding` suffix is likely a combo/alias defined by
configuration — the earlier CI attempt failed with `Model not found: auto/coding` because the
fresh container had **no upstream provider** configured.

### Model catalog & aliases

```
GET /v1/models                # All chat, embedding, image models + combos (OpenAI format)
GET /api/models/catalog       # All models by provider + type
GET /api/models/alias         # Model aliases
POST /api/models/alias        # Create alias
```

---

## 6. Complete curl examples (verbatim)

**VS Code tokenized alias:**

```bash
curl -X POST https://your-host.example/api/v1/vscode/YOUR_API_KEY/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"hello"}]}'
```

**Standard Bearer auth:**

```bash
curl -X POST http://localhost:20128/v1/chat/completions \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"hello"}]}'
```

**Management auth (cookie-based):**

```bash
curl -X DELETE http://localhost:20128/api/resilience/model-cooldowns \
  -H "Cookie: auth_token=..." \
  -H "Content-Type: application/json" \
  -d '{"provider":"openai","model":"gpt-4o-mini"}'
```

---

## 7. Recommended CI provisioning sequence

This is the logical path if OmniRoute routing is ever re-enabled in CI or used in a sandbox:

1. **Start OmniRoute** with `REQUIRE_API_KEY=false` (or seed `INITIAL_PASSWORD`).
2. **Login** to get a management session: `POST /api/auth/login` → `auth_token` cookie.
3. **Create a provider connection:** `POST /api/providers` with the upstream API key
   (body shape from source or `GET /api/providers` on a live instance).
4. **Test the provider:** `POST /api/providers/[id]/test`.
5. **Issue a runtime API key:** `POST /api/v1/registered-keys` with `{"name":"ci-key"}` and
   capture the raw key from the response.
6. **Call chat completions:** `POST /v1/chat/completions` with
   `Authorization: Bearer <raw-key>` and `"model":"auto"` (or a specific model like
   `cc/claude-opus-4-6`).

---

## 8. Gaps (not covered by the API Reference page)

Consult the [Environment Variables](https://github.com/diegosouzapw/OmniRoute/wiki/Environment)
wiki or the OmniRoute source for:

- Exact `POST /api/providers` body shape (provider type, API key field, env vars, connection URL).
- Specific env-var names such as `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`.
- Exact `POST /api/auth/login` body shape (username/password fields).
- Detailed `/api/keys*` sub-endpoint bodies (dashboard-managed API key CRUD vs. auto `registered-keys`).
- The `auto/coding` model/combo definition (not present in the API Reference page).
- Auto-Combo configuration details (separate [Auto-Combo](https://github.com/diegosouzapw/OmniRoute/wiki/Auto-Combo) wiki page).

---

## 9. Decision context

- **Accepted config (done):** the `/oc` PR review GitHub Action uses `opencode/big-pickle`
  (OpenCode's own free model) with the `OPENCODE_API_KEY` secret, in a **self-contained**,
  duplicated `opencode.yml` in both `pole-ai-ml` and `pole-ai-ml-infra`. Smoke test passed E2E
  (pole-ai-ml run `33399596897`).
- **OmniRoute path (deferred):** abandoned for CI because a fresh container had no upstream
  provider (`Model not found: auto/coding`). This document preserves the runtime-provisioning
  API hooks so it can be revisited cleanly.
