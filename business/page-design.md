# Professional Services Page — Design & Stitch Description

> This document is the **single source of truth** for the professional-services
> page. It contains (1) the page architecture, (2) the design system, and
> (3) a **paste-ready Stitch description** at the end. All copy lives in
> `docs/business/content/` (hero, sections, and one file per use-case card).

---

## 1. Page purpose

A single-page professional-services site for **Fernando Palero** targeting
**startups and technical founders**. The value proposition: *"I build AI
products that work end-to-end — proven by a live product, not a slide deck."*

The page has one job: convince a technical founder that the author can ship
real AI software (apps, agents, GenAI/RAG, ML) — and give them a click path to
proof (live demo + code) and a contact CTA.

---

## 2. Page structure

```
┌────────────────────────────────────────────────────────┐
│ HERO / PRESENTATION (full-width)                       │
│   headline · subheadline · 3 CTAs                      │
│   [See it live] [Browse the code] [Let's build yours]  │
└────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────┐
│ SECTION 1 — AI Applications                            │
│   outcome-first description                            │
│   ┌──────┐ ┌──────┐ ┌──────┐      (3-column card grid) │
│   │ card │ │ card │ │ card │                           │
│   └──────┘ └──────┘ └──────┘                           │
│   ... (featured cards, then "show more")               │
└────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────┐
│ SECTION 2 — AI Agents                                  │
│ SECTION 3 — Generative AI & RAG                        │
│ SECTION 4 — Machine Learning                           │
│   (each: description + card grid)                      │
└────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────┐
│ FOOTER CTA — "Let's build this"                        │
└────────────────────────────────────────────────────────┘
```

**Four sections** (hero is not a section):

| # | Section | Content file | Use-case count |
| :-- | :-- | :-- | :-- |
| 1 | AI Applications | `content/sections/ai-applications.md` | 19 |
| 2 | AI Agents | `content/sections/ai-agents.md` | 6 |
| 3 | Generative AI & RAG | `content/sections/generative-ai-rag.md` | 6 |
| 4 | Machine Learning | `content/sections/machine-learning.md` | 17 |

---

## 3. Card model (use cases)

Each use case is a **card** in a 3-column grid. Cards render from the article
files in `content/articles/<section>/<slug>.md`.

A card shows:
- **Title** (short)
- **Tiny description** (one practical line — the "What it delivers" sentence)
- **→ More** (opens the detail: technical "how it's built" + proof links)

Each section shows its **featured** cards first (marked `Featured: ✅`), then an
expandable "show more" with the rest.

---

## 4. Design system

| Token | Value |
| :-- | :-- |
| **Tone** | Confident, engineering-first, zero hype. Proof over claims. |
| **Audience** | Startups & technical founders (technical but business-outcome aware) |
| **Colors** | Dark mode, single accent (electric blue or violet), monochrome body |
| **Typography** | Bold display headline; clean sans body (Inter / Space Grotesk) |
| **Shape** | Rounded cards (12px), subtle borders, hover lift |
| **Motion** | Minimal; subtle hover transitions on cards and CTAs |

**Every card and section leads with the business outcome, then proves with
technology.** No "fine-tuning" claim is made anywhere (the project demonstrates
RAG, embeddings, vector search, tool-calling, ReAct/LangGraph agents, and
deterministic guardrails — not LLM fine-tuning).

---

## 5. Links

- **Live demo (pole app):** `https://pole-coach.duckdns.org` (AI Coach) and
  `https://pole-ml.duckdns.org` (training workflow).
- **Code:** `https://github.com/fpalero/pole-ai-ml` (apps/packages) and
  `https://github.com/fpalero/pole-ai-ml-infra` (infra).

> ⚠️ **Before publishing:** verify the per-article GitHub file paths in the
> article files resolve (paths are repo-root-relative; branch `develop`), and
> confirm the DuckDNS hosts are reachable.

---

## 6. Paste-ready Stitch description

```
Design a single-page professional services site for an AI engineer targeting
startups and technical founders. Dark mode, one bold accent color (electric
blue), clean sans typography, rounded 12px cards with subtle borders and a
hover lift.

LAYOUT (top to bottom):

1. HERO (full-width): bold headline "I build AI products that work — end to
   end", subheadline below it, then three buttons side by side: "See it live",
   "Browse the code", "Let's build yours".

2. Four content sections stacked vertically. Each section has: a large section
   title, a 2-3 sentence outcome-first description paragraph, then a 3-column
   grid of use-case cards (3 cards per row, wrapping). Each card has a short
   title, a one-line description, and a "More →" link.

3. FOOTER: a centered call-to-action "Let's build this" with a contact line.

SECTIONS AND CARDS:
- "AI Applications" (19 cards)
- "AI Agents" (6 cards)
- "Generative AI & RAG" (6 cards)
- "Machine Learning" (17 cards)

Each section shows its first few cards prominently and collapses the rest
behind a "show more" toggle.

Use the section and card copy from the provided content files. Keep the tone
confident and engineering-first — proof over hype. No stock-photo filler; lead
with the outcome each service delivers, then the technology.
```
