# Ticket: PAIML-POLE-API-079

## Title
[Application] Analyst chatbot tool `progress_trend` — metric trend across all sessions

## Description
Phase 26 (PLAN_PHASE_26.md), tool #6. Answers "am I plateauing on <metric>?" by returning the
metric's 0–100 score across ALL analyzed videos of the same trick, ordered by `analyzed_at`,
together with per-step deltas. Extends the Phase 24 baseline resolution into a chain traversal
over the video's own analysis history (never cross-trick).

## What to Do (Implementation Steps)
- [ ] Repo: helper to walk the same-trick history chain — from the current video, follow
      `find_baseline` repeatedly (collecting each doc's `analyzed_at` + numeric `scores` via the
      Phase 24 `numeric_scores`), or a single indexed query on `(trick_label, analyzed_at)`
      ordered ascending. Return the ordered series; stop at the first gap.
- [ ] `AnalystFacade.progress_trend(video_id, metric=None)` — validate id; no comparable history →
      structured "no prior sessions yet"; otherwise return per-session
      `{video_id, analyzed_at, scores}` and, when `metric` is given, the filtered per-metric series
      + `delta_pct` between consecutive sessions (reuse `compute_metric_deltas` semantics per step).
- [ ] Cap the series (most recent N sessions, e.g. 10) to keep the LLM payload small; include
      `hint_to_agent` for a trend table / sparkline-like summary.
- [ ] Register `ToolSpec(name="progress_trend", mode="sync", ...)` in `analyst_chatbot/tools.py`,
      params `{video_id: string (required), metric: string}`.
- [ ] Add one line to `ANALYST_SYSTEM_PROMPT` tool list.
- [ ] Tests: chain traversal (monotonic / gaps), per-metric filtering, single-session edge case
      (no baseline found → structured "no prior sessions yet", NOT a 1-session trend),
      facade errors, tool registration.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Series is strictly same-trick and ordered by `analyzed_at`; gaps stop the chain (no invented
      intermediate sessions).
- [ ] Never raises to the WS; structured error when there is no comparable history.
- [ ] `pixi run test-api` green; coverage ≥ 80% maintained.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)

## Dependencies
- **Blocks**: None
- **Blocked By**: Phase 24 (`find_baseline`, `numeric_scores`, `compute_metric_deltas`); aligns
  with PAIML-POLE-API-074 baseline resolution

## Estimated Effort
- [M]
