# Theme 04 — RAG & Retrieval · Audience: ML / CV Engineers

> For engineers working with embeddings daily: a RAG you can run forever for
> free, and how to index code without heavy native deps.

## Catalog

### D1 — Zero-Cost Offline Documentation RAG
- **Difficulty:** Intermediate
- **Type:** Tutorial
- **Hook:** "Run RAG on your own docs with zero API cost — local embeddings, ChromaDB, done."
- **Description:** The full offline RAG: `sentence-transformers/all-MiniLM-L6-v2`
  (384-d) for embeddings, ChromaDB `PersistentClient`, chunk size 1000/overlap
  100, incremental (hash-manifest) vs full-rebuild indexing, and per-chunk
  metadata for filtering. Shows reproducible retrieval without an LLM bill.
- **Grounding:** `docs/scripts/README.md`, `docs/scripts/rag_config.py`, `docs/packages/pole_rag/PLAN.md`.
- **Sellable angle:** Everyone wants RAG; almost nobody shows the free, offline
  path. Strong keyword pull.

### D2 — Language-Aware Code Splitting Without tree-sitter
- **Difficulty:** Intermediate/Advanced
- **Type:** Implementation deep-dive
- **Hook:** "Code chunks break at the wrong places — here's a dependency-light splitter that fixes it."
- **Description:** Why generic text splitting mangles code, and the
  `RecursiveCharacterTextSplitter`-based splitter with code-specific separators
  (chunk_size=1000, overlap=100) as a tree-sitter-free alternative. Covers what
  gets indexed, what's excluded (locks, builds, `node_modules`), and scope: .py,
  .ts/.tsx, .html, .md, yaml, toml.
- **Grounding:** `docs/scripts/rag_code.md` / code-rag docs (language-aware splitting), `docs/scripts/README.md`.
- **Sellable angle:** Differentiated deep-dive; teams stuck on tree-sitter
  native deps are the audience.

### D3 — Multimodal RAG with Image Descriptions
- **Difficulty:** Advanced
- **Type:** Architecture guide
- **Hook:** "Your docs have figures. Your RAG is blind to them — index descriptions, not pixels."
- **Description:** The `pole_rag` store with **two collections** — text chunks
  and image descriptions — embedded side by side in ChromaDB.
  Readers query across prose and figures (e.g., an architecture diagram) by
  meaning, with idempotent/full-rebuild semantics shared with the docs RAG.
- **Grounding:** `docs/packages/pole_rag/phase-3-embeddings-storage/PAIML-POLE-RAG-013.md`,
  `docs/diagrams/pole_rag/CLASSES.md`.
- **Sellable angle:** "Multimodal RAG" is a hot search; showing it with local
  embeddings + screenshots/figures is an underserved, concrete angle.

### D4 — Replacing Marker/Surya with PyMuPDF: Know Your Corpus First
- **Difficulty:** Intermediate
- **Type:** Dependency-optimization case study
- **Hook:** "Your PDF pipeline is paying for multi-GB OCR it doesn't need."
- **Description:** A PDF-heavy RAG hung on Marker/Surya weights + GPU image
  captions. A five-minute corpus scan (13 text-OK, 3 mixed, 0 scanned) proved
  every PDF has embedded text, so PyMuPDF swapped in and the heavy lane died.
  Dependency diets start with data, not with tools.
- **Grounding:** `docs/packages/pole_rag/phase-7-pymupdf-swap/PAIML-POLE-RAG-032/033/034.md`.
- **Sellable angle:** Great "measure before you scale" story; saves readers
  real money and pain on PDF extraction.