# 04 — RAG & Retrieval Systems

> Two RAG flavours built here: a **documentation RAG** (this docs tree) and a
> **code RAG** with language-aware splitting. Local embeddings, ChromaDB
> persistence, reproducible manifests. Grounded in `docs/scripts/rag_*.py` and
> `packages/pole_rag/`.

## Core articles in this theme

| ID | Title | Difficulty | Primary audience |
| :--- | :--- | :--- | :--- |
| D1 | Zero-Cost Offline Documentation RAG | Intermediate | All |
| D2 | Language-Aware Code Splitting Without tree-sitter | Intermediate/Advanced | Backend + ML/CV |
| D3 | Multimodal RAG with Image Descriptions | Advanced | ML/CV + backend |
| D4 | Replacing Marker/Surya with PyMuPDF: Know Your Corpus First | Intermediate | Backend + ML/CV |

## What makes this theme sellable

- **D1** is highly-demanded content (everyone wants RAG) but almost nobody shows
  an **offline, free** one: `all-MiniLM-L6-v2` (384-d), no API cost, ChromaDB
  PersistentClient, incremental vs full rebuild, manifest-based reproducibility.
- **D2** shows a dependency-light `RecursiveCharacterTextSplitter` with
  code-specific separators as an alternative to tree-sitter — a real trade-off
  call most teams face.
- Both are immediately replicable by readers on their own repos.

## Source docs

- `docs/scripts/README.md`, `docs/scripts/rag_config.py`
- `docs/packages/pole_rag/PLAN.md`, `docs/packages/pole_rag/phase-*` tickets
- `docs/packages/pole_rag/phase-3-embeddings-storage/PAIML-POLE-RAG-014.md` (ChromaStore)

---

## Docs per audience

- [`ml-cv.md`](ml-cv.md) — ML / computer vision engineers
- [`fullstack-backend.md`](fullstack-backend.md) — full-stack / backend engineers
- [`junior-mixed.md`](junior-mixed.md) — mixed beginner → intermediate
- [`tech-entrepreneur.md`](tech-entrepreneur.md) — entrepreneur / technical PM