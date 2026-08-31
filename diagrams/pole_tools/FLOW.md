# Flow — `pole_tools` (Reusable Tools + CLI)

> Layers and key classes of the reusable tools package: tool wrappers, the services facade, and
> the CLI entrypoints (`pole_tools`). Shipped in the `pole-train-model` package alongside
> `pole_ml`. Class-level details: [CLASSES.md](./CLASSES.md).

---

## 1. Tools Flow Diagram

```mermaid
flowchart LR
    subgraph CALL["Callers"]
        API["pola_api tools slice"]
        CH["chatbot / pola_agent"]
        CLI["CLI entrypoints"]
    end

    subgraph FACADE["Services facade"]
        SC["services/crop"]
        SS["services/shift"]
        SH["services/histogram"]
        SML["services/similarity"]
    end

    subgraph TOOLS["Tool wrappers"]
        CT["CropTool"]
        ST["ShiftTool"]
        HA["HistogramAnalyzer"]
        PC["PoseCorrector"]
        LLM["OpenCodeLLMClient"]
    end

    subgraph DEP["Dependencies"]
        FC["pole_crop / ffmpeg"]
        ML["pole_ml"]
        OC[("OpenCode sidecar")]
        MONGO[("MongoDB signal_histograms")]
    end

    API --> FACADE
    CH --> FACADE
    CLI --> TOOLS

    FACADE --> CT & ST & HA
    CT --> FC
    ST --> FC
    HA --> ML
    HA --> LLM
    LLM --> OC
```

---

## 2. CLI Flow Diagram

```mermaid
flowchart TD
    subgraph CLI["pole_tools CLI (commands)"]
        PD1["process_data"]
        TM["train_model"]
        PE["process_embeddings"]
        SI["samples_info"]
        VC["video_cutter"]
        EV["evaluate_video"]
        FBS["find_by_similarity"]
        AC["audit_clips"]
        ED["extract_data"]
        MW["migrate_windows"]
    end
    CLI --> ML["pole_ml pipeline"]
    CLI --> REPO[("MongoDB / ChromaDB / files")]
```

### 2.1 Diagram Component Descriptions

| Node | Purpose & Use |
| :--- | :--- |
| **CALL — `pola_api` tools slice** | Backend HTTP slice that exposes crop/shift/correct/histogram to clients. |
| **CALL — `chatbot` / `pola_agent`** | Conversational agents that call the tools facade to perform actions. |
| **CALL — CLI entrypoints** | `pole_tools` command-line tools for data processing/training. |
| **FACADE — services/crop · shift · histogram · similarity** | The **only** public import surface for callers; each facade wraps the matching tool. |
| **CropTool** | Wraps `pole_crop` ffmpeg `crop_segment` to crop a video segment. |
| **ShiftTool** | Wraps `pole_crop` to shift/re-crop a clip. |
| **HistogramAnalyzer** | Computes metrics, classifies trick type, resamples phases (manual `phase_frames`), Z-score, critical frame, deviation plot, feedback. |
| **PoseCorrector** | Straighten/point/level corrections + red/green overlay. |
| **OpenCodeLLMClient** | Multimodal LLM wrapper over `/chat/completions`. |
| **DEP — `pole_crop` / ffmpeg** | Video processing dependency. |
| **DEP — `pole_ml`** | Feature/embedding dependency. |
| **DEP — OpenCode sidecar** | LLM endpoint. |
| **DEP — MongoDB** | Reference cohort `skeleton_data.signal_histograms` (mean/std per trick/metric). |

---

## 3. Layers and Key Classes

### Tool wrappers
- `CropTool`, `ShiftTool` — wrap `pole_crop.ffmpeg.crop_segment`.
- `HistogramAnalyzer` — M-01..M-08 metrics, classify, phase resample (100/phase, manual
  `phase_frames`), Z-score, critical frame, deviation plot, feedback prompt.
- `PoseCorrector` — straighten_leg / point_foot / level_hips + red/green overlay.
- `OpenCodeLLMClient` — multimodal wrapper over `/chat/completions`.

### Services facade (`services/`)
- `crop.py`, `shift.py`, `histogram.py`, `similarity.py` — the **only** import surface for callers.

### Schema / config
- `schema.py` — Pydantic domain models (`CropResult`, `ShiftResult`, `AnalysisResult`).
- `config.py` — settings.

### CLI (`cli/`)
- `process_data`, `train_model`, `process_embeddings`, `samples_info`, `video_cutter`,
  `evaluate_video`, `find_by_similarity`, `audit_clips`, `extract_data`, `migrate_windows`,
  `clip_resolver`, `eval_utils`.

---

## 4. Data Flow (extract → transform → produce)

| Tool | Extract | Transform | Produce |
| :--- | :--- | :--- | :--- |
| Crop | video + bounds | ffmpeg `crop_segment` | cropped clip |
| Shift | clip + delta | ffmpeg re-crop | shifted clip |
| Histogram | landmarks + phase_frames | metrics, phase resample, Z-score, critical frame, plot | `AnalysisResult` + artifacts |
| Pose correct | critical frame landmarks | straighten/point/level | corrected landmarks + overlay |
| LLM feedback | analysis + plot | prompt → LLM | coaching text |
| CLI (process_data) | raw videos | `pole_ml` extract→process | windows + histograms |
