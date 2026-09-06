# E1 — Virtual Trick Challenges / Competitions

> Type: `events/` · one-off entry fees + sponsors · Priority ⭐⭐

## Description

**The idea in plain English.**
Online challenges organized for the pole community: "30-day handspring
challenge" — participants film themselves, the app **verifies** each trick so
nobody can cheat, and results/leaderboards are produced automatically. Brands
and studios sponsor the event to reach a highly engaged niche audience.

**How it makes money.**
Two streams per event:

- **Participant entry fee:** €5–15 per challenge.
- **Sponsorship:** brands/studios pay €200–2,000 to title the event.
- **Event toolkit for federations:** €99–499 to run their own challenges.

**Target public.**
The pole community (athletes who love challenges and certificates),
federations/organizers who want to run verified competitions online, and sports
brands looking for a passionate, targeted audience.

## What it is

Organized online challenges ("30-day handspring challenge", "shoulder-mount
streak week") where participants submit videos and the app **verifies each
trick** with the classifier + confidence history. Results, leaderboards, and
certificates are produced automatically. Brands/studios sponsor the event.

## How it makes money

Two revenue streams:
1. **Entry fees** — per-participant, per-event (the event operator keeps a cut).
2. **Sponsorship** — brands pay to title the event and reach a niche audience.

## Subscription or per-service?

**Per-event, per-service** — an event is a discrete product with a price and
dates. No recurring billing.

| Stream | Suggested price |
| :--- | :--- |
| Participant entry | €5–15 per event |
| Sponsor (brand/studio) | €200–2,000 per event |
| Organizer "event toolkit" (B2B for federations) | €99–499 per event |

## Implementation

**Surface:** event engine (schedule, submissions, verification runs, results) +
capture flow in `pole_fe`. Model reuses the verification pipeline unchanged.

**Already built (reuse):**
- Real-time recognition + confidence history + debounce (`pole_tools.video_cutter`)
  — trick verification per submission.
- Jobs infra (Mongo + Redis) — batch verification of all submissions.
- Keycloak identity + temp access; Angular design system for the event pages.
- Model registry — per-event specific classes/promoted models.

**Must add (gaps):**
- Event CRUD + submission window + payment per event.
- Verification job per submission with threshold config (strict vs relaxed).
- Leaderboard + certificate generation.
- Anti-cheat (one video per session, temporal metadata checks).

## Effort & priority

**Effort: Medium** — event orchestration is new, but it composes existing
building blocks (verify, queue, results) rather than new ML.
**Priority: ⭐⭐** — strong community/PR value and sponsorship upside; best run in
partnership with an existing studio/federation to seed participants.

*See also: `docs/packages/pole_tools/PLAN.md`, `docs/packages/jobs/PLAN.md`,
`docs/app/pole_fe/PLAN.md`.*