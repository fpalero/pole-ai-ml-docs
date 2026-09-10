# Theme 06 — Data Acquisition & Infra · Audience: Entrepreneur / Technical PM

> The ops-cost story: scraping as a data-acquisition channel, a sensible
> deployment footprint, and identity/security as a trust feature.

## Catalog

### F1 (product lens) — Data Acquisition Without a Data Budget
- **Difficulty:** Any
- **Type:** Strategy guide
- **Hook:** "Before you buy a dataset, know what a scraper plus QC can hand you for free."
- **Description:** The economics of scraping + QC as a first data source: cost
  (nothing but infra), the pending/accept QC loop as quality insurance, and when
  to graduate to licensed data. Directly applicable to any content-hungry ML
  product.
- **Grounding:** `docs/packages/pole_crawler/PLAN.md`.
- **Sellable angle:** Founders' data-strategy content.

### F3 (product lens) — Auth as a Trust Feature
- **Difficulty:** Any
- **Type:** Product/ops explainer
- **Hook:** "Magic-link login and SSO-ready identity aren't features — they're prerequisites that sell."
- **Description:** Why standing up proper identity (Keycloak, magic links,
  temp-access sessions) early de-risks B2B sales and multi-user rollout.
- **Grounding:** `docs/app/keycloak/phase-7-magic-link-fix/PAIML-KEYCLOAK-015.md`.
- **Sellable angle:** Bridges security engineering and sales readiness.