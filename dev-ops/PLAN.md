# Implementation Plan - GitHub Actions CI/CD for the pole-ai Monorepo (dev-ops)

## 1. Feature Context & Objective
- **Goal:** Automate CI/CD for the `pole-ai` monorepo via GitHub Actions. When a developer pushes a branch and opens a PR, the workflows run the **unit tests related to the feature** and the **integration tests related to the affected components** (selected by tags embedded in commit messages). If tests pass and the review is positive, the PR can be merged. Additional **on-demand** workflows run the affected component's tests after each **phase** completes, and a **full-suite** run of every component's tests via the common tag `[pole-ai-ml]`. A **nightly** workflow in the docs repo (`pole-ai-ml-docs`) updates the Roadmap, flows, architecture, and user manual from the latest commits. Integration tests must run against **real components** (real database, real Redis, real Chroma, real MediaPipe), mocking as little as possible.
- **Non-Functional Constraints:**
  - Use GitHub's **default hosted-runner limits** (resources, timeouts, concurrency) — no custom budgets.
  - **Branch protection** enforced: required status checks + required reviews gate the merge.
  - Coverage threshold **≥80%** per app/package.
  - Tests must be repeatable and safe: all DB targets carry the `_testing` suffix; `scripts/guard-testing-db.sh` aborts any non-`_testing` run.
  - Real engines (MongoDB, Redis) as **service containers** in the runner; no Postgres in CI.
- **Affected Components (all):**
  - Apps: `pola_api` (FastAPI), `pole_fe` (Angular), `pole_analyst` (Angular), `pola_agent` (crew).
  - Packages: `pole-train-model` (`pole_ml`/`pole_tools`), `pole-crawler`, `pole-crop`, `jobs`, `chatbot`, `pole-tools`.
  - Infrastructure: MongoDB, Redis, Chroma DB, MediaPipe, ffmpeg.
  - Docs repo: `fpalero/pole-ai-ml-docs`.
- **Assumptions:**
  - GitHub Actions **tag-based selection** is driven by commit-message tags of the form `[component][slice]` (e.g., `[fe_pole][tricks_page]`), and the common tag `[pole-ai-ml]` selects the whole suite.
  - The PR workflow reads tags from the PR's commit messages (all head-branch commits), not just the PR title.
  - "Affected components" for a changed app is resolved by a static dependency graph defined in a shared CI helper script (e.g., `fe_pole` → tests `pole_api` integration; `pole_ml` → tests `pola_api`, `pole_analyst`, `pole_fe`, `chatbot`).
  - `E2E_FAKES=1` stays in use for the Angular Playwright E2E suites in the **PR and phase** runs (fake skeleton extraction). The **full-suite** run executes the E2E suites with **real MediaPipe** (no `E2E_FAKES`).
  - No secrets are committed; all credentials live in GitHub Actions secrets and local `.env` files (git-ignored).
  - Chroma persistence is a file-backed store; CI seeds it from a prepared snapshot (`backups/backup-20260805-160715/chromadb`).

## 2. Architectural Layering (The "Where")

### Domain
- **Component registry:** canonical mapping of tag component → app/package path + its test commands (unit / integration / e2e).
- **Tag schema:** `[component][slice]` and `[pole-ai-ml]` commit-message tags.
- **Dependency graph:** `component -> affected components` for integration/E2E selection.
- **Merge-gate policy:** required status checks + required reviews (branch protection).

### Application
- **Tag parser** (`scripts/ci/parse-tags.sh`): extracts `[..]` tokens from commit messages; validates against the component registry.
- **Affected resolver** (`scripts/ci/affected-components.sh`): maps a changed component to the set of components whose tests must run.
- **Test-suite selector** (`scripts/ci/test-selector.sh`): translates parsed tags into the concrete `pixi run` / npm commands per component.
- **Change detection:** skip workflow when no relevant files changed (paths filter + `paths-ignore`).

### Infrastructure
- **GitHub Actions workflows** (`.github/workflows/`): `pr-tests.yml`, `phase-tests.yml`, `full-suite-tests.yml`, `mediapipe-tests.yml`; docs workflow lives in `pole-ai-ml-docs`.
- **Service containers:** `mongodb` (mongo:latest) and `redis` (redis:7) via `services:` in the runner.
- **Artifact provisioning:** download/copy the `.keras` model, Chroma snapshot, Mongo seed, and sample videos before integration runs.
- **Secrets:** `OPENCODE_API_KEY` (chat), `POLE_AI_PAT` (docs repo read), plus optional DB/runner credentials.
- **Branch protection:** documented configuration (Settings → Branches → `main`).

### Presentation
- `workflow_dispatch` inputs for the on-demand workflows (affected app, components, optional `[pole-ai-ml]`).
- PR commit status / required check surfaced to the PR thread; clear error comments for bad tags.

## 3. Implementation Roadmap (Atomic Steps)

### Phase 1: CI Foundation (shared helpers + runner setup)
- [ ] Infra Create `scripts/ci/` helper scripts: `parse-tags.sh`, `affected-components.sh`, `test-selector.sh`, `check-changes.sh`, `retry.sh`.
- [ ] Domain Write the component registry (apps + packages + tag names + test commands) in `scripts/ci/components.sh`.
- [ ] Domain Define the dependency graph (affected components per changed component) in `affected-components.sh`.
- [ ] Infra Add `pixi run test-crop` (`pytest -v packages/pole-crop/tests`) and `pixi run test-crawler` (placeholder that exits 0/skips when no tests exist — crawler currently has no pytest suite) to `pixi.toml`.
- [ ] Infra Add a reusable composite action `.github/actions/run-tests/action.yml` encapsulating: checkout → pixi install → provision artifacts → run selected suite.
- [ ] Infra Add a reusable composite action for service containers + seed provisioning (Mongo seed, Chroma snapshot, model files).
- [ ] Infra Verify `pixi` install works on a `ubuntu-latest` runner (conda-forge + editable local packages).

### Phase 2: PR Workflow (`pr-tests.yml`)
- [ ] Application Trigger: `on: pull_request` (types: opened, synchronize, reopened).
- [ ] Application Parse commit-message tags from the PR head commits.
- [ ] Application Validate tags: unknown/missing component → fail with explicit error comment and set required check to failed.
- [ ] Application Resolve affected components from the tag component.
- [ ] Infrastructure Start MongoDB + Redis service containers; seed Chroma + Mongo; fetch `.keras` model and sample videos.
- [ ] Application Run unit tests of the tagged app + integration tests of the affected components.
- [ ] Infrastructure Upload pytest/Karma/Playwright reports as artifacts.
- [ ] Application Report a required check named `pr-tests` (success/failure) used by branch protection.

### Phase 3: Phase-Completion Workflow (`phase-tests.yml`)
- [ ] Application Trigger: `on: workflow_dispatch` with inputs `app` and `components` (or `[pole-ai-ml]`).
- [ ] Application Run all unit tests of the affected app + integration tests of the affected components (resolved by the dependency graph).
- [ ] Infrastructure Reuse the service-container + artifact provisioning from Phase 1.

### Phase 4: Full-Suite Workflow (`full-suite-tests.yml`)
- [ ] Application Trigger: `workflow_dispatch` and on commit messages containing `[pole-ai-ml]`.
- [ ] Application Run all unit + integration tests from **all** apps and packages.
- [ ] Infrastructure Parallel matrix per component (within GitHub limits); sequential fallback when the matrix is too heavy.
- [ ] Application Run the Angular E2E suites (`fe-e2e`, `pole-analyst-e2e`) with **real MediaPipe** (`E2E_FAKES` unset) in the full-suite run.
- [ ] Application Apply retry policy: infra failure → 2–3 restart attempts via `retry.sh`, then fail the run.

### Phase 5: MediaPipe Dedicated Action (`mediapipe-tests.yml`)
- [ ] Application Dedicated workflow/job running the real MediaPipe extraction tests (`packages/pole-train-model` skeleton extraction + real sample videos).
- [ ] Infrastructure Download `pose_landmarker_heavy.task`; no `E2E_FAKES`; fail on extraction errors.

### Phase 6: Nightly Docs Workflow (in `fpalero/pole-ai-ml-docs`)
- [ ] Application Workflow in the docs repo: `schedule` cron nightly + `workflow_dispatch`.
- [ ] Application Clone/checkout the latest `pole-ai-ml` monorepo (requires `POLE_AI_PAT`), inspect the latest commits/tags since the last run.
- [ ] Application Regenerate/update Roadmap, flows, architecture diagrams, user manual from the changed slices/phases; open a PR against the docs repo.
- [ ] Infrastructure Configure the docs-repo token secret.

### Phase 7: Branch Protection, Secrets & Documentation
- [ ] Infra Document and enable branch protection on `main`: required check `pr-tests`, ≥1 approving review.
- [ ] Infra Add secrets: `OPENCODE_API_KEY`, `POLE_AI_PAT`.
- [ ] Docs Update `docs/DEVELOPEMENT.md` and `docs/index.md` with the CI/CD workflow and the tag convention.
- [ ] Docs Add `docs/dev-ops/README.md` describing tag usage for developers.

## 4. Quality Gates & Testing Commands (DoD)
- **Unit Tests:**
  - `pixi run test` (packages/pole-train-model)
  - `pixi run test-api` (app/pola_api, pytest)
  - `pixi run test-jobs` (packages/jobs)
  - `pixi run test-chatbot` (packages/chatbot)
  - `pixi run test-hardening` (packages/pole-tools)
  - `pixi run test-crawler` (packages/pole-crawler — placeholder, skips when no tests) / `pixi run test-crop` (packages/pole-crop, `tests/test_ffmpeg.py`)
  - `npm run test` (app/pole_fe, app/pole_analyst — `ng test`)
- **Integration Tests:**
  - `pixi run test-integration` (aggregator: `test-api` + `test` + `test-chatbot-live` + `fe-e2e`) against `_testing` DBs guarded by `scripts/guard-testing-db.sh`.
  - `pixi run test-chatbot-live` (real Redis/Mongo/ffmpeg, scripted LLM)
  - `pixi run fe-e2e` / `pixi run pole-analyst-e2e` (Playwright) — `E2E_FAKES=1` in PR/phase runs; **real MediaPipe (no `E2E_FAKES`)** in the full-suite run
- **Automation:** GitHub Actions `pr-tests` required check; `phase-tests` and `full-suite-tests` on-demand; `mediapipe-tests`; nightly docs update.
- **Database Target:** `pole_api_testing`, `skeleton_data_testing`, `analysis_db_testing` (never prod `pole_api` / `skeleton_data` / `analysis_db`).
- **Coverage Requirement:** ≥80% per app/package (repo default; currently ~81.63% on pole-train-model).
- **Additional Checks:** shellcheck/`bash -n` on `scripts/ci/*`; actionlint on `.github/workflows`; secrets scan (no keys in code); keep `.env` git-ignored.

## 5. Defined Use Cases (Gherkin + Technical Matrix)

### UC-01: PR with a valid feature tag runs related tests and can be merged
- **Given** a developer pushes a branch and opens a PR whose commits carry `[fe_pole][tricks_page]`
- **When** the `pr-tests` workflow runs on `pull_request`
- **Then** the workflow runs `pole_fe` unit tests and the affected components' integration tests (resolved from the dependency graph, e.g., `pole_api`), reporting a `pr-tests` required check
- **And** once the check is green and a reviewer approves, the merge is enabled by branch protection

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `.github/workflows/pr-tests.yml` (event) |
| Request Method | `pull_request` (opened / synchronize / reopened) |
| Required Headers | `GITHUB_TOKEN` (permissions: contents: read, checks: write, pull-requests: write) |
| Payload Example | commit message `feat(pole_fe): tricks page (PAIML-FE-042)` `[fe_pole][tricks_page]` |
| DB State (Before) | ephemeral `_testing` DBs empty; service containers up |
| DB State (After) | `_testing` DBs cleaned by conftest (drop/delete) |

### UC-02: PR without a tag or with an unknown component fails and blocks the merge
- **Given** a PR whose commits have no tag or carry `[pole-ai]` (unknown component)
- **When** the `pr-tests` workflow parses the tags
- **Then** the workflow fails immediately, posts an explanatory comment (list of valid components), and sets the required check to failure
- **And** branch protection keeps the merge blocked until the tag is fixed

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `.github/workflows/pr-tests.yml` (event) |
| Request Method | `pull_request` |
| Required Headers | `GITHUB_TOKEN` |
| Payload Example | commit message `fix(pole_api): upload (PAIML-POLA-API-040)` (no tag) |
| DB State (Before) | not started (fail fast) |
| DB State (After) | unchanged |

### UC-03: Infrastructure failure is retried and then fails the run
- **Given** a MongoDB/Redis service container fails to become healthy during a workflow
- **When** the runner's retry helper detects the failed startup
- **Then** the workflow retries 2–3 times; if still failing it fails the run with a clear infrastructure error
- **And** no test is reported as a flaky/false failure — the status is marked failed

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `scripts/ci/retry.sh` |
| Request Method | bash (health-check loop) |
| Required Headers | `MONGODB_URI`, `REDIS_URL` env vars |
| Payload Example | `retry.sh 3 'bash scripts/ci/wait-healthy.sh'` |
| DB State (Before) | containers starting |
| DB State (After) | failed run, containers stopped |

### UC-04: No relevant changes cause a graceful skip
- **Given** a PR that only touches files outside the tested components (e.g., `docs/`, `README.md`)
- **When** the change-detection step runs
- **Then** the workflow reports success (or is skipped) without running the test suite
- **And** the required check passes (no false failure)

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `scripts/ci/check-changes.sh` |
| Request Method | bash (git diff / paths filter) |
| Required Headers | `GITHUB_TOKEN` |
| Payload Example | changed files: `docs/DEVELOPEMENT.md` only |
| DB State (Before) | none |
| DB State (After) | none |

### UC-05: Full-suite run triggered by the common tag `[pole-ai-ml]`
- **Given** a commit or on-demand dispatch carrying the common tag `[pole-ai-ml]`
- **When** the `full-suite-tests.yml` workflow runs
- **Then** all apps and packages run their unit and integration tests (matrix per component, within GitHub limits)
- **And** the run fails only if a component genuinely fails

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | `.github/workflows/full-suite-tests.yml` |
| Request Method | `workflow_dispatch` or commit tag `[pole-ai-ml]` |
| Required Headers | `GITHUB_TOKEN` |
| Payload Example | commit message `refactor(pole_ml): embeddings [pole-ai-ml]` |
| DB State (Before) | `_testing` DBs empty, seeded service containers |
| DB State (After) | `_testing` DBs cleaned |

### UC-06: Nightly docs update reflects latest monorepo commits
- **Given** the nightly schedule fires in `pole-ai-ml-docs` (or a manual dispatch)
- **When** the docs workflow clones `pole-ai-ml` and checks the latest commits/tags
- **Then** it updates the Roadmap, flows, architecture diagrams, and user manual and opens a docs PR
- **And** it requires the `POLE_AI_PAT` secret to clone/read the monorepo

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | docs repo `.github/workflows/docs-nightly.yml` |
| Request Method | `schedule` (nightly cron) / `workflow_dispatch` |
| Required Headers | `POLE_AI_PAT` |
| Payload Example | cron `0 2 * * *` |
| DB State (Before) | none |
| DB State (After) | docs PR opened on `pole-ai-ml-docs` |

## 6. Risks and Mitigations
- **Risk:** Heavy full-suite runs exceed GitHub runner time limits. **Mitigation:** parallel matrix per component; keep MediaPipe in its own action; add per-job `timeout-minutes`.
- **Risk:** Tag-based selection runs too few or too many tests (missing dependency mapping). **Mitigation:** central dependency graph in `affected-components.sh`, reviewed against the architecture docs; fallback to `[pole-ai-ml]` for ambiguity.
- **Risk:** Integration tests touch production DBs. **Mitigation:** reuse `scripts/guard-testing-db.sh` in every integration step; conftest `_testing` guard; service containers are ephemeral and destroyed after each run.
- **Risk:** Chroma snapshot/model artifacts grow stale or missing. **Mitigation:** versioned artifact step re-seeds from `backups/backup-20260805-160715/chromadb` + `packages/pole-train-model/models/lstm_model_normal_final.keras`; fail loudly if a required artifact is absent.
- **Risk:** AI-token-secret required for chat tests but absent → tests skipped silently. **Mitigation:** chat live tests are conditional on `OPENCODE_API_KEY`; PR check documents the skip explicitly in the job summary.
- **Risk:** Secrets/keys committed by accident. **Mitigation:** keep `.env` git-ignored, run secret scanning, and only reference `secrets.*`.
- **Risk:** Nightly docs workflow can't read the monorepo without auth. **Mitigation:** `POLE_AI_PAT` secret with read-only `contents` scope on `pole-ai-ml`.

## 7. Open Questions and Decisions
- **Decision:** DB strategy is **service containers** (real engines, ephemeral) — confirmed by PO.
- **Decision:** Merge gating via **branch protection** (required `pr-tests` check + ≥1 review) — confirmed.
- **Decision:** Coverage threshold **≥80%** — confirmed.
- **Decision:** MediaPipe gets its own dedicated action — confirmed.
- **Decision (resolved):** `E2E_FAKES=1` for the Angular E2E suites in **PR and phase** runs; the **full-suite** run uses **real MediaPipe** (no fakes).
- **Decision (resolved):** `pole-crawler` and `pole-crop` are **included** in the workflows with minimal tasks: `pixi run test-crop` (real pytest) and `pixi run test-crawler` (skip-when-empty placeholder).
- **Decision (resolved):** Nightly docs workflow lives **in `pole-ai-ml-docs`**: it clones `pole-ai-ml`, checks the latest commits/tags, and updates Roadmap/flows/architecture/manual via a PR. Uses `POLE_AI_PAT` to read the monorepo.
