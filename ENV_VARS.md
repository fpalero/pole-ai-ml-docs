# Environment Variables Reference

> **Environment mapping (2026-09-10 — no prod exists):** live staging/pre-prod
> = namespace `pole-ai` on DuckDNS (`pole-coach.duckdns.org`,
> `pole-ml.duckdns.org`, `pole-keycloack.duckdns.org`, working DBs `pole_api` /
> `skeleton_data` / `analysis_db`); `pole-ai-staging` + `*.pole.local` (e.g.
> `keycloak.pole.local` examples below) = local/legacy overlay;
> `values-prod.yaml` naming is historical, NOT production traffic.

All environment variables used by the **pole-ai** monorepo, grouped by app /
package. Column meanings:

- **NAME** — variable (build-time `environment.ts` / runtime `window.*` for the
  Angular apps are marked accordingly).
- **DESCRIPTION** — what it controls and who reads it.
- **EXAMPLE** — a representative value.
- **POSIBLE VALUES** — accepted values / default.

Sources: `app/pole_api/src/core/config.py`, `app/pole_api/src/core/auth.py`,
`packages/*/config.py`, the Angular `environments/*.ts` + `assets/env.js`, and
the k3s Helm configmaps (`infrastracture/helm/pole-ai/charts/*/templates/configmap.yaml`).

---

## pole_api — FastAPI backend

### Core / storage

| NAME | DESCRIPTION | EXAMPLE | POSIBLE VALUES |
|---|---|---|---|
| `MONGODB_URI` (alias `MONGO_URI`) | MongoDB connection string (backend, tools, chatbot). | `mongodb://admin:password@localhost:27017/?authSource=admin` | any Mongo URI; default `mongodb://localhost:27017/` |
| `POLE_AI_ROOT` | Repo root the app resolves default paths from. | `/home/fernando/Proyectos/pole-ai` | absolute path; auto-derived |
| `POLE_API_DB` | App database (classes, videos, jobs, uploads). | `pole_api` | any DB name; default `pole_api` |
| `SKELETON_DB` | ML/skeleton database (windows, trick histograms, cohort). | `skeleton_data` | any DB name; default `skeleton_data` |
| `ANALYSIS_DB` | Analysis database (video histograms, landmarks, insights). | `analysis_db` | any DB name; default `analysis_db` |
| `REDIS_URL` | Redis connection for the job queue + chatbot sessions. | `redis://localhost:6379/0` | any Redis URL; default `redis://localhost:6379/0` |
| `FFMPEG_BIN` | ffmpeg binary used by crop/thumbnail/pose stages. | `ffmpeg` | binary name/path; default `ffmpeg` |
| `API_KEY` | Optional static bearer key enforcement (REST). | `sk-...` | any string or empty; default none |
| `DATABASE_URL` | Postgres DSN for the optional chatbot session store (falls back to Redis when unset). | `postgresql://user:password@localhost:5432/pole_ai` | Postgres DSN or empty; default none |

### Paths / ML assets

| NAME | DESCRIPTION | EXAMPLE | POSIBLE VALUES |
|---|---|---|---|
| `CRAWLER_DOWNLOADS_DIR` | Where the crawler writes downloaded videos. | `<root>/app/pole_api/downloads` | absolute path |
| `UPLOADS_DIR` | Where uploaded videos are stored. | `<root>/app/pole_api/uploads` | absolute path |
| `ANALYSIS_UPLOAD_DIR` | Where analysis videos are stored. | `<root>/app/pole_api/analysis_uploads` | absolute path |
| `CURATED_DIR` | Curated clip storage. | `<root>/app/pole_api/curated` | absolute path |
| `POSE_MODEL_PATH` | MediaPipe pose landmarker model file. | `packages/pole-train-model/models/pose_landmarker_heavy.task` | path to `.task` |
| `EMBEDDING_MODEL_PATH` | LSTM embedding/classifier model file. | `packages/pole-train-model/models/lstm_model_normal_final.keras` | path to `.keras` |
| `CHROMA_PERSIST_DIR` | ChromaDB persist directory (embeddings). | `<root>/app/pole_api/FeaturesEmbeddings` | absolute path |
| `MODEL_RUNS_DIR` | Directory for model run artifacts. | `packages/pole-train-model/models/runs` | absolute path |

### Pipeline / ML tuning

| NAME | DESCRIPTION | EXAMPLE | POSIBLE VALUES |
|---|---|---|---|
| `EXTRACTION_STRIDE` | Frame stride during skeleton extraction. | `5` | positive int; default `1` |
| `E2E_FAKES` | Use fake skeleton/ML extractors for end-to-end runs. | `1` | `0/1`, `true/false`, `yes/no`, `on/off`; default off |
| `ALLOW_SEED_MEASUREMENTS` | Opt-in that lets the `seed-measurements` endpoint (PAIML-POLE-API-131) run on non-testing datasets; testing datasets always allowed. | `1` | `0/1`, `true/false`; default off/unset — never set in prod |
| `ZSCORE_SIGMA_FLOOR` | Floor for the z-score denominator (std). | `0.000001` | float ≥ `1e-6`; default `1e-6` |
| `CLASSIFY_CONFIDENCE_THRESHOLD` | LSTM trick-classification confidence floor. | `0.7` | `0.0–1.0`; default `0.7` |
| `ANALYZE_WORKER_POOL_SIZE` | Max concurrent analyze workers (MediaPipe gate). | `2` | int ≥ 1; default `2` |

### Chatbot / LLM agent

| NAME | DESCRIPTION | EXAMPLE | POSIBLE VALUES |
|---|---|---|---|
| `LLM_PROVIDER` | LLM backend for the chatbot/coach. | `ollama` | `ollama`, `openrouter`; default `ollama` |
| `OLLAMA_HOST` | Ollama server URL (host Ollama must bind `0.0.0.0` for pods). | `http://localhost:11434` | any URL; default `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama model name. | `qwen3.8:27b` | any installed model; default `qwen3.8:27b` |
| `OPENROUTER_API_KEY` | OpenRouter API key (`LLM_PROVIDER=openrouter`). | `sk-or-...` | key or empty; default none |
| `OPENROUTER_MODEL` | OpenRouter model. | `meta-llama/llama-3.3-70b-instruct` | model id |
| `OPENROUTER_BASE_URL` | OpenRouter endpoint. | `https://openrouter.ai/api/v1` | URL |
| `OPENROUTER_FALLBACK_MODEL` | Fallback model when the blank-retry budget is exhausted (PAIML-POLE-API-097). | `meta-llama/llama-3.3-70b-instruct` | model id or empty; default unset (disabled) |
| `LLM_MONTHLY_BUDGET_USD` | Per-user monthly LLM budget. | `5.5` | float; default `5.5` |
| `LLM_DAILY_BUDGET_USD` | Per-user daily LLM budget. | `0.75` | float; default `0.75` |
| `MAX_AGENT_ITERATIONS` | Max agent reasoning iterations. | `6` | positive int; default `6` |
| `LLM_TIMEOUT` | LLM request timeout (seconds). | `120` | seconds; default `120` |
| `CHATBOT_TURN_TIMEOUT` | Wall-clock budget for a single ReAct `agent.run` (PAIML-POLE-API-095; raised 120 → 240 by PAIML-POLE-API-129 so long analyst composed chains complete before the WS per-turn guard). Feeds `Settings.chatbot_max_turn_seconds` → `PoleLangGraphAgent.max_turn_seconds`; `LLM_TIMEOUT` (per-call LLM HTTP timeout) is a different knob. | `240` | seconds; default `240` (must stay < WS guard `ANALYST_WS_TURN_BUDGET_S` 300 and FE `TURN_BUDGET_MS` 360s) |
| `CHATBOT_BLANK_MAX_RETRIES` | Max blank-completion retries before model fallback (PAIML-POLE-API-097). | `2` | int; default `2` |
| `AGENT_REPHRASE_BUDGET` | Max agent rephrase attempts. | `2` | int; default `2` |
| `CHATBOT_COLLECT_METRICS` | Collect chatbot usage metrics. | `true` | `0/1`, `true/false`; default off |
| `CHATBOT_OUT_DIR` | Chatbot output directory (tool artifacts). | `chatbot_output` | path; default `chatbot_output` |
| `CHATBOT_RATE_LIMIT_MAX` | Chatbot rate-limit max requests per window. | `10` | int; default `10` |
| `CHATBOT_RATE_LIMIT_WINDOW_S` | Chatbot rate-limit window (seconds). | `30` | int; default `30` |
| `ANALYST_WS_TURN_BUDGET_S` | Per-turn wall-clock budget for an analyst-chat WS turn — wraps the ENTIRE composed turn (brain + ReAct chain + retries + shaping) so a slow turn emits a terminal frame instead of zero frames (PAIML-POLE-API-126). | `300` | float seconds; default `300` (above supergraph 30s / ReAct 240s — PAIML-POLE-API-129, below FE `TURN_BUDGET_MS` 360s) |

### Auth / Keycloak (`app/pole_api/src/core/auth.py`)

| NAME | DESCRIPTION | EXAMPLE | POSIBLE VALUES |
|---|---|---|---|
| `AUTH_ENABLED` | Enable JWT enforcement (`0` bypasses; resolves anonymous claims). | `1` | `0/1`, `true/false`; default `1` (enabled) |
| `KEYCLOAK_ISSUER` | Expected token `iss` (browser-facing Keycloak URL). | `https://keycloak.pole.local/realms/pole-ai` | URL ending `/realms/<realm>` |
| `KEYCLOAK_JWKS_URL` | JWKS endpoint used to verify RS256 signatures. | `http://pole-ai-keycloak:8080/realms/pole-ai/protocol/openid-connect/certs` | URL to the realm `certs` endpoint |
| `KEYCLOAK_CLIENTS` | Comma-separated allowed `azp` clients. | `pole-fe,pole-analyst,mcp-server` | client IDs, comma-separated |

### Temporary access / magic link (`app/pole_api/src/core/config.py`) — implemented (Phases 2–4, 9 of `docs/app/keycloak`)

> These variables back the Keycloak temporary magic-link access feature (see `docs/app/keycloak`,
> Phases 1–4 ✅ DONE). `KEYCLOAK_ADMIN_*` are supplied by the `pole-api-admin` confidential client
> service account (secret from a Helm Secret); `TEMP_ACCESS_*` are consumed by
> `app/pole_api/src/core/temp_access.py`.
>
> **Phase 9 (PAIML-KEYCLOAK-021)** changed the delivery model: `pole_api` now emails the
> per-app direct link through **Brevo** and Keycloak sends **no** email on the temp path.
> **PAIML-KEYCLOAK-022** added the 6-digit OTP second factor (`send-code` / `verify-code`).
> See the Brevo + host-map table below and the OTP table after it.

| NAME | DESCRIPTION | EXAMPLE | POSIBLE VALUES |
|---|---|---|---|
| `KEYCLOAK_ADMIN_CLIENT_ID` | Confidential `pole-api-admin` client id used by the Keycloak admin client (create/disable users). | `pole-api-admin` | confidential client id |
| `KEYCLOAK_ADMIN_CLIENT_SECRET` | Secret for the `pole-api-admin` service account (from a Helm Secret, not the realm JSON). | `***` | secret string |
| `KEYCLOAK_ADMIN_ISSUER` | Token issuer for the admin client client-credentials grant. | `http://pole-ai-keycloak:8080/realms/pole-ai` | realm issuer URL |
| `TEMP_ACCESS_COOLDOWN_S` | 14-day cooldown between temp-access requests for the same email (Redis `temp:req` TTL). | `1209600` | seconds; default 14d |
| `TEMP_ACCESS_WINDOW_S` | 2-hour activated window for a temp user (Redis `temp:active` TTL; aligns with 2h token `exp`). | `7200` | seconds; default 2h |
| `TEMP_ACCESS_TOKEN_TTL_S` | TTL of a pending magic-link token (Redis `temp:token` TTL). | `86400` | seconds; default 24h |
| App→role map | Per-app temporary role assignment (`pole-fe`→`fe-user`, `pole-analyst`→`analyst-user`), enforced from token `azp`. | `pole-fe:fe-user,pole-analyst:analyst-user` | comma-separated map |

### Brevo direct-link email + per-app host map (PAIML-KEYCLOAK-021) — implemented

> `pole_api` owns temp-access delivery: it emails the per-app direct link
> `https://<host>/?temp_token=xxx` via Brevo (sender `no-reply@fpalero.cc`, EN + ES).
> The host map is **also** the app binding: the `temp_token` is only ever delivered to the
> host that owns the requesting `clientId`, so presenting it on the other app is rejected.
> Consumed by `app/pole_api/src/core/email/{link_templates,brevo_email}.py`.

| NAME | DESCRIPTION | EXAMPLE | POSIBLE VALUES |
|---|---|---|---|
| `BREVO_API_KEY` | Brevo API key for the transactional-email API (`POST /v3/smtp/email`). **Required** for temp access: when unset the endpoint answers `503` rather than promising an email it cannot send. | `xkeysib-***` | secret string / unset |
| `DEFAULT_EMAIL_LOCALE` | Fallback template locale when the request carries none. | `en` | `en` \| `es` |
| `FE_BASE_URL` | Public origin of the `pole-fe` app — the link target for a `pole-fe` temp token. **Required per environment**; the code default is the local sandbox host so an unset environment fails closed. | `https://demo-ml-agent.duckdns.org` | URL |
| `ANALYST_BASE_URL` | Public origin of the `pole-analyst` app — the link target for a `pole-analyst` temp token. **Required per environment** (same rationale). | `https://demo-ai-agent.duckdns.org` | URL |

Because these are the temp-token **app binding**, an environment that forgets
them must fail closed rather than mint links to a public host — so the code
defaults are the local sandbox origins, and dev/staging/prod must each set
both explicitly:

| Environment | `FE_BASE_URL` | `ANALYST_BASE_URL` |
|---|---|---|
| demo / staging | `https://demo-ml-agent.duckdns.org` | `https://demo-ai-agent.duckdns.org` |
| local sandbox | `http://localhost:4200` | `http://localhost:4300` |

> **Not yet wired in the `pole-api` helm ConfigMap** (it sets `TEMP_ACCESS_*`
> but not `FE_BASE_URL` / `ANALYST_BASE_URL` / `BREVO_API_KEY`). Until that
> lands in `pole-ai-ml-infra`, the endpoint answers 503 without a Brevo key and
> would link to the sandbox hosts.

> The realm SMTP (`smtpServer`) is **no longer used by the temp-access path**. It stays
> configured for Keycloak's own non-temp self-service flows.

### 6-digit OTP send/verify + session grant (PAIML-KEYCLOAK-022) — implemented

> Backs `POST /api/auth/temporary-access/send-code {temp_token}` and
> `POST /api/auth/temporary-access/verify-code {temp_token, code}`. Codes are stored
> **hashed only** (peppered SHA-256, never plaintext). Consumed by
> `app/pole_api/src/core/{config.py,temp_access.py}` and
> `auth/controllers/temporary_access.py`.

| NAME | DESCRIPTION | EXAMPLE | POSIBLE VALUES |
|---|---|---|---|
| `TEMP_ACCESS_OTP_PEPPER` | Server-side secret mixed into the OTP hash (peppered SHA-256) so a Redis dump cannot be brute-forced offline. **Required**: when unset, `send-code` / `verify-code` answer **503** (fail-closed — never issue or accept a code hashed without it). | `***` (32+ random bytes) | secret string / unset |
| `TEMP_ACCESS_OTP_TTL_S` | TTL of a pending 6-digit code (Redis `temp:code` TTL). | `600` | seconds; default 10min |
| `TEMP_ACCESS_OTP_MAX_ATTEMPTS` | Wrong-code attempts allowed per send before `verify-code` answers `429`. Counted with an **atomic `HINCRBY`** so the cap holds under concurrency. | `5` | integer; default 5 |
| `TEMP_ACCESS_OTP_RESEND_COOLDOWN_S` | Resend cooldown per `(email, app)` (Redis `temp:code-resend` TTL); a `send-code` inside the window answers `429`. | `60` | seconds; default 60 |
| `TEMP_ACCESS_WINDOW_S` (reused) | 2-hour activated window. `ts_end` is written **once** (`SETNX`); re-entry inside the live window asks a fresh code but **never** moves the end. | `7200` | seconds; default 2h |

**Not a variable — the hidden password.** The plan's "stored server-side" secret
is **never stored**: 021 generated it inline in the Keycloak create POST and
discarded it, so `verify-code` **rotates** the nobody-held password and logs in
with it **inside a single call** (Direct Access Grant). Nothing is persisted, so
there is no variable, no secret and no rotation burden. Ticket
`PAIML-KEYCLOAK-025` (FUTURE) removes the mechanism entirely in favour of
token-exchange impersonation via `pole-api-admin`.

**App binding without a `clientId`.** The OTP bodies carry no `clientId`; the
presenting app is resolved from the request **`Origin`** header against the
`FE_BASE_URL` / `ANALYST_BASE_URL` host map. A **missing or unrecognised
`Origin` is not treated as a mismatch** (so curl / server-side local
verification still works) — which makes the `403` a **guardrail / UX boundary,
not a security boundary**. The real second factor is the inbox OTP plus the
non-extendable 2h window.

#### 🔴 ROLLOUT BLOCKERS for the OTP path (infra repo `pole-ai-ml-infra`, not code)

Until these land, the OTP endpoints cannot work in a deployed environment:

1. **`TEMP_ACCESS_OTP_PEPPER` must be provisioned per environment** (Helm
   Secret) or `send-code` / `verify-code` answer **503**.
2. **Direct Access Grants must be enabled on the `pole-fe` and `pole-analyst`
   clients** (realm config) — the session fetch is a Direct Access Grant and is
   rejected otherwise.
3. **Carried over from 021:** `FE_BASE_URL`, `ANALYST_BASE_URL` and
   `BREVO_API_KEY` must be set per environment.

> The `pole-api` ConfigMap currently sets only `TEMP_ACCESS_*` — none of the
> variables in these three groups are wired yet. Items 1–2 change the **realm
> clients** and the **`pole-api` Secret**, so they belong to
> `pole-ai-ml-infra` (`infrastracture/helm/pole-ai/…`), **never** to `pole-ai-ml`.


### Instagram / crawler (also used by `pole_crawler`)

| NAME | DESCRIPTION | EXAMPLE | POSIBLE VALUES |
|---|---|---|---|
| `INSTAGRAM_USERNAME` | Instagram account username for scraping. | `adeveloper266` | any username |
| `INSTAGRAM_CSRFTOKEN` | Instagram CSRF token cookie. | `XomxsJEH44Mo2mmeWD7zAs` | token string |
| `INSTAGRAM_SESSIONID` | Instagram sessionid cookie. | `49033096789%3A...` | session string |
| `INSTAGRAM_DS_USER_ID` | Instagram `ds_user_id` cookie. | `49033096789` | numeric id |
| `INSTAGRAM_IG_DID` | Instagram `ig_did` cookie. | `EF8410A0-...` | uuid |
| `SESSION_FILE_PATH` | Path to the saved session file. | `/app/session-adeveloper266` | path |
| `INSTAGRAM_PROXY_URL` | Proxy for Instagram requests. | `http://proxy:8080` | URL or empty |

---

## pole_fe — Angular SPA (frontend)

| NAME | DESCRIPTION | EXAMPLE | POSIBLE VALUES |
|---|---|---|---|
| `environment.apiBaseUrl` (build-time) | API base for service calls. Dev = local API; prod = `''` (nginx proxies `/api`). | `''` | dev: `http://localhost:8000`; prod: `''` |
| `window.keycloakUrl` (runtime `assets/env.js`) | Keycloak server URL the app logs into. | `https://keycloak.pole.local` | any Keycloak base URL |
| `window.keycloakRealm` (runtime `assets/env.js`) | Keycloak realm. | `pole-ai` | realm name |
| `KEYCLOAK_CLIENT_ID` (compiled) | Keycloak client id for this app. | `pole-fe` | fixed |

---

## pole_analyst — Angular coach SPA (frontend)

| NAME | DESCRIPTION | EXAMPLE | POSIBLE VALUES |
|---|---|---|---|
| `environment.apiBaseUrl` (build-time) | API base for service calls (relative `/api`, proxied). | `/api` | `/api` |
| `window.keycloakUrl` (runtime `assets/env.js`) | Keycloak server URL the app logs into. | `https://keycloak.pole.local` | any Keycloak base URL |
| `window.keycloakRealm` (runtime `assets/env.js`) | Keycloak realm. | `pole-ai` | realm name |
| `KEYCLOAK_CLIENT_ID` (compiled) | Keycloak client id for this app. | `pole-analyst` | fixed |

---

## packages

### pole_crawler (`packages/pole-crawler`)

| NAME | DESCRIPTION | EXAMPLE | POSIBLE VALUES |
|---|---|---|---|
| `INSTAGRAM_USERNAME` | Instagram account for scraping. | `adeveloper266` | username |
| `INSTAGRAM_CSRFTOKEN` | Instagram CSRF token cookie. | `XomxsJEH44Mo2mmeWD7zAs` | token |
| `INSTAGRAM_SESSIONID` | Instagram sessionid cookie. | `49033096789%3A...` | session |
| `INSTAGRAM_DS_USER_ID` | Instagram `ds_user_id`. | `49033096789` | numeric id |
| `INSTAGRAM_IG_DID` | Instagram `ig_did`. | `EF8410A0-...` | uuid |
| `SESSION_FILE_PATH` | Saved session file path. | `/app/session-adeveloper266` | path |
| `INSTAGRAM_PROXY_URL` | Proxy for Instagram requests. | `http://proxy:8080` | URL or empty |
| `DOWNLOADS_DIR` | Downloaded-video output directory. | `/downloads` | path |
| `SMTP_USER` | SMTP user for alert emails. | `user@example.com` | user |
| `SMTP_PASS` | SMTP password. | `secret` | password |
| `SMTP_SERVER` | SMTP host. | `smtp.example.com` | host |
| `SMTP_PORT` | SMTP port. | `587` | int; default `587` |
| `ALERT_EMAIL` | Recipient for alert emails. | `dev@pole.local` | email |

### pole_tools / pole-train-model (`packages/pole-train-model/src/pole_tools/config.py`)

| NAME | DESCRIPTION | EXAMPLE | POSIBLE VALUES |
|---|---|---|---|
| `MONGODB_URI` (alias `MONGO_URI`) | Mongo connection for the CLI tools. | `mongodb://admin:password@localhost:27017/?authSource=admin` | URI; default `mongodb://localhost:27017/` |
| `POLE_API_DB` | App DB name for tools. | `pole_api` | DB name; default `pole_api` |
| `SKELETON_DB` | ML data DB name for tools. | `skeleton_data` | DB name; default `skeleton_data` |
| `OUTPUT_DIR` | CLI output directory. | `./results` | path; default `./results` |
| `MODEL_PATH` | LSTM model file for tools. | `models/lstm_model_normal.keras` | path |
| `POSE_MODEL_PATH` | MediaPipe pose model file. | `models/pose_landmarker_heavy.task` | path |
| `CHROMA_DIR` | ChromaDB persist directory for embeddings. | `./FeaturesEmbeddings` | path |
| `CHROMA_COLLECTION` | ChromaDB collection name. | `movement_embeddings` | collection name |
| `STRIDE` | Processing stride for tools. | `1` | positive int; default `1` |
| `EXTRACTION_STRIDE` | Skeleton extraction stride. | `1` | positive int; default `1` |
| `VISIBILITY_THRESHOLD` | Min landmark visibility to keep a sample. | `0.7` | `0.0–1.0`; default `0.7` |

### pole_chatbot (`packages/chatbot`)

| NAME | DESCRIPTION | EXAMPLE | POSIBLE VALUES |
|---|---|---|---|
| `MONGODB_URI` / `MONGO_URI` | Mongo connection for chatbot infra. | `mongodb://admin:password@localhost:27017/?authSource=admin` | URI |
| `POLE_API_DB` | App DB used by the chatbot worker. | `pole_api` | DB name |
| `SKELETON_DB` | Skeleton DB used by chatbot tools. | `skeleton_data` | DB name |
| `REDIS_URL` | Redis for sessions/jobs. | `redis://localhost:6379/0` | Redis URL |
| `POLE_JOBS_QUEUE` | Job queue name. | `default` | queue name |
| `CHATBOT_OUT_DIR` | Chatbot output directory. | `chatbot_output` | path |
| `MAX_AGENT_ITERATIONS` | Max agent iterations. | `6` | positive int |
| `LLM_TIMEOUT` | LLM timeout (seconds). | `120` | seconds |
| `CHATBOT_COLLECT_METRICS` | Collect usage metrics. | `false` | bool |
| `AGENT_REPHRASE_BUDGET` | Rephrase budget. | `2` | int |
| `OLLAMA_MODEL` | Ollama model. | `qwen3.8:27b` | model |
| `OLLAMA_HOST` | Ollama URL. | `http://localhost:11434` | URL |
| `USE_CHECKPOINT` | Use a checkpointed session. | `false` | bool |