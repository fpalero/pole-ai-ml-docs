# Ticket: PAIML-POLE-API-105

## Title
Fix staging-gate harness failure: coach-flow integration test runs real MediaPipe path (E2E_FAKES unset)

## Description
Staging-gate follow-up (pre-existing on `develop`, touches no `pole_coach` code).
`app/pole_api/tests/analysis/test_coach_flow_integration.py`
(Phases 21–23, PAIML-POLE-API-064..071) uploads a 64-byte fake
`coach_e2e.mp4` (`files={"file": ("coach_e2e.mp4", b"x" * 64, "video/mp4")}`)
and asserts the analyze job reaches `done`. The file's own docstring states
it runs "with ``E2E_FAKES=1`` skeleton extraction" — but the `test-api` pixi
task does NOT set `E2E_FAKES=1`:

```toml
test-api = { cmd = "pytest -v", cwd = "app/pole_api",
             env = { PYTHONPATH = "src:../../packages/pole_rag/src" } }
```

So the real MediaPipe path runs against 64 bytes of `x`, the job fails, and
the assertion fails. Worse, the pytest session then wedges (futex stall,
~289 leaked threads, SIGKILL needed to recover the runner).

What fails today (exact error):

```text
VideoUnreadableError: Cannot open video file
```

→ analyze job status `failed` (expected `done`) → `assert job["status"] == "done"`
fails in the `coached_video` fixture → every test using the fixture errors →
session wedges post-failure (futex stall, ~289 leaked threads, SIGKILL required).

Provenance (why this is NOT a 001 regression): the test file is
byte-identical on `origin/develop`; the 001 diff is `packages/pole_coach/*`
only. This failure is pre-existing on `develop` and blocked leg 2 of the
001 staging gate; it is extracted here to its own ticket.

## Root Cause
Missing harness precondition: the test is designed for the fake-extraction
seam (`E2E_FAKES=1`, per its own docstring), but `test-api` never exports
that variable, so CI/gate runs exercise the real video-decode path with a
deliberately undecodable fixture.

## What to Do (Implementation Steps)
- [ ] (1) **Recommended: set `E2E_FAKES=1` in the `test-api` pixi task env**
  (`pixi.toml`). Justification: it restores the precondition the test file
  itself documents, keeps the test hermetic/fast, and fixes every present
  and future `E2E_FAKES`-gated test in one place. The alternative — making
  the fixture upload a real decodable video — would drag the full MediaPipe
  stack (and possibly model weights) into every `test-api` run, making the
  gate slower and flakier; reject it unless the implementer finds
  `E2E_FAKES=1` changes production behavior under test.
- [ ] (2) Re-run the coach-flow integration file under the fixed task and
  confirm the job reaches `done`.
- [ ] (3) Confirm the pytest session exits cleanly (no futex stall / leaked
  threads / SIGKILL needed). If the wedge reproduces even with the job
  green, file the hang as a separate follow-up — do NOT scope-creep this
  ticket into thread-lifecycle debugging.
- [ ] (4) Test-only + task-config change; no production-code changes under
  `app/pole_api/src/`.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] (1) `pixi run test-api` runs
  `tests/analysis/test_coach_flow_integration.py` GREEN (job reaches `done`).
- [ ] (2) The pytest session terminates on its own — no wedge, no SIGKILL.
- [ ] (3) No production-code changes (pixi task env + tests only).

## Out of Scope
- Any production-code change under `app/pole_api/src/`.
- Thread-lifecycle debugging if a hang persists after the job is green
  (separate follow-up).
- `pole_coach` phase work itself (this ticket only unblocks its gate).

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (full task — must be GREEN with no wedging).
- [ ] Targeted: `cd app/pole_api && PYTHONPATH=src pixi run python -m pytest
  tests/analysis/test_coach_flow_integration.py -v` with the fixed env.

## Unit-Test Requirement
- [ ] The fixed precondition is covered by the existing integration file
  itself going green under `test-api`; if the implementer adds any new
  helper/fixture to support the fix, it ships with its own unit test.

## Dependencies
- **Blocks**: Re-running the full PAIML-POLE-COACH-001 staging gate if gate
  policy requires leg 2 (`test-api`) green before release.
- **Blocked By**: None (pre-existing harness bug, independent of 001).
- Note: unblocks leg 2 of the 001 staging gate (and every later gate that
  runs `test-api` against this file).

## Estimated Effort
- [XS]
