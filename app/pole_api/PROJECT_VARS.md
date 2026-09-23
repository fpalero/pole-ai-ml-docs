# Project Variables: pole_api

## Ticket Counter
- **Last ticket number**: 141

> Docs-unified: incoming `feature/PAIML-POLE-API-099-reviewer-leftovers` counter was 99 (older, 099 era); superseded, MAX 111 kept (099 file keep-both merged: 4-item bundle canonical + HEAD trimmed variant noted).

> Anomaly note (reconciliation): 95 is consumed by adopted ticket PAIML-POLE-API-095
> (canonical file `phase-30-chatbot-turn-budget/PAIML-POLE-API-095.md`, merged in
> pole-ai-ml-docs#26 — NOT duplicated in this PR; see PLAN_PHASE_29 adoption note).
> 96/97 created by this PR. Counter rebased onto develop post-#26 (95 live) → 97.
<> 98 = `phase-31-base-image-hash/PAIML-POLE-API-098.md` (merged #28).
> 99 = `phase-29-staging-qa-followups/PAIML-POLE-API-099.md` (reviewer leftovers from pole-ai-ml#253/#254: test-double timeout + fallback hint + None-safe blank check + ENV_VARS rows; HEAD trimmed variant scoped to timeout test double only — keep-both merged, 4-item bundle canonical).
> 100 = `phase-32-english-only/PAIML-POLE-API-100.md` (parallel session
> pole-ai-ml#257 code + pole-ai-ml-docs#31 docs, both merged — reserved, untouched here).
> 101 = `phase-29-staging-qa-followups/PAIML-POLE-API-101.md` (salvage of
> closed docs #29 items 2–4; #29 item 1 done via pole-ai-ml#259 + docs #30).
> 102 = `phase-29-staging-qa-followups/PAIML-POLE-API-102.md` (gate-3 residual bundle). Same branch salvages the two 101-item-4 ENV rows missed by docs #32.
> 103 = `phase-29-staging-qa-followups/PAIML-POLE-API-103.md` (in-flight tool grace on turn-deadline expiry, option A; reserved parallel branch `feature/PAIML-POLE-API-103-inflight-tool-grace`).
> 104 = `phase-33-test-collection-hygiene/PAIML-POLE-API-104.md` (gate-hygiene: duplicate pytest basename test_temp_access_purge, test-only; reserved parallel branch `feature/PAIML-POLE-GATE-HYGIENE-API104-FE14`).
>
> Backlog gap closes from closed-but-unmerged docs PRs (landed in develop side of this unification):
> 088 = `phase-29-chat-hardening/PAIML-POLE-API-088.md` (never-echo raw JSON for unknown block types — FUTURE hardening; docs PR #19).
> 089 = `phase-29-chat-hardening/PAIML-POLE-API-089.md` (coach signal repo injection for `*_test` isolation — FUTURE hardening; docs PR #19).
> 090 = `phase-30-chatbot-resilience/PAIML-POLE-API-090.md` (empty-reply recovery + RAG picture blocks; note: RAG-picture portion superseded by API-106/109 image-registry; docs PR #20).
> 105 = `phase-29-staging-qa-followups/PAIML-POLE-API-105.md` (staging-gate harness: E2E_FAKES unset for coach-flow integration test; reserved by parallel branch, landed via COACH side).
> 106 = `phase-34-unified-images/PAIML-POLE-API-106.md` (unified image endpoint via path-hash; docs PR #42; COACH side notes parallel branch `feature/PAIML-POLE-API-106-unified-images-docs` commit 12d096f).
> 107 = `phase-29-staging-qa-followups/PAIML-POLE-API-107.md` (analyst turn fail-safes: terminal fallback status + deterministic disclaimer).
> 108 = `phase-29-staging-qa-followups/PAIML-POLE-API-108.md` (data-backed progress matrix tool + deterministic assembly).
> 109 = `phase-35-rag-image-blocks/PAIML-POLE-API-109.md` (deterministic RAG image block synthesis — query_pole/biomechanics/calisthenics/psicology; docs PR #43).
> 110 = `phase-29-staging-qa-followups/PAIML-POLE-API-110.md` (coach catalog stores: trick_catalog Mongo collection + separate catalog RAG).
> 111 = `phase-29-staging-qa-followups/PAIML-POLE-API-111.md` (analyst output-contract enforcement: progress routing + drills emission + tool hygiene).
> 112 = `phase-36-free-text-trick-extraction/PAIML-POLE-API-112.md` (deterministic free-text trick extraction in `_build_state`).
> 113 = `phase-36-free-text-trick-extraction/PAIML-POLE-API-113.md` (progression catalog-first routing: QUERY_DOMAINS + P4 prompt).
> 114 = `phase-36-free-text-trick-extraction/PAIML-POLE-API-114.md` (answer shaping "what next" + UC coverage incl. bank #27).
> 115 = `phase-37-coach-grounding-regression/PAIML-POLE-API-115.md` (coach grounding regression: video resolution + guarded delegation).
> 116 = RESERVED parallel lane `phase-38-coach-routing-residuals/PAIML-POLE-API-116.md` (supergraph routing residuals; unmerged side branch — not consumed here, no collision).
> 117 = `phase-39-staging-gate-residuals/PAIML-POLE-API-117.md` (explicit unknown-trick reply on query-graph path; Phase 36 gate batch-1 Q3).
> 118 = `phase-39-staging-gate-residuals/PAIML-POLE-API-118.md` (M-code to metric-name mapping pre-metric_deep_dive; Phase 36 gate batch-3 Q9).
> 119 = `phase-40-pr-checks-gate/PAIML-POLE-API-119.md` (BE PR checks gate + inline review-merge auto-flow; requested as 117 but 117/118 consumed by Phase 39 staging-gate residuals, counter at 118 → max+1; Phase 40 since 39 taken, 38 reserved by parallel 116 lane).
> 120 = `phase-41-pr-checks-gate-workflow-run/PAIML-POLE-API-120.md` (BE PR checks gate + workflow_run-triggered review-merge, user-confirmed "option C": test-jobs-only be-checks, no inline review job; requested as 117 in phase-39-pr-checks-gate but 117/118 consumed by Phase 39 residuals, 119 by Phase 40 inline design, counter at 119 → max+1; Phase 41 since 39/40 taken).
> 121 = `phase-39-staging-gate-residuals/PAIML-POLE-API-121.md` (carry raw unknown-trick mention into `_build_state`, 117 enabler; code lane requested 119 but 119 consumed by Phase 40 inline design, counter at 120 → max+1; Phase 39 third ticket).
> 124/125/126 = `phase-42-coach-gate-25/` residuals (post-PR-#322 staging run
> `sample5-e743e61-20260912-083119`, 13/25 → 3 classes): 124 = FE renderer +
> image (PR-01..05, TP-05); 125 = prompt/tool-selection RAG grounding
> (TP-01/03, IN-02/03); 126 = WS per-turn wall-clock guard (VA-02/05).
> 127 = `phase-42-coach-gate-25/PAIML-POLE-API-127.md` (gate-25 backend regression fix: terminal fallback flag + grounding lazy-fetch + metric_matrix contract; 11 failing tests from PR #322).
> 128 = `phase-42-coach-gate-25/PAIML-POLE-API-128.md` (upload-dropzone spec timeout flake: mock File.size instead of 501MB allocation).
> 133 = `phase-42-coach-gate-25/PAIML-POLE-API-133.md` (131 review nits bundle, non-blocking: per-line ruff suppressions + .env.example opt-ins + FakeJobRunner mirror + _seed_allowed hardening).
> 129/130/131/132 = `phase-42-coach-gate-25/` SAMPLE-5 gate-fix batch (post-run `sample5-647d57e-20260921-205203`, 15/25 RED → 4 independent follow-ups, none block each other): 129 = analyst ReAct sub-budget deadlock, raise `agent.run` `max_turn_seconds` 120→≤240s below WS guard 300s (VA-05/VA-02); 130 = `assertRendering` broken-image false positive on `loading="lazy"` images — probe after viewport/decode, not before fetch (VA-04/TP-03/TP-05/IN-02); 131 = readiness seed state missing measurements — seed mirror extracted 0 frames → truthful no-metrics reply vs spec:597 retrieval-with-hits (RE-01/02/03/05, RE-04 stays green); 132 = `ensureCoachSession` `waitForURL` bootstrap flake — retry on navigation timeout only, assert destination URL (TP-04).
>
> Anomaly note (docs-unified reconciliation): MAX counter 111 wins (develop side was 109). No numbers skipped in 103–111; 103/104 reserved meanings from both sides kept above.
> Docs-unified: incoming `feature/PAIML-POLE-DOCS-028-026-phase-docs-commit` counter was 87 (older); superseded, MAX 111 kept.
> Docs-unified: incoming `docs/PAIML-POLE-API-083-coach-insights-positives` counter was 83 (older, 083 era); superseded, MAX 111 kept (083 file already present).
> Docs-unified: incoming `feature/PAIML-POLE-API-099-reviewer-leftovers` 98/99 note (98 base-hash, 099 reviewer leftovers) already covered above; superseded, MAX 111 kept.
> 134–137 = `phase-42-coach-gate-25/` iter-3 follow-ups (gate RED 19/25, user-confirmed docs-first): 134 = readiness tiered contract (T1/T2/T3) + RE-02 session-resolution; 135 = blank-retry on ABANDONED turns (VA-05/VA-02); 136 = deterministic readiness retrieval (RE-04); 137 = harness real-session discovery + fake seed-measurements revert (code PR #332).
> 138–139 = `phase-42-coach-gate-25/` local-k3s training-slice seeding (user-confirmed docs-first, NO mocks): 138 = training-flow seeding run (cleanup 4 analyst-seeded videos, 3 classes × 67 real clips 21/25/21, median-bounds phase frames handspring/shouldermount only, extract/process/embed + LSTM + cohort signals); 139 = `overall_score` computation + persistence (zero writers today → mean-of-scores formula, worker write + backfill, empty → None).
> 140–141 = `phase-42-coach-gate-25/` local SAMPLE-5 gate 21/25 follow-ups (run `20260923-205700`, user-confirmed docs-first, deterministic only — grounded-summary explicitly REJECTED): 140 = md-first structural enforcement in shaping (drop whitespace-only md + prepend synthesized per-flow header, prompt prose-first line, unit tests); 141 = RE T2/T3 tier-appropriate spec assertions (test-only, tier shapes replace "matrix has data rows", T1 unchanged).
