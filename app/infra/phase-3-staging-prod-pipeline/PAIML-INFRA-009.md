# Ticket: PAIML-INFRA-009

## Title
[Infrastructure] Create GitHub Environment `prod`

## Description
Create the GitHub Environment `prod` with manual approval protection. Deployment to PROD requires explicit approval from a required reviewer.

## What to Do (Implementation Steps)
- [ ] Step 1: Create GitHub Environment `prod` via `gh` CLI or GitHub UI
- [ ] Step 2: Add protection rule: required reviewers (1 reviewer minimum)
- [ ] Step 3: Configure environment variables: `NAMESPACE=pole-ai-prod`, `RELEASE_NAME=pole-ai`
- [ ] Step 4: Add kubeconfig secret for production k3s cluster access

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] GitHub Environment `prod` exists with protection rules
- [ ] Required reviewers configured (at least 1)
- [ ] `KUBECONFIG` secret is configured for production cluster
- [ ] Environment variables are set

## Integration Tests to Run (Local Verification)
- [ ] Verify environment appears in `gh api repos/{owner}/{repo}/environments` with protection rules

## Dependencies
- **Blocks:** PAIML-INFRA-010 (deploy-prod workflow needs this environment)
- **Blocked By:** None (can create independently)

## Estimated Effort
- [S] (Small < 1h)
