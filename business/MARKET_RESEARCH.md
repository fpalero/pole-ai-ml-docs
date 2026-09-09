# Market Research — `pole-ai` business models

> **What this file is.** A fast, first-pass market sizing for the 12 monetization
> options in this folder. For each idea it answers two business questions:
> who is the target, and roughly how many people could realistically become
> customers. Estimated from public 2025–26 industry data; ranges are deliberately
> wide and each option ends with the check that tightens the estimate.

---

## How market research works

You don't need a data team. You need a **funnel** with three numbers and two
checks.

### The funnel: TAM → SAM → SOM

| Term | Meaning | In one line |
| :--- | :--- | :--- |
| **TAM** | Total Addressable Market | Everyone who could ever use it |
| **SAM** | Serviceable Addressable Market | The slice you can actually reach (language, region, platform) |
| **SOM** | Serviceable Obtainable Market | Customers you can realistically win in ~3 years — **the number that matters** |

As a small business, assume you capture **0.5–3% of SAM**. Optimistic marketing
can stretch that; a B2B niche with few competitors can beat it on revenue per
customer.

### The two checks

1. **Willingness to pay** — look at what 5–10 real competitors charge. Their
   prices *are* the market's answer; you price around them.
2. **Bottom-up validation** — shrink the problem: talk to 10 coaches, run a
   waitlist landing page, count every studio in one region with a directory.
   Regret-direction: an estimate an order of magnitude wrong only costs you a
   week to correct when you start small.

What follows is the **top-down** half. Treat it as planning input, then run the
bottom-up checks before building anything.

---

## Anchor numbers (data used)

| Fact | Value | Source |
| :--- | :--- | :--- |
| Pole-fitness equipment market | $520M (2024) → $1.13B (2033), ~9.1% CAGR | Research Intelo, 2025 |
| US audience actively searching pole-dance | ~2.1M people (≈20% of global → ~10M "interested") | Rascasse audience data, 2026 |
| Active practitioners worldwide (training, not just curious) | **est. 1–3M** (derived from studios + equipment + audience) | reasonable bounds |
| "Serious" athletes (train at home, track progress) | est. 10% of practitioners → **100–300k** | assumption |
| Competitive athletes | 3,000+ compete in PSO events yearly; IPSF worlds from 40+ countries; >200 athletes at German nationals | PSO, IPSF, polecamps |
| Studios + independent coaches | **est. 2–5k studios + 5–10k freelancers** (Mexico alone 400+; US ~1k+; "thousands" worldwide) | yourpolepal, PoleLife, IPIA |
| B2B benchmark pool (video-analysis APIs) | Hundreds of sport/fitness apps globally (Hudl/Dartfish-class demand) | industry |

**Why the ranges?** "Interested" (~10M) is much bigger than "practices" (1–3M),
which is bigger than "would pay" (tens of thousands to a few hundred thousand).
Every row below keeps that gap explicit.

---

## Per idea

| Idea | Target public | Interested pool (SAM) | Realistic goal (SOM, yr 3) | Validate by |
| :--- | :--- | :--- | :--- | :--- |
| **S1 — Personal trainer (subs)** | Serious athletes training at home | 50–150k reachable (of 100–300k serious) | **1–3k subscribers** (~€20–65k/mo) | Waitlist; compare workout-app churn |
| **S2 — Coach / gym SaaS** | Studios (2–5k) + freelancers (5–10k) | 7–15k orgs | **100–500 studios** (~€15–75k/mo) | Interview 10 coaches; count studios locally |
| **S3 — Deep-report freemium** | Everyone doing trick ID (free) → upgraders | 50–150k engaged free users | **2–5k paying** (2–5% conversion) | A/B a paywall on a landing page |
| **A1 — Chatbot pay-per-query** | App/platform developers needing video analysis | Hundreds of apps globally; pole niche <50 | **5–30 API customers** | Survey fitness-app teams; check API signups |
| **A2 — B2B video-analysis API** | Sports/fitness apps + media | Same pool as A1 | **5–25 customers** (~€5–50k/mo) | Publish API docs; watch signup rate |
| **P1 — Per-video credits** | Casual practitioners (the 90%) | 900k–2.7M casual | **1–3k paying/yr** (~€10–50k) | Pre-sell "pay as you use" |
| **P2 — Grade / level assessment** | Syllabus- and competition-oriented athletes | 20–50k (serious + competitive) | **500–5k assessments/yr** | Partner with a federation; price test |
| **L1 — White-label license** | Studios, chains, federations that can afford it (€1.5–5k) | 500–1.5k orgs | **5–30 licenses** (~€8–150k/yr) | Pitch 3 studios before building |
| **L2 — Dataset library** | Sports-tech companies, researchers | Tens of buyers globally | **1–10 deals** | Verify data rights FIRST (legal) |
| **M1 — Coach lead-generation** | Coaches/studios near athletes | Your city/region only (hundreds) | **10–50 paid accounts** (needs density!) | Pick 1 metro; count studios there |
| **M2 — Verified athlete profiles** | Ambitious athletes (social proof) | 100–300k serious | **1–5k paid badges** | Check engagement in pole FB/IG groups |
| **E1 — Virtual trick challenges** | Community + competitors + sponsors | 20–50k engaged athletes | **500–5k entries/yr + 2–20 sponsors** | Run one pilot event free |

---

## What this tells you

1. **The niche is small but real and growing (~9% CAGR).** No idea here is a
   "hundreds of millions" play — but several are very healthy for a 1–3 person
   product.
2. **Highest revenue per customer**: S2, L1, P2 (B2B / services) — fewer
   customers, more money each.
3. **Largest raw pools**: S1 / S3 / P1 (B2C volume) — with the *hardest* problem
   being marketing (reaching even 2% of a niche).
4. **B2B API (A1/A2)**: the pool is small but buyers churn the least once
   integrated — the classic "10 customers who pay forever" pattern.
5. **Most realistic first move, by data**: **P2 (assessment)** if you can partner
   with a federation, or **A1 / P1** for the fastest self-serve revenue. SOM is
   small everywhere, so winning = distribution, not just the build.

---

## Sources

- Research Intelo — *Pole Fitness Pole Market Report 2033* (2025).
- Rascasse — *Pole dance: 2.1M Fans in the United States (2026)*.
- Pole Sport Organization — *How It Works* (3,000+ competitors/year).
- IPSF / Wikipedia — *Pole sports* (federation, world championships).
- yourpolepal — *Worldwide Pole Studio Directory* (Mexico 400+ studios).
- PoleLife — *Pole studio directory* (289 US studios).
- IPIA — *Pole Industry Financial Survey* (2024/2026).
- polecamps — *A guide to pole competitions worldwide* (2026).

*Estimates are the author's own; ranges were chosen to be directionally safe
rather than precise. Last updated 2026-09-06.*