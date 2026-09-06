# Ticket: PAIML-POLE-API-084

## Title
[Coach] Make LLM-generated insights primary (remove rule-based short-circuit)

## Description
Phase 28. `app/pole_api/src/analysis/services/coach_service.py`: the LLM insight generation path already exists (`build_insights_prompt` + METRIC_GLOSSARY "never about numbers" persona), but the Q5=C rule-based path (`_rule_insights` → `coach_insights_service`) wins whenever the analyze worker already computed insights. This causes the Tips & Insights panel to show template text with raw z-scores instead of agent-written explanations.

**Fix:** Make the LLM path authoritative. `coach_service.insights()` should always run the LLM (persona + METRIC_GLOSSARY) when frames have classification data, and the LLM-written `explanation` is what's cached and served. Rule-based compute stays only as an offline/fallback pre-classification, never as the served explanation. The stored agent explanation powers both the Tips panel and the chat's `get_coach_insights`.

Caching: insights are already cached once generated (`insights_for_frames` reuses cached frames and only LLM-generates missing ones). Keep this pattern — generate once → cache → reuse, minimizing tokens.

## What to Do (Implementation Steps)
- [ ] In `coach_service.insights()` (line ~321): remove the rule-based short-circuit (`_rule_insights` check). When frames have classification data, always run the LLM path (`build_insights_prompt` → `_ask` → LLM-written explanation).
- [ ] Keep `_rule_insights()` as a fallback only for frames without classification data (pre-classification / cold-start).
- [ ] Verify `insights_for_frames()` still caches correctly — once LLM explanation is generated, it's stored and reused on subsequent calls.
- [ ] Verify `segment_insight()` (facade tool) still returns the LLM-written explanation.
- [ ] Verify the Tips & Insights panel receives the LLM-written `explanation` field (not template text).
- [ ] Update unit tests in `test_coach_insights_service.py` to assert LLM path is primary.
- [ ] Update unit tests in `test_coach_prompts.py` if prompt changes.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `coach_service.insights()` always runs LLM for frames with classification data.
- [ ] Rule-based path only used as fallback for unclassified frames.
- [ ] Tips & Insights panel shows agent-written explanation (no template z-score text).
- [ ] Caching works: generate once → reuse on subsequent calls.
- [ ] Unit tests updated and green.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)

## Dependencies
- **Blocks**: None
- **Blocked By**: None

## Estimated Effort
- [S]
