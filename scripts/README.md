# RAG Tooling — Docs & Code

Tools to index project documentation and source code into ChromaDB vector
stores and query them. Two flavors share a generic engine
(`rag_engine.py`):

- **Docs RAG** — indexes `*.md` under a *docs folder* (default `docs/`).
- **Code RAG** — indexes the source tree of an app / package with a
  language-aware code splitter.

The RAGs let the **team-lead** and **sub-agents** retrieve relevant project
context instead of reading files directly.

Everything runs from the workspace root via pixi tasks:

```bash
# Docs RAG (first arg = docs folder; a rag/ folder is created inside it)
pixi run docs-rag-generate   # wipe & rebuild the RAG from all docs/
pixi run docs-rag-write      # incremental: only re-embed changed docs
pixi run docs-rag-read       # query the RAG (print or JSON)
pixi run docs-rag-export     # dump the collection to a versionable JSON file
pixi run docs-rag-import     # rebuild Chroma from an export JSON or from source

# Code RAG (first arg = project name/path; a rag/ folder is created inside it)
pixi run code-rag-write <project>      # incremental index of a project's source
pixi run code-rag-read <project> "..." # query a project's code RAG
pixi run code-rag-generate <project>   # wipe & rebuild a project's code RAG
```

Both flavors store their artifacts under `<source>/rag/`:
`<source>/rag/chroma/` (git-ignored) + `<source>/rag/manifests/manifest.json`
(versioned).

---

## What the RAG stores

- **Source:** every `*.md` under `docs/` (the git-tracked sources are the
  source of truth).
- **Embeddings:** local HuggingFace `sentence-transformers` model
  `all-MiniLM-L6-v2` (384-dim). No API cost, works offline.
- **Vector store:** ChromaDB persisted at `docs/rag/chroma/` (git-ignored).
- **Metadata per chunk:** `path`, `file_name`, `project_name` (inferred from the
  path, e.g. `docs/app/pole_api/x.md` → `pole_api`), `created_date`,
  `last_update`, `file_hash`.

### Version control / reproducibility

- The markdown sources are committed to git and are the single source of truth.
- `docs/rag/` (binary SQLite + parquet) is **git-ignored** because it is fully
  reproducible from the sources — run `pixi run docs-rag-generate` to rebuild it.
- `docs/rag/manifests/manifest.json` **is versioned**: it records every file's
  sha256 hash + dates, enabling incremental rebuilds and cross-machine
  reproducibility.
- `pixi run docs-rag-export` writes a full JSON snapshot (ids + documents + embeddings
  + metadata) to `docs/rag/manifests/export.json` for portability/audit.

---

## Scripts (in this folder)

**Shared engine & config:**

| Script | Purpose |
| :--- | :--- |
| `rag_engine.py` | Generic RAG core (incremental write / query / generate) parameterized by a `RagSpec`. Shared by docs + code flavors. |
| `rag_config.py` | Shared configuration (paths, model, chunking, metadata keys, project registry). Not meant to be run directly. |
| `code_splitter.py` | Language-aware code splitting (Python / TS / JS / CSS / HTML / …). |
| `rag_docs.py` | Docs specialization: builds the docs `RagSpec` (markdown splitter + `*.md` iterator). |
| `requirements.txt` | Python deps for running these scripts in a standalone venv. |

**Docs RAG CLIs (`docs-rag-*`):**

| Script | Purpose |
| :--- | :--- |
| `rag_generate.py` | **Wipe & rebuild** the docs RAG then re-embed every doc. |
| `rag_write.py` | **Incremental indexer** (sha256 per file, only re-embed changed docs, purge deleted). |
| `rag_read.py` | **Query tool** (plain text or JSON, optional `--path`/`--project` filters). |
| `rag_export.py` | **Export** the collection (with embeddings) to a portable JSON file. |
| `rag_import.py` | **Import / rebuild** from an export JSON, or re-embed from source. |

**Code RAG CLIs (`code-rag-*`):**

| Script | Purpose |
| :--- | :--- |
| `code_rag_generate.py` | **Wipe & rebuild** a project's code RAG. |
| `code_rag_write.py` | **Incremental indexer** for a project's source (language-aware splitting). |
| `code_rag_read.py` | **Query tool** for a project's code RAG. |

---

## Usage

### 1) Build the RAG (full rebuild)

```bash
pixi run docs-rag-generate
```

Deletes any existing RAG and re-embeds **all** docs. Output reports the number
of docs indexed and the total chunks stored.

### 2) Keep the RAG up to date (incremental)

```bash
pixi run docs-rag-write
```

Only re-embeds files whose content changed since the last run. Safe to run
regularly; the manifest makes it idempotent.

### 3) Query the RAG

Print the top 4 relevant chunks as text:

```bash
pixi run docs-rag-read "how does the skeleton extractor normalize landmarks?"
```

Get JSON (best for programmatic use / agents):

```bash
pixi run docs-rag-read "config" --k 5 --json
```

Filter by source path or project:

```bash
pixi run docs-rag-read "trick classifier" --path packages/pole_ml
pixi run docs-rag-read "training workflow" --project pole_ml --k 3
```

Show similarity distance, or dump the full source of the top hit:

```bash
pixi run docs-rag-read "api spec" --score
pixi run docs-rag-read "retraining" --extract
```

### 4) Export / import for portability

```bash
pixi run docs-rag-export                        # -> docs/rag/manifests/export.json
pixi run docs-rag-import --from-export docs/rag/manifests/export.json
pixi run docs-rag-import --from-source --reset  # rebuild from sources (== docs-rag-generate)
```

### Advanced options

Each docs script takes an optional positional **docs folder** as its first
argument (default `docs/`); internals (chroma dir, manifest) live under that
folder's `rag/`. Code scripts take the **project name or path**. Use
`python docs/scripts/<name>.py --help` for details.

---

## Code RAG (per app / package)

Each app (`app/`) and package (`packages/`) can host its own code RAG so agents
can answer "how is X implemented" questions against the actual source. The
artifacts live under `<project>/rag/`. Example with `pole_api`:

```bash
pixi run code-rag-write pole_api      # index the project's source (incremental)
pixi run code-rag-read pole_api "how is the trick service wired?" --k 4
pixi run code-rag-generate pole_api   # wipe & rebuild from scratch
```

`<project>` is an app/package **name** (e.g. `pole_api`, `chatbot`) or a path to
a project folder. The collection is named `<project>_code`, and metadata mirrors
the docs RAG (plus the source `path`).

### What gets indexed

- **Source + light config suffixes:** `.py`, `.ts`, `.tsx`, `.js`, `.jsx`,
  `.html`, `.css`, `.scss`, `.json`, `.md`, `.yaml/.yml`, `.toml`.
- **Excluded directories:** `rag/`, `models/`, `dist/`, `node_modules/`,
  `__pycache__/`, `.git/`, cache dirs, virtualenvs, build output.
- **Excluded files:** lockfiles (`package-lock.json`, `poetry.lock`, …).
- Everything else is indexed, including **tests** and migrations.

### Splitting

Code is split with a language-aware splitter (``RecursiveCharacterTextSplitter``
with code-specific separators, `chunk_size=1000`, `chunk_overlap=100`). The
upstream `CodeSplitter` needs the heavy native `tree-sitter-languages` package,
so a dependency-light equivalent is used instead (`code_splitter.py`) — swap in
the real `CodeSplitter` later if tree-sitter becomes acceptable.

---

## Metadata reference

Every chunk carries the following metadata (query against any of them with the
`--path` / `--project` filters on `docs-rag-read.py`):

| Key | Meaning |
| :--- | :--- |
| `path` | Relative path of the source file, e.g. `packages/pole_ml/PLAN.md` |
| `file_name` | Basename of the source file |
| `project_name` | Project inferred from the path, e.g. `pole_api`, `pole_ml`, `root` |
| `created_date` | ISO date the file was first indexed |
| `last_update` | ISO datetime of the file's last modification |
| `file_hash` | sha256 of the file content at last index |

---

## Configuring (rag_config.py)

```python
EMBED_MODEL    = "sentence-transformers/all-MiniLM-L6-v2"  # shared
CHUNK_SIZE     = 1000   # chars per chunk (shared default)
CHUNK_OVERLAP  = 100    # overlap between chunks
# Docs collection name lives in rag_docs.py (DOCS_COLLECTION = "pole_ai_docs");
# code collections are named "<project>_code".
```

If you change `EMBED_MODEL` or the chunking values, run `pixi run docs-rag-generate`
(and the affected `code-rag-generate`) once so each index is rebuilt consistently.
