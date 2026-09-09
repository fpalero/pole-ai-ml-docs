# Implementation Plan — `pole_coach` (LangGraph multi-agent virtual coach)

> Formal plan artifacts. The **phases and tickets are final and unchanged**: 6 phases,
> one big ticket per phase (`PAIML-POLE-COACH-001..006`), scope and dependency chain
> exactly as authored in `PLAN.md` / `ROADMAP.md` / the phase tickets. This document
> ADDS the integration test use cases, quality gates, and risk register on top of the
> reviewed tickets. Source of flow semantics: `MainState`, per-agent I/O schemas, and
> the 7 graphs (`video_analysis`, `progress`, `query`, `training_plan`, `injury`,
> `improve_trick`, `readiness`).

## 1. Architectural Context
- **Database:** no new DB for the coach core. Phase 1 ships a checked-in
  `packages/pole_coach/trick_catalog.json` + `images/` + curated `slug → trick_label`
  alias map (readiness reads catalog + best-historical metrics via injected provider).
  Phase 4 extends `analysis-db.athlete_profiles` (`experience_level`, `goals`,
  `days_per_week`, `injury_history`/`limitations`) and adds `biomech_features` angle
  keys, back-computable at read time — no re-extraction. Phase 6 reuses **Redis**
  (existing runtime dep): L1 exact-hash `tr:{src}:{tgt}:{sha}` (~30-day TTL,
  glossary-version + model-id keys) + L2 semantic near-match (MiniLM, cosine ≥0.95,
  placeholders-first). Integration runs only against `*_test` DBs (`_testing` suffix
  guard; never production).
- **Caching/performance:** catalog is a static runtime asset; the scraper is an offline
  CLI (honest UA, ≥1s delay, resume/skip, per-page `{"error"}` records). Nodes are
  sync, single LLM call each (one call + one schema-validation retry, mirrors
  `CoachService._ask`). RAG retrieval capped `k=3` per domain. Translation: English
  pays zero (gated); caps per field (query ~128, answer ~1024); Redis L1+L2 cache.
- **Scalability/resilience:** `pole_coach` stays framework-agnostic — `MetricsProvider`
  and `RAGProvider` are injected via `build_supergraph()`; **no direct Mongo imports**
  in `pole_coach` (pole_api injects facade-backed providers). Nodes never raise to the
  graph: typed errors → graph-level fallback → safe reply. Graphs are pure composition,
  each `compile()`-able standalone. Supergraph LLM intent router → conditional edges to
  the 7 graphs; low-confidence → `query` graph fallback (logged). Translator fails →
  English answer (never blank); provider down → existing `FALLBACK_ADVICE`; translator
  calls tagged in `llm_quota` (visible per-user spend).
- **External dependencies:** `polemovebook.com` (+ `sitemap.xml`; no auth; ToS/robots
  review required before any public deploy). LLM via `pole_chatbot.llm`
  (`OllamaLLM`/`build_llm`); RAG via `pole_rag.query.query` (pole, biomechanics,
  calisthenics, psychology). Phase 6 translator: local Ollama
  `hf.co/tencent/Hy-MT2-1.8B-GGUF:Q4_K_M` (pull once) / staging OpenRouter
  `tencent/hy-mt2-1.8b` — no torch in-process, no new serving runtime; Helm
  `translatorModel` value/ConfigMap lives in the **`pole-ai-ml-infra`** repo.
  Untouched surfaces: `chatbot`, `training_chatbot`, `pole_fe`.
- **Branch discipline:** `feature/PAIML-POLE-COACH-<NNN>-<slug>` cut from `develop`,
  PR vs `develop`, never push `main` / never open `develop→main` (user-owned). Separate
  track from in-flight `PAIML-POLE-API-101` / `PAIML-POLE-ANALYST-076`; rebase each
  worktree on latest `develop`. Rollback: tag `pole-ai-v1` on `origin/develop` in all
  three repos (`pole-ai-ml`, `pole-ai-ml-docs`, `pole-ai-ml-infra`).

## 2. Phased Breakdown (unchanged; tasks as authored in the tickets)
- **Phase 1 (A) — `PAIML-POLE-COACH-001`** (blocks 002,003,004,005):
  scaffold `packages/pole_coach` (Option A: `src/pole_coach/`, PYTHONPATH, no
  pyproject) + `beautifulsoup4` root dep; polemovebook scraper → versioned
  `trick_catalog.json` + `images/`; `slug → trick_label` alias map; pixi tasks
  `scrape-polecoach`/`test-polecoach`; unit tests (parse fixtures, schema, dangling
  refs, alias coverage).
- **Phase 2 (B) — `PAIML-POLE-COACH-002`** (blocks 003,004,005; blocked by 001):
  `CoachState` TypedDict + per-agent JSON schemas (`jsonschema`); `MetricsProvider` /
  `RAGProvider` protocols (+ fakes); 7 reusable nodes one file each (retrieve, pole,
  biomechanics, coach, metrics_retriever, intent_router, formatter); metrics contract
  = M-01…M-05 + known `FEATURE_NAMES` only; unit tests per node.
- **Phase 3 (C) — `PAIML-POLE-COACH-003`** (blocks 004,005; blocked by 002; catalog
  by 001): 7 graphs (`improve_trick`, `readiness`, `injury`, `training_plan`,
  `video_analysis`, `progress`, `query`), each `compile()`-able standalone; supergraph
  + `build_supergraph(metrics_provider, rag_provider)`; readiness gating
  (catalog-driven prereqs/regressions/progressions + latest+best-historical); unit
  tests (compile, ≥20 routing fixtures ≥90%, gating).
- **Phase 4 (D) — `PAIML-POLE-COACH-004`** (blocks 005; blocked by 003): supergraph
  behind `analyst_chatbot` (providers injected; WS contract + answer blocks
  unchanged); athlete profile extension end-to-end (BE schema/repo/controller + FE
  model/form/modal); **elbow/knee vertex-convention fix first**, then new joint angles
  (shoulder_flexion_l/r_deg, hip_angle_l/r_deg, spine_angle_deg) + risk/coach/prompt
  updates; unit tests (wiring, profile CRUD, golden-vector angles, legacy back-compute);
  `pole_api` Docker build imports `pole_coach`.
- **Phase 5 (E) — `PAIML-POLE-COACH-005`** (blocked by 004): 7 scripted chat scenarios
  (one per graph) against wired `analyst_chatbot`; `pole-analyst-e2e` additions
  (profile form, supergraph chat blocks, readiness/injury/plan); docs close-out
  (`PLAN.md` states → ✅ DONE, `docs/diagrams/pole-coach/` FLOW+CLASSES, RAG re-embed +
  manifest commit); phase-end QA gate on staging.
- **Phase 6 (F) — `PAIML-POLE-COACH-006`** (blocked by 001+002; extends 005's gate):
  `translator.py` (detect+translate entry, glossary-attached back-translation in
  formatter, Redis L1+L2, quota tagging, English fallback); glossary builder from
  catalog + static codes (versioned); `Settings.translator_model` + Helm
  `translatorModel` (**infra repo**); host pull (local) / OpenRouter model (staging);
  evals (ES round-trip, near-miss threshold, latency spike) + unit tests.

## 3. Defined Integration Test Use Cases
> Executed on `*_test` DBs only (`_testing` suffix guard, never prod); phases 1–3 need
> no live DB (catalog artifact + fakes); the phase-end gate runs on the staging stack
> (`ipsf-server`).

- **UC-01 (001) Scrape smoke:** `pixi run scrape-polecoach --help` → `pixi run
  scrape-polecoach` twice with one malformed fixture page; expect schema-valid
  `trick_catalog.json` (≥400 moves) + `images/<slug>.webp`, a per-page `{"error"}`
  record, no crash, and a second run that skips already-fetched slugs (resume).
- **UC-02 (001) Catalog gate:** fixture with a dangling `transitions-into` target + an
  alias map missing one classifier `trick_label`; expect validator rejection with
  non-zero exit naming the slug + label (e.g. `shoulder-mount → shoulder_mount`).
- **UC-03 (002) Retrieval node:** `retrieve(domain, query, k=3)` via mocked RAG →
  `hits[≤3]` with text + source + image meta; empty-hit mode returns zero hits without
  error.
- **UC-04 (002) Pole agent:** `pole_agent(trick_name="shoulder_mount")` (alias
  normalized, RAG mocked) → `{description, anatomy{muscles,joints,contact_points},
  conditioning[]}` schema-valid.
- **UC-05 (002) Biomech dual-mode:** pipeline input
  `{pole_context + metrics{M-01…M-05, percentiles, risk_flags, best_historical}}` →
  `metric_interpretation[]` non-empty; standalone `{free_question}` → `[]`.
- **UC-06 (002) Coach + formatter:** `{pole + biomech + free_question + profile/goal}`
  → `{advice, training_plan{weeks/days}|null, summary, recommendation[]}` →
  `final_blocks[]` of only known block types (`md/score_summary/drills/metric_matrix/
  quick_replies/video_segment/image`).
- **UC-07 (002) Router node:** `{free_question}` → `{intent, confidence}` one of the 7
  labels; low-confidence → `query` fallback.
- **UC-08 (003) Compile:** each of the 7 graphs imports + `compile()` standalone;
  `build_supergraph(metrics_provider, rag_provider)` wires conditional edges → `END`.
- **UC-09 (003) Route:** fixture set ≥20 queries → ≥90% routed to the expected graph;
  low-confidence → `query` fallback, logged.
- **UC-10 (003) Readiness gating:** catalog fixture (prereq + metric/joint gates) ×
  latest-vs-best-historical states → met / unmet-regression / progression-suggestion
  branches; unknown trick → "unknown trick" guidance, never fabricates.
- **UC-11 (004) Analyst wiring:** `/ws/analyst-chat` scripted turn via the supergraph
  (providers faked) → unchanged WS frame + existing blocks render; the full tool
  registry remains callable.
- **UC-12 (004) Profile round-trip:** PUT + GET athlete profile with the 4 new fields
  (`days_per_week` 1–7, enums for `experience_level`/`goals`) BE→FE; FE form
  validation enforces ranges.
- **UC-13 (004) Angles:** golden vectors prove the elbow/knee vertex convention (e.g.
  straight arm → ~180° at the elbow, not the shoulder); new keys
  `shoulder_flexion_l/r_deg`, `hip_angle_l/r_deg`, `spine_angle_deg` in
  `FEATURE_NAMES`/`compute_frame_features`/`phase_feature_stats`; legacy docs
  back-compute equals recompute (no re-extraction); `scan_risk_frames` bands
  re-validated.
- **UC-14 (004) Image:** `pole_api` Docker build imports `pole_coach` clean.
- **UC-15..21 (005) Seven chat scenarios** on staging `ipsf-server` `*_test` DBs
  (mocked LLM where deterministic, live where conversational): video_analysis,
  progress, query, training_plan, injury, improve_trick, readiness → expected blocks,
  no-blank, no-crash (assert structure, not prose).
- **UC-22 (005) Analyst E2E:** `pixi run pole-analyst-e2e` — new profile fields form,
  supergraph chat replies render, readiness/injury/plan answers. `_testing` DBs + fakes.
- **UC-23 (006) ES round-trip:** ES query → EN routing/retrieval → ES answer; trick
  names + M-codes + joint names intact (glossary via Hy-MT2 workflow); Redis L1+L2 hit
  verified.
- **UC-24 (006) Degradation:** translator/provider down → English answer /
  `FALLBACK_ADVICE`, never blank; calls tagged in `llm_quota`; English path pays zero;
  p95 within turn wall-clock budget.

## 4. Quality Gates
- **Phase start:** `pixi run crew-validate <phase-folder>` (dependency graph
  consistent) + `./scripts/cleanup-worktrees.sh`.
- **Per ticket (001..006):**
  1. Isolated worktree + `feature/PAIML-POLE-COACH-<NNN>-<slug>` cut from `develop`.
  2. Full phase scope + unit suites green (`test-polecoach`/`test-pole-coach`; 002/003
     `pytest packages/pole_coach`; 004 `test-api` + `test-chatbot`; 006 translation
     evals). Coverage ≥80% (repo policy).
  3. Push, PR vs `develop`, `/oc review`, CI green, merge. Dependents start only on
     MERGED + CI-green (lanes: 001→002→003→004→005; 006 after 001+002, lands last).
  4. Per-ticket DoD: integration aggregator smoke (`pixi run test-integration` behind
     `guard-testing-db.sh`) run and reported.
  5. `doc` incremental RAG refresh (`docs-rag-write`) + manifest commit on every merge.
- **Phase-end (005, extended by 006):** tester-owned staging QA gate on `ipsf-server`
  with `*_test` DBs only — M5 GREEN → handover for manual acceptance; M6 GREEN →
  report and stop. `develop→main` is **user-owned**, never opened by the agent.
- **Verification set:** `pixi run test-pole-coach` · `test-api` · `test-chatbot` ·
  `test-integration` · `pole-analyst-e2e` · `eval-coach-grounding`.

## 5. Risks and Mitigations
- **PMB ToS/copyright (001):** robots.txt/ToS may disallow AI bots; prose+images are
  copyrighted. **Mitigation:** confirm redistribution rights before any public deploy;
  honest UA + ≥1s delay; resume/skip; per-page `{"error"}` records; no
  credentialed/JS-gated endpoints.
- **PMB slug renames break transitions (001/003):** dangling-ref validator rejects;
  readiness returns "unknown trick" guidance, never fabricates.
- **LLM JSON drift (002):** `jsonschema` + one retry + typed error, never raise to the
  graph; graph-level fallback → safe reply.
- **Metric vocabulary drift (002/004):** M-01…M-05 contract enforced (reject unknown
  keys loudly) while histogram/facade advertise M-01…M-08 — the plan must enumerate
  which keys exist vs are gated so real histogram payloads do not crash a turn.
- **Provider protocol drift (002/004):** `MetricsProvider`/`RAGProvider` surfaces are
  greenfield; freeze shapes in `protocols.py` before graph composition.
- **Router misclassification (003):** low-confidence → `query` graph fallback + logged;
  ≥90% fixture gate on ≥20 queries.
- **Catalog alias gaps (003):** classifier `trick_label` without alias entry fails the
  coverage test; readiness never fabricates.
- **Angle-convention fix rewrites history (004):** `_ANGLE_JOINTS` currently measures at
  the proximal joint (shoulder/hip vertex). **Mitigation:** land the fix BEFORE new
  joints; golden-vector test; back-compute legacy docs at read time; re-validate
  `scan_risk_frames` bands / `_DEGREE_FEATURES` / `_joint_angle_description` / prompt
  glossary — do not carry thresholds over blindly.
- **FE validation ranges (004):** `days_per_week` 1–7, enums for
  `experience_level`/`goals` — validated both BE and FE.
- **LLM nondeterminism in E2E (005):** assert on blocks/structure, never prose.
- **Translation cache correctness (006):** near-miss pairs (`mount` vs `mount-flag`)
  must never share an L1/L2 entry (threshold eval); keys carry glossary version +
  model id; English path pays zero; caps sized per field.
- **Glossary staleness (006):** catalog updates must bust the cache — versioned keys.
- **OpenRouter micro-cost (006):** bounded by cache + caps; spend tagged in
  `llm_quota` and measured before any further optimization.
- **In-flight `-101`/`-076` coexistence:** `-004` touches the `analyst_chatbot` surface;
  separate track, rebase each worktree on latest `develop`, verify no file conflicts.
- **Rollback readiness:** `pole-ai-v1` tag must exist on `origin/develop` in all three
  repos before work starts.

### Flagged surface (advisory — does NOT change ticket scope)
- `biomech_features` lives in `app/pole_api/src/analysis/services/biomech_features.py`
  (tickets reference "pole_ml"); verify the "Phase-33 biomech" numbering.
- `AthleteProfileRepository` is in `analysis/repositories/analysis_repository.py`;
  profile controller in `analysis/controllers/profile.py`; `schemas.py` holds
  `AthleteProfile/Update` (height/weight only today).
- "17 tools" = 17 analyst tools + 4 RAG tools on the registry — state acceptance as
  "17 analyst + 4 RAG callable".
- RAG domain names: real tool key `query_psicology` (sic) → DB `psychology`;
  `RAGProvider` needs an explicit domain → `RAG_DB_BY_TOOL` map; decide on the typo.
- Task-name drift: tickets 001 use `scrape-polecoach`/`test-polecoach`; ROADMAP
  verification lists `test-pole-coach` — normalize at implementation (pole_rag
  precedent: `rag-seed`/`test-rag`).
