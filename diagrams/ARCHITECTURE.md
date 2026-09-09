# System Architecture — `pole-ai`

> This document describes the **overall architecture** of the repository: the applications,
> the reusable packages, the communication layers between them, and the shared infrastructure.
> Per-component flow and class-level documents live in sibling folders:
> `docs/diagrams/<component>/FLOW.md` and `docs/diagrams/<component>/CLASSES.md`.

---

## 1. Architecture Diagram

```mermaid
flowchart LR
    %% ======================= FRONTEND (apps) =======================
    subgraph FE["Frontend Apps (Angular)"]
        PF["pole_fe<br/>Training workflow manager"]
        PA["pole_analyst<br/>Pole AI Coach"]
    end

    %% ======================= BACKEND (apps) =======================
    subgraph BE["Backend Apps (FastAPI)"]
        API["pole_api<br/>Orchestrator + slices"]
        AG["pola_agent<br/>Chatbot host (consolidated into pole_api)"]
    end

    %% ======================= PACKAGES =======================
    subgraph PKG["Reusable Packages"]
        ML["pole_ml / pole_tools<br/>(pole-train-model)"]
        CROP["pole_crop<br/>FFmpeg"]
        CR["pole_crawler<br/>Instagram"]
        CH["chatbot<br/>pole_chatbot + rag_tools"]
        RAG["pole_rag<br/>seeder + query (4 Chroma DBs)"]
        J["jobs<br/>pole_jobs"]
    end

    %% ======================= INFRASTRUCTURE =======================
    subgraph INFRA["Shared Infrastructure"]
        MONGO[("MongoDB<br/>skeleton_data / analysis-db / pole_api")]
        REDIS[("Redis<br/>job queue + pub/sub")]
        CHROMA[("ChromaDB<br/>movement_embeddings (/data/chroma)")]
        RAGDB[("RAG Chroma<br/>/data/rag: pole · calisthenics<br/>psychology · biomechanics")]
        PG[("PostgreSQL<br/>chatbot sessions")]
        FFMPEG["FFmpeg<br/>(process binary)"]
        OC["OpenCode sidecar<br/>/v1/chat/completions"]
        IG["Instagram<br/>(external)"]
        CICD["CI/CD<br/>PAT merge + reconcile belt<br/>short-sha deploy (026/027)"]
    end

    %% ======================= COMMUNICATION =======================
    PF -- "HTTP /api + WS /ws" --> API
    PA -- "HTTP /api + WS /ws" --> API
    AG -- "WS /ws/chat" --> CH

    API --> ML
    API --> CROP
    API --> CR
    API --> CH
    API --> RAG
    API --> J

    AG --> CH
    AG --> J

    CH --> J
    CH --> RAG
    RAG --> RAGDB
    RAG --> CHROMA

    ML --> MONGO
    ML --> CHROMA
    CR --> IG

    CH --> OC
    CH --> J

    API --> MONGO
    API --> REDIS
    API --> PG

    CH --> MONGO
    CH --> REDIS
    J --> REDIS
    J --> MONGO

    CROP --> FFMPEG
    ML --> CROP
    API --> CROP
    CH --> CROP

    CICD -.->|"build-push + deploy-dev<br/>(sha-tag 027)"| API
```

---

## 2. Component Description

### Applications

| Component | Type | Description |
| :--- | :--- | :--- |
| **`pole_fe`** | Angular SPA | Training-workflow manager: tricks CRUD, video management + editor/shift, training studio, model registry, system jobs, and a chatbot page. Communicates with `pole_api` over HTTP (`/api`) and WebSocket (`/ws`). |
| **`pole_analyst`** | Angular SPA | Athlete-facing "Pole AI Coach": two-pane UI (chat + tools), video upload, analysis tabs (Summary/Histogram/Pose/Plan), resilient WebSocket + session resume. Consumes the `pole_api` `analysis` slice + chatbot WS. |
| **`pole_api`** | FastAPI app | Central orchestrator. Implements slices: `training`, `crawler`, `video`, `tools` (histograms), `analysis`, `chatbot`, and `training_chatbot`. Owns HTTP/WS controllers, application services, and Mongo repositories. Ships `pole_rag` in the base image (`PYTHONPATH`, `POLE_RAG_DATA_DIR=/data/rag` on staging). |
| **`pola_agent`** | FastAPI app | Thin host of the `chatbot` package (standalone on port 8001) exposing `WS /ws/chat`. Consolidated into `pole_api` as a slice (Phase 5). |

### Packages

| Component | Description |
| :--- | :--- |
| **`pole_ml`** | ML pipeline: skeleton extraction (MediaPipe), biomechanical + histogram feature processors, sliding windows, LSTM training, embeddings, Chroma + hybrid classifiers. Data source/sink for Mongo and ChromaDB. |
| **`pole_tools`** | Reusable tool wrappers: `CropTool`, `ShiftTool`, `HistogramAnalyzer`, `PoseCorrector`, `OpenCodeLLMClient`, plus a services facade (`crop`/`shift`/`histogram`/`similarity`). Phases are manual only (`phase_frames`) — automatic phase detection was removed. |
| **`pole_crop`** | FFmpeg video service: crop, shift, thumbnail, frame capture. |
| **`pole_crawler`** | Instagram video crawler: session, client, disk storage, notifications. |
| **`chatbot`** | ReAct conversational agent backend: `ReActAgent`, `ToolRegistry`, OpenCode LLM client, job handlers, WS router, session persistence. Plus `rag_tools.py`: 4 sync RAG tools (`query_pole`, `query_calisthenics`, `query_psicology`, `query_biomechanics`, k=3, unknown-DB `ToolError`; `query_psicology` → `psychology` DB since 036). |
| **`pole_rag`** | Multimodal RAG seeder + query: Marker/PyMuPDF extraction, atomic-table chunking (1000/150), MiniLM-L6-v2 embeddings, `ChromaStore` (`text_chunks` + `image_descriptions`), 4 DBs under `/data/rag`. Phase 6 ✅ DONE (030 CLOSED); Phase 7 PyMuPDF swap planned. |
| **`jobs`** | Shared job infrastructure: `Job` model, Mongo repository, Redis queue + pub/sub events, `JobWorker`, `JobOrchestrator`, FastAPI job router. |

### Shared Infrastructure

| Component | Description |
| :--- | :--- |
| **MongoDB** | Primary datastore. DBs: `skeleton_data` (reference `signal_histograms`, `skeleton_histograms`, classes/clips), `pole_api` (training/crawler/video docs), `analysis-db` (`videos`, `skeleton-landmarks`, `video_histograms`), plus `*_testing` variants. |
| **Redis** | Job queue (FIFO of ids) + pub/sub job events (`job:started/progress/done/error`) for `jobs`/`chatbot`. |
| **ChromaDB (`/data/chroma`)** | Movement-embeddings store (`movement_embeddings`, 7712 entries) for video similarity. Untouched by the RAG ship. |
| **RAG Chroma (`/data/rag`)** | 4 RAG DBs (`pole`, `calisthenics`, `psychology`, `biomechanics`), each `chroma.sqlite3` with `text_chunks` + `image_descriptions`. Seeded locally then `kubectl cp` into the PVC (029); queried offline via baked MiniLM weights (035, CPU-torch 037). |
| **PostgreSQL** | Chatbot session persistence (`002_chatbot_sessions.sql`, `PostgresChatbotSessionRepository`). The `reference_*` Postgres vertical was removed with `pola_api` Phase 11 — reference data now lives in Mongo `skeleton_data.signal_histograms`. |
| **FFmpeg** | Video processing binary invoked by `pole_crop`. |
| **OpenCode sidecar** | `opencode serve` exposing `/v1/chat/completions` used by `pole_tools.OpenCodeLLMClient` / `chatbot.OpenCodeClient` for LLM feedback. |
| **Instagram** | External source crawled by `pole_crawler`. |
| **CI/CD (026/027)** | `ML_REVIEW_PAT`-authenticated `/oc` merges fire `build-push.yml`; `build-reconcile.yml` cron belt (15 min) covers fallback merges; `deploy-dev` dispatches immutable short-sha tags published by `build-and-push` (E2E green `85e6148`). |

---

## 3. Communication Layers

| Edge | Protocol | Description |
| :--- | :--- | :--- |
| `pole_fe` / `pole_analyst` → `pole_api` | HTTP (`/api`), WebSocket (`/ws`) | REST controllers for CRUD/jobs; WS for chatbot and job progress. |
| `pola_agent` → `chatbot` | WS (`/ws/chat`) | Chatbot host delegates to `pole_chatbot` router. |
| `pole_api` → packages | Python imports | Uses `pole_ml`, `pole_tools`, `pole_crop`, `pole_crawler`, `chatbot`, `pole_rag`, `jobs` as libraries (imported as `pole_ml.*`, `pole_tools.*`, etc.; `pole_rag` via `PYTHONPATH`, no pyproject). |
| `chatbot` → `pole_tools` | Python imports | Tool facade (`crop`/`shift`/`histogram`/`similarity`) — the **only** import surface chatbot may use (plus `pole_rag.query` via `rag_tools.py` for the 4 RAG tools). |
| `chatbot` → `pole_rag` | Python imports | `rag_tools.py` calls `pole_rag.query.query` (k=3, `source_document` metadata; `POLE_RAG_DATA_DIR` default, explicit `data_dir` wins). |
| packages → infra | Drivers | Mongo/Redis/Chroma clients, FFmpeg subprocess, httpx to OpenCode/Instagram. |

> **Reuse rule:** packages are installed editable by the pixi workspace and imported as
> `pole_ml.*` / `pole_tools.*` / `pole_crawler.*` — no `sys.path` hacks.
