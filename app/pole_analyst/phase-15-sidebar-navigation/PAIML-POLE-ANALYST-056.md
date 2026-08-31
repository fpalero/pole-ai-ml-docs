# PAIML-POLE-ANALYST-056 — Unit Tests for Sidebar + Updated App Shell

> **Phase:** 15 — Sidebar Navigation · **State:** 📋 PLANNED

## Objective

Add unit tests for the new `SidebarComponent` and update existing `AppComponent` tests to
cover the new layout with sidebar.

## Scope

### Files to create/modify

- `app/pole_analyst/src/app/shared/components/sidebar/sidebar.component.spec.ts` — new
- `app/pole_analyst/src/app/app.spec.ts` — update for new layout
- `app/pole_analyst/src/app/features/videos/pages/library/videos-library.page.ts` — verify TabBar removed

### SidebarComponent tests

1. **Renders brand block** — "Pole AI Coach" title and tagline visible
2. **Renders upload button** — "Upload Video" button present and clickable
3. **Renders 4 nav items** — Dashboard, Library, Analysis, Settings visible
4. **Settings is disabled** — Settings item has `disabled` attribute or `opacity-50`
5. **Dashboard link navigates to /chat** — click triggers router navigation
6. **Library link navigates to tools:videos** — click triggers router navigation
7. **Analysis link navigates to tools:history** — click triggers router navigation
8. **Active state for Dashboard** — when URL is `/chat`, Dashboard has active class
9. **Active state for Library** — when URL contains `videos`, Library has active class
10. **Active state for Analysis** — when URL contains `history`, Analysis has active class
11. **Upload button emits event** — `uploadClick` event emitted on click
12. **Keyboard navigation** — Tab moves focus through items, Enter activates

### AppComponent tests

1. **Renders sidebar** — `app-sidebar` element present
2. **Renders slim top bar** — top bar without brand block
3. **Renders two panes** — chat and tools panes present
4. **Content area offset** — main content has left margin equal to sidebar width

## Acceptance Criteria

1. All new sidebar tests pass
2. Updated app shell tests pass
3. Overall test coverage maintained (≥ 80%)
4. No flaky tests

## Testing

```bash
cd app/pole_analyst
npx ng test --watch=false       # unit tests
```
