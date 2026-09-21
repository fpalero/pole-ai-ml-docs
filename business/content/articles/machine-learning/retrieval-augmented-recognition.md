# Retrieval-Augmented Recognition: Nearest-Neighbor Fallback

**Section:** Machine Learning

## What it delivers
A few-shot-friendly classifier for when novelty is the norm — ranked matches
that rescue low-confidence cases without retraining.

## How it's built
ChromaClassifier k-NN voting with confidence, plugged under the hybrid pattern
as the LSTM fallback, with cosine-distance thresholds and metadata hygiene.

## Proof
- **Code:** [packages/pole-train-model/src/pole_ml/classifiers/chroma_classifier.py](https://github.com/fpalero/pole-ai-ml/blob/develop/packages/pole-train-model/src/pole_ml/classifiers/chroma_classifier.py)
- **Live in the pole app:** the low-confidence fallback in trick recognition
