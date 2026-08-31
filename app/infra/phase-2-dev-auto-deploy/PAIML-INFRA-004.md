# Ticket: PAIML-INFRA-004

## Title
[Infrastructure] Create GitHub Environment `dev`

## Description
Create the GitHub Environment `dev` for automatic deployments. This environment has no protection rules — deployments happen automatically after a successful build.

## What to Do (Implementation Steps)
- [ ] Step 1: Create GitHub Environment `dev` via `gh` CLI or GitHub UI
- [ ] Step 2: Configure environment variables: `NAMESPACE=pole-ai`, `RELEASE_NAME=pole-ai`
- [ ] Step 3: Add kubeconfig secret for k3s cluster access
- [ ] Step 4: Verify environment is available to workflows

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] GitHub Environment `dev` exists in repository settings
- [ ] No protection rules configured (auto-deploy)
- [ ] `KUBECONFIG` secret is configured
- [ ] Environment variables `NAMESPACE` and `RELEASE_NAME` are set

## Integration Tests to Run (Local Verification)
- [ ] Verify environment appears in `gh api repos/{owner}/{repo}/environments` response

## Dependencies
- **Blocks:** PAIML-INFRA-005 (deploy-dev workflow needs this environment)
- **Blocked By:** None (can create independently)

## Estimated Effort
- [S] (Small < 1h)
