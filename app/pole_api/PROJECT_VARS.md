# Project Variables: pole_api

## Ticket Counter
- **Last ticket number**: 120

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
>
> Anomaly note (docs-unified reconciliation): MAX counter 111 wins (develop side was 109). No numbers skipped in 103–111; 103/104 reserved meanings from both sides kept above.
> Docs-unified: incoming `feature/PAIML-POLE-DOCS-028-026-phase-docs-commit` counter was 87 (older); superseded, MAX 111 kept.
> Docs-unified: incoming `docs/PAIML-POLE-API-083-coach-insights-positives` counter was 83 (older, 083 era); superseded, MAX 111 kept (083 file already present).
> Docs-unified: incoming `feature/PAIML-POLE-API-099-reviewer-leftovers` 98/99 note (98 base-hash, 099 reviewer leftovers) already covered above; superseded, MAX 111 kept.
