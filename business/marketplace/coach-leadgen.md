# M1 — Coach Lead-Generation Marketplace

> Type: `marketplace/` · two-sided marketplace · Priority ⭐

## Description

**The idea in plain English.**
An athlete analyzes a trick and the app asks: "why not learn it properly?" —
showing coaches and studios near them who teach exactly that move. Athletes
stay free; coaches pay to appear in the results and receive new students.

**How it makes money.**
Coaches are the paying side:

- Per lead (verified contact): €20–50.
- Featured in results (per trick): €50/month.
- Studio profile + unlimited leads: €99/month.

**Target public.**
Pole studios and independent coaches looking for new students — they already
pay for ads and think nothing of a cost-per-lead. Athletes remain free users,
which keeps the pool of leads growing.

## What it is

After a free trick analysis, the app shows "coaches who teach this trick":
studios/coaches pay to appear in those results, and athletes message/visit them.
The analysis becomes a **discovery funnel** — "you just landed a shoulder mount;
here are 3 local coaches who teach it."

## How it makes money

Coaches/studios are the paying side: pay-per-lead, featured listings, or a
monthly visibility subscription. Athletes stay free (keeps the funnel big).

## Subscription or per-service?

**Per-lead or featured listing** (per-service for coaches), optionally wrapped
in a monthly "visibility" subscription.

| Coach option | Price |
| :--- | :--- |
| Per lead (verified contact) | €20–50 |
| Featured in results ("teaches: shoulder mount") | €50 /mo per trick |
| Studio profile + unlimited leads | €99 /mo |

## Implementation

**Surface: new marketplace app** (listing, matching, messaging/lead capture) on
top of existing analysis. No new ML (embedding similarity can rank "coach
teaches trick X").

**Already built (reuse):**
- Classifier + embeddings — "which tricks" per analysis (the matching key).
- Keycloak identity, temp access; Angular design system for a fast frontend.
- `pole_api` jobs + data layers.

**Must add (gaps):**
- Coach/studio accounts + onboarding (separate of athlete accounts).
- Listing + search/matching ("teaches" ↔ "just landed").
- Lead-capture mechanism (email relay or chat).
- Billing for coaches (subscription or per-lead) — the only monetization path.

## Effort & priority

**Effort: High** (marketplaces need both sides seeded; cold-start problem).
**Priority: ⭐** — big upside if a local network exists, but the hardest to launch
and most dependent on distribution.

*See also: `docs/app/pole_fe/PLAN.md`, `docs/packages/pole_ml/PLAN.md`.*