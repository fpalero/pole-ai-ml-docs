# Ticket: PAIML-POLE-API-089

## Title
[Coach] Inject signal repo for coach cohort reads (full *_test isolation)

## Description
Phase 29 (follow-up hardening from the phase-28 QA gate). `CoachService._gather_insights()` and `_insight_z_context()` currently import the GLOBAL settings (`from core.config import settings as _settings`) and read `get_database(_settings.skeleton_db)` / `skeleton_cohort_signals`, bypassing the injected `self._settings` — so tests hit production `skeleton_data` instead of `skeleton_data_test`, violating the `_testing`-suffix guard convention (PLAN.md §4).

**Fix:** add an optional `signal_repo: HistogramRepository | None = None` constructor param to `CoachService` (default built from the injected `settings`) and use it for both cohort reads.

## What to Do (Implementation Steps)
- [ ] Add optional `signal_repo: HistogramRepository | None = None` constructor param to `CoachService` (`app/pole_api/src/analysis/services/coach_service.py`); default builds the repo from the injected `settings`.
- [ ] Route both cohort reads (`_gather_insights()`, `_insight_z_context()`) through the injected repo instead of `get_database(_settings.skeleton_db)` / direct `skeleton_cohort_signals` access.
- [ ] Remove the GLOBAL-settings import path for these reads so the injected `self._settings` is authoritative.
- [ ] Add tests that seed `skeleton_data_test` cohort docs and assert no production DB is read when a repo is injected.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Both cohort reads go through the injected `signal_repo`; no `from core.config import settings as _settings` path remains for them.
- [ ] Tests seed `skeleton_data_test` cohort docs and pass with an injected repo.
- [ ] No production `skeleton_data` DB is read in tests.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs)

## Dependencies
- **Blocks**: —
- **Blocked By**: — (does NOT block API-088; independent — either may land first)

## Estimated Effort
- [S]
