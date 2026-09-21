# From Recognition to Action: VideoCutter with Confidence & Debounce

**Section:** Machine Learning

## What it delivers
The bridge from classifier output to a shipped feature — per-frame predictions
become clean, usable clips.

## How it's built
Confidence history, dual LSTM+Chroma thresholds, debounce, transition
filtering, region reconstruction, and lossless ffmpeg extraction.

## Proof
- **Code:** [packages/pole-train-model/src/pole_tools](https://github.com/fpalero/pole-ai-ml/tree/develop/packages/pole-train-model/src/pole_tools)
- **Live in the pole app:** the crop tool in the training UI
