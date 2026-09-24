# Ticket: PAIML-POLE-FE-016

## Title
Add remote (staging) mode to pole_fe Playwright harness

## Description
The `pole_fe` e2e harness is localhost-pinned and cannot target the live staging demo domain (the analyst harness already supports remote mode). Concrete gaps:
- `app/pole_fe/e2e/helpers.ts:6` hardcodes `export const API = 'http://localhost:8000'` — no env override.
- `app/pole_fe/playwright.config.ts` hardcodes `baseURL: 'http://localhost:4200'` and always boots the local `webServer` (FastAPI `AUTH_ENABLED=0` + `ng serve`), with no `E2E_USE_REMOTE_BACKEND` / `E2E_BASE_URL` support.
- No Keycloak auth `setup` project (the analyst has `e2e/auth.setup.ts` driven by `E2E_KEYCLOAK_*`).

Mirror the analyst harness (`app/pole_analyst/playwright.config.ts` + `e2e/auth.setup.ts`): `E2E_USE_REMOTE_BACKEND=1` skips the local webServer, `E2E_BASE_URL` overrides the browser base URL, `E2E_API_BASE` overrides the API origin used by `helpers.ts`, and `E2E_KEYCLOAK_URL/REALM/USER/PASS` drives an auth setup that hands a signed-in session (localStorage) to specs. Keep the local hermetic path (backend `AUTH_ENABLED=0` + FE bypass from FE-014/015) as the DEFAULT — remote mode is opt-in via env.

## Repository
`pole-ai-ml`

## Affected
- `app/pole_fe/e2e/helpers.ts` (API origin env override + optional bearer auth)
- `app/pole_fe/playwright.config.ts` (remote-mode env wiring + optional auth setup project)
- `app/pole_fe/e2e/auth.setup.ts` (NEW — mirror analyst; only runs in remote mode)

## What to Do (Implementation Steps)
- [ ] Step 1: `helpers.ts` — replace the hardcoded `API` const with `const API = process.env.E2E_API_BASE ?? 'http://localhost:8000'`; add optional bearer-token attachment for remote (read a token from the auth setup storage, if present)
- [ ] Step 2: `playwright.config.ts` — add `E2E_USE_REMOTE_BACKEND` / `E2E_BASE_URL` parsing; when remote + non-local base URL, skip the `webServer` entirely (mirror analyst's `SKIP_FE_SERVER` logic)
- [ ] Step 3: add `auth.setup.ts` (Keycloak login via `E2E_KEYCLOAK_*`, store token/session) registered as a setup project ONLY in remote mode
- [ ] Step 4: local default path unchanged (no env set → same hermetic behavior as today)

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pixi run fe-e2e` (local hermetic) still GREEN with no env set
- [ ] Remote run smoke works: `E2E_USE_REMOTE_BACKEND=1 E2E_BASE_URL=https://demo-ml-agent.duckdns.org E2E_API_BASE=https://demo-ml-agent.duckdns.org E2E_KEYCLOAK_URL=https://demo-ai-keycloak.duckdns.org E2E_KEYCLOAK_REALM=pole-ai E2E_KEYCLOAK_USER=dev E2E_KEYCLOAK_PASS=dev npx playwright test health.spec.ts` reaches the staging origin (no `localhost:8000` hit)
- [ ] No production-code change under `app/pole_fe/src/`

## Dependencies
- **Blocks:** None
- **Blocked By:** None
- **Related:** PAIML-POLE-FE-014, PAIML-POLE-FE-015, PAIML-POLE-ANALYST-077 (analyst remote harness)