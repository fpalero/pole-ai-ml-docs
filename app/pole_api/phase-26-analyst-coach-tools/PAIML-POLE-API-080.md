# Ticket: PAIML-POLE-API-080

## Title
[Application] Analyst chatbot tool `focus_recommendation` — top-N focus areas for next session

## Description
Phase 26 (PLAN_PHASE_26.md), tool #7. Answers "what should I work on next?" by deterministically
ranking the top-N most deviant (metric, phase) pairs from the stored `detections` (abs z-score,
with a phase weight), returning each focus area with its supporting worst frames and the specific
biomech feature in play. The chat LLM phrases the final coaching language; the tool stays
deterministic (v1). Optional extension (documented, not implemented here): an LLM narrative via a
future `CoachService` action.

## What to Do (Implementation Steps)
- [ ] Pure helper `rank_focus_areas(detections, top_n=3, phase_weights=None)` — dedupe by
      `(metric, phase)` keeping the worst |z|, sort desc by |z| (optionally weighted by phase:
      execution > entry > exit), return top-N with the worst frame per area.
- [ ] `AnalystFacade.focus_recommendation(video_id, top_n=3)` — validate id + clamp `top_n`
      (1..5); structured error for unanalyzed video / empty detections; otherwise return
      `{video_id, trick_label, focus_areas: [{metric, phase, z_score, worst_frame,
      frame_second, count_of_deviations}], hint_to_agent}` — hint asks the agent to present the
      top areas as a priority list and suggest 1–2 concrete cues per area.
- [ ] Reuse the existing per-phase deviation grouping semantics (`CoachService._deviations_by_phase`
      — expose/reuse rather than duplicate; if it stays private, extract a small shared helper).
- [ ] Register `ToolSpec(name="focus_recommendation", mode="sync", ...)` in
      `analyst_chatbot/tools.py`, params `{video_id: string (required), top_n: integer}`.
- [ ] Add one line to `ANALYST_SYSTEM_PROMPT` tool list.
- [ ] Tests: pure ranking (dedupe, weights, top-N clamp, ties), facade (empty detections,
      not-analyzed), tool registration.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Ranking is deterministic and deduplicated by (metric, phase); top-N clamped to a safe range.
- [ ] Never raises to the WS; structured error when there is nothing to focus on.
- [ ] `pixi run test-api` green; coverage ≥ 80% maintained.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)

## Dependencies
- **Blocks**: None
- **Blocked By**: None (reads stored `detections`)

## Estimated Effort
- [S]
