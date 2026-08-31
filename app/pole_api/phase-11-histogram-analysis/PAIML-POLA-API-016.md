# Ticket: PAIML-POLA-API-016

## Title
[Application] Delete `threshold_discovery` + Postgres/in-memory reference+attempt repos + migration

## Description
Phase 11 (§8.3.4 bullets 2-3). Remove the now-unused threshold discovery module and the Postgres /
in-memory reference+attempt repository layer and its SQL migration.

## What to Do (Implementation Steps)
- [ ] Step 1: Delete `src/tools/services/threshold_discovery.py`.
- [ ] Step 2: Delete `src/tools/repositories/postgres.py` and `src/tools/repositories/base.py` (Reference/Attempt ABCs).
- [ ] Step 3: Remove the reference/attempt classes in `src/tools/repositories/memory.py` + their exports.
- [ ] Step 4: Delete `app/pola_api/migrations/001_tools_postgres.sql` and any migration runner reference.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] No reference/attempt/threshold-discover/Postgres code remains in the tools slice.
- [ ] No dangling imports; lints clean.
- [ ] Migration file removed and no longer referenced.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` import/lint gate; no `threshold_discovery`/Postgres references.

## Dependencies
- **Blocks**: PAIML-POLA-API-017, PAIML-POLA-API-018
- **Blocked By**: PAIML-POLA-API-009, PAIML-POLA-API-015

## Estimated Effort
- [M]
