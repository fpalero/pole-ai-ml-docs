# L1 — White-Label Studio / Gym License

> Type: `licensing/` · B2B license fee · Priority ⭐⭐

## Description

**The idea in plain English.**
Studios, gyms, and federations buy the whole platform and run it **under their
own name and branding** — their own login page, their own athletes, full
recognition + coaching features. They get a professional product overnight with
"Powered by us" invisible to their customers.

**How it makes money.**
Annual B2B license fee:

- **Studio (€1,500/year)** — 1 venue, 2 coaches, up to 100 athletes.
- **Gym Chain (€5,000/year)** — multiple venues, custom branding, SLA.
- **Federation (negotiated)** — full white-label bundle.

**Target public.**
Training studios, gym chains, and pole federations that want to offer their
members a branded digital coaching product but have no AI/software team. High
check size, few customers needed to matter.

## What it is

License the **entire platform** (recognition, coaching, dashboard) to a studio
or coaching brand that runs it under **their own name and branding**. They get
their own realm/branded login, their own athletes, and the full analysis stack —
you get a recurring license fee and zero user-support burden.

## How it makes money

Annual/per-seat license fee to studios, gyms, or federations that want the tool
as "their" product without building ML.

## Subscription or per-service?

**License (B2B), recurring annual.** The contract is a license, not metered
usage; support/SLA tiers add revenue.

| Tier | Annual fee | Includes |
| :--- | :--- | :--- |
| Studio | €1,500 /yr | 1 realm, 2 coaches, 100 athletes, email support |
| Gym Chain | €5,000 /yr | Multi-location realms, custom branding, SLA |
| Federation | negotiated | White-label appstore-ready bundle |

## Implementation

**Surface: infra-heavy** — multi-tenant provisioning, branding, and onboarding
tooling. No model changes (shared model, per-tenant data isolation).

**Already built (reuse):**
- Keycloak multi-realm setup, theme/branding pipeline (`phase-6` Stitch restyle) —
  white-label login is the easy, solved part.
- Design-system tokens → per-tenant theming in Angular.
- Model registry / training studio (per-tenant promoted classes).
- Jobs infra, logging (Filebeat→ES), CI/CD, k3s/Helm for isolated namespaces.

**Must add (gaps):**
- Tenant provisioning automation (realm + namespace + storage per client).
- Data isolation guarantees + tenant-aware quotas (Mongo/Chroma partitioning).
- Admin/onboarding UI for new tenants (branding upload, athlete import).
- Legal: licensing terms, data ownership/processing agreement (GDPR).

## Effort & priority

**Effort: High** — tenant isolation and onboarding automation dominate the work.
**Priority: ⭐⭐** — high margin but only makes sense once you have 2-3 committed
deal prospects; it is the "enterprise" version of S2.

*See also: `docs/app/keycloak/PLAN.md`, `docs/app/infra/PLAN.md`,
`docs/app/pole_fe/PLAN.md`.*