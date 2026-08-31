# Testing Plan

## Overview
This plan outlines the approach to achieve **≥80 % code coverage** for all modules in `src/ml` and `src/tools`. The strategy relies on **pytest** for test execution, **coverage.py** for instrumentation, and stubbed‑in mocks to isolate external dependencies. A GitHub Actions workflow will enforce the coverage threshold in CI.

> **Status (2026‑08‑03):** ✅ Target reached — **478 tests pass, 89.31 % coverage** (line + branch). Implemented in commit `861533a` (B6). The coverage threshold is enforced locally via `[tool.coverage.report] fail_under = 80` in `pyproject.toml`.

## Scope of Coverage
- **Targeted directories:** `src/ml/`, `src/tools/` (and any subpackages).
- **Included modules:** Every `.py` file under those two directories.
- **Excluded:** Anything outside `src/`. The plan does not touch `backend/`, `frontend/`, or other top‑level packages.

## Test Framework
- **Framework:** pytest 7.x (latest stable).
- **Assertions:** Standard `assert` statements; no additional assertion libraries.
- **Fixtures:** Reusable fixtures for common test data and stubs.
- **Marker:** Optional custom marker `@pytest.mark.integration` for integration‑style tests if needed.

## Coverage Measurement
1. `pytest` + `pytest-cov` are installed as pixi dev dependencies.
2. Coverage config lives in `pyproject.toml` (equivalent of a `setup.cfg` section):
   ```ini
   [tool.pytest.ini_options]
   testpaths = ["tests"]
   addopts = "--cov=src --cov-report term-missing"
   pythonpath = ["src"]
   [tool.coverage.run]
   branch = True
   source = ["src"]
   omit = ["*/tests/*"]
   [tool.coverage.report]
   fail_under = 80
   show_missing = True
   ```
3. Run `pytest` locally to generate a coverage report.
4. The `fail_under` directive causes the run to fail if coverage falls below 80 %.

## Test Naming Conventions
- **File naming:** `test_<module_name>.py` (e.g., `test_video_cutter.py`).
- **Test functions:** `def test_<description>():` using descriptive names such as `test_cutter_raises_on_invalid_file()`.
- **Markers:** Use `@pytest.mark.parametrize` for data‑driven tests.

## Mocking Strategy
- **Stubbed‑in mocks**: Use `unittest.mock.patch` to replace heavy or external components:
  - MediaPipe Pose model → a stub that returns deterministic keypoints.
  - OpenCV video capture/read → in‑memory frames.
  - MongoDB client → an in‑memory dictionary simulating the collection API.
- **Fixtures for mocks**: Provide reusable fixtures such as `mock_mediapipe_pose`, `mock_opencv_capture`, and `mock_mongo_collection`.

## Detailed Module Coverage Matrix
| Module | Key Functions/Classes to Test | Sample Assertions | Result |
|--------|-------------------------------|-------------------|--------|
| `src/tools/video_cutter.py` | `VideoCutter.__init__`, `cut_video()`, `_detect_target_class_windowed()` | Verify output file paths, segment detection, error handling on missing input | 65 % (mocked `test_video_cutter.py`) |
| `src/tools/evaluate_video.py` | `build_pipeline()`, scoring helpers | Correct score range, edge cases with empty clip | 99 % |
| `src/tools/find_by_similarity.py` | `find_similar_clips()` | Returns correct number of matches, similarity threshold enforcement | 98 % |
| `src/tools/process_embeddings.py` | embedding generation / storage | Vector dimensionality, stored value correctness | 96 % |
| `src/ml/processors/skeleton_extractor.py` | `extract_skeleton_from_video()`, `_normalize_points()` | Correct landmark count, normalization consistency | 97 % |
| `src/ml/processors/processing_pipeline.py` | `process_video()`, sliding-window builders | Sliding window length, stride behavior | 88 % |
| `src/ml/repositories/storage.py` | `SkeletonStorage.__init__`, `save_skeleton_data()` | Connection parameters passed, data inserted into collection | 100 % |

(Additional modules under the two directories are mapped similarly. Full report: `pytest` shows per-module coverage; **overall 89.31 %**.)

## Implementation Steps
1. **Set up development environment**
   ```bash
   pip install -e .[dev]  # Assuming a setup.py or pyproject.toml with dev extras
   ```
2. **Create test directory structure**
   ```text
   tests/
     ├── __init__.py
     ├── conftest.py        # Fixtures & hooks
     ├── test_video_cutter.py
     ├── test_evaluate_video.py
     └── ... (one per module)
   ```
3. **Write `conftest.py`** with fixtures for mocks and common utilities.
4. **Implement tests** following the matrix; use parametrization where appropriate.
5. **Run locally**:
   ```bash
   pytest --cov=src --cov-report html
   ```
   Verify the coverage report meets the 80 % threshold.
6. **Add GitHub Actions workflow** (`.github/workflows/ci.yml`):
   - Checkout repo
   - Set up Python
   - Install dependencies (including dev extras)
   - Run `pytest`
   - Upload coverage artifact if desired.

## CI Integration
```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install .[dev]
      - name: Run tests
        run: pytest --cov=src --cov-report term-missing
```
The workflow will fail automatically if coverage < 80 %.

## Checklist
- [x] All modules in `src/ml` and `src/tools` have at least one test file.
- [x] Coverage ≥ 80 % for lines and branches (**89.31 %**).
- [x] Stubs/mock fixtures cover external dependencies (`tests/conftest.py`: MediaPipe, OpenCV, Mongo, ChromaDB, Keras).
- [ ] GitHub Actions CI enforces coverage threshold (not yet wired; enforced locally via `fail_under = 80`).
- [x] Tests are deterministic (in-memory fakes; no external services).

---

## Integration-test inventory (2026-08-12)

Beyond the unit matrix above, the repo runs a cross-layer integration suite, all against `_testing`
DBs (`pole_api_testing` + `skeleton_data_testing`, never prod):

| Suite | Command | Scope |
|---|---|---|
| BE integration | `pixi run test-api` | `app/pola_api/tests` incl. `test_e2e.py`, `test_process_integration.py`, `test_upload_integration.py` |
| CLI integration | `pixi run test` | `test_cli_integration.py` (extract→process, no-extract error, idempotent re-run, `--phase-frames` skip) |
| Chatbot live | `pixi run test-chatbot-live` | `packages/chatbot/tests/test_ws_integration.py` (WS→jobs→ffmpeg) |
| FE+BE E2E | `pixi run fe-e2e` | `app/pole_fe/e2e/` (Playwright, E2E-1..20) |

Aggregator: `pixi run test-integration` runs the four suites sequentially with `_testing` DB env
overrides and a guard that aborts if a DB name lacks the `_testing` suffix.

---
**Author:** Claude Code Agent
**Date:** 2026‑08‑02