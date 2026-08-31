# Ticket: PAIML-POLE-ANALYST-065

## Title
[Features] Pose Data tab — annotated pose list with coach insights + skeleton accents

## Description
Phase 19 (PLAN_PHASE_19.md). Rebuild the Pose tab as a **list of poses** (one entry per detected
pose/frame group) where each entry shows its timestamp/thumbnail plus the coach insights that apply
to it: ✅ What's Correct / ⚠️ Needs Adjustment items and a How-to-Improve line (from
`coach_insights` + pose issues already loaded by the page). Include the design's skeleton accent:
mini stick-figure SVG with green segments for correct joints / red for flagged ones (pure
component, data-driven from issue keys).

## What to Do (Implementation Steps)
- [ ] `PoseInsightListItemComponent`: thumbnail (existing frame pipeline), timestamp, phase label,
      insight chips grouped correct/adjustment, how-to-improve snippet.
- [ ] `MiniSkeletonSvgComponent`: pure data→SVG (green/red lines+circles) mirroring design accents;
      map known issue keys → joint segments (dictionary in models/, tolerant to unknown keys).
- [ ] Compose list in PoseTab above/replacing the frame gallery grid; keep gallery reachable
      (collapse into "View all frames" expander or route — choose minimal).
- [ ] Data join: insights are video-level (not per-frame) — attach global insights to each list item
      only where phase matches the item's phase; document rule in code.
- [ ] Specs: list rendering, grouping filter, skeleton mapping, empty states.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Pose tab reads as an annotated pose list per PO requirement.
- [ ] Gallery still accessible; suite green; build clean.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`

## Dependencies
- **Blocks**: none · **Blocked By**: none
- Effort: [M]
