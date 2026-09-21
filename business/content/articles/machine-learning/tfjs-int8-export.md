# Exporting to the Browser: TensorFlow.js + int8 Quantization

**Section:** Machine Learning · **Featured:** ✅

## What it delivers
The model runs in the browser — sub-2 MB payload, sub-30 ms inference — so
users get results without a server round-trip.

## How it's built
The LSTM is converted to TensorFlow.js with int8 quantization, versioned by
run_id, and the exact training-time input window is rebuilt in the browser.

## Proof
- **Code:** [packages/pole-train-model/src/pole_tools](https://github.com/fpalero/pole-ai-ml/tree/develop/packages/pole-train-model/src/pole_tools)
- **Live in the pole app:** client-side inference path
