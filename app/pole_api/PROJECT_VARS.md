# Project Variables: pole_api

## Ticket Counter
- **Last ticket number**: 111

> Anomaly note (reconciliation): 95 is consumed by adopted ticket PAIML-POLE-API-095
> (canonical file `phase-30-chatbot-turn-budget/PAIML-POLE-API-095.md`, merged in
> pole-ai-ml-docs#26 — NOT duplicated in this PR; see PLAN_PHASE_29 adoption note).
> 96/97 created by this PR. Counter rebased onto develop post-#26 (95 live) → 97.
> 98 = `phase-31-base-image-hash/PAIML-POLE-API-098.md` (merged #28).
> 99 = `phase-29-staging-qa-followups/PAIML-POLE-API-099.md` (timeout test double, test-only).
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
>
> Anomaly note (docs-unified reconciliation): MAX counter 111 wins (develop side was 109). No numbers skipped in 103–111; 103/104 reserved meanings from both sides kept above.
> Docs-unified: incoming `feature/PAIML-POLE-DOCS-028-026-phase-docs-commit` counter was 87 (older); superseded, MAX 111 kept.
