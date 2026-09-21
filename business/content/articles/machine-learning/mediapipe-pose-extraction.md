# Production-Grade Pose Extraction with MediaPipe

**Section:** Machine Learning · **Featured:** ✅

## What it delivers
A pose pipeline that works regardless of athlete position or scale — clean,
classifier-ready vectors instead of raw pixel noise.

## How it's built
MediaPipe Pose in VIDEO mode with frame-by-frame landmark capture, hip-center
plus shoulder-width normalization for translation and scale invariance, and
visibility filtering.

## Proof
- **Code:** [packages/pole-train-model/src/pole_ml/processors/skeleton_extractor.py](https://github.com/fpalero/pole-ai-ml/blob/develop/packages/pole-train-model/src/pole_ml/processors/skeleton_extractor.py)
- **Live in the pole app:** skeleton extraction feeding every analysis
