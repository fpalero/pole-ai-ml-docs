# Tutorials — Article Catalog

Every tutorial here is grounded in **real, working, documented code** from the
`pole-ai` project (see the `docs/app/*`, `docs/packages/*`, `docs/diagrams/*`
and `docs/decisions/*` trees). Nothing is theoretical: each article teaches a
pattern, a bug, or an architecture that was actually built and shipped here.

> **Repo note:** this `docs/tutorials/` tree lives in the `pole-ai-ml-docs`
> repo. After editing any file, run `pixi run docs-rag-write` so the tutorials
> become retrievable from the docs RAG.

---

## Audience profiles

| Profile | File suffix | Focus |
| :--- | :--- | :--- |
| **ML / Computer Vision engineers** | `ml-cv.md` | MediaPipe, TensorFlow, embeddings, vectors, deployment of models |
| **Full-stack / backend engineers** | `fullstack-backend.md` | FastAPI, WebSockets, RAG services, agents, infra, crawlers |
| **Mixed — beginner → intermediate** | `junior-mixed.md` | End-to-end product building, gentle entry to ML + backend |
| **Entrepreneur / technical PM** | `tech-entrepreneur.md` | Product value, scoping, process, decision records |

---

## Themes

| # | Theme folder | Core content |
| :--- | :--- | :--- |
| 01 | [`01-skeleton-pose/`](01-skeleton-pose/) | MediaPipe pose extraction, normalization, biomechanical features, small-data augmentation |
| 02 | [`02-tensorflow-models/`](02-tensorflow-models/) | LSTM sequence-to-vector, training/eval, hybrid classifier, tfjs export, video cutter |
| 03 | [`03-embeddings-vector-search/`](03-embeddings-vector-search/) | 128-d embeddings, ChromaDB, k-NN voting, retrieval-augmented recognition |
| 04 | [`04-rag-retrieval/`](04-rag-retrieval/) | Offline/local RAG, language-aware code splitting, reproducible indexing |
| 05 | [`05-realtime-fullstack/`](05-realtime-fullstack/) | Real-time recognition, WebSocket agents, coaching-feedback LLM |
| 06 | [`06-data-infra/`](06-data-infra/) | Instagram crawler, Docker → k3s + Helm, Keycloak identity |
| 07 | [`07-meta-process/`](07-meta-process/) | Doc-driven development, LLM crew, multi-repo routing, ADRs |

Each theme folder contains one catalog document **per audience profile**
(`ml-cv.md`, `fullstack-backend.md`, `junior-mixed.md`, `tech-entrepreneur.md`),
plus a `README.md` overview of the theme.

---

## Recommended "launch pack" (ship first, establish authority)

A coherent first set of 5 that spans the product arc and has the strongest
differentiation for the ML/CV audience:

1. **Hybrid Classifier pattern** — `02-tensorflow-models/ml-cv.md`
2. **Skeleton normalization done right** — `01-skeleton-pose/ml-cv.md`
3. **Sequence-to-Vector LSTM embeddings** — `02-tensorflow-models/ml-cv.md`
4. **ChromaDB in practice + config-bug case study** — `03-embeddings-vector-search/ml-cv.md`
5. **Zero-cost offline RAG** — `04-rag-retrieval/ml-cv.md`

---

## Quick list

- [`ARTICLE_CATALOG.md`](ARTICLE_CATALOG.md) — all 48 articles grouped by topic, with title + short description

## Index of documents

- `01-skeleton-pose/` — [`README.md`](01-skeleton-pose/README.md) ·
  `ml-cv.md` · `fullstack-backend.md` · `junior-mixed.md` · `tech-entrepreneur.md`
- `02-tensorflow-models/` — [`README.md`](02-tensorflow-models/README.md) ·
  `ml-cv.md` · `fullstack-backend.md` · `junior-mixed.md` · `tech-entrepreneur.md`
- `03-embeddings-vector-search/` — [`README.md`](03-embeddings-vector-search/README.md) ·
  `ml-cv.md` · `fullstack-backend.md` · `junior-mixed.md` · `tech-entrepreneur.md`
- `04-rag-retrieval/` — [`README.md`](04-rag-retrieval/README.md) ·
  `ml-cv.md` · `fullstack-backend.md` · `junior-mixed.md` · `tech-entrepreneur.md`
- `05-realtime-fullstack/` — [`README.md`](05-realtime-fullstack/README.md) ·
  `ml-cv.md` · `fullstack-backend.md` · `junior-mixed.md` · `tech-entrepreneur.md`
- `06-data-infra/` — [`README.md`](06-data-infra/README.md) ·
  `ml-cv.md` · `fullstack-backend.md` · `junior-mixed.md` · `tech-entrepreneur.md`
- `07-meta-process/` — [`README.md`](07-meta-process/README.md) ·
  `ml-cv.md` · `fullstack-backend.md` · `junior-mixed.md` · `tech-entrepreneur.md`