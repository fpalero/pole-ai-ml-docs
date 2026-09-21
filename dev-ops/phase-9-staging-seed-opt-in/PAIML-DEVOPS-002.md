# PAIML-DEVOPS-002 — staging seed opt-in helm plumbing (`ALLOW_SEED_MEASUREMENTS`)

- **Status**: ✅ DONE
- **Project**: dev-ops
- **Phase**: Phase 9 — staging seed opt-in
- **Created**: 2026-09-21
- **Merged**: infra PR `fpalero/pole-ai-ml-infra#39` merged into infra `develop` — chart renders `ALLOW_SEED_MEASUREMENTS` default `"0"`; `deploy-dev.yml` sets `=1` staging-only; helm `pending-upgrade` lock cleared via rollback to rev 254 → rev 257 deployed; follow-up deploy rev 258 rolled `3a335cf` images + opt-in `=1` verified on staging.
- **Repo**: `fpalero/pole-ai-ml-infra` (helm + workflows only — implementation PR goes to infra `develop`, NOT `pole-ai-ml`)
- **Type**: Helm plumbing (staging-only opt-in)

## Context

Phase-42 gate iteration 2 (tester report): staging `seed-measurements`
endpoint (ticket 131) is gated to **403 on staging** because:

- (a) `ALLOW_SEED_MEASUREMENTS` is **unset**, and staging DBs are the working
  DBs (not `_testing`/`_test`-suffixed), so the endpoint's default-deny path
  rejects the call;
- (b) the helm chart has **NO mapping** for it —
  `infrastracture/helm/pole-ai/charts/pole-api/templates/configmap.yaml`
  renders no such env, no value exists, `deploy-dev.yml` sets nothing.

## Scope (3 files, infra repo only — STAGING ONLY)

All paths relative to the infra repo root (`pole-ai-ml-infra`):

1. `helm/pole-ai/charts/pole-api/values.yaml` — add chart default
   `allowSeedMeasurements: "0"` (follow the existing `llmProvider` /
   `openrouterModel` / `ollamaHost` pattern).
2. `helm/pole-ai/charts/pole-api/templates/configmap.yaml` (ConfigMap
   `pole-api-env`) — add line
   `ALLOW_SEED_MEASUREMENTS: {{ .Values.allowSeedMeasurements | quote }}`
   (follow neighboring style).
3. `.github/workflows/deploy-dev.yml` — add
   `--set pole-api.allowSeedMeasurements=1` alongside the existing
   `--set pole-api.tag=...` args (lines ~76-86). **STAGING ONLY: prod must
   stay default-off — do not touch any prod workflow/values.**

Required change summary: chart default `"0"` + ConfigMap line + `--set ...=1`
in `deploy-dev.yml` ONLY.

## Incident note (context only, no action)

The helm `pending-upgrade` lock (rev 256) was cleared by the team-lead via
rollback to 254 (rev 257 deployed). Recorded here as incident context for the
iteration-2 gate failure; no action needed in this ticket.

## Validation plan

- `helm template` proof (from infra repo root):
  - with `--set pole-api.allowSeedMeasurements=1` renders
    `ALLOW_SEED_MEASUREMENTS="1"`;
  - without the `--set` renders `ALLOW_SEED_MEASUREMENTS="0"`.
- After merge: post-roll staging ConfigMap shows
  `ALLOW_SEED_MEASUREMENTS=1`.

## Acceptance Criteria

- [ ] a. Chart default `allowSeedMeasurements: "0"` present in subchart
      `values.yaml`.
- [ ] b. ConfigMap `pole-api-env` renders `ALLOW_SEED_MEASUREMENTS` from the
      value (quoted, neighboring style).
- [ ] c. `deploy-dev.yml` (staging only) passes
      `--set pole-api.allowSeedMeasurements=1`; no prod workflow/values
      touched.
- [ ] d. `helm template` proof: `="1"` with the `--set`, `="0"` without.
- [ ] e. Post-roll staging ConfigMap shows `ALLOW_SEED_MEASUREMENTS=1`.

## Security note

Staging-only opt-in; prod default deny preserved; never set in prod values.

## Blocks

— (none; blocks the iteration-3 gate re-run)

## Blocked By

— (none)

## Implementation notes

- Implementation goes in a **fresh worktree** on branch
  `feature/PAIML-DEVOPS-002-seed-opt-in` cut from the **INFRA repo's
  `develop`**, PR into infra `develop` (NOT `pole-ai-ml`).
- **Warning:** the infra main checkout has pre-existing dirt (staged
  `values-local.yaml` mod + 4 unstaged deletions) — implementation must use a
  fresh worktree and NOT touch that dirt.
