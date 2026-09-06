# P2 — Grade / Level Assessment

> Type: `per-service/` · one-off service (B2C) · Priority ⭐⭐

## Description

**The idea in plain English.**
"What level am I?" — an exam you can take at home. The athlete performs the
official syllabus moves for a pole grading system, the app evaluates each one
automatically, and the result is a report saying their assessed level, with
video proof of every move and a clear list of what to train to reach the next
level.

**How it makes money.**
One-off fee per assessment, no subscription:

- Single level assessment: €19–29.
- Full syllabus assessment (every level): €39–59.
- Re-assessment within 3 months: €15–25 (keeps people coming back).

**Target public.**
Students who want to know their level, prepare for official exams, or prove
progress to themselves — plus coaches who use the assessment to place new
students into the right class.

## What it is

A paid **"What level am I?"** certification: the athlete performs the syllabus
moves for a federation grading system (e.g., IPSF/IUPPA), the app detects and
rates each trick, and the result is a report stating the assessed level with
per-move evidence (critical frames), plus a gap list of what to train next.

## How it makes money

One-off fee per assessment (higher than a normal analysis because it is
certification-like and includes a curated step-by-step protocol). Repeat buyers
re-assess after a few months to see progress — a natural re-purchase loop.

## Subscription or per-service?

**Per-service, one-off.** No subscription required.

| Item | Price |
| :--- | :--- |
| Single level assessment | €19–29 |
| Full syllabus assessment (all levels) | €39–59 |
| Progress re-assessment (same athlete, ≤3 mo later) | €15–25 |

## Implementation

**Surface:** `pole_api` assessment slice + `pole_fe` guided capture flow.

**Already built (reuse):**
- Classifier + confidence history + debounce (`pole_tools.video_cutter`) — detect
  each attempted move cleanly.
- Histogram / cohort z-scores + critical-frame extraction — per-move evidence.
- `pole_chatbot` LLM tips — gaps + next steps generation.
- Keycloak identity + temp access (multi-athlete-same-account/studio flow).
- Jobs infra for longer assessment runs.

**Must add (gaps):**
- **Syllabus/curriculum DB**: move → level → required landmarks, imported per
  federation. (The biggest add — domain mapping, not modeling.)
- Assessment orchestration: guided capture (record N moves), scoring rules
  (which levels passed), report assembly.
- Optional badge/PDF certificate output.

## Effort & priority

**Effort: Medium** — new domain logic (syllabus + scoring), but zero new ML.
**Priority: ⭐⭐** — best defensibility of the per-service group (domain-grounded)
and the cleanest story for "pay for a concrete outcome."

*See also: `docs/packages/pole_ml/PLAN.md`, `docs/packages/pole_tools/PLAN.md`,
`docs/app/pole_fe/PLAN.md`.*