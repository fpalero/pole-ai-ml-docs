# Ticket: PAIML-INFRA-015

## Title
[Infrastructure] Create Health Check Verification Script

## Description
Create a standalone health check verification script that validates all services are healthy after a deploy. Can be used locally or in CI/CD workflows.

## What to Do (Implementation Steps)
- [ ] Step 1: Create `infrastracture/scripts/health-check.sh`
- [ ] Step 2: Check pole-api `/health` endpoint (retry with backoff)
- [ ] Step 3: Check pole-fe ingress responds (HTTP 200)
- [ ] Step 4: Check pole-analyst ingress responds (HTTP 200)
- [ ] Step 5: Check keycloak admin console responds
- [ ] Step 6: Exit 0 if all healthy, exit 1 if any fails
- [ ] Step 7: Add usage instructions to README

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Script `infrastracture/scripts/health-check.sh` exists and is executable
- [ ] Script checks all 4 services (pole-api, pole-fe, pole-analyst, keycloak)
- [ ] Script retries with backoff on transient failures
- [ ] Script exits 0 on success, 1 on failure
- [ ] Script is documented in README

## Integration Tests to Run (Local Verification)
- [ ] Deploy locally, run `./scripts/health-check.sh`, verify all checks pass

## Dependencies
- **Blocks:** None
- **Blocked By:** None (can create independently)

## Estimated Effort
- [S] (Small < 1h)
