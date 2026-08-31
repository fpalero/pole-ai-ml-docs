# Implementation Plan — `pole-tools` (Reusable Tools Package)

> **Status:** Phase 1 complete — HTTP-free tool wrappers (CropTool, ShiftTool, HistogramAnalyzer,
> PoseCorrector, OpenCodeLLMClient) + services facade + unit tests. Consumed by
> `packages/chatbot`. Future work: trick-boundary auto-detection in CropTool, histogram metrics parity
> with `HistogramDataProcessor`, tools API slice in `pola_api`. Reference data now lives in Mongo
> `skeleton_data.signal_histograms` (not Postgres; `ReferenceBuilder` was removed).
> **2026-08-13 (PO):** automatic phase detection was **removed** — `PhaseDetector` deleted via
> `PAIML-POLE-AGENT-015`; `HistogramAnalyzer` requires manual `phase_frames`.
> **Source docs:** `docs/app/pola_agent/implementation_plan.md` (§1–11, §12), `agent_requirements.md`,
> `agent-react.md`, `pose_correction.md`.

---

## 1. Feature Context & Objective

- **Goal:** Provide reusable, HTTP-free tools that power the conversational coaching agent and the
  `tools`/`chatbot` API slices: crop, shift, histogram analysis, pose correction, similarity,
  and LLM chat. The `chatbot` slice may only call the `pole_tools.services` facade — never
  `pole_ml`/`pole_crop`/DBs directly.
- **Non-Functional Constraints:** no FastAPI imports; injectable HTTP clients for testability;
  matplotlib Agg backend (headless); ffmpeg via `pole_crop`; ≥ 80% coverage.
- **Affected Components:**
  - `packages/pole-tools/src/pole_tools/` — `exceptions.py`, `schema.py`, `llm_client.py`,
    `crop_tool.py`, `shift_tool.py`, `histogram_analyzer.py`, `pose_corrector.py`,
    `services/` (crop, shift, histogram, similarity).
  - `packages/pole-tools/tests/` — `test_llm_client`, `test_crop_shift_tools`,
    `test_pose_corrector`, `test_histogram_analyzer`, `test_hardening_analysis`.
- **Assumptions:** `pole-crop`, `pole-train-model` installed editable (namespace `pole_tools` merges
  with the CLI distribution); `pole_tools.config` lives in `pole-train-model`.

---

## 2. Architectural Layering (The "Where")

- **Domain:** Pydantic result models (`CropResult`, `ShiftResult`, `AnalysisResult`); error taxonomy
  (`ToolError`, `VideoError`, `LLMError`).
- **Application:** `CropTool`, `ShiftTool`, `HistogramAnalyzer` (metrics/classify/phase/z-score/
  plot/feedback; phases supplied manually via `phase_frames`), `PoseCorrector` (correct/overlay),
  `OpenCodeLLMClient` (multimodal chat).
- **Infrastructure:** `pole_crop.ffmpeg` (crop_segment, probe), `pole_ml` (landmarks, embeddings,
  Chroma via services), `pole_tools.config` (env), `matplotlib`/`PIL`/`opencv`.
- **Presentation:** none (library) — consumed by `chatbot` tools and planned `/api/tools/*` slice.

---

## 3. Implementation Roadmap (Atomic Steps)

### Phase 1: Tools core — ✅ DONE
- [x] `exceptions.py` + `schema.py` (Pydantic v2 results).
- [x] `OpenCodeLLMClient` — `/chat/completions`, multimodal images, tool payloads, injectable
  httpx; `LLMError` on HTTP errors/empty choices.
- [x] `crop_tool.py` / `shift_tool.py` — explicit-boundary wrappers over `pole_crop.ffmpeg`.
- [x] `histogram_analyzer.py` — M-01..M-08, classify (STATIC/SPIN/MOMENTUM), phase resample (300),
  Z-score, critical frame, deviation plot, feedback prompt, `HistogramAnalyzer.analyze/feedback`.
- [x] `pose_corrector.py` — straighten_leg, point_foot, level_hips, `extract_frame`, `correct`,
  `overlay`.
- [x] `services/` facade — `crop_clip`, `shift_clip`, `compute_histogram`, `compute_metrics`,
  `embed_window`, `classify_window`.
- [x] Unit tests (≥80%): stub HTTP, real fixture video (skips if missing), synthetic landmarks.

> **Note (2026-08-13):** `ReferenceBuilder` (reference mean/std aggregation) and its test were
> **removed** — reference data is now the Mongo `skeleton_data.signal_histograms` cohort produced by
> the `pola_api` histogram-analysis job.
>
> **Note (2026-08-13, PAIML-POLE-AGENT-015):** automatic phase detection was **removed** — the
> `phase_detector.py` module, its tests, and the `HistogramAnalyzer` auto-detection fallback were
> deleted (PO decision: phases are manual only). `HistogramAnalyzer.analyze` now **requires**
> explicit `phase_frames` and raises a clear `ToolError` when they are missing.

### Phase 2: Future — auto-detection & polish
- [ ] Application `CropTool` trick-boundary auto-detection (VideoCutter integration) instead of
  explicit boundaries.
- [ ] Application `services.histogram` parity check vs `HistogramDataProcessor` (metric naming:
  `METRICS` map vs `histogram_analyzer.METRIC_NAMES`).
- [ ] Application expose `analysis` via `tools` slice (`POST /api/tools/analyze` — pending the
  re-plan onto `/histograms/analysis` + `/histograms/summary`).

> **Note (2026-08-13, PAIML-POLE-AGENT-015):** the "wire `PhaseDetector` fallback into
> `/histograms/analysis`" item was **removed** — automatic phase detection is no longer a
> requirement; phases are manual only.

---

## 4. Quality Gates & Testing Commands (DoD)

- **Unit Tests:** `pytest -v` in `packages/pole-tools` (≥ 80% coverage).
- **Integration Tests:** `pixi run test-chatbot-live` (real ffmpeg crop through the stack);
  `pixi run test-api` once the `tools` slice lands.
- **Automation:** CI runs the package suite; import linter forbids `pole_ml`/`pole_crop` imports in
  chatbot slice.
- **Database Target:** n/a for pure tools; `skeleton_data_testing`/Chroma temp for services when
  exercised via chatbot.
- **Coverage Requirement:** ≥ 80%.
- **Additional Checks:** fixture videos present under `packages/pole-train-model/sources/videos/`
  or tests skip gracefully; no FastAPI imports in package.

---

## 5. Defined Use Cases (Gherkin + Technical Matrix)

### UC-TL-01: Crop a segment via CropTool
- **Given** a source mp4 and explicit boundaries
- **When** `CropTool.run(src, 10, 20)` is called
- **Then** it returns `CropResult` with `duration=10`
- **And** an mp4 artifact exists in `out_dir` (re-encoded)

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | library call (future `POST /api/tools/crop`) |
| Request Method | n/a |
| Required Headers | n/a |
| Payload Example | `CropTool.run(src="clean_invert.mp4", start=10, end=20)` |
| DB State (Before) | source file exists |
| DB State (After) | output clip written; missing source → `VideoError`; out-of-range → `ToolError` |

### UC-TL-02: Histogram analysis with critical frame
- **Given** landmark frames + phase_frames + in-memory reference
- **When** `HistogramAnalyzer.analyze(...)` runs
- **Then** it returns trick_type, critical_frame/phase/metric, max_z_score, metrics, resampled
- **And** deviation plot + critical frame image saved to `out_dir`

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | library call (future `POST /api/tools/analyze`) |
| Request Method | n/a |
| Required Headers | n/a |
| Payload Example | `analyze(landmark_frames, phase_frames, video_path=..., out_dir=...)` |
| DB State (Before) | n/a |
| DB State (After) | artifacts written; empty input → `ToolError` |

### UC-TL-03: Pose correction overlay
- **Given** a landmark frame with a bent knee
- **When** `PoseCorrector.correct(landmarks)` runs
- **Then** it returns corrected landmarks + issue list (`left_knee_bent`, etc.)
- **And** `overlay` produces a red/green annotated image; originals not mutated

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | library call (future `POST /api/tools/correct`) |
| Request Method | n/a |
| Required Headers | n/a |
| Payload Example | `correct(landmarks)` |
| DB State (Before) | n/a |
| DB State (After) | overlay artifact; perfect pose → empty issues |

### UC-TL-04: LLM feedback with images
- **Given** an OpenCode-compatible endpoint and plot + critical frame images
- **When** `OpenCodeLLMClient.chat(messages, images=[...])` is called
- **Then** it returns the completion
- **And** HTTP error / empty choices raise `LLMError`

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | HTTP `POST {OPENCODE_URL}/chat/completions` |
| Request Method | POST |
| Required Headers | `Content-Type: application/json` |
| Payload Example | messages + `image_url` data-URIs |
| DB State (Before) | n/a |
| DB State (After) | completion returned; endpoint down → `LLMError` |

---

## 6. Risks and Mitigations

- **Risk:** namespace collision with CLI `pole_tools` (config). **Mitigation:** config centralized in
  pole-train-model; facade re-export only.
- **Risk:** metric name drift (`METRICS` in services vs `METRIC_NAMES` in analyzer). **Mitigation:**
  parity test planned; single source of truth in `HistogramDataProcessor`.
- **Risk:** fixture videos missing → tests skip silently. **Mitigation:** explicit `pytest.skip` with
  reason; CI ensures sources present or runs mocks.
- **Risk:** LLM sidecar down. **Mitigation:** injectable client + `LLMError` → chatbot fallback
  advice/503.
- **Risk:** matplotlib/Agg headless plot generation on CI. **Mitigation:** `MPLBACKEND=Agg`; plot
  tests assert file existence not rendering.

---

## 7. Open Questions and Decisions

- Decision: tools are HTTP-free; the `chatbot` slice talks only to `pole_tools.services`.
- Decision: OpenCode accessed over HTTP (`/chat/completions`), not a Python package.
- Decision (2026-08-13): reference data lives in Mongo `skeleton_data.signal_histograms` (cohort
  produced by the histogram-analysis job); the in-memory/Postgres `ReferenceBuilder` path was removed.
- Decision (2026-08-13, PO): automatic phase detection is **removed** — phases are manual only;
  `HistogramAnalyzer` requires explicit `phase_frames` (no `PhaseDetector` fallback).
- Open: CropTool auto-detection (VideoCutter) integration priority.
- Open: whether `services.histogram` and `histogram_analyzer` should be unified (single analyzer).
