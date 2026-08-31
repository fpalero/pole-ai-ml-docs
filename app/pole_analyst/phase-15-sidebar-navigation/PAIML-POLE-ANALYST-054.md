# PAIML-POLE-ANALYST-054 — Refactor AppComponent Layout (Sidebar + Slim Top Bar)

> **Phase:** 15 — Sidebar Navigation · **State:** 📋 PLANNED

## Objective

Update `AppComponent` to include the sidebar and slim top bar, replacing the current
top-bar-only layout. The brand moves from the top bar to the sidebar header.

## Scope

### Files to modify

- `app/pole_analyst/src/app/app.ts` — update template and styles

### New layout

```
┌──────────┬────────────────────────────────────┐
│          │ Top Bar (56px, slim)                │
│ Sidebar  ├────────────────┬───────────────────┤
│ (256px)  │ Chat (40%)     │ Tools (60%)       │
│          │                │                   │
│          │                │                   │
└──────────┴────────────────┴───────────────────┘
```

### Template changes

```html
<div class="app-shell">
  <a class="skip-link" href="#main-content">Skip to content</a>

  <!-- Sidebar (fixed left, 256px) -->
  <app-sidebar (uploadClick)="onUploadClick()" />

  <!-- Content area (right of sidebar) -->
  <div class="content-area">
    <!-- Slim top bar -->
    <header class="top-bar">
      <div class="top-bar-actions">
        <button type="button" class="icon-btn" aria-label="Settings">
          <span class="material-symbols-outlined" aria-hidden="true">settings</span>
        </button>
        <div class="avatar" aria-label="User avatar">PA</div>
      </div>
    </header>

    <!-- Two-pane split -->
    <main id="main-content" class="panes" tabindex="-1">
      <section class="pane pane-chat" aria-label="Chat with the Coach">
        <router-outlet />
      </section>
      <div class="pane-divider" role="separator" aria-orientation="vertical"></div>
      <section class="pane pane-tools" aria-label="Tools">
        <router-outlet name="tools" />
      </section>
    </main>
  </div>
</div>
```

### Style changes

- `.app-shell`: `display: flex; height: 100vh;` (horizontal flex for sidebar + content)
- `.content-area`: `flex: 1; display: flex; flex-direction: column; margin-left: var(--sidebar-width);`
- `.top-bar`: remove brand block, keep actions (settings + avatar), slim height
- `.panes`: `flex: 1;` fills remaining space below top bar
- Remove `.brand-glyph`, `.brand-text`, `.brand-title`, `.brand-subtitle` from top bar

### Upload handler

```typescript
onUploadClick(): void {
  // Trigger upload flow — navigate to library or open upload dialog
  this.router.navigate([{ outlets: { tools: ['videos'] } }]);
}
```

## Acceptance Criteria

1. Sidebar renders at 256px fixed-left
2. Top bar is slim (56px) and spans remaining width
3. Brand block removed from top bar (lives in sidebar)
4. Two-pane layout (chat + tools) preserved below top bar
5. Upload button in sidebar triggers navigation to library
6. All existing functionality preserved
7. Unit tests pass
8. No visual regressions in pane layout

## Testing

```bash
cd app/pole_analyst
npx ng build                    # typecheck
npx ng test --watch=false       # unit tests
```
