# Implementation Roadmap — Pending Work & Implementation Order

> **Current as of:** 2026-09-04. Shared view of every project's pending phases and the recommended
> implementation order, considering blockers and inter-app dependencies.
> **Re-verify before starting work:** `docs/app/<project>/PLAN.md`, `docs/packages/<project>/PLAN.md`,
> and the live `git log` + `.opencode/state/` merge logs. Full phase/ticket inventory: `docs/DEVELOPEMENT.md`.

> **Status reconciliation note (2026-09-04):** phase tables reconciled against `docs/app/*/PLAN.md`,
> `docs/packages/*/PLAN.md`, `PROJECT_VARS.md` counters, `git log` (through `53b5d27` 2026-09-04),
> and `.opencode/state/tickets-status.jsonl`.
> - **New ✅ DONE this pass:** `keycloak` **Phases 5–6** (Brevo SMTP `-013`, Stitch login restyle
>   `-014`; merges `#178`–`#189` 2026-09-02/03, QA-verified on the local cluster; Phase 6 awaits
>   USER manual testing + manual develop→main promotion) and `pole_fe` **Phase 12** (user menu +
>   logout via Keycloak end-session, `PAIML-POLE-FE-001` #192, merged `53b5d27` 2026-09-04).
> - **`infra` counter 24 → 25:** new ticket `PAIML-INFRA-025` (CI build-push guard: tag override must
>   run on develop, #190 merged `b172a55` 2026-09-03) filed under `phase-2-dev-auto-deploy/`.
>   Phase folders renamed/restructured (phase-1…phase-8 as listed below); Phases 3–8 still 📋 PLANNED.
> - **`crew` split:** `docs/packages/crew/` (engine guardrails+multi-repo, counter 9: Phase 1 PARTIAL
>   `001..008`, Phase 2 `009` MERGED #163) vs `docs/app/crew/` (LLM provider follow-ups, counter 12:
>   `009..012` in `phase-5-cli-model-cleanup/`; `010` #165 + `011` #170 MERGED, `012` OpenRouter pending).
> - **New project `pole_rag`** (multimodal RAG seeder, `docs/packages/pole_rag/`): counter 26,
>   Phases 1–5 📋 PLANNED (`PAIML-POLE-RAG-001..026`); no code yet (`packages/pole_rag/` absent).
> - **Historical context (2026-08-31):** `pole_api` Phases 25–26 ✅, `pole_analyst` Phases 18–20 ✅,
>   `pola_agent` complete (0–7 ✅); `pole_fe` only Phase 10 (FUTURE) remained before Phase 12 landed.

---

## 1. Dependency map (why this order)

| Blocked phase | Blocked by | Blocker status |
| :--- | :--- | :--- |
| `infra` Phases 3–8 (STAGING+PROD / security / docs / elastic-stack / logs) | none | ✅ Unblocked |
| `keycloak` Phases 1–6 | none | ✅ Done (merged + QA-verified; Phase 6 awaits user manual develop→main) |
| `pole_rag` Phases 1–5 | none (standalone CLI; Phase 5 consumes chatbot `ToolSpec` surface) | ✅ Unblocked |
| `crew` packages Phase 1 `-008` (Ollama integration) | local Ollama (`qwen3.8:27b`) reachable | ⏳ Blocked on Ollama env |
| `crew` app Phase 5 `-012` (OpenRouter) | none | ✅ Unblocked |
| dev-ops CI phases 1–7 (unticketed) | none | ✅ Unblocked |

> **Done chains (2026-09-02/04):** keycloak `-005..-012` (#178–#189), `-013` Brevo SMTP, `-014`
> Stitch login restyle; `infra` `-025` (#190 tag-override guard); `pole_fe` Phase 12 (#192).
> `crew` `-009` (#163 multi-repo) + `-010` (#165) + `-011` (#170) merged.
> Historical chains in earlier passes (analyst 18–20, `pole_api` 24–26).

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

### `pole_fe` (workflow-manager frontend) — counter: 13

| Phase | Name | Tickets | Status |
| :--- | :--- | :--- | :--- |
| 10 | Future — Chatbot FE + cluster selector | unticketed | FUTURE |
| 12 | User menu + logout (Keycloak end-session) | `PAIML-POLE-FE-001` | ✅ DONE (#192, `53b5d27` 2026-09-04) |

> **Done:** Phases 1–9, 11, 12. Only Phase 10 (FUTURE) remains.

### `pola_agent` (agent/chatbot package origin) — counter: 15

> **Complete:** Phases 0–7 all ✅ DONE. No pending phases.

### `keycloak` (temporary magic-link access) — counter: 14

| Phase | Name | Tickets | Status |
| :--- | :--- | :--- | :--- |
| 1 | Keycloak realm, SMTP & custom login theme | `PAIML-KEYCLOAK-001..004` | ✅ DONE |
| 2 | pole_api temp-access orchestration (endpoint + Redis + activation) | `PAIML-KEYCLOAK-005..007` | ✅ DONE |
| 3 | Temp-user data isolation & expiry purge | `PAIML-KEYCLOAK-008..010` | ✅ DONE |
| 4 | Tests, docs & verification | `PAIML-KEYCLOAK-011..012` | ✅ DONE |
| 5 | Brevo SMTP | `PAIML-KEYCLOAK-013` | ✅ DONE |
| 6 | Stitch pixel-perfect login restyle | `PAIML-KEYCLOAK-014` | ✅ DONE (impl + QA GREEN; awaiting user manual develop→main promotion) |

> **Done:** Phases 1–6 ✅ (`PAIML-KEYCLOAK-001..014` merged into `develop` via #178–#189,
> QA-verified on the local cluster 2026-09-03). No pending keycloak phases; do NOT close
> Phase 6 until the user confirms manual testing + develop→main promotion.

> Temp access: custom Keycloak login theme offers Login / Get temporary access; Keycloak verify-email
> magic link; per-app role (`pole-fe`→`fe-user`, `pole-analyst`→`analyst-user`); Redis `temp:req`
> (14d cooldown) + `temp:active` (2h window); on expiry delete **all** resources the temp user created
> (option 2) and disable the user. Reuses `VideoDeletionService` / analysis cascade deletes.

### `crew` (CrewAI implementation engine) — packages counter: 9 / app counter: 12

| Location | Phase | Name | Tickets | Status |
| :--- | :--- | :--- | :--- | :--- |
| `docs/packages/crew/` | 1 | Guardrails (anti-infinite-loop) | `PAIML-CREW-001..008` | 🟡 PARTIAL (code in `develop`; `-008` Ollama integration pending) |
| `docs/packages/crew/` | 2 | Multi-repo support (per-ticket repo routing) | `PAIML-CREW-009` | ✅ DONE (#163 merged) |
| `docs/app/crew/` | 5 | CLI / model cleanup + LLM providers | `PAIML-CREW-009..012` | 🟡 PARTIAL (`-009` condense prompts #163, `-010` #165, `-011` retries/RPM #170 MERGED; `-012` OpenRouter pending) |

> CrewAI-based multi-agent engine at `crew/` (top-level dev-tooling). Implements opencode tickets
> end-to-end: Developer → Reviewer → Tester → PR against `develop`. Note the numbering overlap:
> `packages/crew` `009` (multi-repo routing) and `app/crew` `009` (condense subagent prompts) are
> different tickets in different projects — check the path, not just the number.

### `infra` (CI/CD deploy pipeline) — counter: 25

| Phase | Name | Tickets | Status |
| :--- | :--- | :--- | :--- |
| 1 | GHCR build & push | `PAIML-INFRA-001..003` | ✅ DONE (landed in code) |
| 2 | DEV auto-deploy | `PAIML-INFRA-004..006` + `PAIML-INFRA-025` | ✅ DONE in code + 🟡 PARTIAL (`-025` tag-override guard #190 merged `b172a55`; re-verify DEV workflow vs code) |
| 3 | STAGING & PROD pipelines | `PAIML-INFRA-007..010` | 📋 PLANNED / ticketed |
| 4 | Security & notifications | `PAIML-INFRA-011..012` | 📋 PLANNED / ticketed |
| 5 | Documentation & health verification | `PAIML-INFRA-013..015` | 📋 PLANNED / ticketed |
| 6 | Elasticsearch + Kibana foundation | `PAIML-INFRA-016..018` | 📋 PLANNED |
| 7 | Structured logging in pole_api | `PAIML-INFRA-019..021` | 📋 PLANNED |
| 8 | Structured logging in packages + Filebeat shipping | `PAIML-INFRA-022..024` | 📋 PLANNED |

> `.github/workflows/` currently holds `build-push.yml`, `deploy-prod.yml`, `deploy-staging.yml`
> (+ `cleanup-worktrees.yml`, `opencode.yml`) — no `deploy-dev.yml` yet. Phases 6–8
> (`elastic-stack`, `pole-api-logs`, `packages-logs`) are ticketed but **not implemented**
> (no ES/Filebeat refs in `infrastracture/helm/` or `app/pole_api/src/core/`).

### Packages (`docs/packages/*`)

| Package | State |
| :--- | :--- |
| `pole_ml` | v1 complete; future-work items (multi-trick models, temporal smoothing) listed without plans/tickets |
| `pole_tools` | v1 complete (all CLI tools shipped); future items unticketed |
| `chatbot` | Complete (LangGraph agent + Ollama); no pending phases |
| `jobs` | v1 complete; future items (retry policies, DLQ) unticketed |
| `pole_crawler` | v1 complete; future items unticketed |
| `pole_crop` | v1 complete; future items unticketed |
| `pole_rag` — NEW (counter: 26) | 📋 PLANNED — 5 phases, `PAIML-POLE-RAG-001..026`, no code yet (`packages/pole_rag/` absent): Phase 1 scaffold/sources/dedupe/config (`001..008`), Phase 2 Marker extraction + atomic-table chunking (`009..011`), Phase 3 embeddings + Chroma multi-collection storage (`012..016`), Phase 4 CLI seed/reseed/query/inspect (`017..022`), Phase 5 chatbot tools `query_pole/calithenics/psicology/biomechanics` (`023..026`) |

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
1. **`keycloak` Phases 5→6** — ✅ **Complete** (Brevo SMTP `-013`, Stitch login restyle `-014`;
   `PAIML-KEYCLOAK-001..014` merged + QA-verified). Phase 6 awaits USER manual testing +
   manual develop→main promotion — do NOT close until the user confirms.
2. **`pole_rag` Phases 1→5** — multimodal RAG seeder CLI (scaffold → extraction/chunking →
   embeddings/Chroma → CLI → chatbot tools). Standalone, no external blockers; Phase 5 wires
   4 sync tools into `packages/chatbot`.
3. **`crew` app Phase 5 `-012`** — OpenRouter provider support. Standalone dev-tooling; no blockers.
4. **`crew` packages Phase 1 `-008`** — guardrails Ollama integration tests (needs local Ollama).

### Tier 2 — `pole_analyst` remaining
5. **`pole_analyst` Phase 19 `-066`** — plan auto-generation for detected trick (only open app ticket).

### Tier 3 — Cross-cutting infra (parallel anytime)
6. **`infra` Phases 3→8** — STAGING/PROD → security/notifications → docs → elastic-stack →
   pole-api logs → packages logs. Phases 1–2 landed in code (+ `-025` guard); re-verify DEV
   workflow vs code before starting.
7. **dev-ops Phases 1→7** — CI foundation → PR gate → heavier workflows (unticketed; needs ticketing).

### Tier 4 — Deferred / future (no dates)
5. `pole_fe` Phase 10 — Chatbot FE + cluster selector.
6. `pole_api` Phase 10 — Production hardening.

---

## 4. Key blockers to communicate

- **No active blocker chains** — every ticketed pending phase is unblocked except `crew`
  `-008` (needs local Ollama): `pole_analyst` 19 `-066`, `pole_rag` 1–5, `crew` app `-012`,
  `infra` 3–8. (`pole_api` Phases 25–26, `keycloak` 1–6, `pole_fe` 12 are ✅ done.)
- `pole_analyst` Phase 7 (Keycloak per-user library) remains deferred; the *login* is already deployed.
- **Keycloak Phase 6 is NOT closed** until the user finishes manual testing and promotes
  develop→main themselves.
- **Ticket-number overlap warning:** `PAIML-CREW-009` exists twice in different projects
  (`docs/packages/crew/phase-2-multi-repo/` = multi-repo routing ✅ vs
  `docs/app/crew/phase-5-cli-model-cleanup/` = condense prompts ✅) — always use the full path.
- **Non-blocking follow-ups backlog (from 2026-08-23/24 reviews):** peak aggregation `$isNaN` guard
  (BE); fail-open cutoff docstring; extract shared search-bar component; stale-response race guard;
  modal a11y focus restore; sidebar `Coach` deeper route target.

---

## 5. Ticket counters (last ID per project)

| Project | Last ticket ID | File |
| :--- | :--- | :--- |
| `pole_api` | 82 | `docs/app/pole_api/PROJECT_VARS.md` |
| `pole_analyst` | 69 | `docs/app/pole_analyst/PROJECT_VARS.md` |
| `pole_fe` | 13 | `docs/app/pole_fe/PROJECT_VARS.md` |
| `pola_agent` | 15 | `docs/app/pola_agent/PROJECT_VARS.md` |
| `keycloak` | 14 | `docs/app/keycloak/PROJECT_VARS.md` |
| `infra` | 25 | `docs/app/infra/PROJECT_VARS.md` |
| `crew` (packages) | 9 | `docs/packages/crew/PROJECT_VARS.md` |
| `crew` (app) | 12 | `docs/app/crew/PROJECT_VARS.md` |
| `pole_rag` | 26 | `docs/packages/pole_rag/PROJECT_VARS.md` |
| `dev-ops` | 0 | `docs/dev-ops/PROJECT_VARS.md` |
| `pole_ml` | 1 | `docs/packages/pole_ml/PROJECT_VARS.md` |