# Ticket: PAIML-POLE-API-115

## Title
Coach chatbot grounding regression — video resolution + guarded delegation

## Status
📋 PLANNED

## Description
Regression discovered by the PAIML-POLE-COACH-007 SAMPLE-5 gate (25 asked, 0/25
vs staging `https://pole-coach.duckdns.org`). Two gaps make the supergraph return
"I couldn't build full coaching advice from the available data right now." on
every turn:

1. Video leg (R2): `SupergraphAnalystAgent._video_candidates` only finds an
   ObjectId hex, a filename, or `session.original_video`. "my/latest/last/this
   video" (no id/filename) never resolves, so video_analysis / progress graphs
   fall back.
2. Delegation (R4): PAIML-POLE-API-107 made a graph-level fallback terminal
   instead of delegating to the ReAct tool agent, so the 17 tools (`list_videos`,
   `get_progress_matrix`, …) never run for resolvable turns.

Composes with PAIML-POLE-API-112 (deterministic free-text trick extraction;
precedence video label > free text > None).

What to do (no code in this ticket — spec for the implementer):

- [ ] R2: resolve "my/latest/last/this video" via a SINGLE "most recent
      analyzed video" repository query (sort+limit). MUST NOT call
      `facade.list_videos()` (it is N+1 — one histogram read per video). Lazy:
      only fire when the message references a video and no id/filename/
      `original_video` resolves.
- [ ] R4: restore delegation on graph-level fallback (return None → the ReAct
      tool agent runs), guarded by a bounded deadline so the 107 hang does not
      return. Keep the terminal fallback only for genuinely unresolvable turns.

## Files Affected
- `app/pole_api/src/analyst_chatbot/coach_providers.py` (`_video_candidates`,
  `_build_state`, `answer`)
- analysis repository (latest-analyzed-video query)
- tests: `test_analyst_chatbot_video_resolution.py`,
  `test_analyst_supergraph_wiring_004.py`

## Unit-Test Requirement
- [ ] "analyse my latest video" (no id/filename) resolves the most recent
      analyzed video; assert a SINGLE query (no `list_videos` N+1).
- [ ] No video reference in the message → no extra query (lazy).
- [ ] Graph fallback on a resolvable turn delegates (returns None) → ReAct runs.
- [ ] Delegation is deadline-bounded (no 360 s hang regression).

## Integration Tests
- [ ] SAMPLE-5 gate green with 112 (each flow >=5/5), no bare "couldn't".
- [ ] `pixi run test-api` green.

## Acceptance Criteria
- [ ] "my latest handspring video" and "list my videos" answer correctly
      (not the "couldn't" fallback).
- [ ] No 107 hang regression (bounded delegation).

## Dependencies
- **Blocks**: none.
- **Blocked By**: none.

## Estimated Effort
- [S]
