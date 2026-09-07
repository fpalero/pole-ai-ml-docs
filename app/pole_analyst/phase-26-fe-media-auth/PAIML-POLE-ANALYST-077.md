# Ticket: PAIML-POLE-ANALYST-077

## Title
[Chat] Tool-chip artifact links render broken `[artifact]` placeholders instead of tokenized URLs

## Description
Phase 26 — see [PLAN_PHASE_26](../plan/PLAN_PHASE_26.md). Live staging defect,
root-caused by live probe (2026-09-07 21:44–21:48 UTC, evidence local, not
committed): `/tmp/opencode/img-broken/dom-evidence.json` + `attempt1-chat.png`.

Question `Extract 6 frames from my handspring video so I can review the entry.`
(TOOL-04, video `6a9e65efc910c95e7f430d6a`) returned 6 real images that render
FINE in the chat — 076 verified working: `figure.rag-image-card > img.rag-image`,
`src` carries `?token=`, all 200 first try, `naturalWidth` 720.

BUT the same answer renders a SECOND, broken copy of the frames inside the
`extract_frames` tool chip: `ul.tool-artifact-frames > li.tool-artifact-frame >
a.artifact-link` with `href="[artifact]"` literal and text `[artifact]` literal
(×6). Clicking resolves `https://pole-coach.duckdns.org/[artifact]` → 404.
Server logs show zero 401/403 — no fetch ever fires because the placeholder is
unclickable junk.

Staging `pole-fe` image `ghcr.io/fpalero/pole-fe:8345065` includes 076, so this
path is genuinely uncovered by 076 (main path fixed, chip path not).

## What to Do (Implementation Steps)
- [ ] Root-cause + fix in the FE chat tool-chip renderer: the `extract_frames`
      (and any sibling tool emitting artifact frames) chip must render REAL
      artifact URLs tokenized via the existing 076 `withMediaToken` helper
      (plus the retry-once fresh-token error handler), reusing the same
      transport the `.rag-image-card` path uses. If tokenized hrefs are not
      feasible inside chips, the fallback is to stop rendering the broken
      `[artifact]` links entirely (plain filename text, no href) — never raw
      placeholders.
- [ ] Backend sanitize/hygiene layer (075/096 `sanitize_tool_calls` etc.): if
      the `[artifact]` literal originates server-side (URL redaction for
      chips), the chip renderer must resolve it back to the real URL from the
      tool result — no redaction may reach the DOM as a clickable-looking link.
- [ ] Add FE unit tests for the tool-chip artifact rendering: (a) real
      tokenized href after `withMediaToken`, (b) retry-once-then-placeholder
      on 401, (c) no `[artifact]` literal anywhere in rendered chips. Follow
      the 074/075 spec conventions.
- [ ] Scope discipline: chip renderer + its spec (and the server-side
      substitution point if the literal originates there) only; no changes to
      the working `.rag-image-card` path, no shaping/retry/blank logic.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] An `extract_frames` turn renders its tool chip with real tokenized
      artifact hrefs (asserted by specs) — or with plain non-link text if
      tokenized hrefs are infeasible; zero `[artifact]` literals in the DOM.
- [ ] No `[artifact]` string anywhere in rendered chips (`href` or text),
      asserted by a dedicated spec.
- [ ] Retry-once-with-fresh-token on 401 covered for the chip path (or
      documented as inherited from the shared 076 helper path).
- [ ] `npx ng test --watch=false` green, `npx ng lint` clean,
      `npx ng build` typecheck passes.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`
- [ ] `npx ng lint`
- [ ] `npx ng build`
- [ ] Staging spot check: TOOL-04-class (`extract_frames`) turn — chat images
      load AND the tool chip shows real tokenized links (or plain text), no
      `[artifact]`, clicking a chip link does not 404.

## Dependencies
- **Blocks**: None.
- **Blocked By**: None (FE chip renderer + spec; server-side substitution
  point only if the literal originates there).
  Related: `PAIML-POLE-ANALYST-076` (main `.rag-image-card` path — working,
  do not touch), `PAIML-POLE-ANALYST-075` (chip display sanitization),
  `PAIML-POLE-API-096` (backend sanitize/hygiene layer).

## Estimated Effort
- [S]
