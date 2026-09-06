# Ticket: PAIML-POLE-API-085

## Title
[Chatbot] Coach prompt v3 — remove dead metric_deviation contract + enforce RAG-grounded athlete language

## Description
Phase 28. `app/pole_api/src/analyst_chatbot/prompts.py` (building on the already-merged `f8cb460` which added the four RAG tools):

(a) **REMOVE `metric_deviation`** from the ANSWER BLOCK TYPES contract — backend `blocks.py` `VALID_TYPES` is only `md`/`video_segment`/`analysis_link` and the FE union has no `metric_deviation`, so emitted blocks are silently dropped and the raw JSON fallback shows instead; md blocks already carry explanations + frames.

(b) **STRENGTHEN the tone**: athlete-facing plain language MANDATORY; forbid dumping raw z-scores / metric names / micro magnitudes into md; every deviation MUST be grounded via `query_pole` + `query_biomechanics` (plus `query_calisthenics` / `query_psicology` when relevant) and phrased for the athlete (e.g. "your hip drops during the exit — focus on…"); keep mirroring the user's language and concise readable answers.

(c) **Fix thumbnail_url**: the LLM is copying `"https://example.com/thumbnail.jpg"` from the prompt template. Add instruction: if no real URL available, omit the `thumbnail_url` field entirely.

## What to Do (Implementation Steps)
- [ ] Remove `metric_deviation` from the ANSWER BLOCK TYPES contract in `analyst_chatbot/prompts.py` (lines 95, 97, 113, 119).
- [ ] Strengthen the tone rules: athlete-facing plain language MANDATORY; forbid dumping raw z-scores / metric names / micro magnitudes into md blocks.
- [ ] Add explicit RAG-grounding rule: every deviation MUST be grounded via `query_pole` + `query_biomechanics` (plus `query_calisthenics` / `query_psicology` when relevant), phrased for the athlete.
- [ ] Add instruction: never use `example.com` or placeholder URLs in `thumbnail_url`; omit the field if no real URL available.
- [ ] Update prompt assertions in `app/pole_api/tests/test_analyst_chatbot.py` and `app/pole_api/tests/test_analyst_chatbot_coach_tools.py` to assert the tone contract.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Prompt no longer references `metric_deviation`.
- [ ] Prompt contains explicit anti-number-dump + RAG-grounding rules.
- [ ] Prompt instructs LLM to omit `thumbnail_url` when no real URL available.
- [ ] Tests updated to assert the tone contract.
- [ ] A sample deviation answer contains no raw z-score.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)

## Dependencies
- **Blocks**: None
- **Blocked By**: None

## Estimated Effort
- [S]
