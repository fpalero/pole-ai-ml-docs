# 8-Signal Histogram Analysis & Cohort Z-Scores

**Section:** Machine Learning

## What it delivers
Reading "shape" instead of raw frames — scoring every athlete against a cohort
to surface exactly where they deviate.

## How it's built
Two-pass shape analysis: resample each trick to 300 points (100 per phase),
aggregate a cohort mean/std, then score with z-scores (0–100) and extract
critical-frame JPEGs at |z|>1.

## Proof
- **Code:** [packages/pole-train-model/src/pole_tools](https://github.com/fpalero/pole-ai-ml/tree/develop/packages/pole-train-model/src/pole_tools)
- **Live in the pole app:** the histogram + z-score analysis tabs
