# The "Monotonically Increasing Timestamp" Bug

**Section:** Machine Learning

## What it delivers
A real production bug story that teaches lifecycle discipline — the kind of
hard-won lesson that prevents a crash in your pipeline.

## How it's built
MediaPipe crashed with "Input timestamp must be monotonically increasing" when
one extractor instance was reused across files in VIDEO mode; the fix is
`reset()` lifecycle discipline and per-video extractor instances.

## Proof
- **Code:** [packages/pole-train-model/src/pole_ml/processors/skeleton_extractor.py](https://github.com/fpalero/pole-ai-ml/blob/develop/packages/pole-train-model/src/pole_ml/processors/skeleton_extractor.py)
- **Live in the pole app:** extractor lifecycle handled in the analysis slice
