# Real-Time Recognition over WebSockets

**Section:** AI Applications · **Featured:** ✅

## What it delivers
Live ML inference delivered to the user under a 100 ms budget — the difference
between a "demo" and a product that responds while you use it.

## How it's built
WebSockets streaming results computed from a 30-frame circular buffer stepped
at stride 5, with 3/5 vote consensus and cosine checks — interleaving frames,
inference, and I/O without breaking latency.

## Proof
- **Code:** [app/pole_api/src](https://github.com/fpalero/pole-ai-ml/tree/develop/app/pole_api/src)
- **Live in the pole app:** real-time coaching feedback on `pole-coach.duckdns.org`
