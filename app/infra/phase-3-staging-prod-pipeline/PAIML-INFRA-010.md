# Ticket: PAIML-INFRA-010

## Title
[Infrastructure] Create PROD Deploy Workflow with Rollback

## Description
Create the GitHub Actions workflow for PROD deployment. Triggered manually, requires approval, uses `helm upgrade --wait`, and auto-rollbacks on failure.

## What to Do (Implementation Steps)
- [ ] Step 1: Create `.github/workflows/deploy-prod.yml` with `workflow_dispatch` trigger
- [ ] Step 2: Add `environment: prod` to the deploy job (triggers approval)
- [ ] Step 3: Add job to checkout `infrastracture/` repo
- [ ] Step 4: Add Helm setup and kubeconfig steps
- [ ] Step 5: Add Helm upgrade: `helm upgrade --install pole-ai ./helm/pole-ai -n pole-ai-prod --create-namespace --wait --set global.registry=ghcr.io/<owner> --set poleApi.tag=$TAG --set poleFe.tag=$TAG --set poleAnalyst.tag=$TAG`
- [ ] Step 6: Add health check step with retry
- [ ] Step 7: Add rollback step: `if: failure()` → `helm rollback pole-ai --wait -n pole-ai-prod`

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Workflow file `.github/workflows/deploy-prod.yml` exists
- [ ] Workflow requires manual approval before deployment
- [ ] Helm upgrade deploys to PROD namespace with `--wait`
- [ ] Health check verifies pole-api is healthy post-deploy
- [ ] Auto-rollback triggers on failure (Helm release reverts)

## Integration Tests to Run (Local Verification)
- [ ] Run UC-04: PROD deploy with rollback on failure — trigger workflow, verify approval required and rollback works

## Dependencies
- **Blocks:** PAIML-INFRA-013 (documentation depends on this workflow existing)
- **Blocked By:** PAIML-INFRA-009 (prod environment must exist)

## Estimated Effort
- [M] (Medium < 4h)
