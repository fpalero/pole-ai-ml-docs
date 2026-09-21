# Zero-Dependency FFmpeg Primitives

**Section:** AI Applications

## What it delivers
Reusable media primitives that power every crop, shift, and preview — one
small, well-tested layer instead of scattered ffmpeg subprocess calls.

## How it's built
A stdlib-only wrapper that shells out to ffmpeg/ffprobe for frame-accurate
re-encode crops, keyframe-aligned stream copies, duration/metadata probes, and
320px thumbnails.

## Proof
- **Code:** [packages/pole_crop](https://github.com/fpalero/pole-ai-ml/tree/develop/packages/pole_crop)
- **Live in the pole app:** video crop/shift/preview in the training UI
