# Ticket: PAIML-INFRA-006

## Title
[Infrastructure] Add Health Check Verification to Deploy Workflow

## Description
Add health check verification step to the DEV deploy workflow. After Helm upgrade completes, verify that all services are healthy by checking the pole-api `/health` endpoint.

## What to Do (Implementation Steps)
- [ ] Step 1: Add health check step after Helm upgrade in deploy-dev.yml
- [ ] Step 2: Use `curl -f --retry 5 --retry-delay 10 http://<endpoint>/health`
- [ ] Step 3: Configure endpoint based on environment (local vs. remote k3s)
- [ ] Step 4: Add timeout and retry logic for slow-starting services

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Health check step runs after Helm upgrade
- [ ] Health check retries up to 5 times with 10s delay
- [ ] Health check fails the workflow if pole-api is not healthy
- [ ] Health check output is visible in GitHub Actions logs

## Integration Tests to Run (Local Verification)
- [ ] Deploy to DEV, verify health check step passes and reports 200

## Dependencies
- **Blocks:** None
- **Blocked By:** PAIML-INFRA-005 (deploy-dev workflow must exist first)

## Estimated Effort
- [S] (Small < 1h)
