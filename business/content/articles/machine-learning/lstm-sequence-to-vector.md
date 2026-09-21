# Sequence-to-Vector: LSTM that Outputs Embeddings

**Section:** Machine Learning · **Featured:** ✅

## What it delivers
One model that does two jobs — classify *and* power similarity search — so you
don't train and ship two models.

## How it's built
A single LSTM forward pass yields both classification logits and a
128-dimensional bottleneck embedding, with an input contract that makes the
dual output reliable.

## Proof
- **Code:** [packages/pole-train-model/src/pole_ml/models/video_training.py](https://github.com/fpalero/pole-ai-ml/blob/develop/packages/pole-train-model/src/pole_ml/models/video_training.py)
- **Live in the pole app:** the classifier + embedding store behind search
