# The Hybrid Classifier: Neural Net + Vector-Search Fallback

**Section:** Machine Learning · **Featured:** ✅

## What it delivers
Higher accuracy *and* graceful handling of novel classes — the signature
pattern of this project, and reusable in any classification product.

## How it's built
The LSTM classifies first; below a 0.7 confidence threshold a ChromaDB
nearest-neighbor fallback rescues low-confidence and unseen classes.

## Proof
- **Code:** [packages/pole-train-model/src/pole_ml/classifiers/chroma_classifier.py](https://github.com/fpalero/pole-ai-ml/blob/develop/packages/pole-train-model/src/pole_ml/classifiers/chroma_classifier.py)
- **Live in the pole app:** trick recognition in the AI Coach
