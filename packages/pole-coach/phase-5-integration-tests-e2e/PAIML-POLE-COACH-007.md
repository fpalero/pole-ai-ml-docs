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

## Bank approval (2026-09-08)

- **Verdict:** user-approved as-is, no edits. Bank copied verbatim (no question
  reworded) to `coach-150q.bank.json` (same folder as this ticket — the bank is
  this ticket's core artifact).
- **Scope:** 150 English-only questions, 30 per flow — `video_analysis`
  (`COACH7-VA-01..30`), `progress` (`COACH7-PR-01..30`), `training_plan`
  (`COACH7-TP-01..30`), `injury` (`COACH7-IN-01..30`), `readiness`
  (`COACH7-RE-01..30`). Shape per entry: `id`, `flow`, `question`,
  `expected_blocks`, `rag_domains`, `requires_disclaimer`.
- **Pass threshold:** >=27/30 per flow.
- **Run environment:** staging `ipsf-server`, `*_test` DBs only.
- **Required artifacts:** full transcript + LLM-judge report attached to the run
  report; gate verdict per this ticket's DoD.
- **Pointer:** [`coach-150q.bank.json`](./coach-150q.bank.json).

## Gate run 1 (2026-09-08) — aborted on systematic signal

- **Verdict:** RED. 14/14 `video_analysis` (VA) turns failed; run aborted on the
  systematic signal (no point burning the remaining flows). Wall-clock ~27 min
  (probe 19:25–19:31Z, run 19:32–19:59Z). 0 retries — systematic, not flaky.
  Worktree verified clean afterwards; the run modified no code.
- **Probe GREEN:** live OpenRouter `deepseek-v4-flash` turn — 5× HTTP 200,
  114.5 s wall, status ok, markdown-first blocks rendered, 9 successful
  `tool_calls`. No stub, no bare LLM. Chat shell renders (077 fix present).
- **Topology deviation (SAFETY-CRITICAL):** the staging `pole-api` deployment
  is wired to the PROD DBs (`pole_api`, `skeleton_data`, `analysis_db`) — the
  literal remote-backend path would have touched prod. The run used the
  compliant equivalent instead: local backend + FE built from the 007 worktree,
  data plane = staging Mongo via `ipsf-server` port-forward, `*_test` DBs only,
  `*_test` suffix guard passed. **Recommendation (noted, not created):** open a
  ticket for a staging deployment DB-wiring review.
- **RAG caveat:** local RAG domain DBs were unseeded, so the
  `query_pole` / `biomechanics` / `calisthenics` tools errored (caught, empty
  hits). Answers were metric-grounded, not RAG-hit-grounded. Options for the
  record: seed `POLE_RAG_DATA_DIR` (staging `/data/rag` is 1.1G) or accept
  metric-only grounding in judge review.
- **Failure modes:** A — 7× turn exceeded the 150 s budget (server likely still
  reasoning; live p50 114 s, tails 25–52 s); B — 6× multi-md assertion defect
  despite rendered answers; C — 1× VA-09 missing `video_segment` block (agent
  behaviour, needs judge review). Fix: A+B addressed in the spec (in progress
  on the 007 branch); full-150 estimate ~5 h+ at current pace.
- **Artifacts:** `app/pole_analyst/test-results/coach-150q/probe-20260908-1925/`
  + `full-20260908-1932/` (in the 007 worktree, gitignored — not committed).

## Gate run 2 — SAMPLE-5 retry (2026-09-08): RED 0/25, harness session lifetime

- **RUN_ID:** `sample5-retry-20260908-222654`.
- **Verdict:** RED — 0/5 per flow against the 5/5 bar. 2 passed / 26 failed,
  setup+seed turns only; execution 18.8 min; 0 retries (deterministic harness
  failure — retrying identically cannot pass).
- **VA-01:** server-side graph timeout → fallback reply (transient-infra
  candidate). **VA-02:** hung turn + pymongo `_OperationCancelled` (staging
  port-forward stall; transient-infra candidate).
- **Other 23 (deterministic):** single setup login cannot span the >10-min
  sequential run (VA-01 3.8m + VA-02 6.0m); all later turns land on the login
  page (screenshot-proven). Fix in progress: per-turn re-auth + honest tally
  (asked-fixed counting).
- **Gate-fidelity quirk:** tally counted transcript rows (asked=2/0/0/0/0) —
  unrecorded turns invisible; fixed to count the asked set.
- **Artifacts:** `app/pole_analyst/test-results/coach-150q/sample5-retry-20260908-222654/`
  (worktree, gitignored); `/tmp/coach150q-sample5-retry-20260908-222654.log`.

## Gate run 3 — SAMPLE-5 retry2 (2026-09-09): RED 11/25

- **Verdict:** RED vs the 5/5-per-flow bar. Per-flow live turns: `video_analysis`
  4/5, `progress` 0/5, `training_plan` 1/5, `injury` 2/5, `readiness` 4/5 →
  **11/25 PASS**. Zero `unrecorded-turn` rows — the run-2 re-auth (per-turn
  login) + honest-tally (asked-set counting) fixes are verified. Retry budget
  spent (1/1): the first attempt died in Keycloak setup login on
  `ERR_NETWORK_CHANGED`; this retry ran clean. No per-turn retries left.
  Wall ~36 m (46 s setup-blocked attempt + 35.4 m retry).
- **Failing modes (14):** 3× turn-timeouts (VA-03, TP-03, RE-02 — transient
  family, UNRETRIED, need fresh budget); 11× missing-block / wrong-shape with
  `rag=false` — PR-01 no matrix ("only one session on file"); PR-02–05 matrix
  rendered without M-01..M-05 metric names; TP-02/04/05 bare markdown, TP-05
  "knowledge-base tools are currently offline"; IN-01/02/04
  `SAFETY_DISCLAIMER` regex miss, IN-02 "couldn't pull my technique library
  just now".
- **Key correlation:** `rag=false` on ALL 14 fails, `rag=true` on ALL 11
  passes — mid-run RAG flakiness (tools reporting "offline") is the likely
  common cause, not 14 independent model failures. Run-1 caveat stands: local
  RAG domain DBs unseeded — candidate root cause. Recommendation (noted, not
  created): seed from staging `/data/rag` (1.1G) before re-gate.
- **Rendering:** `img` 0/0 on all 25 turns — zero images rendered anywhere (no
  broken `src`s, but zero RAG visuals). `tables=3` (VA-01/VA-04), `tables=5`
  (RE-03), `cards=4` (TP-01) — all valued/titled where present.
- **Safety flag (follow-up ticket needed, NOT created):** deterministic
  `SAFETY_DISCLAIMER` is not enforced on the analyst path — IN-03/05 carry it
  (LLM-generated), IN-01/02/04 don't. Companion gap: block-contract-on-fallbacks
  (bare-md answers, nameless matrices pass through instead of a contract-shaped
  fallback).
- **Artifacts:** `app/pole_analyst/test-results/coach-150q/20260909-gate-retry2/`
  (worktree, gitignored).

## Gate run 4 — SAMPLE-5 staging-direct (2026-09-09): RED 5/25, stale staging image

- **RUN_ID:** `sample5-20260909-direct`.
- **Verdict:** RED vs the 5/5-per-flow bar. Per-flow: `video_analysis` 2/5
  (VA-01,02), `progress` 0/5, `training_plan` 2/5 (TP-02,03), `injury` 1/5
  (IN-03), `readiness` 1/5 (RE-04) → **5/25 live turns PASS**.
- **Live-turn quality:** all 5 PASS turns had answer + rendering + RAG OK;
  tables up to 4 rows, cards up to 4, zero broken images.
- **Wall / retries:** ~1.1 h wall. 1 retry spent: COACH7-SETUP seed died on
  harness `spawnSync python ENOENT` under npx-direct → retry with pixi python
  on PATH, PASS in 9.6 s.
- **Mode T — 7 turns never complete (@360 s):** staging `pole-api` logs
  `status=ABANDONED` on every one; `agent: unknown tool requested:
  metric_matrix`; repeated `coach LLM reply invalid` (JSON
  control-char/unterminated-string) → graph-level fallback reply that never
  reaches terminal status on the FE. Systematic backend defects, not transient.
- **Mode R — 13 completed-but-assert-fails:** PR-03 matrix names a real metric
  yet asserts fail; PR-04 no `.matrix-card`; TP-04/05 no `.drills-list`
  DESPITE successful `query_*` RAG calls; IN-01/02/04/05 missing
  `SAFETY_DISCLAIMER`; RE-01/02/03/05 bare-md zero-tool-calls.
- **HEADLINE — staging image STALE:** `unknown tool requested: metric_matrix`
  proves the deployed staging backend predates current develop (001–005 +
  fixes). Gate tested old code; verdicts provisional pending staging redeploy
  + re-run.
- **Recommended app follow-ups (NOT created):** (1) register/stop-hallucinating
  `metric_matrix` tool, (2) harden coach summary JSON parsing, (3) fallbacks
  must drive terminal FE status, (4) disclaimer + retrieval + block-contract
  enforcement on fallback paths, (5) harness python-PATH note.
- **Artifacts:** worktree
  `test-results/coach-150q/sample5-20260909-direct/` (transcript + judge,
  gitignored); `/tmp/coach150q-sample5.log` (75 KB).
