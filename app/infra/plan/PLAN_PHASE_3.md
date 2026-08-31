# Plan Phase 3 — DEV Auto-Deploy

> **Parent plan:** [PLAN.md](../PLAN.md)
- **Status:** 📋 PLANNED

## Scope

Create a GitHub Actions workflow that automatically deploys to the DEV environment after images are pushed to GHCR. Includes health check verification post-deploy.

## Tasks

1. Create GitHub Environment `dev` (no protection rules, auto-deploy)
2. Create `.github/workflows/deploy-dev.yml` triggered after build-push succeeds
3. Configure Helm upgrade with `--wait` flag for DEV namespace
4. Add health check verification (curl pole-api `/health`)
5. Configure k3s cluster connection for GitHub Actions runner

## Dependencies

- **Blocked By:** Phase 2 (images must be in GHCR)
- **Blocks:** Phase 4 (STAGING deploy depends on DEV succeeding)

## Acceptance Criteria

- [ ] GitHub Environment `dev` created with no protection rules
- [ ] `deploy-dev.yml` triggers automatically after build-push succeeds
- [ ] Helm upgrade deploys all services to DEV namespace
- [ ] Health check confirms pole-api `/health` returns 200
- [ ] Deploy status reported in GitHub Actions

## Use Cases Validated

- UC-02: DEV environment auto-deploys after successful build
