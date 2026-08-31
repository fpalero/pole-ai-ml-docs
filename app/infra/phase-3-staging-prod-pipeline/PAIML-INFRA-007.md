# Ticket: PAIML-INFRA-007

## Title
[Infrastructure] Create GitHub Environment `staging`

## Description
Create the GitHub Environment `staging` with manual gate protection. Deployment to STAGING requires manual approval from a required reviewer before proceeding.

## What to Do (Implementation Steps)
- [ ] Step 1: Create GitHub Environment `staging` via `gh` CLI or GitHub UI
- [ ] Step 2: Add protection rule: required reviewers (1 reviewer minimum)
- [ ] Step 3: Configure environment variables: `NAMESPACE=pole-ai-staging`, `RELEASE_NAME=pole-ai`
- [ ] Step 4: Add kubeconfig secret for staging k3s cluster access

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] GitHub Environment `staging` exists with protection rules
- [ ] Required reviewers configured (at least 1)
- [ ] `KUBECONFIG` secret is configured for staging cluster
- [ ] Environment variables are set

## Integration Tests to Run (Local Verification)
- [ ] Verify environment appears in `gh api repos/{owner}/{repo}/environments` with protection rules

## Dependencies
- **Blocks:** PAIML-INFRA-008 (deploy-staging workflow needs this environment)
- **Blocked By:** None (can create independently)

## Estimated Effort
- [S] (Small < 1h)
