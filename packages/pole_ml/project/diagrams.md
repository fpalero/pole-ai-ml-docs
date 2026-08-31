# Pipeline & Integration Diagrams (Pole AI)

**Scope:** Mermaid diagrams documenting the current ML pipeline and the planned FE↔BE integration.
**Sources:** `docs/project/retraining-tool-plan.md`, `docs/project/pole-api-plan.md`, `docs/project/VIDEO_CUTTER.md`.
**Date:** 2026-08-04

> Status note: the ingestion steps (`process-embeddings` tracking fields, `samples-info`,
> modified `train-model`, `ModelTrainer.fine_tune`) are **planned** (see retraining-tool-plan.md).
> The `Classifier` interface, window→embedding `ChromaClassifier`, and `VideoCutter --chroma-only`
> are **implemented** (commit `d8d78e5`). `pole-api` / `pole-ui` are **planned** (pole-api-plan.md).

---

## 1. Current pipeline: training / re-training & cutting

```mermaid
flowchart TD

    subgraph ING["Ingestion (per class)"]
        A["videos/&lt;class&gt;/*.mp4"] --> B["SkeletonExtractor<br/>(MediaPipe: 33 landmarks → 14 features/frame, visibility ≥ 0.7)"]
        B --> C["ProcessingPipeline<br/>(sliding windows 30×14, stride)"]
        C --> D["MongoDB skeleton_windows<br/>(label = folder, embedding_models, training_status)"]
        D --> E["process-embeddings<br/>SkeletonEmbedding → 128-d feature_vector"]
        E --> F["ChromaDB movement_embeddings<br/>(./FeaturesEmbeddings, cosine, label metadata)"]
    end

    subgraph TRN["Training / re-training (LSTM)"]
        D --> G["ModelData.get_training_data"]
        G --> H{"retrain mode"}
        H -->|"normal (full)"| H1["ModelTrainer.train<br/>rebuild net with n+1 classes"]
        H -->|"fine-tune"| H2["ModelTrainer.fine_tune<br/>swap softmax head to n+1"]
        H -->|"loo (eval)"| H3["Leave-One-Video-Out evaluation"]
        H1 --> I["models/*.keras + *_encoder.pkl"]
        H2 --> I
        H3 -.-> I
        I --> J["--reembed selected classes → ChromaDB"]
        J --> F
        I --> K["HybridClassifier<br/>(LSTM first, ChromaDB kNN fallback when conf < 0.7)"]
    end

    subgraph CUT["Cutting videos (VideoCutter)"]
        V["video.mp4"] --> W["SkeletonExtractor"]
        W --> X["sliding windows 30×14"]
        X --> Y{"classifier.predict(window)"}
        Y -->|"HybridClassifier (LSTM + Chroma fallback)"| Z["(class, confidence)"]
        Y -->|"ChromaClassifier --chroma-only (embeds window internally)"| Z
        Z --> R["confidence history / debounce / dual thresholds"]
        R --> S["transition filtering / segment reconstruction"]
        S --> T["ffmpeg extraction"]
        T --> U["output_clips/*.mp4"]
    end
```

**Reading notes**
- The **training / re-training** branch starts from Mongo windows; `transition` doubles as the
  noise/negative class in the cutter.
- The **cutting** branch is classifier-agnostic: `VideoCutter` only calls the shared
  `Classifier.predict(window) → (class, confidence, metadata)` contract, so a new trick can be
  cut through `--chroma-only` (ChromaClassifier embeds the window internally) with no LSTM.

---

## 2. FE ↔ BE API interaction (pole-ui ↔ pole-api)

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as pole-ui (Next.js)
    participant API as pole-api (FastAPI)
    participant KC as Keycloak (OIDC)
    participant PG as PostgreSQL
    participant Mongo as MongoDB
    participant Chroma as ChromaDB

    User->>UI: login
    UI->>KC: authorization-code flow
    KC-->>UI: JWT tokens
    User->>UI: trigger action (create class / crawl / cut / review / retrain)
    UI->>API: HTTPS request + Bearer JWT
    API->>PG: read/write curation state (classes, crawls, posts, clips, jobs)
    API->>API: enqueue BackgroundTask (job_id)
    API-->>UI: 202 {job_id}

    loop Poll job status
        UI->>API: GET /api/jobs/{id}
        API->>PG: read job row (status / progress / result / error)
        API-->>UI: {status, progress, result}
    end

    Note over API,Mongo: job → process-data (windows → Mongo) + process-embeddings (pending → ChromaDB)
    Note over API,Chroma: job → pole-crawler (Instagram download) / VideoCutter --chroma-only (cut)
    Note over API,PG: retrain job → modified train-model (training_runs + window marking)
```

---

## 3. FE ↔ BE flow: add a class, download from Instagram, re-train

```mermaid
flowchart TD
    U1["FE: user creates a new trick (form)"] --> B1["BE: POST /api/classes<br/>{name, hashtags, limit, min_windows}"]
    B1 --> B2["BE: persist class (PostgreSQL)"]
    B2 --> U2["FE: POST /api/classes/{id}/crawl"]
    U2 --> B3["BE: pole-crawler downloads Instagram videos<br/>(hashtag → downloads/&lt;trick&gt;/)"]
    B3 --> U3["FE: POST /api/classes/{id}/cut"]
    U3 --> B4["BE: VideoCutter --chroma-only (ChromaClassifier kNN)<br/>→ curated/&lt;trick&gt;/ clips"]
    B4 --> U4["FE: human review (watch / accept / discard clips)"]
    U4 --> U5["FE: POST /api/classes/{id}/process (on accepted clips)"]
    U5 --> B5["BE: process-data (windows → Mongo)<br/>+ process-embeddings (pending → ChromaDB)"]
    B5 --> U6["FE: GET /api/classes/{id}/stats<br/>(samples-info: embedded / trained / pending)"]
    U6 --> D{"enough samples to promote?"}

    D -->|"No — keep few-shot"| P1["New class stays Chroma-only<br/>(HybridClassifier kNN fallback, no retrain)"]
    D -->|"Yes — promote"| U7["FE: POST /api/classes/{id}/retrain<br/>{mode: full | fine-tune, augment, class_weight, reembed}"]
    U7 --> B6["BE: run train-model --classes ...<br/>old classes + new trick"]
    B6 --> B7["BE: new models/*.keras + *_encoder.pkl<br/>+ training_runs doc + windows marked trained"]
    B7 --> B8["BE: re-embed selected classes (--reembed)"]
    B8 --> P2["New class now classified by LSTM alongside old classes"]

    P1 --> END["Done"]
    P2 --> END
```

**Sequence summary**
1. **Add class** — user creates the trick in `pole-ui`; `pole-api` stores it in PostgreSQL.
2. **Download from Instagram** — `crawl` job runs `pole-crawler`; raw videos land in `downloads/<trick>/`.
3. **Cut & review** — `cut` job runs `VideoCutter --chroma-only`; the user accepts/discards clips in the UI.
4. **Process** — accepted clips go through `process-data` (windows → Mongo) + `process-embeddings` (pending → ChromaDB).
5. **Decide** — `samples-info`-powered stats drive the promotion decision.
6. **Re-train (promote)** — `retrain` runs the modified `train-model` (`full`/`fine-tune`) + `--reembed`;
   until promoted the new class is served by the ChromaDB few-shot path.
