# Environment Variables Reference

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
| `LLM_MONTHLY_BUDGET_USD` | Per-user monthly LLM budget. | `5.5` | float; default `5.5` |
| `LLM_DAILY_BUDGET_USD` | Per-user daily LLM budget. | `0.75` | float; default `0.75` |
| `MAX_AGENT_ITERATIONS` | Max agent reasoning iterations. | `6` | positive int; default `6` |
| `LLM_TIMEOUT` | LLM request timeout (seconds). | `120` | seconds; default `120` |
| `CHATBOT_TURN_TIMEOUT` | Wall-clock budget for a whole agent turn (PAIML-POLE-API-095). | `120` | seconds; default `120` |
| `AGENT_REPHRASE_BUDGET` | Max agent rephrase attempts. | `2` | int; default `2` |
| `CHATBOT_COLLECT_METRICS` | Collect chatbot usage metrics. | `true` | `0/1`, `true/false`; default off |
| `CHATBOT_OUT_DIR` | Chatbot output directory (tool artifacts). | `chatbot_output` | path; default `chatbot_output` |
| `CHATBOT_RATE_LIMIT_MAX` | Chatbot rate-limit max requests per window. | `10` | int; default `10` |
| `CHATBOT_RATE_LIMIT_WINDOW_S` | Chatbot rate-limit window (seconds). | `30` | int; default `30` |

### Auth / Keycloak (`app/pole_api/src/core/auth.py`)

| NAME | DESCRIPTION | EXAMPLE | POSIBLE VALUES |
|---|---|---|---|
| `AUTH_ENABLED` | Enable JWT enforcement (`0` bypasses; resolves anonymous claims). | `1` | `0/1`, `true/false`; default `1` (enabled) |
| `KEYCLOAK_ISSUER` | Expected token `iss` (browser-facing Keycloak URL). | `https://keycloak.pole.local/realms/pole-ai` | URL ending `/realms/<realm>` |
| `KEYCLOAK_JWKS_URL` | JWKS endpoint used to verify RS256 signatures. | `http://pole-ai-keycloak:8080/realms/pole-ai/protocol/openid-connect/certs` | URL to the realm `certs` endpoint |
| `KEYCLOAK_CLIENTS` | Comma-separated allowed `azp` clients. | `pole-fe,pole-analyst,mcp-server` | client IDs, comma-separated |

### Temporary access / magic link (`app/pole_api/src/core/config.py`) — implemented (Phases 2–4 of `docs/app/keycloak`)

> These variables back the Keycloak temporary magic-link access feature (see `docs/app/keycloak`,
> Phases 1–4 ✅ DONE). `KEYCLOAK_ADMIN_*` are supplied by the `pole-api-admin` confidential client
> service account (secret from a Helm Secret); `TEMP_ACCESS_*` are consumed by
> `app/pole_api/src/core/temp_access.py`.

| NAME | DESCRIPTION | EXAMPLE | POSIBLE VALUES |
|---|---|---|---|
| `KEYCLOAK_ADMIN_CLIENT_ID` | Confidential `pole-api-admin` client id used by the Keycloak admin client (create/disable users, verify-email). | `pole-api-admin` | confidential client id |
| `KEYCLOAK_ADMIN_CLIENT_SECRET` | Secret for the `pole-api-admin` service account (from a Helm Secret, not the realm JSON). | `***` | secret string |
| `KEYCLOAK_ADMIN_ISSUER` | Token issuer for the admin client client-credentials grant. | `http://pole-ai-keycloak:8080/realms/pole-ai` | realm issuer URL |
| `TEMP_ACCESS_COOLDOWN_S` | 14-day cooldown between temp-access requests for the same email (Redis `temp:req` TTL). | `1209600` | seconds; default 14d |
| `TEMP_ACCESS_WINDOW_S` | 2-hour activated window for a temp user (Redis `temp:active` TTL; aligns with 2h token `exp`). | `7200` | seconds; default 2h |
| `TEMP_ACCESS_TOKEN_TTL_S` | TTL of a pending magic-link token (Redis `temp:token` TTL). | `86400` | seconds; default 24h |
| App→role map | Per-app temporary role assignment (`pole-fe`→`fe-user`, `pole-analyst`→`analyst-user`), enforced from token `azp`. | `pole-fe:fe-user,pole-analyst:analyst-user` | comma-separated map |

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