# Ticket: PAIML-POLE-API-045

## Title
[Application] Regeneración + reseed de referencias para los trucos existentes

## Description
Phase 16 (§3). Regenerate and reseed `skeleton_trick_histograms` for all existing tricks using the
5 used metrics (`angular_speed` 0.40, `body_tilt` 0.25, `hip_height` 0.15, `wrist_stability` 0.15,
`torso_tilt_speed` 0.05) with configurable bins (default `[-3.0, -2.5, ..., 1.0]`, 8 bins).

## What to Do (Implementation Steps)
- [ ] Seed script/task iterating over tricks with `approved`/`accepted` clips.
- [ ] Verify all 5 metrics produced per phase; drop unused metrics (`horizontal_speed`, `vertical_speed`, `smoothness`).
- [ ] Configurable bins default `[-3.0, -2.5, ..., 1.0]`.
- [ ] Smoke check: classes endpoint lists seeded tricks; each has 5 metrics × 3 phases.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] All existing tricks reseeded; reference docs have the 5 used metrics across ENTRADA/EJECUCIÓN/SALIDA.
- [ ] `pixi run test-api` green (guarded `_testing` DBs).

## Integration Tests to Run (Local Verification)
- [ ] `pixi run test-api` (guarded `_testing` DBs; never prod).

## Dependencies
- **Blocks**: PAIML-POLE-API-046
- **Blocked By**: PAIML-POLE-API-043, PAIML-POLE-API-044

## Estimated Effort
- [S]