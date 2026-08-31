# Ticket: PAIML-INFRA-008

## Title
[Infrastructure] Create STAGING Deploy Workflow

## Description
Create the GitHub Actions workflow for STAGING deployment. Triggered manually via `workflow_dispatch`, requires approval through GitHub Environment protection rules before deploying.

## What to Do (Implementation Steps)
- [ ] Step 1: Create `.github/workflows/deploy-staging.yml` with `workflow_dispatch` trigger
- [ ] Step 2: Add `environment: staging` to the deploy job (triggers protection rules)
- [ ] Step 3: Add job to checkout `infrastracture/` repo
- [ ] Step 4: Add Helm setup and kubeconfig steps
- [ ] Step 5: Add Helm upgrade: `helm upgrade --install pole-ai ./helm/pole-ai -n pole-ai-staging --create-namespace --wait --set global.registry=ghcr.io/<owner> --set poleApi.tag=$TAG --set poleFe.tag=$TAG --set poleAnalyst.tag=$TAG`
- [ ] Step 6: Add health check step

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Workflow file `.github/workflows/deploy-staging.yml` exists
- [ ] Workflow requires manual approval before deployment
- [ ] Helm upgrade deploys to STAGING namespace
- [ ] Health check verifies pole-api is healthy post-deploy

## Integration Tests to Run (Local Verification)
- [ ] Run UC-03: STAGING deploy requires manual gate — trigger workflow, verify approval is required

## Dependencies
- **Blocks:** PAIML-INFRA-009 (PROD deploy depends on STAGING working)
- **Blocked By:** PAIML-INFRA-007 (staging environment must exist)

## Estimated Effort
- [M] (Medium < 4h)
