# PAIML-POLE-ANALYST-055 — Wire Sidebar Navigation to Routes + Remove TabBar

> **Phase:** 15 — Sidebar Navigation · **State:** 📋 PLANNED

## Objective

Wire the sidebar navigation items to the correct routes and remove the `TabBar` from
`VideosLibraryPage` since navigation is now handled by the sidebar.

## Scope

### Files to modify

- `app/pole_analyst/src/app/features/videos/pages/library/videos-library.page.ts` — remove TabBar
- `app/pole_analyst/src/app/app.routes.spec.ts` — update tests if needed

### VideosLibraryPage changes

Remove the `TabBar` import and template. The page now directly shows the `VideosLibraryPane`
without tab switching:

```typescript
@Component({
  selector: 'app-videos-library-page',
  standalone: true,
  imports: [VideosLibraryPane],
  template: `
    <div class="videos-library-page">
      <app-videos-library-pane />
    </div>
  `,
  // ...
})
export class VideosLibraryPage {}
```

Remove:
- `TabBar` import
- `tabs` array
- `activeTab` signal
- `onTabChange` method
- `VideosLibraryTabId` type

### Route wiring

The sidebar uses `RouterLink` with `[routerLink]` and `[routerLinkActive]`:

- Dashboard: `[routerLink]="['/chat']"` (primary outlet)
- Library: `[routerLink]="[{ outlets: { tools: ['videos'] } }]"` (tools outlet)
- Analysis: `[routerLink]="[{ outlets: { tools: ['history'] } }]"` (tools outlet)

Active state detection:
- For primary outlet routes: `routerLinkActive="active"` on the link
- For tools outlet routes: check if URL contains the path segment

### Cleanup

- Delete `VideosLibraryTabId` type export (no longer needed)
- Update any imports that referenced the tab types

## Acceptance Criteria

1. `VideosLibraryPage` renders without TabBar
2. Library page shows `VideosLibraryPane` directly
3. Sidebar navigation correctly routes to all 3 pages
4. Active sidebar item highlights correctly for each route
5. No broken imports or unused code
6. All unit tests pass
7. Playwright e2e tests pass

## Testing

```bash
cd app/pole_analyst
npx ng build                    # typecheck
npx ng test --watch=false       # unit tests
```
