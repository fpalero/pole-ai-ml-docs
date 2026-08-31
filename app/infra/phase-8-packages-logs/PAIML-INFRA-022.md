# Ticket: PAIML-INFRA-022

## Title
[Packages] Create shared logging utility module in pole_tools

## Description
Extract a shared JSON logging helper from the pole_api logging changes into a reusable module under `pole_tools`. The module should expose a `get_json_logger(service_name: str)` function that returns a `logging.Logger` instance configured with `python-json-logger.JsonFormatter`, a `Filter` that injects `service_name`, and a `StreamHandler` writing to stderr. All packages (`pole_ml`, `pole_crawler`, `pole_jobs`) should import from this shared module instead of using their own `logging.basicConfig`.

## What to Do (Implementation Steps)
- [ ] Step 1: Create `pole_tools/logging.py` with `get_json_logger(service_name: str) -> logging.Logger` — configures logger with `JsonFormatter`, a filter adding `service_name`, and `StreamHandler` with stderr output.
- [ ] Step 2: Update `pole_tools/__init__.py` to export `get_json_logger`.
- [ ] Step 3: Replace `logging.basicConfig(...)` in `pole_ml/src/pole_ml/main.py` (or equivalent entry point) with `get_json_logger("pole_ml")`.
- [ ] Step 4: Replace `logging.basicConfig(...)` in `pole_crawler/src/pole_crawler/main.py` with `get_json_logger("pole-crawler")`.
- [ ] Step 5: Replace `logging.basicConfig(...)` in `packages/jobs/src/pole_jobs/worker.py` with `get_json_logger("pole-jobs")`.
- [ ] Step 6: Run `pixi run test` across packages to confirm no regressions; each package's test suite should still exercise logging calls.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `pole_tools.logging` module is importable and `get_json_logger` works out of the box.
- [ ] All three packages (`pole_ml`, `pole_crawler`, `pole_jobs`) emit JSON-formatted logs via the shared helper.
- [ ] `pixi run test` passes for all affected packages.

## Integration Tests to Run (Local Verification)
- [ ] `python3 -c "from pole_tools.logging import get_json_logger; logger = get_json_logger('test'); logger.info('hello')"` — output is valid JSON.
- [ ] Run `pixi run test` in each package (`packages/pole-train-model`, `packages/pole-crawler`, `packages/jobs`).
- [ ] Verify no `basicConfig` calls remain in the three packages (grep for `basicConfig`).

## Dependencies
- **Blocks:** PAIML-INFRA-023 (packages need shared helper first)
- **Blocked By:** PAIML-INFRA-024 (shipping/Filebeat needs structured logs from packages)

## Estimated Effort
- [M] (Medium < 4h)