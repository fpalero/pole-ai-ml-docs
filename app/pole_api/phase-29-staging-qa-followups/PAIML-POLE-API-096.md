# Ticket: PAIML-POLE-API-096

## Title
[Chatbot] Analyst answer shaping: typed card blocks + no server paths + no raw call/block-JSON in user prose

## Description
Phase 29 — see [PLAN_PHASE_29](../plan/PLAN_PHASE_29.md). Third bundle from the
staging QA gate-2 rerun (tester evidence, local, not committed):
`/tmp/opencode/staging-gate2/` (`summary.json`, `replies.json`, `errors.json`,
`TOOL-*.json`, `RAG-*.json`, screenshots). Gate re-runs use **handspring
variants** for TOOL-06/11/20 (`TOOL-06-SUB`, `TOOL-11-SUB`, `TOOL-20-SUB` with
`"substituted": true`); ayesha questions stay deferred per the FUTURE note in
`PLAN_PHASE_29.md`.

Root causes established by the rerun (all backend answer-shaping, all user-visible):

- (F1) **Tool results never become typed card blocks.** Every TOOL-class reply
  renders `md` only — `summary.json` shows `renderedBlocks: ["md"]` with all
  typed `domCards` at zero across the battery (e.g. TOOL-04 `missing:image`,
  TOOL-05/TOOL-06-SUB `missing:video_segment`, TOOL-11-SUB `missing:drills`,
  TOOL-12 `missing:metric_matrix,video_segment`, TOOL-13 `missing:video_segment`,
  TOOL-18 `missing:image`, TOOL-19 `missing:score_summary,quick_replies`,
  TOOL-20-SUB `missing:metric_matrix`). The blocks contract exists
  (`PAIML-POLE-API-093`, blocks vocabulary `score_summary` / `phasic_feedback` /
  `metric_matrix` / `drills` / `quick_replies` / `image` / `video_segment`), but
  tool results are flattened to prose instead of mapped to their typed block.
- (F2-backend) **Server paths still leak.** `TOOL-06-SUB.json` `bubbleHead`
  ends with `crop` + `/data/uploads/analys…` — a container-local path reaches
  the user surface (related: `PAIML-POLE-API-093(b)` path-leak strip; this ticket
  closes the residual in tool results/prose — the FE chip-display sibling is
  `PAIML-POLE-ANALYST-075`).
- (F3) **Raw call syntax and inline block-JSON in user prose.**
  `TOOL-05.json` `replyHead` is a verbatim call string
  (`<|python_tag|>function=crop{"video_id": "…", "start": 0, "end": 3}`), also
  rendered into the bubble. `TOOL-10.json` / `TOOL-19.json` `replyHead` values
  are inline block-JSON (`{"type": "md", "content": "You stand at the following
  percentiles…"}`, `{"type": "score_summary", …}`) instead of rendered blocks —
  the same shape also leaks through the `agent_reply` frame (see
  `errors.json`, TOOL-10 `errFrames` entry).

## What to Do (Implementation Steps)
- [ ] (F1) Map tool results to their typed card block before reply synthesis:
  `extract_frames`/`get_coach_pose` → `image`, `crop` → `video_segment`,
  `cohort_percentiles`/`compare_sessions`/`metric_deep_dive` → `metric_matrix`,
  `improvement_plan`/`get_coach_summary` → `drills` (+ `score_summary` /
  `quick_replies` where the contract defines them). A TOOL-class turn whose
  tool succeeded must emit its typed block, never `md`-only prose describing
  the result. Keep the wire block shapes unchanged (FE renders them per
  `PAIML-POLE-ANALYST-072` / Phase 23).
- [ ] (F2-backend) Extend the `PAIML-POLE-API-093(b)` strip to tool results and
  tool-error branches: no `/data/…` (or other absolute server-path) substring
  in any wire `reply` / `blocks[].content` / tool-chip source string the backend
  emits. Strengthen the regression assertion helper from 093(b) to cover the
  TOOL-06-SUB-class (crop) path.
- [ ] (F3) Never emit raw call syntax or block-JSON as user prose: post-process
  the final `reply` so `<|python_tag|>…` call strings and `{"type": "<block>",
  …}` payloads are either parsed into their real blocks or dropped with a
  graceful prose fallback — never rendered verbatim. Add regression assertions
  (no `<|python_tag|>` substring; no `reply` starting with `{"type":`).
- [ ] Add/update tests in `app/pole_api/tests/test_analyst_chatbot*.py` covering
  (F1)–(F3): TOOL-04/05/06/11/12/13/18/19/20-class turns emit typed blocks;
  no `/data/` in replies; no raw call/block-JSON in prose.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] (F1) Staging rerun of the TOOL battery: tool-success turns render their
  typed card block (no `missing:<block>` flags for resolved tools).
- [ ] (F2-backend) No `/data/` (or other absolute server-path) strings in any
  chatbot `reply`/`blocks`/backend-emitted chip strings across the rerun.
- [ ] (F3) No `<|python_tag|>…` call strings and no inline `{"type": "<block>",
  …}` JSON in user-visible prose across the rerun.
- [ ] `pixi run test-api` green (guarded `_testing` DBs), coverage ≥ 80%.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)
- [ ] Staging battery rerun through the real FE (`TOOL-01..20` handspring
  variants): assert typed blocks present, no path strings, no raw call/JSON prose.

## Dependencies
- **Blocks**: `PAIML-POLE-ANALYST-075` (FE chip-arg sanitization consumes the
  backend-clean strings from (F2-backend); independent display-side work).
- **Blocked By**: None (backend-only; evidence paths above are local tester artifacts).
  Related: `PAIML-POLE-API-095` (turn lifecycle — adopted, see
  [PLAN_PHASE_29](../plan/PLAN_PHASE_29.md)), `PAIML-POLE-API-093` (blocks
  contract + (b) strip this ticket extends).

## Estimated Effort
- [M]
