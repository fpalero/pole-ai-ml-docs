# Ticket: PAIML-POLE-ANALYST-077

## Title
[Chat] Tool-chip artifact links render literal `[artifact]` placeholder (broken links; images not reachable from tool chip)

## Description
Phase 26 follow-up — see [PLAN_PHASE_26](../plan/PLAN_PHASE_26.md). Sibling of
`PAIML-POLE-ANALYST-076` (main gallery auth) and `PAIML-POLE-ANALYST-075`
(chip sanitize). Live staging capture 2026-09-07T21:44–47 (staging current
`8345065`, 076 deployed):

- When `extract_frames` returns 6 frames, the main chat renders them fine:
  `figure.rag-image-card > img.rag-image` with `?token=`, browser 200s,
  `naturalWidth > 0` — 076 covers that path. Do not alter it.
- BUT the tool-chip duplicates the frames as **unsubstituted placeholder links**:
  `ul.tool-artifact-frames > li.tool-artifact-frame > a.artifact-link` with
  literal `href="[artifact]"` and text `[artifact]` (×6). Resolves to
  `https://pole-coach.duckdns.org/[artifact]` (404/broken if clicked); no fetch
  ever fires.

DOM evidence (local, not committed): `/tmp/opencode/img-broken/dom-evidence.json`;
screenshot `/tmp/opencode/img-broken/attempt1-chat.png`. Key excerpt:

```json
"uncovered_path": {
  "selector": "ul.tool-artifact-frames > li.tool-artifact-frame > a.artifact-link",
  "count": 6,
  "href_literal": "[artifact]",
  "text_literal": "[artifact]",
  "resolved_url": "https://pole-coach.duckdns.org/[artifact]",
  "token_present": false,
  "note": "076 withMediaToken+retry covers figure.rag-image-card img; it does NOT cover tool-chip artifact links."
}
```

Root-cause hypothesis: the tool-chip renderer receives the **sanitized** tool
result where artifact URLs were rewritten to `[artifact]` (chip sanitization),
and never substitutes/tokenizes them back. Audit the chip renderer's data
source and the sanitizer that produces `[artifact]` — likely the 075 chip
sanitize or the agent's tool-result sanitization — and fix at the right layer
so other tool chips (`rag_image`, `segment`, `pose`) also cannot leak
placeholders.

## What to Do (Implementation Steps)
- [ ] Audit the tool-chip render path: find where `ul.tool-artifact-frames >
  li.tool-artifact-frame > a.artifact-link` gets its `href`/text, and where
  the literal `[artifact]` is introduced (075 sanitize helper vs agent
  tool-result sanitization vs chip template default). Fix at the layer that
  covers ALL tool chips, not just `extract_frames`.
- [ ] Fix, choosing the option that best matches the chip's purpose:
  - **Option A (link them):** each `.tool-artifact-frame > .artifact-link`
    shows a real, clickable artifact URL with `?token=` — reuse the 076
    `withMediaToken` helper / `refreshMediaToken` retry. OR
  - **Option B (drop them):** if the chip is purely a redundant summary of the
    main gallery, remove the unsubstituted placeholder entirely — no literal
    `[artifact]` rendered anywhere in the FE.
- [ ] Acceptance bar (either option): **no literal `[artifact]` link survives
  on screen for ANY answered tool** — grep + DOM assertion; audit sibling
  chips (`rag_image`, `segment`, `pose`) for the same leak.
- [ ] Add/adjust unit specs: chip renderer with artifact-bearing tool results
  (real URL + token asserted when Option A; absence asserted when Option B);
  empty/absent-result case → no broken link; regression on 075 sanitize specs.
  ≥ 80% coverage on touched code.

Out of scope: the `.rag-image-card` main gallery (already working per 076) —
do not alter it. No backend changes.

Regression grep before closing (must return zero hits in FE source/templates):

```bash
grep -rn '\[artifact\]' app/pole_analyst/src --include="*.ts" --include="*.html"
```

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] A 6-frame `extract_frames` turn renders zero `a.artifact-link` elements
  with literal `href="[artifact]"` / text `[artifact]` — either real
  tokenized URLs (Option A) or no placeholder links at all (Option B).
- [ ] Same guarantee holds for ALL answered tool chips (`rag_image`,
  `segment`, `pose`, `extract_frames`, `crop`): no `[artifact]` placeholder
  leaks from the sanitizer path.
- [ ] Component/unit specs cover the chip renderer (artifact-bearing result +
  empty/absent result) + 075 sanitize regression green.
- [ ] `npx ng test --watch=false` green (FE scoped specs), `npx ng lint`
  clean, `npx ng build` typecheck passes; coverage ≥ 80% touched.
- [ ] Zero changes to the `.rag-image-card` main gallery path; zero backend change.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`
- [ ] `npx ng lint`
- [ ] `npx ng build`
- [ ] Staging DOM spot check: answered `extract_frames` turn shows no
  `a[href="[artifact]"]`; screenshot archived alongside evidence.

## Dependencies
- **Blocks**: None.
- **Blocked By**: None (FE-only). Builds on `PAIML-POLE-ANALYST-076`
  (`withMediaToken` / retry helper — reuse, do not fork) and
  `PAIML-POLE-ANALYST-075` (chip sanitize — fix at the right layer, keep its
  specs green).
  Related: main gallery path (076, frozen) vs chip path (this ticket).

## Estimated Effort
- [S]

---

## Supplementary note (docs-unified keep-both)

Incoming `feature/PAIML-POLE-ANALYST-077-chip-artifact-links` carried a 75-line
concise variant of this same ticket (same defect, same evidence paths
`/tmp/opencode/img-broken/`, same Stitch image IDs). This 103-line expanded
version is kept canonical (full DOM excerpt + root-cause hypothesis + Option A/B
fix framing); the concise variant is superseded with no content loss.
