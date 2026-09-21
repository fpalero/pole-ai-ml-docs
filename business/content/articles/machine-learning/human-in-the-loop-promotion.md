# Human-in-the-Loop Model Promotion

**Section:** Machine Learning

## What it delivers
A deploy step that is a human decision, not an API call — scraped data becomes
a training set through a deliberate gate.

## How it's built
Per-video `selected_for_training` flags, readiness stats, train vs fine-tune
window selection, then approve/activate to make a run live.

## Proof
- **Code:** [app/pole_api/src](https://github.com/fpalero/pole-ai-ml/tree/develop/app/pole_api/src) · [app/pole_fe](https://github.com/fpalero/pole-ai-ml/tree/develop/app/pole_fe)
- **Live in the pole app:** the approve/activate flow in the model registry
