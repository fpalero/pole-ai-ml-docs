# PAIML-POLE-ANALYST-057 — Playwright E2E Tests for Sidebar Navigation

> **Phase:** 15 — Sidebar Navigation · **State:** 📋 PLANNED

## Objective

Add Playwright end-to-end tests verifying sidebar navigation works correctly in the browser.

## Scope

### Files to create/modify

- `app/pole_analyst/e2e/workflow-sidebar-navigation.spec.ts` — new spec

### Test scenarios

**UC-Sidebar-1: Sidebar renders on all pages**
- Navigate to `/chat`
- Verify sidebar is visible with brand block, upload button, 4 nav items
- Navigate to `/videos` (tools outlet)
- Verify sidebar is still visible

**UC-Sidebar-2: Dashboard navigation**
- Start at `/videos` (tools outlet)
- Click "Dashboard" in sidebar
- Verify URL is `/chat`
- Verify Dashboard item has active state (filled icon, highlight bg)

**UC-Sidebar-3: Library navigation**
- Start at `/chat`
- Click "Library" in sidebar
- Verify tools outlet shows video library
- Verify Library item has active state

**UC-Sidebar-4: Analysis navigation**
- Click "Analysis" in sidebar
- Verify tools outlet shows analysis history
- Verify Analysis item has active state

**UC-Sidebar-5: Upload button**
- Click "Upload Video" button in sidebar
- Verify navigation to library (tools outlet)

**UC-Sidebar-6: Settings is disabled**
- Verify Settings item exists
- Verify Settings item is not clickable / has disabled state

**UC-Sidebar-7: Active state persists across reload**
- Click "Library" in sidebar
- Reload page
- Verify Library item still has active state

**UC-Sidebar-8: Sidebar accessibility**
- Verify sidebar has `nav` element with `aria-label="Main navigation"`
- Verify active item has `aria-current="page"`
- Verify keyboard navigation (Tab through items)

## Acceptance Criteria

1. All 8 e2e test scenarios pass
2. Tests run against `_testing` databases with `E2E_FAKES=1`
3. No test isolation issues (each test starts clean)
4. Tests complete within 60s total

## Testing

```bash
pixi run pole-analyst-e2e
```
