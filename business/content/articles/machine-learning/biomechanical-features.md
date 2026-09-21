# From Video to Vectors: Biomechanical Feature Engineering

**Section:** Machine Learning

## What it delivers
Hand-crafted features that win on small datasets — turning raw motion into
angles and speeds the model can actually learn from.

## How it's built
Normalized landmark time-series become per-frame joint angles and speeds,
feeding 30×14 sliding windows and 8-signal histogram metrics resampled to 100
points per phase.

## Proof
- **Code:** [packages/pole-train-model/src/pole_ml](https://github.com/fpalero/pole-ai-ml/tree/develop/packages/pole-train-model/src/pole_ml)
- **Live in the pole app:** biomechanical features behind the histogram analysis
