# S3 — Deep-Report Upgrade (Freemium)

> Type: `subscription/` · freemium → subscription · Priority ⭐⭐

## Description

**The idea in plain English.**
Everyone can identify their trick for free — the fun part. Paying users unlock
the **understanding** part: a full "deep report" per trick that explains how
their execution compares to other athletes, shows the exact frames to fix, and
delivers a 4-week training plan written for them.

**How it makes money.**
Freemium subscription: the free tier feeds the funnel, the paid tier converts:

- **Free** — trick identification + confidence, 3 analyses/week.
- **Deep Report (€7/month)** — unlimited analyses + full deep report.
- **Coach Pack (€14/month)** — deep report + monthly plans + progress history.

**Target public.**
Athletes who don't just want to know the name of their move — they want to know
*why* and *how to improve*. The natural step between "curious beginner" and
"serious trainee" who will later pay for the full personal-trainer tier.

## What it is

Free users get **trick identification** (the classifier output); paying users get
the **deep biomechanical report**: 8-signal histograms, cohort percentile,
critical-frame JPEGs, and a 4-week LLM-written plan for a single trick.

## How it makes money

Pure freemium upgrade path. The free tier is deliberately *just* identification
(exciting, shareable), the paid tier is the *understanding* (repeat value).
Converts one trick into a habit; the habit converts into a subscription.

## Subscription or per-service?

**Subscription** (though the same report can also be sold as a per-service item
after — see P2 for the one-off version).

| Tier | Price | What it includes |
| :--- | :--- | :--- |
| Free | €0 | Trick ID + confidence, 3 analyses/week |
| Deep Report | €7 /mo | Unlimited ID + full histogram/cohort/critical-frame report |
| Coach Pack | €14 /mo | Deep report + 4-week plans + historical trends |

## Implementation

**Surface:** frontend paywall (`pole_fe` / `pole_analyst`) + `pole_api` report endpoint. No new ML.

**Already built (reuse):**
- Histogram/cohort z-score analysis, critical-frame extraction (the report guts).
- `pole_chatbot` coaching prompt (LLM-CF-03) for tips + 4-week plans.
- Keycloak identity + rate limiter (free-tier cap).
- `pole_fe` UI (report chart components already exist).

**Must add (gaps):**
- Billing (Stripe/Paddle) + tier attribute on the Keycloak session/token (or API JWT claim).
- Paywall guard on the report endpoint (`pole_api` `billing` slice).
- Usage counting per account (free weekly cap, unlimited+ for paid).

## Effort & priority

**Effort: Low** — smallest-scope monetization: gate an endpoint, join the dots in the UI.
**Priority: ⭐⭐** — a quick win to validate willingness-to-pay before S1/S2.

*See also: `docs/packages/pole_ml/PLAN.md`, `docs/app/pole_analyst/PLAN.md`.*