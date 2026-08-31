# Ticket: PAIML-INFRA-001

## Title
[Infrastructure] Create GHCR Build & Push Workflow

## Description
Create the GitHub Actions workflow that builds Docker images for pole-api, pole-fe, and pole-analyst on every merge to main, and pushes them to GitHub Container Registry (ghcr.io). This is the foundation of the CI/CD pipeline — all deployment phases depend on images being available in GHCR.

## What to Do (Implementation Steps)
- [ ] Step 1: Create `.github/workflows/build-push.yml` with `on: push` trigger on `main` branch
- [ ] Step 2: Add job to checkout code (actions/checkout@v4)
- [ ] Step 3: Add Docker Buildx setup (docker/setup-buildx-action@v3)
- [ ] Step 4: Add GHCR login (docker/login-action@v3 with `GITHUB_TOKEN`)
- [ ] Step 5: Build and push pole-api image using `docker/build-push-action@v5` with `app/pole_api/docker/Dockerfile`
- [ ] Step 6: Build and push pole-fe image using `app/pole_fe/docker/Dockerfile`
- [ ] Step 7: Build and push pole-analyst image using `app/pole_analyst/docker/Dockerfile`
- [ ] Step 8: Use `docker/metadata-action@v5` for deterministic tags (SHA + branch + semver)
- [ ] Step 9: Configure GitHub Actions cache for Docker layers (`type=gha`)

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Workflow file `.github/workflows/build-push.yml` exists and is valid YAML
- [ ] Workflow triggers on push to main
- [ ] All three images are built and pushed to ghcr.io
- [ ] Images have deterministic tags: `sha-<7chars>`, `main`, and branch name
- [ ] Docker layer caching is configured and reduces subsequent build times

## Integration Tests to Run (Local Verification)
- [ ] Run UC-01: Merge to main triggers build and push to GHCR — verify via `gh workflow run build-push.yml` or push to main

## Dependencies
- **Blocks:** PAIML-INFRA-005 (DEV deploy needs images)
- **Blocked By:** None (can start immediately)

## Estimated Effort
- [M] (Medium < 4h)
