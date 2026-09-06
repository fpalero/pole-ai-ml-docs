# S2 — Coach / Gym SaaS (Seat License)

> Type: `subscription/` · B2B recurring revenue · Priority ⭐⭐⭐

## Description

**The idea in plain English.**
A dashboard for pole coaches and gyms to manage their whole team in one place:
each athlete's tricks, how they compare with each other, and automatic alerts
when someone is improving or stalling — even for athletes training at home.
The coach suddenly sees the entire roster without filming anything himself.

**How it makes money.**
Per-studio monthly subscription:

- **Coach Solo (€49/month)** — one coach, up to 20 athletes.
- **Gym (€149/month)** — 3 coaches, 100 athletes, team comparisons.
- **Gym+ (€299/month)** — unlimited, white-label reports, priority support.

Recurring B2B revenue: once a studio builds years of athlete history on the
platform, it is very hard to leave.

**Target public.**
Pole studios, gyms, and independent coaches who train multiple athletes and
already pay for booking/video tools. They buy the "full roster visibility"
that a human coach can't get alone.

## What it is

A per-studio subscription for pole coaches and gyms: the coach manages a
**roster of athletes**, tracks their tricks, and gets cross-athlete cohort
analytics and progress alerts. Athletes film at the studio or at home; the
coach sees everything in one dashboard.

## How it makes money

B2B monthly seat/studio pricing. Coaches already pay for tools (booking apps,
video review); the pitch is "automatic trick-level progress tracking for your
whole roster."

## Subscription or per-service?

**Subscription (per studio, with seats).** Pricing suggestion:

| Plan | Price | What it includes |
| :--- | :--- | :--- |
| Coach Solo | €49 /mo | 1 coach, 20 active athletes, full analytics |
| Gym | €149 /mo | 3 coaches, 100 athletes, multi-team cohorts |
| Gym+ | €299 /mo | Unlimited coaches/athletes, white-label reports, SLA |

## Implementation

**Surface:** `pole_fe` coach dashboard + multi-tenant security layer. No new ML.

**Already built (reuse):**
- Cohort z-score + histogram engine (exactly the cross-athlete analytics needed).
- Model registry / training studio (coach can retrain class usage over time).
- Keycloak — org/group support, magic links, temp access, GDPR purge.
- `pole_api` slices (video, training, tools) + jobs infra for async processing.
- Angular frontends with design-system tokens (dashboards come cheap).

**Must add (gaps):**
- Organization/tenant model in Keycloak (realm groups or org clients).
- Coach dashboard screens: roster management, per-athlete history, alerts.
- Billing per studio (Stripe subscriptions + seat math).
- Role-based gating (coach vs athlete see different scopes).

## Effort & priority

**Effort: Medium.** Multi-tenant scoping + dashboard UX are the bulk; no model work.
**Priority: ⭐⭐⭐** — highest ARPU per customer of the B2C options and a strong
moat (coaches lock in their roster's history).

*See also: `docs/app/pole_api/slices.md`, `docs/app/pole_fe/PLAN.md`,
`docs/app/keycloak/PLAN.md`.*