# Flow — `pole_rag` (Multimodal RAG Seeder + Query)

> Layers and key classes of the local CLI RAG seeder and its query path. Shipped in
> `packages/pole_rag` (no pyproject — root `pixi.toml`, `PYTHONPATH=src`). Chatbot tools:
> [`chatbot/FLOW.md`](../chatbot/FLOW.md). Class-level details: [CLASSES.md](./CLASSES.md).
> Plan: `packages/pole_rag/PLAN.md` · Phase 6: `packages/pole_rag/plan/PLAN_PHASE_6.md` (✅ DONE).

---

## 1. Seed → Query Flow Diagram

```mermaid
flowchart LR
    subgraph SRC["Sources"]
        PDF["PDFs<br/>sources/pole · calisthenics<br/>psicology · biomechanics"]
    end

    subgraph EXT["Extraction (Phase 7: PyMuPDF default)"]
        MZ["MarkerExtractor<br/>(legacy)"]
        FZ["fitz_extractor<br/>(pymupdf, POLE_RAG_EXTRACTOR)"]
    end

    subgraph CHK["Chunking + Captions"]
        AT["AtomicTableChunker<br/>(1000/150 + 3-line ctx)"]
        OV["OllamaVision<br/>llama3.2-vision"]
    end

    subgraph EMB["Embeddings + Store"]
        HF["HuggingFaceEmbeddings<br/>all-MiniLM-L6-v2 (384)"]
        CS["ChromaStore<br/>text_chunks + image_descriptions"]
    end

    subgraph CLI["CLI (root pixi tasks)"]
        SD["rag-seed / rag-reseed<br/>(full rebuild)"]
        Q["rag-query (k=3)"]
        INSP["rag-inspect"]
    end

    subgraph SRV["Serve (staging)"]
        IMG["pole-api base image<br/>COPY + PYTHONPATH + CPU-torch<br/>baked MiniLM (035/037)"]
        RAGDIR[("/data/rag<br/>pole · calisthenics<br/>psychology · biomechanics")]
        TOOLS["rag_tools.py<br/>4 query_* tools"]
    end

    PDF --> MZ
    PDF --> FZ
    MZ --> AT
    FZ --> AT
    PDF --> OV
    OV --> HF
    AT --> HF
    HF --> CS
    CS --> SD
    SD --> RAGDIR
    IMG --> TOOLS
    RAGDIR --> TOOLS
    TOOLS --> Q
    CS --> INSP
```

### 1.1 Diagram Component Descriptions

| Node | Purpose & Use |
| :--- | :--- |
| **Sources** | 4 resource folders (`pole`, `calisthenics`, `psicology`, `biomechanics`); dedupe by sha256 before seeding. |
| **MarkerExtractor / fitz_extractor** | PDF → Markdown + images. `POLE_RAG_EXTRACTOR=pymupdf\|marker` (default `pymupdf` since 033); Marker dropped in 032 (Surya CPU hang + `llava` cost). |
| **AtomicTableChunker** | Keeps `|...|` tables atomic, injects ≤3 preceding lines, splits rest with `RecursiveCharacterTextSplitter` (1000/150). |
| **OllamaVision** | Captions each image via local `llama3.2-vision`; per-image fallback, `tqdm captioning` bar (034), `--skip-images` on seed CLI. |
| **HuggingFaceEmbeddings / ChromaStore** | Shared MiniLM instance; `PersistentClient(path=<data>/<name>)`, deterministic ids `{stem}_text_{i}` / `_img_{i}`. |
| **CLI** | `rag-seed`/`rag-reseed` (full rebuild), `rag-query -k 3` (merges both collections by distance), `rag-inspect` (counts + sources). |
| **Serve** | Base image carries `pole_rag` (027) + baked embedder (035 CPU-torch 037, `HF_HOME` pre-download, `HF_HUB_OFFLINE=1`); staging reads `/data/rag` via `POLE_RAG_DATA_DIR` (028/029); 4 tools verified per 030. |

---

## 2. Staging Ship Sequence (Phase 6, DONE)

```mermaid
sequenceDiagram
    participant D as Developer
    participant CI as build-push.yml
    participant INF as deploy-dev.yml
    participant POD as staging pole-api pod
    participant OPS as seed runbook (029)

    D->>CI: merge (PAT 026) → base rebuild (pole_rag COPY 027 + HASH 031 + bake 035 + CPU-torch 037)
    OPS->>OPS: seed 4 DBs locally + rag-inspect
    OPS->>POD: kubectl cp /tmp/rag-staging/* → /data/rag/* (appuser)
    CI->>INF: repository_dispatch tag=<SHA_SHORT> (027)
    INF->>POD: helm upgrade --set tag=sha (pod rolls, no manual restart)
    D->>POD: 030 verify — 4 tools k=3 + unknown-DB ToolError + /data/chroma 7712 intact
```

---

## 3. Layers and Key Classes

### Extraction
- `extractor.py` — `MarkerExtractor.convert(pdf) -> (markdown, images_dir)`; per-PDF warn-and-continue.
- `fitz_extractor.py` — PyMuPDF backend (`page_chunks` + `write_images`); default since 033.

### Application
- `dedupe.py` — sha256 duplicate detection.
- `chunker.py` — `chunk_markdown_with_atomic_tables(md) -> list[str]`.
- `seeder.py` — `seed_resource(input_dir, output_dir, name)` (full rebuild).
- `query.py` — similarity over both collections, merged top-k (`DEFAULT_K=3`).
- `config.py` — `DATA_DIR`, `default_data_dir()` (`POLE_RAG_DATA_DIR` override, 028), `EMBED_MODEL`, `CHUNK_SIZE/OVERLAP`, `EXTRACTOR`.

### Infrastructure
- `embeddings.py` — shared `HuggingFaceEmbeddings` (`all-MiniLM-L6-v2`).
- `vision.py` — `OllamaVision.describe(image_path)` + `describe_many` (tqdm).
- `chroma_store.py` — `ChromaStore(output_dir, name)` (`text_chunks` + `image_descriptions`).

### Presentation
- `cli/seed.py`, `cli/reseed.py`, `cli/query.py`, `cli/inspect.py` — thin CLIs behind root pixi tasks.

---

## 4. Data Flow (extract → transform → respond)

| Step | Extract | Transform | Produce |
| :--- | :--- | :--- | :--- |
| Seed | PDFs + images | extract → chunk/caption → embed | Chroma DBs (`chroma.sqlite3` per resource) |
| Transfer | local `/tmp/rag-staging` | `kubectl cp` → PVC | `/data/rag/<name>/chroma.sqlite3` |
| Query | query string + k | embed → similarity over both collections, merge by distance | k hits + `source_document` (+ `image_path`) |
| Unknown DB | bad `--name` | `FileNotFoundError` → `ToolError` | safe error, no crash |
