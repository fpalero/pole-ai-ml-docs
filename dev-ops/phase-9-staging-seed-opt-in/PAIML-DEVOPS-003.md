# PAIML-DEVOPS-003 — revert staging seed opt-in (infra PR #39; `allowSeedMeasurements`)

- **Status**: 📋 PLANNED
- **Project**: dev-ops
- **Phase**: Phase 9 — staging seed opt-in
- **Repo**: `fpalero/pole-ai-ml-infra` (helm + workflows only — implementation PR goes to infra `develop`, NOT `pole-ai-ml`)
- **Type**: Revert (staging-only)
- **Blocks**: —
- **Blocked By**: — (pairs with PAIML-POLE-API-137 code revert; neither blocks the other).

## Context

Phase-42 gate iter-3 USER DECISIONS (binding): revert ticket 131's fake
`seed-measurements` endpoint (code PR #332 → reverted in PAIML-POLE-API-137)
and this ticket's predecessor DEVOPS-002 staging opt-in (`--set
pole-api.allowSeedMeasurements=1`, infra PR #39). No mock data — real
performances via pole_fe (handspring + Shoulder Mount only). DEVOPS-002
(✅ DONE) is therefore superseded for its opt-in line only.

## Scope (1 line, infra repo only)

All paths relative to the infra repo root (`pole-ai-ml-infra`):

1. `.github/workflows/deploy-dev.yml` — remove the
   `--set pole-api.allowSeedMeasurements=1` arg added by PR #39 (ONE line).
2. Keep the chart default `allowSeedMeasurements: "0"` + ConfigMap
   `ALLOW_SEED_MEASUREMENTS` mapping as inert forward-compat — state explicitly
   in the PR that they are intentionally retained (default-off, unused).

**Prod untouched** — never set there (as in DEVOPS-002).

## Validation Plan

- `git diff` on `deploy-dev.yml` shows only the line removal.
- After next staging roll: ConfigMap `pole-api-env` shows
  `ALLOW_SEED_MEASUREMENTS="0"` (or absent if chart default renders empty —
  record actual).
- Prod workflows/values untouched.

## Acceptance Criteria

- [ ] `deploy-dev.yml` diff shows only the `--set
      pole-api.allowSeedMeasurements=1` line removal.
- [ ] Chart default `"0"` + ConfigMap mapping retained as inert
      forward-compat (explicitly stated in PR).
- [ ] Staging ConfigMap after next roll shows `"0"` (or absent — record
      actual).
- [ ] Prod untouched (never set there).

## Implementation notes

- Implementation goes in a **fresh worktree** on branch
  `feature/PAIML-DEVOPS-003-revert-seed-opt-in` cut from the **INFRA repo's
  `develop`**, PR into infra `develop` (NOT `pole-ai-ml`).
