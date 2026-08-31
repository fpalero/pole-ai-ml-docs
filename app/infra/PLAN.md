# Implementation Plan — `infra` (CI/CD Deployment Pipeline)

> **Status:** Phases 1–2 largely landed in code (build-push GitHub Action + deploy workflows).
> Phases 3–8 📋 PLANNED — Phases 3–5 ticketed, Phases 6–8 (`elastic-stack`, `pole-api-logs`,
> `packages-logs`) ticketed but not implemented. 24 tickets total (`PAIML-INFRA-001..024`),
> 8 phase folders (`phase-1-ghcr-build-push` … `phase-8-packages-logs`).

---

## 1. Feature Context & Objective

- **Goal:** Automate CI/CD for the `pole-ai` monorepo — build Docker images, push to GHCR, and deploy to DEV/STAGING/PROD via Helm on k3s. Complete the improved flow defined in `docs/diagrams/infra/INFRA.md`.
- **Non-Functional Constraints:**
  - GitHub Actions for CI/CD; GitHub-hosted runners for lint/test, self-hosted for Docker builds
  - GHCR (ghcr.io) as container registry; deterministic image tags (SHA + branch + semver)
  - Helm (`helm upgrade --wait`) for all deploys; `infrastracture/` repo owns charts
  - Health checks post-deploy; auto-rollback on failure; Slack notifications
  - Trivy for container security scanning; ≥80% test coverage (existing)
  - GitHub Environments with protection rules for STAGING and PROD
- **Affected Components:**
  - `infrastracture/helm/pole-ai/` — umbrella Helm chart with subcharts (pole-api, pole-fe, pole-analyst, mongodb, redis, keycloak)
  - `infrastracture/scripts/` — build-push.sh, deploy.sh, teardown.sh (already exist)
  - `.github/workflows/` — new CI/CD workflows (build-push, deploy-dev, deploy-staging, deploy-prod)
  - `infrastracture/k3s/registries.yaml` — registry mirror config (exists)
  - `app/pole_api/docker/Dockerfile`, `app/pole_fe/docker/Dockerfile`, `app/pole_analyst/docker/Dockerfile` — existing Dockerfiles
- **Assumptions:**
  - Helm charts are already fully functional for local k3s deployment
  - Dockerfiles for all three apps already exist and build correctly
  - The existing `scripts/build-push.sh` and `scripts/deploy.sh` work locally; CI adapts them for GHCR + multi-env
  - Keycloak, MongoDB, Redis are managed by the umbrella chart; no external managed services
  - `pole-fe` and `pole-analyst` are static bundles served by nginx with API proxying

## 2. Architectural Layering (The "Where")

- **Domain:** Image tag strategy (SHA + branch + semver), deployment environment model (DEV/STAGING/PROD), Helm release lifecycle, health check contract, rollback policy
- **Application:** GitHub Actions workflow orchestration (build → scan → push → deploy → verify → notify), environment protection rules, Helm upgrade commands
- **Infrastructure:** GHCR registry, k3s cluster, Trivy scanner, Slack webhook, GitHub Environments, self-hosted runners for Docker builds
- **Presentation:** GitHub Actions workflow run status, Slack notifications, PR/commit status checks

## 3. Implementation Roadmap (Atomic Steps)

### Phase 1: Helm Charts & Local Deploy (Foundation)
- ✅ Umbrella chart (`helm/pole-ai/`) with 6 subcharts (mongodb, redis, keycloak, pole-api, pole-fe, pole-analyst)
- ✅ `scripts/build-push.sh` — local Docker build + push to localhost:5000
- ✅ `scripts/deploy.sh` — `helm upgrade --install` with values-local.yaml overlay
- ✅ `scripts/teardown.sh` — `helm uninstall` + optional PVC cleanup
- ✅ `k3s/registries.yaml` — containerd mirror for insecure local registry
- ✅ Health probes (readiness + liveness) in all deployment templates
- ✅ ConfigMaps, Secrets, PVCs, Ingress (Traefik) configured

### Phase 2: Build & Push to GHCR
- [ ] [Infrastructure] `.github/workflows/build-push.yml` — workflow triggered on push to main or develop
- [ ] [Infrastructure] Docker layer caching with `actions/cache` for pixi, npm, uv
- [ ] [Infrastructure] Image tagging: `type=sha`, `type=ref,event=branch`, `type=semver`
- [ ] [Infrastructure] Trivy security scan on built images (severity CRITICAL,HIGH)

### Phase 3: DEV Auto-Deploy
- [ ] [Infrastructure] GitHub Environment `dev` (auto-deploy, no protection rules)
- [ ] [Infrastructure] `.github/workflows/deploy-dev.yml` — auto-deploy on push to main or develop after build-push
- [ ] [Infrastructure] Helm upgrade with `--wait` + health check verification

### Phase 4: STAGING & PROD Pipelines
- [ ] [Infrastructure] GitHub Environment `staging` (manual gate, 1 required reviewer)
- [ ] [Infrastructure] `.github/workflows/deploy-staging.yml` — triggered after DEV deploy succeeds
- [ ] [Infrastructure] GitHub Environment `prod` (manual approval, 1 required reviewer)
- [ ] [Infrastructure] `.github/workflows/deploy-prod.yml` — `helm upgrade --wait` + auto-rollback on failure
- [ ] [Infrastructure] Slack notification on deploy success/failure

### Phase 5: Documentation & Health Verification
- [ ] [Documentation] Document GitHub Environment protection rules and secrets
- [ ] [Documentation] Update `infrastracture/README.md` with CI/CD pipeline documentation
- [ ] [Infrastructure] Health check verification script for post-deploy validation


### Phase 6: Elasticsearch + Kibana foundation in k3s
- [ ] Add Elasticsearch subchart to umbrella Helm chart with single-node config, PVC, health probes.
- [ ] Configure ILM 7-day retention (see PAIML-INFRA-017).
- [ ] Set up Kibana ingress at pole-kibana.duckdns.org with TLS and Keycloak SSO (see PAIML-INFRA-018).
- [ ] Verify `_cluster/health` and ingress access.

### Phase 7: Structured logging in pole_api
- [ ] Add python-json-logger dependency and JSON formatter (see PAIML-INFRA-019).
- [ ] Configure LOG_LEVEL and LOG_SERVICE_NAME env vars (see PAIML-INFRA-020).
- [ ] Update caplog tests and add JSON format verification (see PAIML-INFRA-021).

### Phase 8: Structured logging in packages + shipping
- [ ] Create shared logging utility in pole_tools (see PAIML-INFRA-022).
- [ ] Migrate pole_ml, pole_crawler, pole_jobs to shared JSON logger (see PAIML-INFRA-023).
- [ ] Deploy Filebeat DaemonSet for log shipping to ES (see PAIML-INFRA-024).
## 4. Quality Gates & Testing Commands (DoD)

- **Unit Tests:** Existing — `pixi run test` (≥80% coverage)
- **Integration Tests:** Existing — Playwright E2E, `pixi run test-integration`
- **Infrastructure Tests:** Helm template lint (`helm lint`), dry-run deploy (`helm upgrade --dry-run`)
- **Automation:** GitHub Actions workflows; required checks via branch protection
- **Security:** Trivy scan on Docker images (CRITICAL + HIGH severity)
- **Database Target:** N/A (CI/CD infrastructure only, no DB changes)
- **Coverage Requirement:** ≥80% (existing, no changes)
- **Additional Checks:** `actionlint` on workflow files; `shellcheck` on scripts

## 5. Defined Use Cases (Gherkin + Technical Matrix)

### UC-01: Merge to main triggers build and push to GHCR
- **Given** a PR is approved and merged to main
- **When** the `build-push.yml` workflow runs
- **Then** Docker images for pole-api, pole-fe, pole-analyst are built and pushed to ghcr.io with deterministic tags
- **And** Trivy scans pass (no CRITICAL/HIGH vulnerabilities)

| Technical Check | Expected Value |
| :--- | :--- |
| Workflow File | `.github/workflows/build-push.yml` |
| Trigger | `push` to `main` or `develop` |
| Images | `ghcr.io/<owner>/pole-api:<tag>`, `ghcr.io/<owner>/pole-fe:<tag>`, `ghcr.io/<owner>/pole-analyst:<tag>` |
| Tag Format | `sha-<7chars>`, `main`, `develop`, `v1.2.3` (semver) |
| Registry | `ghcr.io` |
| Required Secrets | `GITHUB_TOKEN` (automatic) |

### UC-02: DEV environment auto-deploys after successful build
- **Given** images are successfully pushed to GHCR
- **When** the `deploy-dev.yml` workflow runs
- **Then** Helm upgrade deploys to the DEV k3s cluster with `--wait`
- **And** health check confirms pole-api `/health` returns 200

| Technical Check | Expected Value |
| :--- | :--- |
| Workflow File | `.github/workflows/deploy-dev.yml` |
| Trigger | `workflow_run` (after build-push succeeds) or `workflow_call` |
| Environment | `dev` (no protection rules) |
| Helm Command | `helm upgrade --install pole-ai ./helm/pole-ai -n pole-ai --wait` |
| Health Check | `curl -f http://api.pole.local/health` |

### UC-03: STAGING deploy requires manual gate
- **Given** DEV deploy succeeds
- **When** a maintainer triggers `deploy-staging.yml`
- **Then** deployment proceeds only after manual approval in GitHub Environment
- **And** Helm upgrade deploys to STAGING with `--wait`

| Technical Check | Expected Value |
| :--- | :--- |
| Workflow File | `.github/workflows/deploy-staging.yml` |
| Trigger | `workflow_dispatch` |
| Environment | `staging` (1 required reviewer) |
| Helm Command | `helm upgrade --install pole-ai ./helm/pole-ai -n pole-ai-staging --wait` |

### UC-04: PROD deploy with rollback on failure
- **Given** STAGING deploy succeeds and is verified
- **When** a maintainer triggers `deploy-prod.yml` and approves
- **Then** Helm upgrade deploys to PROD with `--wait`
- **And** on failure, `helm rollback` reverts to the previous release

| Technical Check | Expected Value |
| :--- | :--- |
| Workflow File | `.github/workflows/deploy-prod.yml` |
| Trigger | `workflow_dispatch` |
| Environment | `prod` (1 required reviewer) |
| Helm Command | `helm upgrade --install pole-ai ./helm/pole-ai -n pole-ai-prod --wait` |
| Rollback | `helm rollback pole-ai --wait` on failure |

### UC-05: Slack notification on deploy outcome
- **Given** any deploy workflow completes (success or failure)
- **When** the notification job runs
- **Then** a Slack message is posted with deploy status, commit SHA, and environment

| Technical Check | Expected Value |
| :--- | :--- |
| Action | `slackapi/slack-github-action@v1` |
| Secret | `SLACK_WEBHOOK_URL` |
| Payload | `{"text": "Deploy <status>: <sha> to <env>"}` |

## 6. Risks and Mitigations

- **Risk:** GHCR image size exceeds limits or build times out. **Mitigation:** Multi-stage Dockerfiles (already in use); Docker layer caching; self-hosted runners for heavy builds.
- **Risk:** Helm `--wait` hangs due to pending PVC or unhealthy pod. **Mitigation:** Recreate strategy for pole-api (already configured); timeout limits on Helm commands; health check retries.
- **Risk:** Trivy blocks deployment on existing vulnerabilities. **Mitigation:** Start with `--severity HIGH,CRITICAL` and `--exit-code 1`; add exceptions for known acceptable risks; scan in a separate non-blocking step initially.
- **Risk:** GitHub Environment protection rules prevent auto-merge. **Mitigation:** Only PROD requires approval; DEV is auto-deploy; document the approval workflow.
- **Risk:** Keycloak realm config not synced across environments. **Mitigation:** Helm chart includes keycloak subchart with realm config; values per environment override as needed.

## 7. Open Questions and Decisions

- **Decision:** Helm (not Kustomize) for all deployments — confirmed by PO.
- **Decision:** GHCR as primary registry — confirmed by PO.
- **Decision:** DEV auto-deploy, STAGING manual gate, PROD manual approval — confirmed by PO.
- **Decision:** Slack notifications for deploy outcomes — confirmed by PO.
- **Decision:** Keep existing health probes (readiness + liveness) in Helm charts — already implemented.
- **Open:** Should `build-push.yml` run on self-hosted or GitHub-hosted runners? (Recommendation: self-hosted for Docker builds per INFRA.md suggestion 8)
- **Open:** Should Trivy scan be blocking or advisory initially? (Recommendation: advisory first, then blocking after baseline is established)
