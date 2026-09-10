# Theme 05 — Real-Time & Full-Stack · Audience: ML / CV Engineers

> ML engineers shipping real-time products: sub-100 ms inference serving,
> live consensus over streaming windows, and LLM-generated coaching derived
> from quantitative metrics.

## Catalog

### E1 — Real-Time Recognition: WebSockets, Circular Buffers & Vote Consensus
- **Difficulty:** Advanced
- **Type:** Systems deep-dive
- **Hook:** "The model is fast; the pipeline is what breaks your 100 ms budget."
- **Description:** End-to-end real-time recognition: a 30-frame circular buffer
  stepped at stride 5, vote-based consensus (3/5), cosine-threshold checks, and
  pushing results over WebSocket. Focus on latency: where frames, inference, and
  I/O interleave, and how to stay under the 100 ms round-trip goal.
- **Grounding:** `docs/diagrams/pola_agent/FLOW.md`, `docs/packages/pole_ml/TODO.md` (Phase 5 real-time recognition).
- **Sellable angle:** Rare concrete real-time ML; high differentiation.

### E3 — Coaching Feedback from Metrics: Z-Score Outliers + LLM
- **Difficulty:** Intermediate
- **Type:** Case study
- **Hook:** "The LLM writes the coaching tip; the statistics find the flaw."
- **Description:** `CoachService`: compare a frame's metric against cohort
  average, compute z-score, flag outliers as likely technical flaws, then drive
  an LLM to produce contextual feedback (with the "critical frame + deviation
  plot" attachments). Also covers the 4-week improvement-plan generation and
  pose-correction heuristics (straight legs, level hips, pointed toes).
- **Grounding:** `docs/app/pola_agent/pose_correction.md`, `docs/app/pola_agent/agent_requirements.md`, `docs/app/pole_api/phase-26-analyst-coach-tools/PAIML-POLE-API-076.md`.
- **Sellable angle:** "AI sports-coach" case study (Dartfish/Hudl analogy) — a
  story with a product.