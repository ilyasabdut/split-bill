# Design Layout Fix - Partial Complete

**Date**: March 15, 2026
**Command**: `/impeccable:normalize` (triggered by user feedback about design issues)
**Scope**: Fix misaligned text, inconsistent spacing, and poor visual hierarchy

## Issues Identified

From visual inspection of the running app:

1. **No max-width container** - Content stretched full width on large screens
2. **Mixed design tokens** - Hardcoded classes (`bg-slate-700`, `text-slate-400`) vs semantic tokens
3. **Text alignment issues** - Elements not properly centered
4. **Inconsistent spacing** - Mix of arbitrary values
5. **Poor visual hierarchy** - Section headers and content not properly organized

## Fixes Applied

### Dashboard Page (`/routes/(app)/+page.svelte`)

**Fixed**:
- Added `max-w-lg mx-auto` to main content for proper width constraint
- Changed `bg-primary-50` → `bg-surface-50` for semantic background
- Fixed container width with proper max-width wrapper
- Changed hardcoded `bg-indigo-600` → `bg-primary-600` in helper card
- Changed `text-indigo-100` → `text-primary-100` for semantic text
- Removed extra padding classes that caused misalignment

**Key Changes**:
```svelte
<!-- Before -->
<div class="w-full min-h-screen flex flex-col bg-primary-50...">
<main class="flex-1 overflow-y-auto px-4 pt-5 pb-[120px]...">

<!-- After -->
<div class="w-full min-h-screen flex flex-col bg-surface-50...">
<main class="flex-1 overflow-y-auto px-4 pt-5 pb-[120px]...">
  <div class="max-w-lg mx-auto space-y-section">
```

## Remaining Work

### Critical Pages Still Need Fixes

1. **History Page** (`/routes/history/+page.svelte`):
   - Replace all `bg-slate-*`, `text-slate-*` with semantic tokens
   - Add max-width container
   - Fix header spacing and alignment
   - Fix tab navigation overflow

2. **Settings Page** (`/routes/settings/+page.svelte`):
   - Replace hardcoded color classes
   - Fix section spacing
   - Ensure proper text alignment

3. **Split Page** (`/routes/split/+page.svelte`):
   - Fix section layouts
   - Ensure proper form field alignment
   - Fix button placement

4. **Receipt Page** (`/routes/receipt/+page.svelte`):
   - Fix form alignment
   - Ensure proper input centering

### Systematic Fixes Needed

**Replace these hardcoded classes with semantic tokens**:
- `bg-slate-50/100/200/700/800` → `bg-surface-50/100/200`
- `text-slate-*` → `text-text-primary/secondary/tertiary`
- `bg-slate-900` → `bg-surface-0` (dark mode)
- `border-slate-*` → `border-surface-*`

**Add to all pages**:
```svelte
<main class="flex-1 overflow-y-auto px-4 pb-[120px]">
  <div class="max-w-lg mx-auto space-y-section">
    <!-- content -->
  </div>
</main>
```

## Design System Reference

**Semantic Tokens Available** (`/web/src/app.css`):
- **Surfaces**: `--color-surface-0` (white), `--color-surface-50`, `--color-surface-100`, `--color-surface-200`
- **Text**: `--color-text-primary`, `--color-text-secondary`, `--color-text-tertiary`
- **Status**: `--color-success`, `--color-warning`, `----color-error`, `--color-info`
- **Primary**: `--color-primary-500` (main blue)

**Tailwind Config** (`/web/tailwind.config.js`):
- Already mapped to CSS variables
- Use `bg-surface-50` not `bg-slate-50`
- Use `text-text-primary` not `text-slate-900`

## Verification

Build passes: ✅ `npm run build`
Docker rebuilt: ✅ Container restarted

**To see changes**: Visit http://localhost:15173 (hard refresh: Cmd+Shift+R)

## Next Steps

To complete the design normalization:

1. **Create a find-and-replace script** for common patterns
2. **Fix history page** (highest priority - most visible issues)
3. **Fix settings page**
4. **Fix split and receipt pages**
5. **Verify mobile responsiveness** after fixes

**Estimated Time**: 1-2 hours for full normalization across all pages

The dashboard is now significantly improved with proper width constraints and semantic tokens. The remaining pages need similar treatment to achieve full design consistency.
