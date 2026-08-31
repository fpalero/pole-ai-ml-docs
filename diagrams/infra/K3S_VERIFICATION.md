# k3s Deployment Verification & Test Results

> Live validation of the **pole-ai** stack deployed on the local k3s cluster
> (`context: k3s-local`, Traefik ingress). Results from the tester run after the
> integration tests were made environment-configurable (commit `c93bdd6`).

## 1. Environment Status

| Pod | Status |
| :-- | :-- |
| `pole-ai-keycloak` | 1/1 Running |
| `pole-ai-mongodb` | 1/1 Running (7 restarts, recovered) |
| `pole-ai-pole-analyst` | 1/1 Running |
| `pole-ai-pole-api` | 1/1 Running |
| `pole-ai-pole-fe` | 1/1 Running |
| `pole-ai-redis` | 1/1 Running |

Ingresses (all HTTP, Traefik, port 80): `pole-fe.local`, `pole-analyst.local`,
`api.pole.local`, `keycloak.pole.local`.

| Endpoint | Result |
| :-- | :-- |
| `http://api.pole.local/health` | 200 `{"status":"ok"}` |
| `http://pole-fe.local` | 200 (`PoleFe`) |
| `http://pole-analyst.local` | 200 (`Pole AI Coach`) |
| `http://keycloak.pole.local/realms/pole-ai` | 200 (issuer served) |

Keycloak realm `pole-ai` enabled; clients `pole-fe`, `pole-analyst` (public,
direct grants, redirectUris pinned to `*.pole.local`) and `mcp-server`.

MongoDB + Redis reached via `kubectl port-forward` on `27017` / `6379`.

## 2. Integration Test Results (pytest, against k3s services)

| Suite | Result |
| :-- | :-- |
| `test_analysis_enriched_list_integration` | 3 passed |
| `test_analysis_pose_frames_integration` | 5 passed |
| `test_coach_flow_integration` | 5 passed, **3 failed** (pre-existing, see below) |
| `test_process_integration` + `test_upload_integration` | 3 passed |
| `packages/chatbot` `test_ws_integration` | 1 passed |
| `packages/pole-train-model` `test_cli_integration` | 4 passed |

**Total: 21 passed / 3 failed** (3 pre-existing failures — confirmed identical
on the original code before the env-configurability changes).

### Known failures (pre-existing, fixed)

1. `test_get_coach_insights_serves_computed_data` — 404: `GET /coach-insights`
   did not serve persisted insights.
2. `test_coach_summary_generate_then_cached` — 503: coach summary LLM path
   popped from an empty `FakeLLM` script.
3. `test_llm_down_503_but_insights_still_served` — 503 on summary expected, but
   follow-up insights GET returned 404 (same root cause as #1).

All three fixed: `CoachService.insights()` now serves the rule-based insights
the analyze worker persists (`analysis-db.coach_insights`, Q5=C) as the
canonical cache, `CoachService._get_llm` builds `OllamaLLM` directly (the
`build_llm` import was stale), `CoachInsightOut` gained `metric`, and the
integration test's `SUMMARY_REPLY` was updated to the coach-prompt-v2 schema.

## 3. Exploratory Live Tests (deployed k3s API)

15/15 PASS — malformed/empty/missing JWTs → 401; bad ObjectId, SQL-injection
path and unknown route → 404; `/health` public 200; JWKS certs 200; authorized
client token (`pole-fe`) 200; non-whitelisted client rejected; wrong password →
`invalid_grant`; method-not-allowed → 405; authorized reads (`/api/analysis/videos/summary`,
`/api/training/classes`) 200; token shape = access+refresh+expires_in=300.

## 4. Playwright E2E

Blocked at the time of this report by a Keycloak prerequisite (the Angular app
defaults to a Keycloak at `localhost:8090`, and the k3s `pole-analyst` client
pinned redirectUris to `pole-analyst.local`).

Resolved:
- Keycloak `pole-analyst` + `pole-fe` clients now accept `http://localhost:4200`
  redirects; `webOrigins` use exact origins (no `/*` wildcard — keycloak rejects
  the token exchange otherwise). Applied to the running realm and to the Helm
  chart (`analystClientRedirects` / `feWebOrigins` / `analystWebOrigins`).
- App keycloak defaults point at the k3s realm (`http://keycloak.pole.local`)
  instead of `localhost:8090` (`keycloak.factory.ts` + `assets/env.js`).
- The Playwright harness adds a `setup` project that logs into the realm once
  and shares `storageState`; the local e2e backend boots with `AUTH_ENABLED=0`;
  remote mode (`E2E_USE_REMOTE_BACKEND=1`) attaches direct-grant tokens to the
  API fixtures. Run via `pixi run pole-analyst-e2e` (with the `MONGODB_URI`/
  `SKELETON_DB`/`POLE_API_DB` env the task sets).

Status: the harness now boots and authenticates (33 tests collect). The
remaining per-spec failures are pre-existing app/test bugs (e.g. coach-insights
serving, pose-frames gallery) tracked against the fixes above.

## 5. Test Configurability (env vars)

Existing tests were made environment-configurable without changing local
defaults. Key vars:

| Var | Default | Purpose |
| :-- | :-- | :-- |
| `TEST_POLE_API_DB` / `TEST_SKELETON_DB` / `TEST_ANALYSIS_DB` | `*_testing` | Test DB names |
| `ITEST_VIDEO_ROOT` | repo `sources/videos` | Source videos root |
| `POLE_API_BASE` | `http://localhost:8000` | HTTP/WS integration API base |
| `CHATBOT_ITEST_MONGO_URI` / `REDIS_URL` / `SOURCE` / `APP_DB` / `SKELETON_DB` / `JOBS_QUEUE` | localhost defaults | Chatbot integration |
| `E2E_BASE_URL` | `http://localhost:4200` | Playwright base URL |
| `E2E_USE_REMOTE_BACKEND=1` | unset (boot local backend) | Skip local backend, target deployed API |
| `E2E_API_BASE` | `http://localhost:8000` | Direct-API fixtures base |