# PAIML-POLE-COACH-007 — FE 150-question integration test (5 flows x 30, English-only)

- **Status:** 📋 PLANNED
- **Blocks:** PAIML-POLE-COACH-006 (this test gates 006 — no 006 implementation until green)
- **Blocked By:** PAIML-POLE-ANALYST-077 (hidden-h1 drift fix, partial / in progress — must be merged first)

## Goal

Prove the coach end-to-end via Playwright on the `pole_analyst` FE page
(staging `ipsf-server`, `*_test` DBs only) before PAIML-POLE-COACH-006 starts:
150 different English-only questions — 30 per flow across 5 supergraph flows —
with per-flow structure + RAG-correctness assertions, full transcript, and an
LLM-judge column for human review.

Explicitly out of this run: `query` + `improve_trick` flows.

## Architectural context

- **Database:** `_testing` DBs only (`*_test` suffix guard; never prod).
- **Environment:** staging `ipsf-server` stack only; FE entry point is the
  `pole_analyst` page.
- **Runner:** Playwright (long run; transcript + judge report as artifacts).
- **RAG:** seeded domains per flow — assertions must prove RAG was actually
  called (not a bare-LLM answer).
- **Caching/performance:** full turn budgets honored (supergraph inherits the
  `PoleLangGraphAgent` wall-clock/blank hardening via the shared LLM path).

## Scope (in)

5 flows x 30 different questions each = 150 total, English-only:

| # | Flow | Questions | Per-flow assertion list |
|---|------|-----------|-------------------------|
| 1 | `video_analysis` | 30 | no-crash / no-blank / WS-contract-valid md-first blocks; `analysis_link` (video) present; RAG called against seeded video-analysis domain |
| 2 | `progress` | 30 | no-crash / no-blank / WS-contract-valid md-first blocks; `metric_matrix` present; RAG called against seeded progress domain |
| 3 | `training_plan` | 30 | no-crash / no-blank / WS-contract-valid md-first blocks; `drills` present; RAG called against seeded training-plan domain |
| 4 | `injury` | 30 | no-crash / no-blank / WS-contract-valid md-first blocks; `SAFETY_DISCLAIMER` present; RAG called against seeded injury domain |
| 5 | `readiness` | 30 | no-crash / no-blank / WS-contract-valid md-first blocks; retrieval-with-hits (readiness retrieval returns hits); RAG called against seeded readiness domain |

Cross-flow assertions for every one of the 150 turns:

- No crash, no blank reply.
- WS contract valid, markdown-first blocks render.
- RAG actually called against the seeded domain (fail if bare LLM).
- Turn recorded in full transcript + LLM-judge column for human review.

## Scope (out)

- `query` + `improve_trick` flows (explicitly excluded from this run).
- Non-English questions (follow-up: 10-language question set — 10 most used
  European languages — after 006).
- New features. Production data.

## Prerequisites / chain

1. Hidden-h1 drift fix merged (PAIML-POLE-ANALYST-077, currently partial / in progress).
2. Question bank generated (next step after this ticket shell).
3. User confirms bank before any run.
4. Long run → green → implement PAIML-POLE-COACH-006.
5. Follow-up after 006: 10-language question set.

Note: the bank itself will be generated next and confirmed by the user before
any run. Per-flow pass thresholds to be confirmed with the user at bank review.

## Tasks

- 7.1 Generate 150-question bank (5 x 30, English-only, no `query`/`improve_trick`) — user confirms bank.
- 7.2 Playwright run on `pole_analyst` FE page (staging `ipsf-server`, `*_test` DBs): ask 150/150.
- 7.3 Assert per-turn: no-crash / no-blank / WS-contract-valid md-first blocks + per-flow block (see matrix) + RAG-called proof.
- 7.4 Emit full transcript + LLM-judge column for human review; attach to run report.
- 7.5 Gate verdict → unblock PAIML-POLE-COACH-006 only on green.

## Acceptance

- [ ] 150/150 questions asked (30 per flow x 5 flows).
- [ ] Per-flow pass thresholds met (thresholds to be confirmed with user at bank review).
- [ ] Transcript + judge report attached for human review.
- [ ] Green → PAIML-POLE-COACH-006 unblocked.

## Verification

Playwright run artifacts (transcript + LLM-judge report) on staging; per-flow
block assertions per the matrix above. Then gate verdict per ticket DoD.

## Risks

- LLM nondeterminism → assert on blocks/structure + RAG-called proof, not prose.
- Long-run flake on staging → transcript preserves evidence for human review.
- Hidden-h1 drift (ANALYST-077) unmerged → blocks the run; do not start early.

## Definition of Done

150/150 asked, thresholds met, transcript + judge report attached, gate verdict
reported. Green unblocks 006. (`develop` → `main` stays user-owned; never opened
by the agent.)
