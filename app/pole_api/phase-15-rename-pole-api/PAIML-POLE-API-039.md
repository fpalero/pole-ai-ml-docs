# Ticket: PAIML-POLE-API-039

## Title
[Infrastructure] Rename `pola_api` → `pole_api` (package + imports + tasks + docs)

## Description
Phase 15 (§1). Standardize naming: `app/pola_api/` → `app/pole_api/`, imports
`app.pola_api.*` → `app.pole_api.*`, ticket prefix `PAIML-POLA-API` → `PAIML-POLE-API`, and DB names
`pole_api` / `pole_api_testing`. Update all references (`pixi.toml` tasks, `scripts/guard-testing-db.sh`,
`scripts/generate_api_md.py`, `crew/`, AGENTS.md, docs).

## What to Do (Implementation Steps)
- [ ] `git mv app/pola_api app/pole_api`.
- [ ] Update `app/pole_api/src/core/config.py`: paths `os.path.join(root, "app", "pole_api", ...)`; logger names.
- [ ] Update `pixi.toml`: tasks `api`/`api-bg`/`test-api` cwd `app/pole_api`; `test-hardening` PYTHONPATH `app/pole_api/src`.
- [ ] Update `scripts/guard-testing-db.sh` default `APP_DB="${POLE_API_DB:-pole_api}"` (env var rename `POLA_API_DB` → `POLE_API_DB`).
- [ ] Update `scripts/generate_api_md.py` default out path + title.
- [ ] Update `crew/crew_implement.py`, `crew/README.md`, AGENTS.md, `docs/app/pola_api/*` references.
- [ ] Update test files referencing `pola_api` (paths/names) and `POLA_API_DB` env var.
- [ ] Update `PROJECT_VARS.md` prefix → `PAIML-POLE-API` (keeps last number 38).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] No references to `pola_api` / `app.pola_api.*` / `POLA_API_DB` remain in code/tasks/scripts.
- [ ] `pixi run test-api` green against `pole_api_testing` (guarded `_testing` suffix).
- [ ] API boots via `pixi run api`.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-API-040, PAIML-POLE-API-041
- **Blocked By**: None

## Estimated Effort
- [M]