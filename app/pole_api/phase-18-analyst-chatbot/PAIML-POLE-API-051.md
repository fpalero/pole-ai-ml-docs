# Ticket: PAIML-POLE-API-051

## Status
✅ DONE — Implemented

## Title
[Application] Tools `histogram`, `classify`, `extract_frames`, `crop` + `AnalystFacade`

## Description
Phase 18 (§2). Analyst tools exposed to the ReActAgent:
- `histogram` — histogram analysis of a video (reads `skeleton_video_signals` + cohort).
- `classify` — LSTM classification only of a video.
- `extract_frames` — extract frames (returns `frame_image_path`s).
- `crop` — crop/select a video segment.
The chat does NOT produce the histogram (FE does via `POST /api/analysis/videos/{id}/analyze`);
chatbot is conversation + query + editing. `AnalystFacade` integrates the tools.

## What to Do (Implementation Steps)
- [x] Implement the 4 tools as callables for the ReActAgent.
- [x] `AnalystFacade` combining tools (mirror `training_chatbot/facade.py`).
- [x] Wire tools to `skeleton_video_signals` / cohort + LSTM stub + frame extraction.
- [x] Unit tests: each tool invocable; facade returns tool results to agent loop.

## Acceptance Criteria (Definition of Done for this Ticket)
- [x] Tools `histogram`/`classify`/`extract_frames`/`crop` invocable via ReActAgent.
- [x] `pixi run test-api` green (guarded `_testing` DBs).

## Integration Tests to Run (Local Verification)
- [x] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-API-052, PAIML-POLE-ANALYST-037
- **Blocked By**: PAIML-POLE-API-050

## Estimated Effort
- [M]