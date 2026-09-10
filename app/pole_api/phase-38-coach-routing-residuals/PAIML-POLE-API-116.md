# Ticket: PAIML-POLE-API-116

## Title
Supergraph routing residuals: progress consumes trick + list reaches list_videos

## Status
📋 PLANNED

## Description
Post-115 staging smoke (`https://pole-coach.duckdns.org`, image `fc479e0`)
went 1/3: Q1 (VA-01 handspring focus) PASS with real grounding; Q2
(`list my videos`) and Q3 (PR-01 "Am I improving on handspring this
month?") FAIL with bare-LLM answers and ZERO tool calls attempted.

Live verification shows trick detection (112) works on staging: the
Mongo `trick_catalog` (447 moves) loads, and `extract_trick_name_from_text`
resolves `handspring` deterministically — 112 needs no rework. Both
residuals fail one step downstream, before tool dispatch:

1. Q3 (progress ignores trick): `trick_name=handspring` sits in state, but
   the progress graph answers generic md+drills without fetching trick
   progress and without falling back cleanly. Same family as the 111
   diagnosis ("progress bypasses the matrix"), now on the supergraph path
   (111 fixed only the ReAct road).
2. Q2 (list never routed): a trick-less list command has neither video_id
   nor trick_name, so it never reaches `list_videos` — neither via query
   routing nor via the R4 delegation guard (which requires video_id OR
   trick_name). Same family as the 094 `list_videos`-first rule, now
   unenforced on the supergraph path.

What to do (no code in this ticket — spec for the implementer):

- [ ] Q3: the progress graph MUST consume `trick_name` from state — fetch
      trick progress (matrix path via providers) when present; when no data
      exists, fall back cleanly (→ delegation) or emit an explicit "data
      unavailable" block. NEVER ungrounded generic md. Reference 111
      (ReAct-side steering) as prior art to mirror supergraph-side.
- [ ] Q2: trick-less list commands ("list my videos", no video/trick) MUST
      reach `list_videos` — via query-graph list routing or by extending
      R4 delegability to list intents. Reference 094 (`list_videos`-first)
      as prior art.
- [ ] Keep 112 untouched (detection proven); keep 107 terminal fallback for
      genuinely unresolvable turns only.

## Files Affected
- `packages/pole_coach` progress graph (trick consumption) and/or analyst
  progress routing; query-graph list routing and/or R4 `_can_delegate`
  (implementer to locate; shared with 113's routing files — coordinate,
  lands after 113)
- tests: progress-with-trick, list-routing (new, co-located)

## Unit-Test Requirement
- [ ] Progress turn with `trick_name` in state, no video → matrix fetch
      attempted OR clean fallback+delegation (assert: never generic md).
- [ ] "list my videos" (no video/trick) → `list_videos` reached
      (routed or delegated).
- [ ] Genuinely unresolvable turn → existing terminal path preserved.

## Integration Tests
- [ ] Staging re-smoke Q2+Q3 green (grounded, no "couldn't", tool proof).
- [ ] `pixi run test-api` green.

## Acceptance Criteria
- [ ] Q3 answers with trick progress data or delegates cleanly — never
      generic advice ignoring the trick.
- [ ] Q2 renders the video list.
- [ ] No regression to Q1/VA grounding or the 107 hang guard.

## Dependencies
- **Blocks**: none.
- **Blocked By**: PAIML-POLE-API-113 (same routing files in flight — land after).

## Estimated Effort
- [S]
