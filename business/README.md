# Business Models — `pole-ai`

> Monetization options for the already-built Athlete Trick Identification System.
> Every option below reuses **existing** packages/apps (`pole_ml`, `pole_tools`,
> `pole_chatbot`, `pole_api`, `pole_fe`, `pole_analyst`, `jobs`, `pole_crop`,
> Keycloak identity, k3s/Helm infra). Each strategy is documented per type under
> this folder with: how it makes money, subscription vs per-service pricing, and
> the implementation surface (new app, API-only, frontend-only, …).

---

## Comparison Matrix

| #   | Type                          | Option                         | Monetization model         | Pricing                | New app?                   | Effort | Priority |
| :-- | :---------------------------- | :----------------------------- | :------------------------- | :--------------------- | :------------------------- | :----- | :------- |
| S1  | [subscription](subscription/) | Personal trainer (tiers)       | Subscription (B2C)         | €9-49 /mo tiers        | pole_fe upgrades           | Medium | ⭐⭐⭐      |
| S2  | [subscription](subscription/) | Coach / gym SaaS               | Subscription (B2B seats)   | €49-199 /mo per studio | pole_fe + multi-tenant     | Medium | ⭐⭐⭐      |
| S3  | [subscription](subscription/) | Deep-report upgrade (freemium) | Freemium subscription      | Free + €7 /mo          | pole_fe (paywall)          | Low    | ⭐⭐       |
| A1  | [api](api/)                   | Chatbot pay-per-query          | Metered API (B2B)          | €0.001-0.01 /query     | API-keys + billing         | Low    | ⭐⭐⭐      |
| A2  | [api](api/)                   | B2B video-analysis API         | Metered API (B2B)          | €0.05-0.20 /video      | API-keys + billing         | Low    | ⭐⭐⭐      |
| P1  | [per-service](per-service/)   | Pay-per-video credits          | Credits (B2C)              | €2-5 /analysis, packs  | pole_fe (checkout)         | Low    | ⭐⭐       |
| P2  | [per-service](per-service/)   | Grade / level assessment       | One-off (B2C)              | €19-39 /assessment     | classifier + curriculum DB | Medium | ⭐⭐       |
| L1  | [licensing](licensing/)       | White-label studio license     | License fee (B2B)          | €1-5k /yr              | infra multi-tenant         | High   | ⭐⭐       |
| L2  | [licensing](licensing/)       | Named-trick dataset library    | Dataset license (B2B)      | €500-5k one-off        | export + data contract     | Medium | ⭐        |
| M1  | [marketplace](marketplace/)   | Coach lead-generation          | Lead fee / listing (B2B)   | €20-50 /lead           | listing app                | High   | ⭐        |
| M2  | [marketplace](marketplace/)   | Verified athlete profiles      | Freemium badges (B2C)      | €4 /mo badges          | profile + verify flow      | Medium | ⭐        |
| E1  | [events](events/)             | Virtual trick challenges       | Entry fee + sponsors (B2C) | €5-15 /event           | event engine               | Medium | ⭐⭐       |

---

## How to read each option

Every strategy file follows the same template:

1. **What it is** — one-line product description.
2. **How it makes money** — the revenue mechanism + pricing rationale.
3. **Subscription or per-service** — explicit, with a tier/price suggestion.
4. **Implementation** — surface (new app vs API-only vs frontend-only), what is
   **already built** (reuse), and what must be **added** (gaps).
5. **Effort & priority** — relative build cost and go-to-market sequencing.

## Quick guidance

- **Fastest to ship (hours, not weeks): A1 / A2 / P1** — they reuse the existing
  `pole_api` + `pole_chatbot` + jobs infra with an API-key + metering layer.
- **Best moat / defensibility: P2, S2, S1** — they sit on the trained LSTM +
  cohort histogram engine that competitors would have to re-train from data.
- **Lowest marginal cost to operate: A1/A2** — per-query billing on already-costed
  inference (LLM tokens + media processing are the variable costs to meter).
- **Realistic first launch:** ship **A1 (chatbot API)** + **P1 (per-video credits)**
  with the same billing rail, then layer **S1/S2 subscriptions** behind Keycloak.

---

*See also: `docs/packages/chatbot/PLAN.md`, `docs/app/pole_api/PLAN.md`,
`docs/app/pole_fe/PLAN.md`, `docs/app/keycloak/PLAN.md`, `docs/packages/pole_ml/PLAN.md`.*