# Ticket: PAIML-POLE-API-094

## Title
[Chatbot] Video resolution end-to-end: substring/trick_label fallbacks + placeholder-ID guard + per-tool unify + resolution ADR

## Description
Phase 29 — see [PLAN_PHASE_29](../plan/PLAN_PHASE_29.md). Second bundle from the
staging QA rerun (tester evidence, local, not committed):
`/tmp/opencode/staging-rerun2/` (`summary.json`, `replies.json`, `errors.json`,
`TOOL-*.png`).

Root causes established by the rerun (all video-resolution, all backend):

- (a) **`AnalysisVideoRepository.get()` misses trick-name videos.**
  `app/pole_api/src/analysis/repositories/analysis_repository.py:39` tries
  ObjectId → exact filename → prefix filename only, so a trick name like
  `handspring`/`ayesha` misses files like `bodybyfran_handspring.mp4` /
  `aysha.mp4`. Verified live against staging: adding **substring-filename**
  and **`trick_label`** fallbacks returns the right doc for both cases.
  Explicit non-requirement: **no fuzzy-spelling** matching (ayesha spelling
  variants deferred — see the FUTURE note in `PLAN_PHASE_29.md`, item 4 below).
- (b) **The analyst LLM fabricates literal placeholder IDs.**
  Turns TOOL-11/12/13 pass `handspring_video` / `ayesha_video` as `video_id`,
  bypassing the resolver entirely. Fix: `list_videos`-first resolution —
  never pass a fabricated id straight into a tool; resolve the user's
  referring expression against the video list, then call the tool with the
  resolved real id.
- (c) **Per-tool resolution inconsistency.** `segment_insight` /
  `get_coach_summary` / `get_coach_pose` resolve the same referring
  expressions that `extract_frames` / `crop` / `metric_deep_dive` /
  `frame_pose` / `compare_sessions` reject with "not analyzed" on analyzed
  videos. Unify: every video-taking tool shares one resolver path.
- (d) **Resolution strategy ADR.** Record the fallback order, the
  `list_videos`-first rule, and the `str`/`ObjectId` `video_id` duality note
  (wire `video_id` is a string; storage is `ObjectId` — the resolver must
  accept both and never leak the distinction to the LLM prompt).
- (e) **Disambiguation.** With 2+ same-trick videos on staging,
  "my handspring video" must resolve to the **latest** and name it in the
  reply (so the user can correct).

## What to Do (Implementation Steps)
- [ ] (a) Extend `AnalysisVideoRepository.get()` (and the chatbot resolver
      that calls it) with ordered fallbacks after the existing
      ObjectId → exact filename → prefix filename chain:
      (1) **substring-filename** match on the normalized trick token,
      (2) **`trick_label`** match on the analysis doc. Keep the existing
      order stable; new fallbacks only fire when earlier steps miss.
      No fuzzy-spelling / edit-distance matching in this ticket.
- [ ] (b) Add a placeholder-ID guard in the analyst chatbot tool path
      (`app/pole_api/src/analyst_chatbot/`): if the LLM emits a `video_id`
      matching `*_video` placeholder shape or one that matches no known
      video, force a `list_videos`-first re-resolution instead of calling
      the tool with the fabricated id. Cover TOOL-11/12/13-class turns.
      Harden the system prompt: tool `video_id` must always be a resolved
      id from `list_videos`, never an invented literal.
- [ ] (c) Unify resolution across all video-taking tools
      (`segment_insight`, `get_coach_summary`, `get_coach_pose`,
      `extract_frames`, `crop`, `metric_deep_dive`, `frame_pose`,
      `compare_sessions`): single shared `resolve_video()` helper; remove
      per-tool ad-hoc lookup branches. Every tool resolves the same way
      or returns the same "not found" shape.
- [ ] (d) Write the resolution ADR (location per repo convention,
      referenced from `PLAN_PHASE_29.md`): fallback order with rationale,
      `list_videos`-first rule, `str`/`ObjectId` `video_id` duality note,
      disambiguation policy (latest-wins + name-it), and the explicitly
      deferred fuzzy-spelling decision (pointer to the ayesha FUTURE note).
- [ ] (e) Disambiguation behavior: when 2+ candidates match, pick latest
      by `created_at` (document tiebreak), and include the chosen filename
      in the reply/tool context so the user can spot a mis-resolution.
- [ ] Add/update tests in `app/pole_api/tests/test_analyst_chatbot*.py`
      covering (a)–(c)+(e): substring file (`bodybyfran_handspring.mp4`
      via `handspring`), `trick_label` fallback (`aysha.mp4` via `ayesha`
      label path — not spelling fuzzy), placeholder-id guard
      (`handspring_video` → re-resolve, never passed through),
      cross-tool parity matrix (same expression resolves identically in
      all eight tools), latest-wins disambiguation naming the file.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] (a) `handspring` resolves `bodybyfran_handspring.mp4` and the
      `trick_label` fallback resolves the `aysha.mp4` doc; previously
      missing trick-name lookups now hit. No fuzzy-spelling behavior added.
- [ ] (b) TOOL-11/12/13-class turns no longer call tools with fabricated
      `*_video` ids; the rerun shows `list_videos`-first resolution on
      those turns.
- [ ] (c) Parity: the same referring expression resolves identically in
      `segment_insight`, `get_coach_summary`, `get_coach_pose`,
      `extract_frames`, `crop`, `metric_deep_dive`, `frame_pose`,
      `compare_sessions` — no tool claims "not analyzed" on an analyzed
      video that a sibling tool resolves.
- [ ] (d) Resolution ADR exists and is linked from `PLAN_PHASE_29.md`,
      covering fallback order, `list_videos`-first, `str`/`ObjectId`
      duality, latest-wins + name-it, and the fuzzy-spelling deferral.
- [ ] (e) With 2+ same-trick videos on staging, "my handspring video"
      resolves to the latest video and names it in the reply.
- [ ] `pixi run test-api` green (guarded `_testing` DBs), coverage ≥ 80%.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)
- [ ] Staging rerun spot check (`/tmp/opencode/staging-rerun2/` battery):
      trick-name resolution, TOOL-11/12/13 placeholder turns, cross-tool
      parity on an analyzed video, 2-video disambiguation naming latest.

## Dependencies
- **Blocks**: None (backend-only; FE needs no contract change — replies
  keep their shape, only resolve correctly).
- **Blocked By**: None. Evidence paths above are local tester artifacts.
  Sibling: `PAIML-POLE-ANALYST-074` is independent (FE summary prose).

## Estimated Effort
- [M]
