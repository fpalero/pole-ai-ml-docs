# A2 — B2B Video-Analysis API

> Type: `api/` · metered API, usage-based · Priority ⭐⭐⭐

## Description

**The idea in plain English.**
Any app can send us a video and receive back, automatically: which trick was
performed, how confident the system is, and the proof clips. Our customers
integrate this "trick recognition" into their own product with a few lines of
code — no model training, no AI experts on their payroll.

**How it makes money.**
Per-video fees with volume discounts:

- Pay-as-you-go: €0.15–0.20 per video.
- Larger volumes (1k+ videos/month): €0.08–0.12 per video.
- Enterprise (50k+/month): negotiated contract.

**Target public.**
Sports/fitness apps and platforms whose product would improve with automatic
trick recognition or movement analysis, but who can't build the ML themselves.
Higher-value bigger contracts than consumer pricing.

## What it is

Expose **video analysis as a service**: a third-party app uploads a video and
receives identified tricks + confidence + crops + similarity matches. Fitness
apps, media, and training platforms integrate it without building any ML.

## How it makes money

Metered **per video** (or per minute of processed footage). Bigger margin than
chat queries because the input is machine-verifiable ("you consumed 12
analyses") and the output is high-value (a recognized trick with proof frames).

## Subscription or per-service?

**Per-service (metered per video), tiered with volume discounts.**

| Volume tier | Price per video | Notes |
| :--- | :--- | :--- |
| Starter (pay-as-you-go) | €0.15–0.20 | + setup fee €0 |
| Growth (1k+ videos/mo) | €0.08–0.12 | volume discount |
| Enterprise (50k+/mo) | negotiated | SLA, dedicated capacity |

Per-minute-of-footage mixed billing is available for long videos (frame
processing is the real cost — Meter that, not the file count).

## Implementation

**Surface:** API-only — extend `pole_api` with a public `analysis` slice +
API-key auth + job-backed upload. **No new app, no new ML.**

**Already built (reuse):**
- `pole_api` video upload + async job pattern (202/job_id, Mongo + Redis jobs,
  WebSocket progress).
- `pole_ml` classifier + embeddings + Chroma nearest-neighbor fallback.
- `pole_crop` / `pole_tools.video_cutter` (FFmpeg primitives) for clip outputs.
- Keycloak API clients + scopes; Trivy/CI/CD already gates deploys.

**Must add (gaps):**
- Public API-key auth + per-key quotas (same rail as A1).
- Metering per video + per processing minute (seconds of footage).
- Stripe usage billing or prepaid packs.
- SLA/uptime page + simple status endpoint for enterprise tier.
- Egress/data-retention policy (GDPR purge already built in Keycloak flows).

## Effort & priority

**Effort: Low.** Same billing/metring rail as A1; the analysis pipeline is done.
**Priority: ⭐⭐⭐** — pairs with A1 as the two "money now" API plays.

*See also: `docs/app/pole_api/PLAN.md`, `docs/packages/pole_ml/PLAN.md`,
`docs/packages/pole_tools/PLAN.md`, `docs/packages/pole_crop/PLAN.md`.*