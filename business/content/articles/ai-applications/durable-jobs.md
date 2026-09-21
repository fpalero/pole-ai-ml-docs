# Durable Jobs: Mongo Authority, Redis Signal

**Section:** AI Applications · **Featured:** ✅

## What it delivers
Background work — video processing, training, analysis — that survives crashes
and reports progress, so long operations never silently disappear.

## How it's built
Authoritative job state in MongoDB, Redis as a FIFO of ids plus pub/sub events,
exponential-backoff retries, cooperative cancellation, and WebSocket progress
relay. The queue is never the source of truth.

## Proof
- **Code:** [packages/jobs](https://github.com/fpalero/pole-ai-ml/tree/develop/packages)
- **Live in the pole app:** job progress streams in the training and analysis UI
