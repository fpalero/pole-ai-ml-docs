# Ticket: PAIML-POLE-ANALYST-076

## Title
[Media] Append Keycloak `?token=` to every FE `<img>`/`<video>` binding + retry-once-with-fresh-token

## Description
Phase 26 — see [PLAN_PHASE_26](../plan/PLAN_PHASE_26.md). Live user-reported
bug on staging, root-caused by live probe (2026-09-07):

- `GET /api/analyst-artifacts/histogram_frames/<vid>/frame_0.jpg` → **401
  without token**, **200 image/jpeg with `?token=<Keycloak access token>`**.
- Backend contract (`get_media_claims`, `app/pole_api/src/core/auth.py:290-303`)
  explicitly supports `?token=` for `<img>`/`<video>` (browsers can't set
  `Authorization` there).
- The FE renders raw media URLs without the token, so authenticated artifact
  images load as broken (401) in the browser.

Zero backend change — the endpoint already supports it. FE-only fix.

## Media-binding audit (app-wide, `app/pole_analyst/src`, specs excluded)

Must-fix (raw URL rendered, no token helper):

1. `features/chat/components/chat-pane/chat-pane.component.ts:141` —
   `video_segment` thumbnail: `<img class="segment-thumb" [src]="block.thumbnail_url">`.
2. `features/chat/components/chat-pane/chat-pane.component.ts:166` — chat
   `image` block: `[src]="block.src"`.
3. `features/analysis/components/pose-gallery/pose-gallery.component.ts:53` —
   gallery thumbnail: `[src]="frame.frame_image_path"`.
4. `features/analysis/components/pose-gallery/pose-gallery.component.ts:72` —
   detail annotated image: `[src]="sel.frame.frame_image_path"`.
5. `features/analysis/components/pose-insight-list-item/pose-insight-list-item.component.ts:28` —
   pose list thumbnail: `[src]="src"` (de `item().frame.frame_image_path`).
6. `shared/components/annotated-frame/annotated-frame.component.ts:33` —
   frame image: `[src]="src() ?? ''"` (verify source; wrap if backend-served).

Already OK (via token helper — regression-guard only):

7. `features/videos/components/video-card/video-card.component.ts:63` —
   `[src]="thumbnailUrl()"` → `VideosService.thumbnailUrl()` (`appendMediaToken`).
8. `features/analysis/components/video-preview/video-preview.component.ts:58-59` —
   `[src]="streamUrl()"` / `[poster]="thumbnailUrl()"` → `VideosService`.
9. `features/analysis/components/analysis-history-table/analysis-history-table.component.ts:105` —
   `[src]="thumbnailSrc(record)"` → `videosService.thumbnailUrl()`.
10. `core/services/api-client.service.ts:79` — `ApiClientService.streamUrl()`
    appends `?token=` (shared primitive).

Rerun audit grep before closing (must return no un-authed binding):

```bash
grep -rn '\[src\]\|\[poster\]\|<video' app/pole_analyst/src --include="*.ts" | grep -v spec
```

Every hit must resolve to `withMediaToken` (or an existing token helper) or be
a `data:`/blob/local asset (documented inline as exempt).

## What to Do (Implementation Steps)
- [ ] Add central helper `withMediaToken(url)` reading the Keycloak access
      token (no-op for `data:`/blob URLs and already-signed URLs); reuse
      `appendMediaToken` / `ApiClientService.streamUrl()` if they cover it —
      one shared path, no per-component token plumbing.
- [ ] Apply the helper at every must-fix binding (1–6 above) plus any extra
      hit the audit grep finds (analysis detail/overview, RAG images).
- [ ] Retry-once-with-fresh-token on `<img>` `(error)`: refresh the token and
      retry the load exactly once before falling back to the degraded
      placeholder. Required: tokens expire (~5min) while artifact
      `Cache-Control` is 24h — without this, cached pages break on stale
      tokens. Cheap, kills the edge.
- [ ] Add/adjust unit specs: rendered `src`s contain `token=` (chat `image`,
      `video_segment` thumbnail, pose-gallery ×2, insight item, annotated
      frame); retry-once spec (stale token → fresh token → loads; double-fail
      → placeholder, no infinite loop); ≥ 80% coverage for the helper.

## Acceptance Criteria (Definition of Done for this Ticket)
- [ ] Staging probe (same curl pair as evidence): 401 without token, 200
      `image/jpeg` with `?token=`; visual spot check: chat `image` blocks and
      `video_segment` thumbnails load authenticated.
- [ ] Unit tests assert token presence in rendered srcs (all must-fix sites).
- [ ] Retry-once-with-fresh-token on img error implemented + spec'd.
- [ ] No un-authed media binding left (audit grep in ticket, rerun at close).
- [ ] `npx ng test --watch=false` green, `npx ng lint` clean,
      `npx ng build` typecheck passes.
- [ ] Zero backend change.

## Integration Tests to Run (Local Verification)
- [ ] `npx ng test --watch=false`
- [ ] `npx ng lint`
- [ ] `npx ng build`
- [ ] Staging curl pair (evidence) + authenticated visual spot check.

## Dependencies
- **Blocks**: None.
- **Blocked By**: None. Backend already supports `?token=`
  (`get_media_claims`, `app/pole_api/src/core/auth.py:290-303`).

## Estimated Effort
- [S]
