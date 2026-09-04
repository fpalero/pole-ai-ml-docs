# Implementation Plan — `pole_rag` (Multimodal RAG Seeder Package)

> **Status:** 📋 PLANNED — new project at `packages/pole_rag/` (no standalone pyproject;
> integrated into root `pixi.toml` per user decision). The chatbot will later consume
> the produced vector DBs through 4 similarity tools (`query_pole`,
> `query_calisthenics`, `query_psicology`, `query_biomechanics`, k=3).
> **Source of requirements:** live interview with the user (Phases 0–5).

---

## 1. Feature Context & Objective

- **Goal:** Create a local CLI RAG seeder that extracts content from PDF books and
  builds a **multimodal RAG** (text + image-description vector stores) in Chroma DB.
  The produced vector DBs will later be consumed by the chatbot agent to ground answers.
- **Non-Functional Constraints:** local CLI only; **no authentication** for the seeder
  (chatbot tools are internal, not exposed as public endpoints); **no performance
  requirement** (large PDFs accepted, ~560 MB total across sources); **no downloads** —
  Marker models, HuggingFace embeddings and Ollama `llama3.2-vision` are already
  available locally; all models local/cached.
- **Affected Components:**
  - `packages/pole_rag/` — new project folder with `src/pole_rag/` modules (Option A layout),
    `sources/`, `data/`; **no pyproject**.
  - `pixi.toml` (root) — new deps `marker-pdf` + `pillow` (dev-only) + tasks
    (`rag-seed`, `rag-reseed`, `rag-query`, `rag-inspect`, `test-rag`, `test-rag-live`).
  - `packages/chatbot/src/pole_chatbot/tools.py` — 4 new sync tools (Phase 5),
    reaching `pole_rag` via workspace `PYTHONPATH`.
  - `.gitignore` — ignore `packages/pole_rag/sources/` + `packages/pole_rag/data/` (large binaries).
  - Docs: `docs/packages/pole_rag/` (this plan + per-phase files + tickets).
- **Assumptions:**
  - **No standalone `pyproject.toml`** for `pole_rag` — deps + tasks live in root `pixi.toml`
    (the `app/pole_api` pattern: tasks run `python -m pole_rag.cli.*` with
    `cwd = "packages/rag"`, `PYTHONPATH = "src"`).
  - **Docker images are unaffected** by root pixi deps — Dockerfiles
    (`app/pole_api/docker/base.Dockerfile`) pin their own deps via `pip install` and never
    read `pixi.toml`, so Marker never enters the API image.
  - 4 Chroma DBs, one per resource: `pole`, `calisthenics`, `psicology`, `biomechanics`.
  - DBs live under `packages/pole_rag/data/` (Chroma persistent path = `<data>/<name>/`).
  - Source PDFs are moved/copied into `packages/pole_rag/sources/<resource>/` (Option B).
  - Duplicate PDFs are deduplicated by content hash.
  - `seed` and `re-seed` both perform a **full rebuild** (drop + recreate; Option C).
  - Embedding model: `sentence-transformers/all-MiniLM-L6-v2` (repo default, 384 dims).
  - Text chunking: atomic Markdown tables + `RecursiveCharacterTextSplitter`
    (chunk_size=1000, overlap=150) — per the user's reference design.
  - Image descriptions: local Ollama VLM `llama3.2-vision` (replaces BLIP).
  - Two collections per DB: `text_chunks` (text + atomic tables) and
    `image_descriptions` (VLM captions linked by `image_path`).
  - Query default `k=3` for CLI and chatbot tools.

---

## 2. Architectural Layering (The "Where")

- **Domain:** document model (`SourceDocument` with hash/source path/resource),
  chunk model (`RagChunk`: text | atomic-table | image-caption + metadata),
  collection schema constants (`text_chunks`, `image_descriptions`).
- **Application:** seeder orchestration (`seed_resource` = extract → chunk →
  embed → store, full rebuild), query service (similarity over both collections,
  merged top-k), inspect service (list DBs/collections/counts/sources),
  dedupe service (hash-based).
- **Infrastructure:**
  - `MarkerExtractor` — wraps `marker.convert.convert_single_pdf` + `save_output`
    (PDF → Markdown + images folder), per-PDF error isolation.
  - `AtomicTableChunker` — regex table isolation + preceding-context injection.
  - `HuggingFaceEmbeddings` (`all-MiniLM-L6-v2`) — text + image caption embeddings.
  - `OllamaVision` — `ChatOllama` with `llama3.2-vision` for image descriptions.
  - `ChromaStore` — `chromadb.PersistentClient(path=<data>/<name>)`, two collections.
- **Presentation:** CLI entry points `rag-seed`, `rag-reseed`, `rag-query`,
  `rag-inspect` via **root pixi tasks** (`python -m pole_rag.cli.*`, `PYTHONPATH=src`).
  No HTTP API.

---

## 3. Implementation Roadmap (Atomic Steps)

### Phase 1: Package scaffold, sources, dedupe, config — 📋 PLANNED
- [ ] [Infrastructure] Add `pole_rag` to root `pixi.toml`: deps `marker-pdf` + `pillow`
      (dev-only); create `packages/pole_rag/` folder. **No pyproject.**
- [ ] [Infrastructure] Create `packages/pole_rag/src/pole_rag/` source layout (Option A,
      pole_api-style, no hatchling) + `cli/` + `tests/`.
- [ ] [Infrastructure] Move/copy `rag/sources/*` → `packages/pole_rag/sources/` (4 folders).
- [ ] [Application] `dedupe.py` — content-hash (sha256) duplicate detection; removes
      duplicate PDFs (e.g., `Fundamentals_of_Biomechanics (1).pdf`), warns per file.
- [ ] [Infrastructure] `config.py` — constants: `DATA_DIR`, `EMBED_MODEL`,
      `CHUNK_SIZE=1000`, `CHUNK_OVERLAP=150`, collection names, `OLLAMA_MODEL`,
      `OLLAMA_HOST`, `DEFAULT_K=3`.
- [ ] [Infrastructure] `.gitignore` — `packages/pole_rag/sources/`, `packages/pole_rag/data/`.
- [ ] [Infrastructure] Root pixi tasks: `rag-seed`, `rag-reseed`, `rag-query`,
      `rag-inspect`, `test-rag`, `test-rag-live` (`python -m pole_rag.cli.*`,
      `cwd=packages/rag`, `PYTHONPATH=src`).
- [ ] [Application] Unit tests: dedupe (duplicate + unique + hash), config defaults.

### Phase 2: Marker extraction + atomic table chunking — 📋 PLANNED
- [ ] [Infrastructure] `extractor.py` — `MarkerExtractor.convert(pdf) -> (markdown, images_dir)`;
      per-PDF try/except, warn-and-continue; empty/unreadable PDF handling.
- [ ] [Application] `chunker.py` — `chunk_markdown_with_atomic_tables(md) -> list[str]`:
      regex isolates complete `|...|` table blocks, injects up to 3 preceding lines as
      context prefix, splits remaining text with `RecursiveCharacterTextSplitter`.
- [ ] [Application] Unit tests: table stays atomic, context injected, plain text splits,
      empty input → [], variant table separators.

### Phase 3: Embeddings + Chroma multi-collection storage — 📋 PLANNED
- [ ] [Infrastructure] `embeddings.py` — shared `HuggingFaceEmbeddings` instance.
- [ ] [Infrastructure] `vision.py` — `OllamaVision.describe(image_path) -> str` via
      `ChatOllama(model="llama3.2-vision")`; per-image error fallback.
- [ ] [Infrastructure] `chroma_store.py` — `ChromaStore(output_dir, name)`:
      `PersistentClient(path=<output>/<name>)`, `get_or_create_collection` for
      `text_chunks` + `image_descriptions`; full-rebuild = delete + recreate collections.
- [ ] [Application] `seeder.py` — `seed_resource(input_dir, output_dir, name)`: dedupe →
      extract each PDF → chunk → embed text chunks; scan images dir → Ollama caption →
      embed captions; deterministic ids `{source_stem}_text_{i}` / `_img_{i}`; metadata
      `{source_document, file_name, type, image_path, image_title}`.
- [ ] [Application] Integration test (marked `integration`): seed the smallest source PDF
      (e.g., `psicology/_OceanofPDF.com_The_Mindful_Athlete_-_George_Mumford.pdf`) into a
      temp output dir with real Marker + real HF + real Ollama; assert both collections
      have > 0 entries.

### Phase 4: CLI commands (seed / reseed / query / inspect) — 📋 PLANNED
- [ ] [Presentation] `cli/seed.py` → `rag-seed -i <folder> -o <dir> --name <db>` (full rebuild).
- [ ] [Presentation] `cli/reseed.py` → `rag-reseed` (alias: full rebuild semantics).
- [ ] [Presentation] `cli/query.py` → `rag-query -o <dir> --name <db> --query "..." [-k 3]`
      (queries both collections, merges, prints text/caption + metadata + distance).
- [ ] [Presentation] `cli/inspect.py` → `rag-inspect -o <dir> [--name <db>]` (list DBs,
      collections, counts, source documents).
- [ ] [Infrastructure] Root pixi tasks verified for all 4 CLIs (`python -m pole_rag.cli.*`,
      `PYTHONPATH=src`); **no `[project.scripts]`**.
- [ ] [Application] Tests: CLI arg parsing, query merge order, inspect output; live query
      against a seeded temp DB returns exactly `k` results.

### Phase 5: Chatbot tool integration — 📋 PLANNED
- [ ] [Application] Chatbot runtime includes `packages/pole_rag/src` on `PYTHONPATH`
      (no `pole-rag` pip dependency).
- [ ] [Application] `packages/chatbot/src/pole_chatbot/` — add 4 sync `ToolSpec`s:
      `query_pole`, `query_calisthenics`, `query_psicology`, `query_biomechanics`
      (params: `query` string, optional `k` default 3, optional `data_dir`); handlers
      call `pole_rag.query` for the matching DB.
- [ ] [Application] Unit tests: each tool returns k=3 results with metadata against a
      Chroma temp dir; unknown DB → ToolError.
- [ ] [Application] Integration test (marked `integration`): tools query a seeded test DB
      and return expected source documents.

### Phase 6: Staging ship (image + data dir + seed + verify) — 📋 PLANNED
- [ ] [Infrastructure] Ship `pole_rag` in the pole-api base image (`base.Dockerfile`
      COPY + import path; slow base rebuild lane). Ticket 027 (`pole-ai-ml`).
- [ ] [Application] `POLE_RAG_DATA_DIR` env override in
      `pole_rag/config.default_data_dir()` (default: package `data/`; staging:
      `/data/rag`). Ticket 028 (`pole-ai-ml`).
- [ ] [Ops] Staging wiring (`POLE_RAG_DATA_DIR=/data/rag`, `/data/rag` dir) + local
      seed of the 4 DBs + `kubectl cp` transfer runbook + embedder-model lane.
      Ticket 029 (`pole-ai-ml-infra`; seed/cp are a runbook, no repo change).
- [ ] [Application] Verify on staging: 4 tools return hits; unknown DB still
      `ToolError`; `/data/chroma` untouched. Ticket 030 (`pole-ai-ml`).
- [ ] Detail: [plan/PLAN_PHASE_6.md](plan/PLAN_PHASE_6.md) · Tickets:
      [phase-6-staging-ship](phase-6-staging-ship/) (027, 028, 029, 030).
- [ ] Decision record (Chroma/RAG investigation: image absence, `/data/chroma`
  occupied by `movement_embeddings`, `/data/rag` home, seed-locally choice):
  [plan/PLAN_PHASE_6.md](plan/PLAN_PHASE_6.md#decision-record--why-datarag-why-seed-then-copy).

### Phase 7: PyMuPDF swap (deterministic text extraction) — 📋 PLANNED
- [ ] [Infrastructure] Ticket 032 (`pole-ai-ml`): uninstall Marker — remove
      `marker-pdf` from `pixi.toml` `[pypi-dependencies]`, trim (not drop)
      the HF offline block, re-verify the `websockets` constraint,
      `pixi install` to regenerate the lock, `pixi run test-rag` still
      collects (extractor failures = known-break fixed by 033).
- [ ] [Infrastructure] Ticket 033 (`pole-ai-ml`): new
      `src/pole_rag/fitz_extractor.py` (same `convert` contract,
      `page_chunks` + `write_images`), `POLE_RAG_EXTRACTOR=pymupdf|marker`
      switch in `config.py` + `extractor.py` fallback, `--skip-images` on
      the seed CLI, per-page progress log, updated extractor tests.
- [ ] Detail: [plan/PLAN_PHASE_7.md](plan/PLAN_PHASE_7.md) · Tickets:
      [phase-7-pymupdf-swap](phase-7-pymupdf-swap/) (032, 033).
- [ ] Decision record (why Marker dropped: Surya multi-GB CPU hang +
      `llava:7b` per-image cost over 550 MB/16 PDFs; 13 TEXT-OK + 3 MIXED,
      0 scanned → PyMuPDF suffices):
      [plan/PLAN_PHASE_7.md](plan/PLAN_PHASE_7.md#decision-record--why-marker-was-dropped).

---

## 4. Quality Gates & Testing Commands (DoD)

- **Unit Tests:** `pixi run test-rag` (pytest from `packages/rag`, excludes `integration`
  via pytest config) — ≥ 80% coverage.
- **Integration Tests:** `pixi run test-rag-live` (real Marker + real HF + real Ollama
  `llama3.2-vision`; seeds the smallest source PDF into a temp output dir; requires
  local Ollama + cached models).
- **Automation:** CI runs the unit suite; import linter keeps chatbot → `pole_rag` only.
- **Database Target:** file-based Chroma under `packages/pole_rag/data/` (tests use temp dirs
  or `data-test/`; never the real `data/`). No Mongo/Postgres involved.
- **Coverage Requirement:** ≥ 80% (repository default).
- **Additional Checks:** CLI smoke (`pixi run rag-seed --help`, `pixi run rag-query
  --help`, `pixi run rag-inspect --help`); no network download needed at runtime (models
  cached); no Dockerfile changes (root pixi deps are dev-only).

---

## 5. Defined Use Cases (Gherkin + Technical Matrix)

### UC-01: Seed one resource DB (happy path)
- **Given** a source folder with valid PDFs (e.g., `packages/pole_rag/sources/pole/`)
- **When** user runs `pixi run rag-seed -- -i packages/pole_rag/sources/pole -o packages/pole_rag/data --name pole`
- **Then** exit code 0, Chroma path `packages/pole_rag/data/pole/` exists
- **And** both `text_chunks` and `image_descriptions` collections have counts > 0

| Technical Check | Expected Value |
| :--- | :--- |
| CLI Command | `pixi run rag-seed -- -i <input> -o <output> --name <db>` |
| Required Env | `OLLAMA_HOST` (default `http://localhost:11434`) |
| Payload Example | `-i packages/pole_rag/sources/pole -o packages/pole_rag/data --name pole` |
| DB State (Before) | `data/pole/` absent or stale |
| DB State (After) | `data/pole/` recreated; text_chunks + image_descriptions > 0 |

### UC-02: Re-seed = full rebuild
- **Given** an existing `data/pole/` with indexed docs
- **When** user runs `pixi run rag-reseed` with the same args
- **Then** collections are dropped and recreated (no stale docs)
- **And** counts reflect only current sources (duplicates removed)

| Technical Check | Expected Value |
| :--- | :--- |
| CLI Command | `pixi run rag-reseed -- -i <input> -o <output> --name <db>` |
| Payload Example | same as UC-01 |
| DB State (Before) | stale entries from previous run |
| DB State (After) | collections recreated from scratch; ids deterministic |

### UC-03: Duplicate PDFs are deduplicated
- **Given** a folder containing a file and its byte-identical copy (e.g., `...Ozkaya.pdf` and `...Ozkaya (1).pdf`)
- **When** seed runs
- **Then** only one copy is indexed
- **And** a warning is logged naming the removed duplicate

| Technical Check | Expected Value |
| :--- | :--- |
| CLI Command | `pixi run rag-seed` (dedupe step) |
| Payload Example | `biomechanics/` folder with duplicate hash |
| DB State (After) | 1 source document for the duplicated content, not 2 |

### UC-04: Unreadable / empty PDF or empty source folder
- **Given** a corrupt PDF or an empty source folder
- **When** seed runs
- **Then** the seeder does not crash
- **And** it logs a warning for the failed PDF / "no PDFs found" for the folder, continuing with the rest

| Technical Check | Expected Value |
| :--- | :--- |
| CLI Command | `pixi run rag-seed` |
| Payload Example | folder with 1 corrupt + 1 valid PDF |
| DB State (After) | valid PDF indexed; corrupt PDF skipped with warning |

### UC-05: Query by similarity with k=3
- **Given** a seeded DB (e.g., `data/pole/`)
- **When** user runs `pixi run rag-query -- -o packages/pole_rag/data --name pole --query "invert grip technique" -k 3`
- **Then** exactly 3 results (merged text + image collections, sorted by distance)
- **And** each result carries `source_document` (+ `image_path` for image captions)

| Technical Check | Expected Value |
| :--- | :--- |
| CLI Command | `pixi run rag-query -- -o <output> --name <db> --query "<q>" [-k 3]` |
| Payload Example | `--name pole --query "invert grip" -k 3` |
| DB State | read-only |
| Response | 3 items: text or image caption + metadata + distance |

### UC-06: Inspect DBs
- **Given** `packages/pole_rag/data/` contains one or more seeded DBs
- **When** user runs `pixi run rag-inspect -- -o packages/pole_rag/data`
- **Then** it lists each DB name, collections, entry counts, and source documents

| Technical Check | Expected Value |
| :--- | :--- |
| CLI Command | `pixi run rag-inspect -- -o <output> [--name <db>]` |
| Payload Example | `-o packages/pole_rag/data` |
| DB State | read-only |
| Response | table of DBs/collections/counts/sources |

### UC-07: Chatbot tool `query_pole` (and the 3 siblings)
- **Given** a chatbot session and seeded DBs under `packages/pole_rag/data/`
- **When** the agent calls tool `query_pole` with `{"query": "invert grip"}`
- **Then** the tool returns k=3 similar chunks with `source_document` metadata
- **And** `query_calisthenics` / `query_psicology` / `query_biomechanics` behave identically against their DBs

| Technical Check | Expected Value |
| :--- | :--- |
| Tool Names | `query_pole`, `query_calisthenics`, `query_psicology`, `query_biomechanics` |
| Mode | sync |
| Payload Example | `{"query": "invert grip", "k": 3}` |
| DB State | read-only |

---

## 6. Risks and Mitigations

- **Risk:** Marker extraction fails or hangs on a specific large PDF. **Mitigation:**
  per-PDF error isolation (warn-and-continue); per-resource runs; no perf budget but
  CLI reports progress per file.
- **Risk:** Ollama `llama3.2-vision` not running / model missing. **Mitigation:**
  configurable `OLLAMA_HOST`/`OLLAMA_MODEL`; clear error message; no-download assumption
  verified at runtime with actionable output.
- **Risk:** Regex table isolation misses a table variant and splits a table.
  **Mitigation:** unit tests with multiple separator formats; fallback path treats
  unmatched lines as plain text.
- **Risk:** Stale entries after re-seed. **Mitigation:** full rebuild deletes + recreates
  collections; deterministic ids make state inspectable via `rag-inspect`.
- **Risk:** Accidental commit of large PDFs / vector stores. **Mitigation:** git-ignore
  `packages/pole_rag/sources/` and `packages/pole_rag/data/`.
- **Risk:** Root pixi deps leak into Docker images. **Mitigation:** Dockerfiles never read
  `pixi.toml`; verified by test (no Dockerfile changes in the PR).
- **Risk:** Chatbot cannot import `pole_rag` (no pip package). **Mitigation:** workspace
  `PYTHONPATH` includes `packages/pole_rag/src` in chatbot task envs; import linter in CI.

---

## 7. Open Questions and Decisions

- Decision: **no standalone pyproject** for `pole_rag`; deps + tasks in root `pixi.toml`
  (dev-only); tasks run `python -m pole_rag.cli.*` with `PYTHONPATH=src` (Option A).
- Decision: root pixi deps (`marker-pdf`, `pillow`) do **not** affect Docker images
  (Dockerfiles pin their own deps).
- Decision: sources moved into `packages/pole_rag/sources/` (Option B); git-ignored.
- Decision: `seed` and `re-seed` are both full rebuilds (Option C).
- Decision: embedding model `all-MiniLM-L6-v2` (repo default); chunk 1000/150.
- Decision: image descriptions via local Ollama `llama3.2-vision` (no BLIP, no downloads).
- Decision: 2 collections per DB (`text_chunks`, `image_descriptions`); query merges both.
- Decision: default `k=3`; no HTTP API; chatbot consumes via 4 internal sync tools.
- Open: whether `packages/pole_rag/data/` should be a fixed default or always explicit via `-o`
  (plan defaults to explicit `-o`, with `config.DATA_DIR` as default).
- Open: exact smallest fixture PDF chosen at implementation time from `sources/psicology/`
  (smallest file), confirmed by size at ticket time.