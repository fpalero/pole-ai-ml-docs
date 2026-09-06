# M2 — Verified Athlete Profiles & Badges (Strava-for-Pole)

> Type: `marketplace/` · freemium profiles · Priority ⭐

## Description

**The idea in plain English.**
A public profile for athletes where every trick is "verified" by the app —
proof, not just claims. The athlete shows the world "I really landed this
shoulder mount", gets ranked on leaderboards, and discovers athletes whose
style matches hers. Think Strava for pole.

**How it makes money.**
Freemium subscription:

- **Free** — profile with up to 5 verified badges, no leaderboard.
- **Verified Athlete (€4/month)** — unlimited badges, ranked leaderboard, advanced stats.
- **Team/Studio (€19/month)** — verified profiles for a whole roster.

**Target public.**
Ambitious athletes who want social recognition for their training, and studios
who want to showcase their students' progress as marketing. The virality comes
from athletes sharing their "verified" badges.

## What it is

Athlete profiles with **verified trick badges**: the classifier confirms a move,
and a "VERIFIED" badge is attached to the profile (trick, date, critical-frame
proof). Creates a public leaderboard / "most similar athletes" discovery layer
powered by embedding similarity.

## How it makes money

Freemium profiles: free profiles with limited badges/bio; paid tier unlocks
**unlimited verified badges**, custom profile, stats dashboard, and appearance
on leaderboards. Optional "verified" re-certification per season.

## Subscription or per-service?

**Freemium subscription** (B2C), with the verified badge as the status good that
drives word-of-mouth.

| Tier | Price | Includes |
| :--- | :--- | :--- |
| Free | €0 | Profile, 5 badges, no leaderboard rank |
| Verified Athlete | €4 /mo | Unlimited badges, ranked leaderboard, advanced stats |
| Team/Studio | €19 /mo | Roster profiles + badges (see S2) |

## Implementation

**Surface:** profile + verification flow in `pole_fe`; reuse similarity engine.

**Already built (reuse):**
- Classifier + confidence history + debounce — the actual trick verification.
- Embedding similarity (`find_by_similarity`) — "athletes like you".
- Histogram/cohort z-scores — the "advanced stats" paid tier.
- Keycloak identity + temp access; Angular design tokens.

**Must add (gaps):**
- Public profile page + badge grants (event-sourced from verified analyses).
- Anti-fraud: reject low-confidence/spoofed videos (confidence threshold, single-session rule).
- Leaderboard computation from cohort stats; moderation (report/remove).
- Billing for the paid tier.

## Effort & priority

**Effort: Medium** — social features + anti-fraud review are the real work.
**Priority: ⭐** — great growth loop (verified = shareable), but only after a
trusted analysis product exists; complements S1 rather than standing alone.

*See also: `docs/app/pole_fe/PLAN.md`, `docs/packages/pole_ml/PLAN.md`,
`packages/pole-train-model/src/pole_ml/classifiers/chroma_classifier.py`.*