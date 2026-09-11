# Ticket: PAIML-POLE-API-121

## Title
Carry raw unknown-trick mention into supergraph state (117 enabler — Q3 names the trick)

## Status
🔧 IN REVIEW — code PR https://github.com/fpalero/pole-ai-ml/pull/316 (`075e409`, branch `feature/PAIML-POLE-API-119-unknown-mention`, OPEN)

## Description
Phase 36 staging gate, batch-1 Q3: *"I can do the moonflip-9000, what
should I try next?"* resolves `unknown` with zero fabrication (good),
but `_build_state` dropped the raw mention (unknown stayed `None`), so
the 117 explicit unknown-trick fallback has nothing to name and the turn
degrades to the bare generic fallback (*"I couldn't build full coaching
advice…"*, 0 tool calls).

Numbering note: the code lane requested 119, but docs 119 is consumed by
the Phase 40 PR-checks-gate lane (counter at 120), so this backfill
lands on the next free number, 121, as the third Phase 39 ticket. No
parallel lane is touched.

What the code PR does (no docs-side code — backfill only):

- [x] `extract_unknown_trick_mention` (new, in `trick_mentions.py`):
      returns the raw mention (e.g. `moonflip-9000`) for
      mastery+progression phrasing when the catalog scan finds nothing.
      Catalog hits stay on the known path; out-of-scope and genuine
      no-mention turns stay `None`.
- [x] `_build_state` carry (in `coach_providers.py`): the unknown
      mention is kept as `trick_name` (resolvable-but-unknown) so 117's
      `is_unknown_trick_progression_turn` fallback can name it. Known
      tricks unchanged; genuine-None keeps the existing generic path;
      zero fabricated transitions.
- [x] 31 collected test cases green in `test_unknown_mention_119.py`
      (extractor units + `_build_state` carry + degraded-graph
      integration: Q3 renders `Unknown trick 'moonflip-9000'`, known
      handspring progression unregressed, genuine-None keeps the safe
      fallback).

Staging proof pending: Q3 re-run must show
`Unknown trick 'moonflip-9000'` with zero candidates.

## Files Affected
- `app/pole_api/src/analyst_chatbot/trick_mentions.py` (`extract_unknown_trick_mention`, new)
- `app/pole_api/src/analyst_chatbot/coach_providers.py` (`_build_state` carry)
- `app/pole_api/tests/test_unknown_mention_119.py` (new, 31 cases green in PR)

## Unit-Test Requirement
- [x] Raw-mention extractor: Q3 verbatim + shape variants + catalog-hit
      exclusion + out-of-scope/invalid inputs stay `None`.
- [x] `_build_state`: Q3 carries the mention, known trick unchanged,
      genuine-None preserved, unknown-without-progression stays `None`.
- [x] Degraded-graph integration: explicit unknown guidance, no bare
      fallback, no candidate headers/numbered lists.

## Integration Tests
- [ ] Re-run staging Q3 only (`moonflip-9000` progression) green:
      explicit unknown-trick guidance, no bare "couldn't", no fabrication.
- [ ] `pixi run test-api` green post-merge.

## Acceptance Criteria
- [ ] Q3 staging re-run names the unknown trick with zero fabricated
      transitions.
- [ ] No regression to known-trick progression or the genuine-None
      generic path.
- [ ] Code PR merged to develop.

## Dependencies
- **Blocks**: none.
- **Blocked By**: none.

## Estimated Effort
- [S]
