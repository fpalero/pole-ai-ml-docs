# Plan Phase 4 — STAGING & PROD Pipelines

> **Parent plan:** [PLAN.md](../PLAN.md)
> **Status:** 📋 PLANNED

## Scope

Create STAGING and PROD deployment workflows with manual gates, health checks, auto-rollback on failure, and Slack notifications.

## Tasks

1. Create GitHub Environment `staging` with manual gate (1 required reviewer)
2. Create `.github/workflows/deploy-staging.yml` (workflow_dispatch trigger)
3. Create GitHub Environment `prod` with manual approval (1 required reviewer)
4. Create `.github/workflows/deploy-prod.yml` with `helm upgrade --wait`
5. Add auto-rollback on failure: `helm rollback pole-ai --wait`
6. Add Slack notification on deploy success/failure

## Dependencies

- **Blocked By:** Phase 3 (DEV deploy must work first)
- **Blocks:** None (final deployment phase)

## Acceptance Criteria

- [ ] GitHub Environments `staging` and `prod` created with protection rules
- [ ] `deploy-staging.yml` requires manual approval before deployment
- [ ] `deploy-prod.yml` requires manual approval before deployment
- [ ] PROD deploy auto-rollbacks on failure
- [ ] Slack notifications sent on deploy success/failure
- [ ] Helm `--wait` ensures all pods are healthy before marking deploy complete

## Use Cases Validated

- UC-03: STAGING deploy requires manual gate
- UC-04: PROD deploy with rollback on failure
- UC-05: Slack notification on deploy outcome
