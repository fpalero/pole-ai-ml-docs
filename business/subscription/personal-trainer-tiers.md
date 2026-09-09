# S1 — Personal Trainer (Subscription Tiers)

> Type: `subscription/` · B2C recurring revenue · Priority ⭐⭐⭐

## Description

**The idea in plain English.**
Trainers are expensive and don't watch you between classes. This product is an
"AI coach in your pocket": an athlete films herself doing a trick (e.g. a
shoulder mount), and the app recognizes the move and acts like a personal
trainer — it tells her how her execution compares to other athletes, highlights
frames where her form can improve, and lays out a simple weekly training plan.

**How it makes money.**
Monthly subscription with a free plan to attract users, then paid tiers:

- **Free** — you get your trick identified, once a week. Enough to taste the product.
- **Plus (€9/month)** — unlimited identification + detailed video feedback.
- **Pro (€19/month)** — full comparison against other athletes + monthly training plans.
- **Studio (€49/month)** — for coaches/gyms managing a whole group.

Recurring revenue: once an athlete is hooked on tracking her progress, she
stays subscribed month after month.

**Target public.**
Pole fitness athletes — from beginners who just landed their first trick to
semi-competitive athletes — and the coaches/studios who train them. People who
already spend €30–80/month on classes and value any tool that makes their
hidden practice time count.

## What it is

A consumer-grade "AI personal trainer" for pole athletes: they record a trick,
the app identifies it, and a monthly subscription unlocks automated coaching —
cohort percentile scores, critical-frame critiques, and a 4-week improvement
plan.

## How it makes money

Recurring monthly subscription with a free tier as acquisition. The value is
"an always-available coach between lessons" — the LLM tips + cohort analytics
are the differentiating content that users pay to keep seeing.

## Subscription or per-service?

**Subscription.** Pricing suggestion (EU market):

| Tier | Price | What unlocks |
| :--- | :--- | :--- |
| Free | €0 | Trick ID + 1 analysis / week, no reports |
| Plus | €9 /mo | Unlimited ID, deep-report, 10 critical-frame critiques |
| Pro | €19 /mo | Cohort percentile, 4-week plans, multi-athlete + history |
| Studio | €49 /mo | Everything + team/class profile (see S2) |

VAT/region pricing and an annual (-20%) option are the normal add-ons.

## Implementation

**Surface:** frontend-first (`pole_fe` / `pole_analyst` upgrades) + billing layer. No new ML.

**Already built (reuse):**
- `/packages/pole_ml` — LSTM classifier + embeddings + hybrid Chroma fallback.
- Histogram/cohort z-score engine and critical-frame extraction (8-signal analysis).
- `pole_chatbot` + `pole_api` — coaching feedback flow (z-score outliers → LLM tip / 4-week plan).
- Keycloak identity — magic links, temp-access sessions, GDPR purge (consumer-ready auth).
- `pole_fe` / `pole_analyst` — Angular frontends, design-system tokens, model registry.

**Must add (gaps):**
- Billing integration (Stripe / Paddle) + webhooks.
- Tier gating on the API layer (`pole_api` slice: `billing`).
- Paywalled report generation with usage counters (meter per analysis).
- Free-tier weekly usage cap (reuse the sliding-window rate limiter already in `pole_chatbot`).

## Effort & priority

**Effort: Medium.** No model work; the work is checkout, gating, and report UX.
**Priority: ⭐⭐⭐** — it monetizes the coaching value already built and is the
natural B2C flagship.

*See also: `docs/app/pole_analyst/PLAN.md`, `docs/packages/pole_ml/PLAN.md`,
`docs/app/pole_fe/PLAN.md`, `docs/app/keycloak/PLAN.md`.*