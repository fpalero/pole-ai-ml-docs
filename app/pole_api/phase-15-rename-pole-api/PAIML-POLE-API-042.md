# Ticket: PAIML-POLE-API-042

## Title
[Infrastructure] CLI de backfill para el rename de colecciones legacy

## Description
Phase 15 (§2). One-off migration CLI (`pole_tools`) that renames the legacy skeleton_data
collections in Mongo so existing data is not lost during the rename:
`signal_histograms` → `skeleton_cohort_signals` (cohort stats) and
`skeleton_histograms` → `skeleton_video_signals` (per-video histograms). Idempotent: if the target
collection already exists, do not duplicate/overwrite — report counts and exit 0. Mirrors the
existing `migrate-windows` CLI pattern (`pole_tools/cli/migrate_windows.py`, registered in `pixi.toml`).

## What to Do (Implementation Steps)
- [ ] `packages/pole-train-model/src/pole_tools/cli/rename_collections.py`: argparse `--db-uri`;
      connect to `get_skeleton_db()` via `get_mongo_uri()` (reuse `pole_tools.config`).
- [ ] `rename_collection(db, old, new)`: if `old` missing → skip (log info); if `new` exists → skip
      (idempotent, log "already exists, skipped"); else `db[old].rename(new)`.
- [ ] Rename `signal_histograms` → `skeleton_cohort_signals` and `skeleton_histograms` →
      `skeleton_video_signals`; log per-collection doc counts.
- [ ] Register pixi task `rename-collections = { cmd = "python -m pole_tools.cli.rename_collections", cwd = "packages/pole-train-model" }`.
- [ ] Unit test the CLI logic (mock pymongo database: missing source, existing target, successful rename).

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] CLI renames both legacy collections idempotently (no duplicate/overwrite).
- [ ] `pixi run rename-collections` works against a `_testing` skeleton DB; legacy names absent after run.
- [ ] Unit tests cover missing-source / existing-target / success paths.

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test` (pole-train-model suite; guarded `_testing` DBs).
- [ ] `pixi run rename-collections` against `skeleton_data_testing`.

## Dependencies
- **Blocks**: None
- **Blocked By**: PAIML-POLE-API-040 (collection constants must exist before backfill)

## Estimated Effort
- [S]