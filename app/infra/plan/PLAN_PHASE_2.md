# Plan Phase 2 — Build & Push to GHCR

> **Parent plan:** [PLAN.md](../PLAN.md)
> **Status:** 📋 PLANNED

## Scope

Create a GitHub Actions workflow that builds Docker images for pole-api, pole-fe, and pole-analyst on push to main or develop, scans them with Trivy, and pushes them to GitHub Container Registry (ghcr.io) with deterministic tags.

## Tasks

1. Create `.github/workflows/build-push.yml` with `on: push` to main or develop trigger
2. Configure Docker layer caching using `actions/cache` for pixi, npm, uv
3. Implement image tagging strategy: SHA + branch + semver
4. Integrate Trivy security scan (CRITICAL + HIGH severity)
5. Push images to ghcr.io using `docker/build-push-action`

## Dependencies

- **Blocked By:** Phase 1 (Helm charts + Dockerfiles must exist)
- **Blocks:** Phase 3 (DEV deploy needs images in GHCR)

## Acceptance Criteria

- [ ] `build-push.yml` triggers on push to main or develop
- [ ] Images built and pushed to ghcr.io with SHA, branch, and semver tags
- [ ] Docker layer caching reduces build time by ≥50%
- [ ] Trivy scan runs and reports results (initially advisory, not blocking)
- [ ] All three images (pole-api, pole-fe, pole-analyst) are available in GHCR

## Use Cases Validated

- UC-01: Merge to main triggers build and push to GHCR
