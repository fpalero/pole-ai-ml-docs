# Ticket: PAIML-INFRA-023

## Title
[Packages] Update pole_ml, pole_crawler, pole_jobs to use shared JSON logger

## Description
Complete the migration of all package-level loggers to use the shared `pole_tools.logging.get_json_logger()` helper. Ensure every `logging.basicConfig(...)` call in the three packages is removed and replaced with a call to `get_json_logger("<package-name>")`. Update any module-level logger instantiations to use the returned logger. Ensure imports are updated and no duplicate handlers exist.

## What to Do (Implementation Steps)
- [ ] Step 1: In `pole_ml/src/pole_ml/main.py` (or the primary module), replace `logging.basicConfig(level=logging.INFO, format=...)` with `logger = get_json_logger("pole_ml")` and use `logger` for all log calls.
- [ ] Step 2: In `pole_crawler/src/pole_crawler/main.py`, same replacement with `get_json_logger("pole-crawler")`.
- [ ] Step 3: In `packages/jobs/src/pole_jobs/worker.py`, same replacement with `get_json_logger("pole-jobs")`.
- [ ] Step 4: Verify no `basicConfig` remains in any of the three packages (grep across all `.py` files).
- [ ] Step 5: Run `pixi run test` in each package to confirm test suites still pass.
- [ ] Step 6: Add a comment at the top of each modified file noting the migration to shared JSON logger.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] All `basicConfig` calls are removed from `pole_ml`, `pole_crawler`, and `pole_jobs`.
- [ ] All packages use `get_json_logger(...)` from `pole_tools.logging`.
- [ ] `pixi run test` passes for all three packages with no new failures.

## Integration Tests to Run (Local Verification)
- [ ] `python3 -c "from pole_ml import ...; ..."` or equivalent smoke test that a log emission produces JSON.
- [ ] `pixi run test` in each package passes.
- [ ] grep confirms zero `basicConfig` remaining.

## Dependencies
- **Blocks:** PAIML-INFRA-024 (Filebeat shipping needs structured logs from all packages)
- **Blocked By:** PAIML-INFRA-022 (shared helper must exist first)

## Estimated Effort
- [M] (Medium < 4h)