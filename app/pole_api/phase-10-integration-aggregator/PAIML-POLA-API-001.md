# Ticket: PAIML-POLA-API-001

## Title
[Infrastructure] E2E fake mode (`E2E_FAKES`) + `fe-e2e` / `test-integration` pixi tasks with `_testing` guard

## Description
The FE+BE Playwright suite (`app/pole_fe/e2e/`) drives a **real uvicorn** backend, so the
monkeypatch-based fakes in `app/pola_api/tests/test_e2e.py` cannot be reused directly. This ticket
adds an env-gated fake mode and the pixi tasks that orchestrate the whole integration suite against
the `_testing` DBs only.

## What to Do (Implementation Steps)
- [ ] Add `e2e_fakes: bool` to `core/config.py` `Settings` (env `E2E_FAKES`, default `False`).
- [ ] In the crawler slice, when `settings.e2e_fakes` is truthy, use `FakeClient` + `FakeStorage`
      (mirror `_patch_crawler` in `test_e2e.py`). Keep the real path untouched otherwise.
- [ ] In the video cutter service, when `settings.e2e_fakes` is truthy, use `FakeCutter`
      (mirror `_patch_cutter`). Keep the real `VideoCutter` path otherwise.
- [ ] In the train/retrain service, when `settings.e2e_fakes` is truthy, use fake
      `train_model_normal` + `save_windows_embeddings` (mirror `_patch_training`). Keep the real
      `ProcessingPipeline` path otherwise.
- [ ] Add a guard script `scripts/guard-testing-db.sh` that exits non-zero unless
      `POLA_API_DB` and `SKELETON_DB` both end with `_testing`.
- [ ] Add `[tasks.fe-e2e]` (cwd `app/pole_fe`, runs `npx playwright test`, env includes the `_testing`
      DB names and a temp `CHROMA_PERSIST_DIR`) and `[tasks.test-integration]` (sequential: guard →
      `test-api` → CLI `test` → `test-chatbot-live` → `fe-e2e`, all with `_testing` env overrides).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `E2E_FAKES=1` + `POLA_API_DB=pole_api_testing` + `SKELETON_DB=skeleton_data_testing` lets a live
      `uvicorn` run Workflow B (crawl→QC→cut→process→embed→train→approve) with no Instagram session
      and no trained LSTM, mirroring `test_e2e.py` assertions.
- [ ] `pixi run test-integration` aborts if DB env names lack `_testing`; otherwise runs all four
      suites sequentially.
- [ ] No prod DB (`pola_api` / `skeleton_data`) is ever touched by the new tasks.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` still green (regression: real path unchanged).
- [ ] `pixi run fe-e2e` green with the E2E fake mode backend.
- [ ] `pixi run test-integration` green end-to-end.

## Dependencies
- **Blocks**: `PAIML-POLE-FE-001` (FE E2E needs the env contract + tasks).
- **Blocked By**: None.

## Estimated Effort
- [M]
