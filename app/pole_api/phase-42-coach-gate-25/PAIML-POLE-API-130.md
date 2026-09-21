# Ticket: PAIML-POLE-API-130

## Title
assertRendering broken-image false positive (Class A, gate assert defect): probe lazy images only after viewport/decode (VA-04, TP-03, TP-05, IN-02)

## Status
📋 PLANNED — follow-up gate-fix ticket for phase-42 coach-gate-25, SAMPLE-5 gate
run `sample5-647d57e-20260921-205203` (**15/25, RED**).

- **Status**: 📋 PLANNED
- **Project**: pole_api (frontend lane / e2e harness)
- **Phase**: 42 coach-gate-25
- **Blocks**: —
- **Blocked By**: — independent of 129/131/132 (none of the four gate-fix
  tickets block each other).

## Context

SAMPLE-5 gate run `app/pole_analyst/test-results/coach-150q/sample5-647d57e-20260921-205203/`
(`coach-150q-judge.md` + `coach-150q-transcript.jsonl`): **COACH7-VA-04,
TP-03, TP-05, IN-02 fail** with `expect(imagesBroken).toEqual([])` in
`assertRendering` — the judge rows show an `image` block rendered in each
failing reply.

### Evidence / root cause
The image is an `<img loading="lazy">` probed via
`img.complete && naturalWidth > 0` **BEFORE** the lazy fetch/decode —
below the fold the spec never scrolls the image into the viewport, the
browser does not start the lazy load, `onerror` never fires, and the assert
reports a "broken" image that was never fetched. Replaying the exact failing
URLs returns **HTTP 200 with valid JPEGs** (token valid, 7200 s TTL,
allowed-origins OK) — this is **NOT an auth bug** and the image
token/registry contract is fine.

- Location: `assertRendering` in
  `app/pole_analyst/e2e/coach-150q.spec.ts:412-466` (image probe at
  `:450-461`).

## Scope

Fix the assert side (default expected fix) so images are evaluated **only after
they are actually in the viewport / lazy-loaded**:

- scroll into view before probing (`locator.scrollIntoViewIfNeeded`) and/or
- `await img.evaluate((el) => el.decode())` before probing `naturalWidth`.

Optionally the product may prefer dropping `loading="lazy"` on the bubbled
images — decide by what keeps the UX intent while making the assert
deterministic. The default expected fix is the **assert side**.

**Do NOT** weaken the token/registry contract and **do NOT** chase token
handling (token, TTL, allowlist are all already correct).

## Files Affected
- `app/pole_analyst/e2e/coach-150q.spec.ts` — `assertRendering` image probe
  (`:450-461`).
- (Optional, product decision) the FE component that emits
  `loading="lazy"` on bubbled images.

## Validation Plan
1. Targeted battery:
   ```bash
   npx playwright test coach-150q.spec.ts --workers=1 -g "COACH7-(VA-04|TP-03|TP-05|IN-02)"
   ```
   Must pass.
2. Images still render in the app — manual check via screenshot acceptable.
3. Full SAMPLE-5 gate **25/25** as phase acceptance (with 129/131/132).

## Acceptance Criteria
- [ ] VA-04, TP-03, TP-05, IN-02 pass in the SAMPLE-5 gate.
- [ ] Images that download HTTP 200 / valid JPEG never fail the assert.
- [ ] A genuinely broken image (404/410, invalid bytes) still fails the assert
      (assert stays deterministic, not disabled).
- [ ] Image token/registry contract unchanged (endpoint, token TTL,
      allowed-origins untouched).

## Dependencies
- **Blocked By**: —.
- **Blocks**: — (independent of 129/131/132).

## Estimated Effort
- [S]