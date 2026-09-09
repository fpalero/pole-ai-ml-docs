# Theme 05 — Real-Time & Full-Stack · Audience: Mixed Beginner → Intermediate

> The "wow, it recognizes my move live" story — the motivating product content
> for learners building their first real-time ML app.

## Catalog

### E1 (intro) — Watching a Model Think in Real Time
- **Difficulty:** Intermediate
- **Type:** Project walkthrough
- **Hook:** "Video goes in, a tidy label streams back — here's the plumbing."
- **Description:** A tour of the live-recognition loop: buffer frames, classify
  a sliding window, emit the winner. Serves as the demo capstone for the
  beginner series and the on-ramp to the advanced E1.
- **Grounding:** `docs/packages/pole_ml/TODO.md` (Phase 5), `docs/diagrams/pola_agent/FLOW.md`.
- **Sellable angle:** Capstone-style content maximizes completion of a series.

### E3 (intro) — From Numbers to a Nudge: How "AI Coaching" Actually Works
- **Difficulty:** Beginner
- **Type:** Explainer + demo
- **Hook:** "It's not magic — it's a z-score, an image, and a prompt."
- **Description:** The coaching pipeline in plain terms: metric vs cohort
  average → deviation → critical frame + plot → LLM tip. Reader understands the
  whole product gesture without the math.
- **Grounding:** `docs/app/pola_agent/agent_requirements.md` (LLM-CF-03 prompt).
- **Sellable angle:** Recruits interest in the "AI sports coach" product story.

### E10 — Model Registry UI: The Human Gate for ML Deploys
- **Difficulty:** Intermediate
- **Type:** Frontend product-design guide
- **Hook:** "A model registry is a table with a superpower: one APPROVE & ACTIVATE click."
- **Description:** The runs-as-rows screen: status chips (COMPLETED/RUNNING/
  FAILED/ARCHIVED), a live TRAINING row streaming epoch progress via polling,
  a two-run comparison matrix with accuracy deltas, and a one-click approve →
  activate flow that archives the previous active model. Making the human
  deploy decision feel inevitable, not bureaucratic.
- **Grounding:** `docs/app/pole_fe/fe_UI_design_model_registry.md` (Page 3, flows 13-17).
- **Sellable angle:** ML engineers ignore UI; this proves the product layer is
  where the human-in-the-loop gate actually ships.

### E11 — Training Studio: Launching Long ML Jobs From a Browser
- **Difficulty:** Intermediate
- **Type:** Frontend UX guide
- **Hook:** "Training is a form: pick a mode, pick classes, budget the wait."
- **Description:** A job-launcher UX for ML: visual mode cards (TRAIN FROM
  SCRATCH vs FINE-TUNE), per-class checkboxes with ready/total video counts,
  data-balance warnings ("handspring has 50, shouldermount has 5"), a dataset
  summary sidebar, and confirmation dialogs that set expectations before a
  multi-hour job streams epoch progress live.
- **Grounding:** `docs/app/pole_fe/fe_UI_design_training.md` (Page 2, flows 10-12).
- **Sellable angle:** Designing "long-running job" UX is a rare, concrete gap;
  pairs with E10 for a complete training-console story.