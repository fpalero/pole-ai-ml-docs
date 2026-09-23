# Ticket: PAIML-POLE-API-133

## Title
131 review nits bundle (non-blocking)

## Status
✅ DONE — 131 review nits bundle merged (code PR #338 → squash `6a7b725` into develop per user override; local review APPROVED — hygiene-only verified: per-line noqas honest, fake mirrors real submit param-for-param, get_pose_frames restoration byte-faithful, 24+7 tests green locally; CI red at merge time = self-hosted runner disk-full infra `No space left on device`, not code — recorded).

- **Status**: ✅ DONE
- **Project**: pole_api (seed/coach flow + e2e harness)
- **Phase**: 42 coach-gate-25
- **Blocks**: —
- **Blocked By**: — independent follow-up to 131; does not block the gate.

## Context

Local review of PR #332 (PAIML-POLE-API-131, `seed-measurements` endpoint via
FakeSkeletonExtractor, merged as `3a335cf`) APPROVED with non-blocking nits.
This ticket parks them as a single bundle so 131 could close DONE without
waiting.

## Scope

(a) Scope the 3 file-level `# ruff: noqa` headers to per-line suppressions
(`videos.py`, `analysis_service.py`, `test_analysis_service.py`).

(b) Add `# ALLOW_SEED_MEASUREMENTS=` + `# E2E_FAKES=` commented lines to
`app/pole_api/.env.example`.

(c) Make `_FakeJobRunner.submit` fully mirror `JobRunner.submit`
(`owner_id`/`ws_connection_id` explicit, update
`test_submit_analyze_forwards_ws_connection_id` assertion).

(d) Consider gating `_seed_allowed()` before `get_video()` (prod
existence-oracle hardening) + `logger.warning` when opt-in active.

## Files Affected
- `app/pole_api/src/routers/videos.py` — file-level noqa → per-line.
- `app/pole_api/src/services/analysis_service.py` — file-level noqa → per-line.
- Analysis service tests (`test_analysis_service.py`) — file-level noqa → per-line.
- `app/pole_api/.env.example` — commented `ALLOW_SEED_MEASUREMENTS` / `E2E_FAKES` lines.
- Fake job runner (`_FakeJobRunner.submit`) + `test_submit_analyze_forwards_ws_connection_id`.
- `_seed_allowed()` / `seed-measurements` endpoint (gating order + warning log).

## Validation Plan
1. `ruff check` clean with per-line suppressions only (no file-level `noqa` in the 3 files).
2. `.env.example` documents both opt-ins as commented lines.
3. Fake runner signature mirrors `JobRunner.submit`; target test asserts explicit `owner_id`/`ws_connection_id` forwarding.
4. If (d) adopted: non-testing dataset without opt-in is rejected before any video fetch; opt-in active emits `logger.warning`.

## Acceptance Criteria
- [ ] No file-level `# ruff: noqa` remains in the 3 files.
- [ ] `.env.example` has the commented opt-in lines.
- [ ] `_FakeJobRunner.submit` mirrors `JobRunner.submit`; test assertion updated.
- [ ] `_seed_allowed()` gating decision recorded (adopted or explicitly declined) + warning log when opt-in active.

## Dependencies
- **Blocked By**: — (follows 131, already merged).
- **Blocks**: —.

## Estimated Effort
- [S]
