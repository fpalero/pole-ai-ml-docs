# Testing Guide — pole-ai monorepo

Reference of every test type in the repo: what each one covers, when to run it,
and roughly how many tests each has. All commands run from the repo root via
`pixi run <task>`.

> **Repo split:** code lives in `pole-ai-ml`, infra in `pole-ai-ml-infra`, docs
> here in `pole-ai-ml-docs`. Tests below are all in the code repo
> (`pole-ai-ml`), driven by the `pixi.toml` tasks.

## Test pyramid

| Category | What it verifies | Speed | Count (approx.) |
| :--- | :--- | :--- | :--- |
| **Unit** (`pytest`) | Isolated logic with mocks — no network/DB/model | Fast | ~3562 |
| **Integration** (`pytest -m integration`) | Real components wired together (LLM, vector store) | Slow | ~6 |
| **E2E** (Playwright) | Full browser → backend flow against `*_testing` DBs | Slow | ~240 |
| **AI gate** (150q) | Quality bar for the coach over real LLM | Very slow | 28 |
| **Aggregator** | The whole chain, sequentially, `_testing`-guarded | Very slow | ~2790+ |

---

## 1. Unit tests — `pytest` per package

Run the task of the package you touched. Hermetic: no live DB, no real model,
no credentials.

| Command | Package | Tests | Files | When to use |
| :--- | :--- | ---: | ---: | :--- |
| `pixi run test-api` | `app/pole_api` (FastAPI backend) | ~2118 | 140 | Backend endpoints / services / workers |
| `pixi run test` | `pole-train-model` (ML pipeline) | ~674 (≈549 collected) | 37 | Skeleton extractor, LSTM, embeddings (≥80% coverage) |
| `pixi run test-chatbot` | `chatbot` (mocked) | 281 | 20 | Chatbot logic without LLM |
| `pixi run test-polecoach` | `pole_coach` | 255 | 24 | Coach logic |
| `pixi run test-rag` | `pole_rag` | 155 | 18 | Retrieval / vector store |
| `pixi run test-analysis-tools` | `analysis-tools` | 40 | 3 | Analysis helpers |
| `pixi run test-jobs` | `jobs` (queues/workers) | 35 | 6 | Job model / orchestrator |
| `pixi run test-hardening` | `pole-tools` (single file) | 4 | 1 | Hardening analysis |

---

## 2. Integration tests — `pytest -m integration` (live)

Rare but important: validate real external components. Need live services /
credentials.

| Command | What | Tests | When |
| :--- | :--- | ---: | :--- |
| `pixi run test-chatbot-live` | Chatbot against **real LLM** (OpenRouter) | ~3 | Verify LLM wiring / prompts |
| `pixi run test-rag-live` | RAG against **real vector store** | ~3 | Verify embedding / retrieval |

---

## 3. E2E tests — Playwright (browser + real backend)

Local by design: the Playwright `webServer` boots FastAPI (`AUTH_ENABLED=0`) +
`ng serve`, drops the `*_testing` DBs first, and uses `E2E_FAKES=1` (fake ML
predictors — no real model needed). Never touches production data.

| Command | App | Tests | Specs | When |
| :--- | :--- | ---: | ---: | :--- |
| `pixi run fe-e2e` | `pole_fe` (Angular) | 21 | 11 | FE UI/flows |
| `pixi run pole-analyst-e2e` | `pole_analyst` | 191 | 11 | Analyst UI/flows |

**Remote mode (staging):** both suites accept `E2E_USE_REMOTE_BACKEND=1` +
`E2E_BASE_URL` (+ `E2E_API_BASE`, `E2E_KEYCLOAK_*`) to target the live `demo-*`
hosts instead of a local stack. **Only the read-only subset applies to
staging** — the empty-library + mutating specs are local-only (they assume the
hermetic `*_testing` DBs). Full battery → run locally.

---

## 4. AI gate — `pole-analyst-150q`

| Command | What | Tests | When |
| :--- | :--- | ---: | :--- |
| `pixi run pole-analyst-150q` | 150 coach questions (5 flows × 30) vs real LLM | 28 | Coach quality gate (bar ≥27/30 per flow) |

Heavy: 28 tests, ~30–60+ min, needs LLM credentials.

---

## 5. Aggregator

| Command | Composition | When |
| :--- | :--- | :--- |
| `pixi run test-integration` | `test-api` → `test` → `test-chatbot-live` → `fe-e2e` → `pole-analyst-e2e` | Full end-to-end signal before a big merge/release |

Note: `test-api` alone is ~1.5–2 h — the aggregator is a release-level run, not
a per-ticket step.

---

## Cross-cutting rules

1. **DB guard** — every integration/E2E task runs `scripts/guard-testing-db.sh`
   first and aborts unless `POLE_API_DB` / `SKELETON_DB` / `ANALYSIS_DB` carry
   the `_testing` suffix. Production DBs are never touched.
2. **Order** — unit first, integration second, E2E last (classic pyramid).
3. **Staging vs local** — staging E2E = read-only subset against `demo-*`; the
   mutating/empty-library specs are local-only by design.
4. **Model-dependent failures** — tests exercising the *real predictor* or
   *coach flow* can fail when model artifacts (`.keras`) or LLM credentials are
   missing; treat those separately from logic failures.
