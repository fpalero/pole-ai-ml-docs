# Ticket: PAIML-INFRA-002

## Title
[Infrastructure] Add Docker Layer Caching to Build Workflow

## Description
Configure Docker layer caching in the build-push workflow to reduce build times by ≥50%. Cache pixi, npm, and uv dependency layers across workflow runs.

## What to Do (Implementation Steps)
- [ ] Step 1: Add `actions/cache@v4` step before Docker build
- [ ] Step 2: Configure cache paths: `~/.cache/pixi`, `~/.npm`, `~/.cache/uv`
- [ ] Step 3: Set cache key: `${{ runner.os }}-deps-${{ hashFiles('pixi.lock', '**/package-lock.json') }}`
- [ ] Step 4: Configure Docker Buildx cache export/import (`type=gha` or `type=registry`)
- [ ] Step 5: Verify cache hit on second run reduces build time

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] `actions/cache@v4` step exists in build-push workflow
- [ ] pixi, npm, uv caches are restored on cache hit
- [ ] Docker Buildx uses GitHub Actions cache backend
- [ ] Second workflow run shows ≥50% build time reduction

## Integration Tests to Run (Local Verification)
- [ ] Run build-push workflow twice, compare build times between first (cold) and second (warm) run

## Dependencies
- **Blocks:** None
- **Blocked By:** PAIML-INFRA-001 (build-push workflow must exist first)

## Estimated Effort
- [S] (Small < 1h)
