# P1 — Pay-Per-Video Analysis Credits

> Type: `per-service/` · prepaid credits (B2C) · Priority ⭐⭐

## Description

**The idea in plain English.**
No subscription, no commitment: an athlete uploads a video, pays a small fee to
have that one performance analyzed, and walks away. Perfect for the user who
just wants to check a single trick today and doesn't want a monthly plan.

**How it makes money.**
Prepaid credit packs (1 analysis ≈ 1 credit, 2 credits for a deep report):

- **Starter (€9)** — 5 analyses.
- **Popular (€25)** — 15 analyses.
- **Pro (€45)** — 30 analyses.

It front-loads cash (you pay before consuming) and catches the occasional user
that subscriptions scare away.

**Target public.**
Casual or occasional athletes — beginners, hobbyists, people preparing a single
routine — who won't subscribe monthly but are happy to pay a few euros when
they train. Also a natural entry door for newcomers before they upgrade to a
subscription.

## What it is

Users upload a video without any subscription and pay per analysis with
**prepaid credit packs** — the "I just want to check this one trick" product.
The same credits can also buy chatbot deep analyses, sharing the billing rail
with A1/A2.

## How it makes money

Credits = a durable currency that monetizes infrequent B2C users who won't
subscribe. It also front-loads cash (prepaid balances) and reduces billing
overhead vs per-invoice metering.

## Subscription or per-service?

**Per-service (credit packs, no subscription required).**

| Pack | Price | Credits (1 analysis ≈ 1 credit) |
| :--- | :--- | :--- |
| Starter | €9 | 5 analyses (€1.80 each) |
| Popular | €25 | 15 analyses (€1.67 each) |
| Pro | €45 | 30 analyses (€1.50 each) |

Deep-report analyses cost 2 credits; chatbot sessions cost 1–3 depending on
length. Expiry (e.g., 12 months) is standard.

## Implementation

**Surface:** `pole_fe` checkout + `pole_api` credit ledger. No new ML.

**Already built (reuse):**
- Video upload + analysis pipeline (`pole_api` video slice, `pole_ml` classifier,
  `pole_crop` output, Chroma fallback).
- Keycloak identity (accounts, temp access, GDPR purge).
- Rate limiter in `pole_chatbot` (per-credit spend guard).
- Jobs infra for async analysis tracking.

**Must add (gaps):**
- Credit ledger (Mongo collection: balance, transactions, expiry).
- Checkout (Stripe Payment Links / Paddle) → credit top-up webhook.
- Spend decrement on each analysis with race-safe reservations.
- UI: credit balance + buy-now modal in `pole_fe`.

## Effort & priority

**Effort: Low** — a ledger + checkout around existing analysis.
**Priority: ⭐⭐** — good bridge revenue that feeds users toward S1/S3.

*See also: `docs/app/pole_fe/PLAN.md`, `docs/app/pole_api/slices.md`,
`docs/packages/pole_ml/PLAN.md`.*