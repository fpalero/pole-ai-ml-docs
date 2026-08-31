# Ticket: PAIML-INFRA-003

## Title
[Infrastructure] Add Trivy Security Scan to Build Workflow

## Description
Integrate Trivy security scanning into the build-push workflow to scan Docker images for vulnerabilities before pushing to GHCR. Initially advisory (non-blocking) to establish a baseline.

## What to Do (Implementation Steps)
- [ ] Step 1: Add `aquasecurity/trivy-action@master` step after each image build
- [ ] Step 2: Configure scan for severity `CRITICAL,HIGH`
- [ ] Step 3: Set output format to `table` for GitHub Actions summary
- [ ] Step 4: Initially configure as non-blocking (`continue-on-error: true` or separate step)
- [ ] Step 5: Add scan results to GitHub Actions job summary

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Trivy scan runs on all three images (pole-api, pole-fe, pole-analyst)
- [ ] Scan results appear in GitHub Actions job summary
- [ ] Scan is advisory (does not block deployment initially)
- [ ] CRITICAL and HIGH vulnerabilities are reported

## Integration Tests to Run (Local Verification)
- [ ] Run build-push workflow, verify Trivy scan output in Actions summary

## Dependencies
- **Blocks:** None
- **Blocked By:** PAIML-INFRA-001 (build-push workflow must exist first)

## Estimated Effort
- [S] (Small < 1h)
