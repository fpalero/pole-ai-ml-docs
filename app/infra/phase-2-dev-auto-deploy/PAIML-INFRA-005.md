# Ticket: PAIML-INFRA-005

## Title
[Infrastructure] Create DEV Auto-Deploy Workflow

## Description
Create the GitHub Actions workflow that automatically deploys to the DEV environment after images are pushed to GHCR. Uses Helm upgrade with `--wait` to ensure all pods are healthy.

## What to Do (Implementation Steps)
- [ ] Step 1: Create `.github/workflows/deploy-dev.yml` with `workflow_run` trigger (after build-push succeeds) or `workflow_call` from build-push
- [ ] Step 2: Add job to checkout `infrastracture/` repo (or the main repo with charts)
- [ ] Step 3: Add Helm setup step (azure/setup-helm@v3)
- [ ] Step 4: Add kubectl/kubeconfig setup step
- [ ] Step 5: Add Helm upgrade step: `helm upgrade --install pole-ai ./helm/pole-ai -n pole-ai --create-namespace --wait --set global.registry=ghcr.io/<owner> --set poleApi.tag=$TAG --set poleFe.tag=$TAG --set poleAnalyst.tag=$TAG`
- [ ] Step 6: Add health check step: `curl -f http://<dev-endpoint>/health || exit 1`

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Workflow file `.github/workflows/deploy-dev.yml` exists
- [ ] Workflow triggers automatically after build-push succeeds
- [ ] Helm upgrade deploys all services to DEV namespace
- [ ] Health check confirms pole-api `/health` returns 200
- [ ] Deploy status is reported in GitHub Actions

## Integration Tests to Run (Local Verification)
- [ ] Run UC-02: DEV environment auto-deploys after successful build — trigger build-push, verify deploy-dev runs

## Dependencies
- **Blocks:** PAIML-INFRA-007 (STAGING deploy depends on DEV working)
- **Blocked By:** PAIML-INFRA-001 (images must be in GHCR), PAIML-INFRA-004 (dev environment must exist)

## Estimated Effort
- [M] (Medium < 4h)
