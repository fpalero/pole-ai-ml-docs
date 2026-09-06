# A1 — Chatbot Pay-Per-Query (API)

> Type: `api/` · metered API, usage-based · Priority ⭐⭐⭐

## Description

**The idea in plain English.**
Companies don't need to build AI to offer pole-video analysis in their own
products. They plug into our assistant, send a video or a question, and get a
conversational analysis back ("that's a shoulder mount — here's what to fix").
They pay **per question answered**, so they only pay for what they use.

**How it makes money.**
Usage-based billing (per query), starting small and scaling with volume:

- Simple text query: €0.001–0.003
- Query + video analysis: €0.01–0.05
- Full chat session (10 messages): €0.02–0.10

No minimums on the starter plan; volume customers get cheaper rates.

**Target public.**
Other fitness/sports apps, media platforms, and training companies that want
"video analysis" as a feature in their product without hiring an AI team —
your idea, sold to developers instead of end users.

## What it is

Expose the **already-built `pole_chatbot` agent** (ReAct + LangGraph variants,
guardrails, session management) as a public API. Third parties send a video /
query and get back the conversational analysis. You bill **per query**.

## How it makes money

Metered usage billing — customers pay for what they consume, no seats, no
commitments. This is your lowest-barrier option: the full chatbot backend
already exists behind `pole_api`.

## Subscription or per-service?

**Per-service (metered per query), with prepaid credits or postpaid metering.**

| Meter | Priced unit | Suggested price |
| :--- | :--- | :--- |
| Simple query (text) | 1 query | €0.001–0.003 |
| Query + video analysis | 1 query | €0.01–0.05 |
| Chat session (10 turns) | 1 session | €0.02–0.10 |

Postpaid: meter monthly, invoice via Stripe Billing usage records.
Prepaid: credit packs with expiry (see P1).

## Implementation

**Surface:** API-only — add an API-key + metering layer around the existing
`pole_chatbot`/`pole_api` slices. **No new app, no new ML.**

**Already built (reuse):**
- `pole_chatbot` — ReAct + LangGraph agents, `GuardrailEngine` (deterministic safety),
  session schema, tool registry (crop/shift/histogram/similarity), rate limiting, metrics.
- `pole_api` — FastAPI backend (feature-sliced), async job pattern (202 + job_id),
  WebSocket relays.
- Keycloak — API clients, temp access, scoped tokens.
- Jobs infra (Mongo authority + Redis signal) for heavy queries.
- OmniRoute / OpenAI-compatible router to control LLM token cost per query.

**Must add (gaps):**
- API-key provisioning + scopes (Keycloak client credentials or service tokens).
- Metering service: count queries/tokens per key → usage DB.
- Stripe Billing (usage records) or Stripe Invoices for prepaid packs.
- Quota enforcement (per-key limits on top of existing rate limiter).
- Usage dashboard for API consumers (read-only portal).

## Effort & priority

**Effort: Low** — this is "put a meter on an endpoint that already exists."
**Priority: ⭐⭐⭐** — fastest revenue, validates B2B demand, and shares its
billing rail with A2 and P1.

*See also: `docs/packages/chatbot/PLAN.md`, `packages/chatbot/src/pole_chatbot/guardrails.py`,
`docs/app/pole_api/slices.md`.*