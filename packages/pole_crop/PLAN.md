# Implementation Plan — `pole-crop` (FFmpeg Video Service)

> **Status:** Complete for v1 — `crop_segment`, `probe_duration`, `probe_metadata`, `capture_frame`,
> frame-accurate re-encode + stream-copy modes, 4 unit tests. Consumed by `pole-tools` (CropTool,
> ShiftTool) and `pole_tools.services`. Future work: real-ffmpeg E2E test, audio handling edge
> cases, concurrency safety.
> **Source docs:** none dedicated — declared in `docs/app/pola_agent/implementation_plan.md` §1/§12;
> package `packages/pole-crop/`.

---

## 1. Feature Context & Objective

- **Goal:** Provide a thin, dependency-free FFmpeg wrapper for trimming/cropping video segments,
  probing duration/metadata, and capturing single frames — the reusable primitive behind crop,
  shift, and thumbnails in the Pole AI pipeline.
- **Non-Functional Constraints:** zero third-party Python deps (stdlib only, shells out to
  `ffmpeg`/`ffprobe`); re-encode mode frame-accurate (accurate seek + libx264/aac + faststart);
  stream-copy mode keyframe-aligned fast path; errors as `CropError`.
- **Affected Components:**
  - `packages/pole-crop/src/pole_crop/ffmpeg.py` — `CropError`, `probe_duration`, `crop_segment`,
    `probe_metadata`, `capture_frame`, `_has_audio`, `_parse_framerate`, `_fmt`, `_validate_range`.
  - `packages/pole-crop/tests/test_ffmpeg.py` — 4 unit tests.
  - Consumers: `pole_tools.services.crop_clip/shift_clip`, `pole_tools.CropTool/ShiftTool`,
    `pole_chatbot` job handlers, `pola_api` cut/shift/thumbnail services.
- **Assumptions:** `ffmpeg` + `ffprobe` binaries on PATH (or `FFMPEG_BIN` env in `pola_api` config).

---

## 2. Architectural Layering (The "Where")

- **Domain:** video segment (src, start, end), output artifact, metadata (duration, width, height,
  framerate, codec).
- **Application:** `crop_segment` (re-encode/stream-copy), `capture_frame` (+ thumbnail),
  `probe_duration` / `probe_metadata`.
- **Infrastructure:** subprocess over `ffmpeg`/`ffprobe` binaries; no Python deps.
- **Presentation:** none (library).

---

## 3. Implementation Roadmap (Atomic Steps)

### Phase 1: FFmpeg primitives — ✅ DONE
- [x] `crop_segment(src, start, end, out, *, reencode=True)` — accurate seek re-encode; stream-copy
  fast path; output existence + non-empty validation; `CropError` on failure.
- [x] `probe_duration`, `probe_metadata` (JSON ffprobe, framerate parsing), `capture_frame`
  (+ optional 320px thumbnail), `_fmt` (HH:MM:SS.mmm).
- [x] Unit tests: `_fmt`, `_validate_range`, missing-file probe → `CropError`, invalid-content
  probe → `CropError`.

### Phase 2: Future — hardening
- [ ] Tests real-ffmpeg E2E crop (re-encode + stream-copy) on a fixture mp4 (skip if ffmpeg absent).
- [ ] Infrastructure audio edge cases — no audio stream, mono/stereo, embedded subtitles
  (`_has_audio` refinement).
- [ ] Infrastructure concurrency safety — unique temp output names to avoid collisions in
  multi-job runs.
- [ ] Infrastructure optional `FFMPEG_BIN`/`FFPROBE_BIN` resolution and startup validation.

---

## 4. Quality Gates & Testing Commands (DoD)

- **Unit Tests:** `pytest -v` in `packages/pole-crop` (≥ 80%).
- **Integration Tests:** real crop exercised via `pixi run test-chatbot-live`
  (WS → crop job → ffmpeg) and `pixi run test-api` (cut/shift/thumbnail services).
- **Automation:** CI runs the package suite.
- **Database Target:** n/a.
- **Coverage Requirement:** ≥ 80%.
- **Additional Checks:** ffmpeg present check; output artifacts non-empty; no third-party imports.

---

## 5. Defined Use Cases (Gherkin + Technical Matrix)

### UC-CP-01: Crop a segment (re-encode)
- **Given** a source mp4 with duration D
- **When** `crop_segment(src, 10, 20, out)` runs with `reencode=True`
- **Then** output file exists and is non-empty
- **And** its duration ≈ 10 s (frame-accurate seek)

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | library call |
| Request Method | n/a |
| Required Headers | n/a |
| Payload Example | `crop_segment("src.mp4", 10, 20, "out.mp4")` |
| DB State (Before) | source exists |
| DB State (After) | out.mp4 exists; invalid range → `CropError` |

### UC-CP-02: Crop a segment (stream copy)
- **Given** a source mp4
- **When** `crop_segment(src, 5, 8, out, reencode=False)` runs
- **Then** output file exists and is non-empty (fast, keyframe-aligned)
- **And** no re-encoding happens (`-c copy`)

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | library call |
| Request Method | n/a |
| Required Headers | n/a |
| Payload Example | `crop_segment("src.mp4", 5, 8, "out.mp4", reencode=False)` |
| DB State (Before) | source exists |
| DB State (After) | out.mp4 exists; boundaries aligned to keyframes |

### UC-CP-03: Probe metadata
- **Given** a valid video file
- **When** `probe_metadata(path)` runs
- **Then** it returns `{duration, width, height, framerate, codec}`
- **And** missing/invalid file raises `CropError`

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | library call |
| Request Method | n/a |
| Required Headers | n/a |
| Payload Example | `probe_metadata("src.mp4")` |
| DB State (Before) | n/a |
| DB State (After) | metadata dict; bad path → `CropError` |

### UC-CP-04: Capture a single frame / thumbnail
- **Given** a valid video file
- **When** `capture_frame(path, time, out, thumbnail=320)` runs
- **Then** output image exists
- **And** thumbnail variant is ~320px wide

| Technical Check | Expected Value |
| :--- | :--- |
| Endpoint Path | library call |
| Request Method | n/a |
| Required Headers | n/a |
| Payload Example | `capture_frame("src.mp4", 12, "frame.jpg", thumbnail=320)` |
| DB State (Before) | n/a |
| DB State (After) | frame image written; failure → `CropError` |

---

## 6. Risks and Mitigations

- **Risk:** frame accuracy varies between re-encode and stream-copy. **Mitigation:** default
  re-encode (accurate seek); document stream-copy keyframe limitation for callers.
- **Risk:** ffmpeg missing on host. **Mitigation:** `FFMPEG_BIN` env resolution + startup checks in
  `pola_api`; tests skip when binary absent.
- **Risk:** large/source-corrupt input hangs. **Mitigation:** subprocess timeout (planned) + output
  existence check.
- **Risk:** concurrent jobs collide on temp output names. **Mitigation:** unique output naming
  (planned Phase 2).

---

## 7. Open Questions and Decisions

- Decision: zero-dependency stdlib package — external binaries only.
- Decision: `reencode=True` default for frame accuracy.
- Decision: `capture_frame` powers thumbnails (eager + lazy) in `pola_api`.
- Open: subprocess timeout default; whether to support non-mp4 containers.
- Open: add a dedicated real-ffmpeg E2E test in this package vs relying on chatbot/api integration tests.
