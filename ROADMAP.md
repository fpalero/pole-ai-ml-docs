# Implementation Roadmap — Pending Work & Implementation Order

> **Current as of:** 2026-08-31. Shared view of every project's pending phases and the recommended
> implementation order, considering blockers and inter-app dependencies.
> **Re-verify before starting work:** `docs/app/<project>/PLAN.md`, `docs/packages/<project>/PLAN.md`,
> and the live `git log` + `.opencode/state/` merge logs. Full phase/ticket inventory: `docs/DEVELOPEMENT.md`.

> **Status reconciliation note (2026-08-31):** phase tables reconciled against `docs/app/*/PLAN.md`,
> `PROJECT_VARS.md` counters, and verified code state.
> - **New ✅ DONE this pass:** `pole_api` **Phase 25** (classify-first, `-073`, commit `b321fda`
>   2026-08-24, merged `3a2fcf8`) and **Phase 26** (analyst coach tools `-074..-082`, commit `52234f7`
>   2026-08-27, tools in `app/pole_api/src/analyst_chatbot/tools.py`, tests present). Both are now
>   ✅ DONE and no longer pending.
> - **`infra` project** (CI/CD deploy pipeline, `docs/app/infra/`): counter 15 → **24**; 8 phase
>   folders (`phase-1-ghcr-build-push` … `phase-8-packages-logs`). Phases 1–2 largely landed in code
>   (`build-push.yml`, `deploy-prod.yml`, `deploy-staging.yml`, repo-dispatch deploy-dev), Phases 3–5
>   ticketed, and **Phases 6–8** (elastic-stack / pole-api-logs / packages-logs,
>   `PAIML-INFRA-016..024`) are new, ticketed, 📋 PLANNED (no ES/Filebeat refs in code yet).
> - **Historical context (2026-08-28):** `pole_api` Phases 21–24 ✅ and `pole_analyst` Phases 18–20 ✅
>   confirmed; `docs/app/keycloak/` introduced (Phases 1–4 📋 PLANNED, `PAIML-KEYCLOAK-001..012`).
> - `pola_agent` complete (0–7 ✅); `pole_fe` only Phase 10 (FUTURE) remains; `pole_analyst` only
>   Phase 19 `-066` (PARTIAL) + Phase 7 (deferred) remain.

---

## 1. Dependency map (why this order)

| Blocked phase | Blocked by | Blocker status |
| :--- | :--- | :--- |
| `infra` Phases 3–8 (DEV / STAGING+PROD / docs / elastic-stack / logs) | none | ✅ Unblocked |
| `keycloak` Phases 1–4 | none | ✅ Done (merged + QA-verified) |
| dev-ops CI phases 1–7 (unticketed) | none | ✅ Unblocked |
| `crew` Phase 1 (guardrails) | none | ✅ Unblocked |

> **Done chains (2026-08-24):** analyst Phase 18 `-063` (#117), Phase 19 `-064/-065` (#119/#118),
> Phase 20 `-068/-069` (#120). `pole_api` Phase 24 `-072` (#114), Phase 25 `-073` (merged `3a2fcf8`),
> Phase 26 `-074..-082` (`52234f7`). Historical chains in earlier passes.

---

## 2. Pending phases (by project)

### `pole_api` (backend) — counter: 82

| Phase | Name | Tickets | Status |
| :--- | :--- | :--- | :--- |
| 10 | Production hardening (Celery/k8s) | unticketed | 🟡 PARTIAL / FUTURE |

> **Done:** Phases 1–9, 11–26. Phases 25 (classify-first `-073`) and 26 (analyst coach tools
> `-074..-082`) confirmed ✅ DONE this pass (code-verified). Follow-ups from `-072` review recorded
> (peak `$isNaN` guard, fail-open cutoff docstring).

### `pole_analyst` (athlete-facing coach frontend) — counter: 69

| Phase | Name | Tickets | Status |
| :--- | :--- | :--- | :--- |
| 7 | Keycloak Auth (per-user library) | unticketed (candidate `-057`) | 🔒 FUTURE / DEFERRED |
| 19 | Stitch tabs parity round 2 | `-066` PLANNED (`-064/-065` ✅ · `-067` ❌ cancelado por PO) | 🟡 PARTIAL |

> **Done:** Phases 1–18, 20. Note: the Keycloak *login* now exists (deployed infra + auth guard); the
> deferred Phase 7 item is per-user library *scoping*. If a temp-access flow is needed in this app it
> is covered by the separate `keycloak` project.

### `pole_fe` (workflow-manager frontend) — counter: 12

| Phase | Name | Tickets | Status |
| :--- | :--- | :--- | :--- |
| 10 | Future — Chatbot FE + cluster selector | unticketed | FUTURE |

> **Done:** Phases 1–9 and 11.

### `pola_agent` (agent/chatbot package origin) — counter: 15

> **Complete:** Phases 0–7 all ✅ DONE. No pending phases.

### `keycloak` (temporary magic-link access) — counter: 12 — NEW

| Phase | Name | Tickets | Status |
| :--- | :--- | :--- | :--- |
| 1 | Keycloak realm, SMTP & custom login theme | `PAIML-KEYCLOAK-001..004` | ✅ DONE |
| 2 | pole_api temp-access orchestration (endpoint + Redis + activation) | `PAIML-KEYCLOAK-005..007` | ✅ DONE |
| 3 | Temp-user data isolation & expiry purge | `PAIML-KEYCLOAK-008..010` | ✅ DONE |
| 4 | Tests, docs & verification | `PAIML-KEYCLOAK-011..012` | ✅ DONE |

> **Done:** Phases 1–4 ✅ (PAIML-KEYCLOAK-001..012 merged into `develop`, QA-verified on the local
> cluster 2026-09-03). No pending keycloak phases.

> Temp access: custom Keycloak login theme offers Login / Get temporary access; Keycloak verify-email
> magic link; per-app role (`pole-fe`→`fe-user`, `pole-analyst`→`analyst-user`); Redis `temp:req`
> (14d cooldown) + `temp:active` (2h window); on expiry delete **all** resources the temp user created
> (option 2) and disable the user. Reuses `VideoDeletionService` / analysis cascade deletes.

### `crew` (CrewAI implementation engine) — counter: 6 — NEW

| Phase | Name | Tickets | Status |
| :--- | :--- | :--- | :--- |
| 1 | Guardrails (anti-infinite-loop) | `PAIML-CREW-001..007` | 📋 PLANNED |

> CrewAI-based multi-agent engine at `crew/` (top-level dev-tooling). Implements opencode tickets
> end-to-end: Developer → Reviewer → Tester → PR against `develop`. Phase 1 adds structural and
> algorithmic guardrails to prevent agent infinite loops: `max_iter`/`max_rpm` on agents, task
> validation functions, and explicit tool success states.

### `infra` (CI/CD deploy pipeline) — counter: 24

| Phase | Name | Tickets | Status |
| :--- | :--- | :--- | :--- |
| 1 | Helm Charts & Local Deploy (Foundation) | `PAIML-INFRA-001..003` | ✅ DONE (landed in code) |
| 2 | Build & Push to GHCR | `PAIML-INFRA-004..006` | ✅ DONE (landed in code) |
| 3 | DEV Auto-Deploy | `PAIML-INFRA-007..010` | 📋 PLANNED / ticketed |
| 4 | STAGING & PROD Pipelines | `PAIML-INFRA-011..012` | 📋 PLANNED / ticketed |
| 5 | Documentation & Health Verification | `PAIML-INFRA-013..015` | 📋 PLANNED / ticketed |
| 6 | Elasticsearch + Kibana foundation | `PAIML-INFRA-016..018` | 📋 PLANNED |
| 7 | Structured logging in pole_api | `PAIML-INFRA-019..021` | 📋 PLANNED |
| 8 | Structured logging in packages + Filebeat shipping | `PAIML-INFRA-022..024` | 📋 PLANNED |

> Phases 1–2 largely landed in code (`.github/workflows/build-push.yml`, `deploy-prod.yml`,
> `deploy-staging.yml`, repository_dispatch deploy-dev); Phases 3–5 are ticketed. Phases 6–8
> (`elastic-stack`, `pole-api-logs`, `packages-logs`) are new this pass — ticketed (`PAIML-INFRA-016..024`)
> but **not implemented** (no ES/Filebeat refs in `infrastracture/helm/` or `app/pole_api/src/core/`).

### Packages (`docs/packages/*`)

| Package | State |
| :--- | :--- |
| `pole_ml` | v1 complete; future-work items (multi-trick models, temporal smoothing) listed without plans/tickets |
| `pole_tools` | v1 complete (all CLI tools shipped); future items unticketed |
| `chatbot` | Complete (LangGraph agent + Ollama); no pending phases |
| `jobs` | v1 complete; future items (retry policies, DLQ) unticketed |
| `pole_crawler` | v1 complete; future items unticketed |
| `pole_crop` | v1 complete; future items unticketed |

### `dev-ops` (CI workflows) — counter: 0

| Phase | Name | Tickets | Status |
| :--- | :--- | :--- | :--- |
| 1 | CI Foundation (helpers + runner setup) | unticketed | ⏳ PENDING ANALYSIS |
| 2 | PR Workflow (`pr-tests.yml`) | unticketed | ⏳ PENDING ANALYSIS |
| 3 | Phase-Completion Workflow (`phase-tests.yml`) | unticketed | ⏳ PENDING ANALYSIS |
| 4 | Full-Suite Workflow (`full-suite-tests.yml`) | unticketed | ⏳ PENDING ANALYSIS |
| 5 | MediaPipe Dedicated Action (`mediapipe-tests.yml`) | unticketed | ⏳ PENDING ANALYSIS |
| 6 | Nightly Docs Workflow | unticketed | ⏳ PENDING ANALYSIS |
| 7 | Branch Protection, Secrets & Documentation | unticketed | ⏳ PENDING ANALYSIS |

> Verified against source tree: `.github/workflows/` contains only `cleanup-worktrees.yml` +
> `opencode.yml` — none of the planned CI workflows exist yet. Needs ticketing before work starts.
> Distinct from the `infra` deploy-pipeline project (GHCR/deploy), which is separately ticketed.

---

## 3. Implementation order (recommended)

### Tier 1 — New app features (parallel, unblocked)
1. **`keycloak` Phases 1→4** — ✅ **Complete** (temp-access end-to-end: realm/SMTP/theme → pole_api
   orchestration → data purge → tests/docs; `PAIML-KEYCLOAK-001..012` merged + QA-verified).
   No longer pending.
2. **`crew` Phase 1** — guardrails (anti-infinite-loop) for the CrewAI engine. Standalone
   dev-tooling improvement; no external blockers.

### Tier 2 — `pole_analyst` remaining
3. **`pole_analyst` Phase 19 `-066`** — plan auto-generation for detected trick (only open app ticket).

### Tier 3 — Cross-cutting infra (parallel anytime)
3. **`infra` Phases 3→8** — DEV auto-deploy → STAGING/PROD → docs → elastic-stack → pole-api logs →
   packages logs. Phases 1–2 already landed in code; re-verify status vs code before starting.
4. **dev-ops Phases 1→7** — CI foundation → PR gate → heavier workflows (unticketed; needs ticketing).

### Tier 4 — Deferred / future (no dates)
5. `pole_fe` Phase 10 — Chatbot FE + cluster selector.
6. `pole_api` Phase 10 — Production hardening.

---

## 4. Key blockers to communicate

- **No active blocker chains** — every ticketed pending phase is unblocked:
  `pole_analyst` 19 `-066`, `infra` 3–8. (`pole_api` Phases 25–26 and `keycloak` 1–4 are ✅ done.)
- `pole_analyst` Phase 7 (Keycloak per-user library) remains deferred; the *login* is already deployed.
- **Non-blocking follow-ups backlog (from 2026-08-23/24 reviews):** peak aggregation `$isNaN` guard
  (BE); fail-open cutoff docstring; extract shared search-bar component; stale-response race guard;
  modal a11y focus restore; sidebar `Coach` deeper route target.

---

## 5. Ticket counters (last ID per project)

| Project | Last ticket ID | File |
| :--- | :--- | :--- |
| `pole_api` | 82 | `docs/app/pole_api/PROJECT_VARS.md` |
| `pole_analyst` | 69 | `docs/app/pole_analyst/PROJECT_VARS.md` |
| `pole_fe` | 12 | `docs/app/pole_fe/PROJECT_VARS.md` |
| `pola_agent` | 15 | `docs/app/pola_agent/PROJECT_VARS.md` |
| `keycloak` | 12 | `docs/app/keycloak/PROJECT_VARS.md` |
| `infra` | 24 | `docs/app/infra/PROJECT_VARS.md` |
| `crew` | 7 | `docs/packages/crew/PROJECT_VARS.md` |
| `dev-ops` | 0 | `docs/dev-ops/PROJECT_VARS.md` |
| `pole_ml` | 1 | `docs/packages/pole_ml/PROJECT_VARS.md` |