# Ticket: PAIML-POLE-API-075

## Title
[Application] Analyst chatbot tool `cohort_percentiles` — athlete standing vs the cohort

## Description
Phase 26 (PLAN_PHASE_26.md), tool #2. Adds a sync `cohort_percentiles` chatbot tool answering
"where do I stand vs the cohort on each metric?" Per analyzed metric, return the athlete's 0–100
score, the cohort min / median / max across all analyzed videos of the same trick, and the athlete's
percentile rank. Reuses `AnalysisHistogramRepository.max_scores_by_trick` (Phase 24) and the
stored `scores` map; adds a score-distribution aggregation to the analysis histogram repo.

## What to Do (Implementation Steps)
- [ ] Repo: extend `AnalysisHistogramRepository` with a score-distribution read for a trick label —
      e.g. `score_distribution_by_trick(trick_label)` returning, per metric key, the full numeric
      score array (one aggregation, no N+1), mirroring `max_scores_by_trick`.
- [ ] Pure helper `cohort_percentile(value, distribution)`: exact percentile rank
      (`count(<= value) / count`); **exact-rank-only** (a decile fallback for small
      cohorts was considered in PLAN_PHASE_26 but rejected as a behavioral no-op:
      with fewer than 10 videos each bucket holds < 1 value).
- [ ] `AnalystFacade.cohort_percentiles(video_id)` — validate id, resolve the video's scored
      histogram (`z_mean`/`scores`), run the aggregation, compute per-key
      `{current, cohort_min, cohort_median, cohort_max, percentile}`. Structured `{"error": ...}`
      for unknown video / no scored analysis / **fully-empty cohort** (no other analyzed videos of
      the trick yet); keys without cohort data on SOME metrics are omitted (never fabricated).
- [ ] Compact agent-facing payload (cap at 8 metrics) + `hint_to_agent` telling the agent to
      surface "top X% on <metric>, bottom quartile on <metric>" phrasing.
- [ ] Register `ToolSpec(name="cohort_percentiles", mode="sync", ...)` in `analyst_chatbot/tools.py`
      (`ANALYST_TOOL_NAMES` + `register_analyst_tools`), params `{video_id: string (required)}`.
- [ ] Add one line to `ANALYST_SYSTEM_PROMPT` tool list.
- [ ] Tests: pure percentile helper (small/large cohorts, tie handling), repo aggregation, facade
      (missing cohort, not-analyzed), tool registration.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Percentile ranks are exact and deterministic; keys without cohort data omitted and a
      fully-empty cohort answered as a structured error.
- [ ] Never raises to the WS; structured errors for missing input/backend data.
- [ ] `pixi run test-api` green; coverage ≥ 80% maintained.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)

## Dependencies
- **Blocks**: None
- **Blocked By**: Phase 24 (`max_scores_by_trick`, merged)

## Estimated Effort
- [M]
