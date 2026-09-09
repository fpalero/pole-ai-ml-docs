# Ticket: PAIML-POLE-API-108

## Title
Data-backed progress matrix tool + deterministic assembly

## Description
User-approved (2026-09-09, answers to six confirmation questions) follow-up to
the 007 gate evidence. Build the Option-A matrix as a REAL tool +
deterministic assembly — no LLM arithmetic, no invented drill IDs.

Locked decisions (user-approved):
1. **Compute/narrate split:** code computes numbers/gates/drill-candidates;
   LLM narrates the `assessment` sentence + picks one drill from candidates.
2. **NEW Mongo collection `progress_matrix`** storing per-(athlete, trick,
   video) snapshots `{percentiles M-01..M-05, ts, cohort_version}` appended on
   every completed analysis (append-only; never rewrite history).
3. **CONSTRAINED drill pick** from registry candidates — the LLM must not
   invent drill IDs.
4. This work is a **new ticket** (not 107).
5. **Update progress/readiness gate assertions** to the data-backed matrix as
   part of implementation.
6. **Sequencing:** 25 re-run first, 006 decision after, this ticket implemented
   on user approval (approval now granted).

`pole_coach` stays langchain-free; the tool lives on the `app/pole_api`
analyst path.

## Evidence (007 ticket gate runs)
Source: `packages/pole-coach/phase-5-integration-tests-e2e/PAIML-POLE-COACH-007.md`.

- Gate runs 3–4 (SAMPLE-5, 2026-09-09) surfaced nameless matrices / bare-md
  shaping and tool-vocabulary hallucination on the analyst path (notably the
  `metric_matrix` collision that caused the hallucination — see below).
  This ticket is the data-backed fix: a real tool with a load-bearing NAME
  plus deterministic rendering.

## What to Do (Implementation Steps)
- [ ] (1) **New collection `progress_matrix` + write path.** Create the
  collection storing per-(athlete, trick, video) snapshots
  `{percentiles M-01..M-05, ts, cohort_version}`. Append one snapshot on every
  completed analysis. Append-only — never rewrite history.
- [ ] (2) **New tool `get_progress_matrix(trick_label, video_id?)`.**
  NAME is load-bearing: never `metric_matrix` — that collision caused the
  hallucination. Lives on the `app/pole_api` analyst path (`pole_coach`
  untouched, stays langchain-free). Returns one row per metric M-01..M-05:
  `{metric, current_pct, prev_pct, baseline_pct, gate{required, met},
  drill_candidates[]}`. Numbers/gates/candidates are code-computed from stored
  snapshots; the LLM performs no arithmetic.
- [ ] (3) **Deterministic assembly.** The formatter / `convert_supergraph_blocks`
  builds the matrix block from tool data (deltas vs previous/baseline, gate
  met/not, drill links). The LLM writes only the `assessment` sentence + picks
  one drill from the candidates. Fallback template when data is missing:
  explicit "data unavailable" block, never a silent bare-md matrix.
- [ ] (4) **Update 25-gate progress/readiness assertions** to data-backed
  expectations (deltas vs previous/baseline, gate mapping to the catalog).
- [ ] (5) Re-run the affected test files green.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] (1) Matrix rows match stored snapshots exactly — no LLM arithmetic
  (asserted in tests).
- [ ] (2) Gates match the catalog (`required`/`met` per metric).
- [ ] (3) Drills resolve in the registry (every candidate ID exists; the pick
  is constrained to candidates).
- [ ] (4) 25-gate progress/readiness green on the data-backed assertions.

## Out of Scope (explicitly out — separate decisions pending)
- 107 fail-safes (terminal fallback frame + deterministic disclaimer —
  `PAIML-POLE-API-107.md`, separate ticket; reference, do not re-implement).
- Translation / 006 decision.
- FE redesign. Row-tap wiring is an FE follow-up if needed — noted, not
  implemented here.

## Integration Tests to Run (Local Verification)
- [ ] Tool unit test: `get_progress_matrix` returns exact snapshot-backed rows
  (current/prev/baseline + gate + candidates) for M-01..M-05.
- [ ] Assembly test: deltas, gate met/not rendering, and drill links come from
  tool data; missing-data case renders the explicit "data unavailable" block.
- [ ] 25-gate progress/readiness suite green on data-backed asserts.
- [ ] `pixi run test-api` (full task — must stay GREEN).

## Unit-Test Requirement
- [ ] Matrix rows asserted equal to stored snapshots (no LLM arithmetic in the
  path under test); gates asserted against the catalog; drill candidates
  asserted resolvable in the registry and the pick asserted within candidates.

## Dependencies
- **Blocks**: Nothing (re-gate of the 25 follows implementation).
- **Blocked By**: — (standalone; sequencing note: 25 re-run first, 006
  decision after — both outside this ticket).

## Estimated Effort
- [M]

## As-built deviations (implementation report)
1. Proceeded despite 2 dirty agent-doc files in main checkout (unrelated
   docs-landing edits; worktree cut from clean develop ref, fully isolated —
   no contamination).
2. 007 spec NOT edited from the 108 worktree (worktree isolation); proposed
   patch supplied for team-lead to apply on the 007 branch (progress
   data-backed asserts: get_progress_matrix called + progress_matrix block;
   readiness keeps retrieval-with-hits; FE pixel-mapping is noted FE
   follow-up). 150 questions untouched.
3. Drill registry is NEW static analyst-path registry (none existed);
   cohort_version=1 constant (no versioned cohort source — bump on methodology
   change).
4. Pre-existing failure observed, untouched:
   test_submit_analyze_submits_analysis_slice_job fails identically on clean
   develop (unrelated kwargs drift).
- HEAD 9d8b235? No — correct HEAD is 9d8bce7, branch
  feature/PAIML-POLE-API-108-progress-matrix-tool; 37/37 new tests,
  progress_matrix.py 95% coverage, 218 regression sweep green.
