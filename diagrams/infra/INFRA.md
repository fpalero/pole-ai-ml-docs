# CI/CD Infrastructure Plan

## Current Proposed Flow

```
PR → Unit Tests → OpenCode Review → Merge → Integration Tests → Docker Build → Deploy k3s
```

## Improved Flow

```
┌─────────────────────────────────────────────────────────┐
│  PR Created/Updated                                     │
│  ├── Lint + Type Check + Unit Tests (GitHub-hosted)     │
│  ├── OpenCode Review (self-hosted)                      │
│  └── Auto-merge if approved + CI passes                 │
├─────────────────────────────────────────────────────────┤
│  Merge to main                                          │
│  ├── Smoke Tests (Docker Compose, <5min)                │
│  ├── Build Docker Images (self-hosted)                  │
│  ├── Push to Registry (GHCR/DockerHub)                  │
│  ├── Trivy Security Scan                                │
│  ├── Deploy to DEV (auto)                               │
│  └── Full Integration Tests (Playwright/Cypress)        │
├─────────────────────────────────────────────────────────┤
│  Manual Approval Gate (GitHub Environment)              │
│  ├── Deploy to STAGING                                  │
│  ├── E2E Tests on Staging                               │
│  ├── Manual Approval                                    │
│  └── Deploy to PROD (Helm upgrade --wait)               │
├─────────────────────────────────────────────────────────┤
│  Post-Deploy                                            │
│  ├── Health Check + Rollback on failure                 │
│  └── Notify Slack                                       │
└─────────────────────────────────────────────────────────┘
```

---

## Suggestions

### 1. Add Quality Gates Before Review

Add lint and type check steps before the OpenCode review to catch syntax/style issues before wasting AI review tokens on trivial fixes.

- **Backend:** `ruff check`, `mypy`, `pytest --cov`
- **Frontend (Angular):** `ng lint`, `ng test --code-coverage`
- **Frontend (Next.js):** `next lint`, `tsc --noEmit`, `jest`

### 2. Split Integration Tests into Two Stages

Split into smoke tests (fast, <5min) and full integration tests. Don't build Docker images if basic integration tests fail.

### 3. Add Image Tagging Strategy

Use deterministic tags instead of only `latest`:

```yaml
tags: |
  type=sha,prefix=        # commit SHA (e.g., a1b2c3d)
  type=ref,event=branch   # branch name
  type=semver,pattern={{version}}  # for releases
```

Rollback requires knowing exactly which image runs in production.

### 4. Add Deployment Environments

Use GitHub Environments with protection rules for prod deployments.

```
Merge → Tests → Build → Deploy to DEV (auto)
                          → Deploy to STAGING (manual gate)
                            → Deploy to PROD (manual approval)
```

### 5. Add Post-Deployment Verification

Detect broken deployments immediately, not from user reports.

```yaml
- name: Health check
  run: curl -f http://<service>/health || exit 1
```

### 6. Add Rollback Strategy

```yaml
- name: Rollback on failure
  if: failure()
  run: helm rollback <release> --wait
```

Automated rollback prevents prolonged outages.

### 7. Cache Dependencies

Cache `pixi`, `npm`, and `uv` to cut PR feedback time by 50-70%.

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pixi
      ~/.npm
      ~/.cache/uv
    key: ${{ runner.os }}-deps-${{ hashFiles('pixi.lock', 'package-lock.json') }}
```

### 8. Use Self-Hosted Runners for Heavy Jobs

- **Self-hosted:** Docker builds, integration tests (need Docker Compose)
- **GitHub-hosted:** Lint, unit tests, type checks (cheap, fast)

### 9. Add Security Scanning

```yaml
# Trivy for Docker images
- name: Scan Docker image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.IMAGE }}
    severity: CRITICAL,HIGH

# Bandit for Python SAST
- name: Run Bandit (Python)
  run: bandit -r backend/ -f json -o bandit-report.json
```

### 10. Add Notification Strategy

```yaml
# On failure:
- uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {"text": "Deploy failed: ${{ github.sha }}"}

# On success to prod:
- uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {"text": "v1.2.3 deployed to production"}
```

---

## Quick Wins

| Priority | Action | Impact |
|----------|--------|--------|
| **High** | Add caching for pixi/npm/uv | -60% build time |
| **High** | Add lint step before review | -AI cost |
| **High** | Use GHCR (ghcr.io) for images | Free for public repos |
| **Medium** | Split smoke vs full integration | Faster feedback |
| **Medium** | Add GitHub Environments for prod | Safety gate |
| **Low** | Add Trivy scanning | Security |

---

## Tech Stack Reference

| Layer | Tech |
|-------|------|
| CI/CD | GitHub Actions |
| Container Registry | GHCR / DockerHub |
| Orchestration | k3s + Helm |
| Frontend | Angular 22, Next.js 15 |
| Backend | Python 3.12, FastAPI |
| ML | TensorFlow, MediaPipe |
| Databases | MongoDB 7, Redis 7, PostgreSQL 16 |
| Auth | Keycloak (OIDC) |
| Monitoring | Prometheus + Grafana (planned) |
