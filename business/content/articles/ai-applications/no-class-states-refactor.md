# The "No Class States" Refactor

**Section:** AI Applications

## What it delivers
Fewer bugs from stale status fields — the system's state is derived from the
data itself, so it can't drift out of sync with reality.

## How it's built
The class status machine is removed and replaced by validation against related
entities: a video is "ready to train" when its windows exist and are flagged,
not because a status field says so.

## Proof
- **Code:** [app/pole_api/src](https://github.com/fpalero/pole-ai-ml/tree/develop/app/pole_api/src)
- **Live in the pole app:** training readiness computed from data
