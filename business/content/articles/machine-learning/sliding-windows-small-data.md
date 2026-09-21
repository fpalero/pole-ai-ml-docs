# Sliding Windows, Data Augmentation & Small Datasets

**Section:** Machine Learning · **Featured:** ✅

## What it delivers
A small-data playbook — "200 videos done right" beats "10k videos done wrong" —
so you ship a useful model without a massive labeled dataset.

## How it's built
30-frame sliding windows with stride 5, mirror/timing/perturbation augmentation,
class weights, and Chroma-based oversampling as a few-shot assist.

## Proof
- **Code:** [packages/pole-train-model/src/pole_ml](https://github.com/fpalero/pole-ai-ml/tree/develop/packages/pole-train-model/src/pole_ml)
- **Live in the pole app:** the training pipeline that beat the big-data baseline
