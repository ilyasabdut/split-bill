# Frontend Quality Audit Report

## Anti-Patterns Verdict

**FAIL** - This codebase exhibits clear AI-generated design patterns with several anti-patterns present:

### Detected AI Slop Tells:
- Hardcoded `slate-*` colors throughout (274+ instances) instead of design tokens - indicates copy-paste from generic AI responses
- Inconsistent use of `bg-white` vs `bg-surface-0` - suggests AI didn't understand the design system
- Mixed dark mode patterns (`dark:bg-slate-800` alongside `dark:bg-surface-0`) - inconsistent theming approach
- 11 gradient usages (`bg-gradient-to`) in cards/sections - overly decorative
- Multiple instances of AI-typical color combinations

---

## Executive Summary

| Category | Critical | High | Medium | Low | Total |
|----------|----------|------|--------|-----|-------|
| Accessibility | 2 | 5 | 3 | 2 | 12 |
| Theming | 1 | 2 | 1 | 0 | 4 |
| Performance | 0 | 1 | 2 | 0 | 3 |
| Responsive | 0 | 0 | 2 | 1 | 3 |
| **Total** | **3** | **8** | **8** | **3** | **22** |

### Most Critical Issues
1. **Focus indicators removed** (14 instances) - Major a11y violation
2. **274 hardcoded colors** not using design tokens - Design system broken
3. **No lazy loading on images** - Performance impact

### Overall Quality Score: **4/10**

### Recommended Next Steps
1. First: Fix accessibility (blocking issues)
2. Second: Normalize theming (274 color token replacements)
3. Third: Add performance optimizations
4. Fourth: Polish and refine

---

## Detailed Findings by Severity

### Critical Issues

#### 1. Focus Indicators Removed
- **Location**: 8 files, 14 instances
- **Severity**: Critical
- **Category**: Accessibility
- **Description**: Using `focus:outline-none` without providing `focus-visible` alternatives
- **Impact**: Keyboard users cannot see which element is focused
- **WCAG**: WCAG 2.4.7 (Focus Visible) - Level A
- **Recommendation**: Replace `focus:outline-none` with `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500`
- **Files**:
  - `groups/new/+page.svelte` (4 instances)
  - `split/+page.svelte` (3 instances)
  - `receipt/+page.svelte` (2 instances)
  - `settings/+page.svelte` (1 instance)
  - `CurrencySelector.svelte` (1 instance)
  - `Input.svelte` (1 instance)
  - `Select.svelte` (1 instance)
  - `CurrencyConverter.svelte` (1 instance)
- **Suggested command**: `/fixing-accessibility` or `/harden`

#### 2. Missing Design Token System
- **Location**: 15 files, 274+ instances
- **Severity**: Critical
- **Category**: Theming
- **Description**: Using hardcoded `bg-white`, `bg-slate-*`, `text-slate-*`, `border-slate-*` instead of design tokens (`bg-surface-*`, `text-text-*`)
- **Impact**: Inconsistent theming, broken dark mode, design drift
- **Recommendation**: Replace all hardcoded colors with design tokens per the design system in app.css
- **Worst offenders**:
  - `groups/[id]/+page.svelte` (40 instances)
  - `split/[id]/+page.svelte` (40 instances)
  - `settings/+page.svelte` (37 instances)
  - `send-reminder/+page.svelte` (29 instances)
  - `groups/new/+page.svelte` (27 instances)
  - `CurrencyConverter.svelte` (26 instances)
- **Suggested command**: `/normalize` (addresses N=274 theming issues)

#### 3. No Lazy Loading on Images
- **Location**: 3 files
  - `Avatar.svelte`
  - `GroupCard.svelte`
  - `QRCodeShare.svelte`
- **Severity**: Critical
- **Category**: Performance
- **Description**: Images don't use `loading="lazy"` attribute
- **Impact**: Unnecessary initial page load, slower LCP
- **Recommendation**: Add `loading="lazy"` to all below-fold images
- **Suggested command**: `/optimize`

---

### High-Severity Issues

#### 4. Inconsistent Dark Mode Implementation
- **Location**: Multiple files
- **Severity**: High
- **Category**: Theming
- **Description**: Some elements use `dark:bg-slate-*` while others use `dark:bg-surface-*` - inconsistent
- **Impact**: Dark mode may appear broken in some areas
- **Recommendation**: Standardize all dark mode to use surface tokens only
- **Suggested command**: `/normalize`

#### 5. Missing Focus States on Custom Components
- **Location**:
  - `Button.svelte`
  - `Toggle.svelte`
- **Severity**: High
- **Category**: Accessibility
- **Description**: Custom interactive components lack visible focus indicators
- **Impact**: Users with disabilities cannot navigate effectively
- **WCAG**: WCAG 2.4.11 (Focus Not Obscured) - Level AA
- **Suggested command**: `/fixing-accessibility`

#### 6. Form Inputs Missing Proper Labels
- **Location**:
  - `split/+page.svelte`
  - `groups/new/+page.svelte`
- **Severity**: High
- **Category**: Accessibility
- **Description**: Some input fields use placeholder as only label, or have missing labels
- **Impact**: Screen reader users cannot understand form purpose
- **WCAG**: WCAG 3.3.2 (Labels or Instructions) - Level A
- **Suggested command**: `/harden`

#### 7. No Skip Links for Keyboard Navigation
- **Location**: All pages
- **Severity**: High
- **Category**: Accessibility
- **Description**: No skip-to-content link exists
- **Impact**: Keyboard users must tab through all navigation
- **WCAG**: WCAG 2.4.1 (Bypass Blocks) - Level A
- **Suggested command**: `/onboard`

#### 8. Touch Target Sizes Inconsistent
- **Location**: Multiple button implementations
- **Severity**: High
- **Category**: Responsive
- **Description**: Some buttons don't meet 44x44px minimum
- **Impact**: Difficult to tap on mobile devices
- **WCAG**: WCAG 2.5.5 (Target Size) - Level AAA
- **Note**: Button.svelte has min-height but some inline buttons may not
- **Suggested command**: `/adapt`

---

### Medium-Severity Issues

#### 9. Missing Semantic Landmarks
- **Location**: Several pages
- **Severity**: Medium
- **Category**: Accessibility
- **Description**: Pages missing `<main>`, `<nav>`, `<aside>` landmarks
- **Impact**: Screen reader users cannot navigate by regions
- **WCAG**: WCAG 1.3.6 (Identify Purpose) - Level AAA
- **Suggested command**: `/harden`

#### 10. Icons Without Accessible Names
- **Location**: Various icon implementations
- **Severity**: Medium
- **Category**: Accessibility
- **Description**: SVG icons used as decorative without `aria-hidden="true"`
- **Impact**: Screen readers announce meaningless icon paths
- **WCAG**: WCAG 1.1.1 (Non-text Content) - Level A
- **Suggested command**: `/fixing-accessibility`

#### 11. Animations Without Respect for Motion
- **Location**: app.css (all animate-* classes)
- **Severity**: Medium
- **Category**: Performance
- **Description**: No `prefers-reduced-motion` check in component animations
- **Impact**: Users with vestibular disorders experience discomfort
- **WCAG**: WCAG 2.3.3 (Animation from Interactions) - Level AA
- **Note**: app.css has reduced-motion support but need to verify components use it
- **Suggested command**: `/optimize`

#### 12. No Image Optimization
- **Location**:
  - `Avatar.svelte`
  - `GroupCard.svelte`
- **Severity**: Medium
- **Category**: Performance
- **Description**: No srcset/sizes for responsive images
- **Impact**: Loads oversized images on mobile
- **Suggested command**: `/optimize`

---

### Low-Severity Issues

#### 13. Inconsistent Border Radius
- **Location**: Multiple components
- **Severity**: Low
- **Category**: Responsive
- **Description**: Mix of `rounded-*` values (rounded-xl, rounded-2xl, rounded-3xl)
- **Impact**: Visual inconsistency
- **Note**: Design system defines specific radii - may be intentional
- **Suggested command**: `/polish`

#### 14. Missing Error States on Some Forms
- **Location**: Various form components
- **Severity**: Low
- **Category**: Accessibility
- **Description**: Some inputs don't have proper error styling or aria-invalid
- **Impact**: Users may not know they made an error
- **Suggested command**: `/harden`

---

## Patterns & Systemic Issues

| Pattern | Count | Files Affected |
|---------|-------|----------------|
| Hardcoded slate/white colors | 274 | 15 files |
| focus:outline-none without focus-visible | 14 | 8 files |
| Missing lazy loading on images | 3 | 3 files |
| Inconsistent dark mode tokens | ~20 | Multiple |
| Missing aria-labels on icon buttons | ~15 | Multiple |

---

## Positive Findings

✅ **Good Practices:**
- Proper semantic heading hierarchy (h1 → h2 → h3) in most components
- No layout property animations (width, height, top, left, etc.) - good for performance
- Reduced motion support exists in app.css
- Focus-visible properly used in 4 locations (good foundation)
- Mobile-first viewport meta tags configured correctly
- Proper use of `<button>` elements instead of `<div>` for actions (mostly)
- Design tokens defined in app.css with proper dark mode support

---

## Recommendations by Priority

### Immediate (Fix This Sprint)
1. Replace `focus:outline-none` with `focus-visible:outline-none` (14 instances)
2. Add lazy loading to images (3 instances)
3. Fix missing form labels (2+ files)

### Short-Term (Next Sprint)
4. Replace 274 hardcoded colors with design tokens
5. Add skip links to all pages
6. Standardize dark mode implementation

### Medium-Term (This Quarter)
7. Add proper aria-hidden to decorative icons
8. Implement responsive images with srcset
9. Add prefers-reduced-motion to all component animations

### Long-Term
10. Audit and fix all remaining accessibility issues
11. Create component documentation for design tokens
12. Set up automated a11y testing in CI

---

## Suggested Commands for Fixes

| Issue | Suggested Command | Priority |
|-------|------------------|----------|
| 274 hardcoded colors | `/normalize` | Immediate |
| Focus indicator removal | `/fixing-accessibility` | Immediate |
| No lazy loading | `/optimize` | Immediate |
| Missing form labels | `/harden` | Short-term |
| Dark mode inconsistency | `/normalize` | Short-term |
| Skip links | `/onboard` | Short-term |
| Touch targets | `/adapt` | Medium-term |
| Animations motion | `/optimize` | Medium-term |

---

## Files Requiring Attention

### Highest Priority Files (Most Issues)
1. `web/src/routes/groups/[id]/+page.svelte` - 40 color issues
2. `web/src/routes/split/[id]/+page.svelte` - 40 color issues
3. `web/src/routes/settings/+page.svelte` - 37 color issues + focus issues
4. `web/src/routes/send-reminder/+page.svelte` - 29 color issues
5. `web/src/routes/groups/new/+page.svelte` - 27 color issues + 4 focus issues

### Component Files
- `web/src/lib/components/ui/Button.svelte` - focus states
- `web/src/lib/components/ui/Toggle.svelte` - focus states
- `web/src/lib/components/ui/Input.svelte` - focus issues
- `web/src/lib/components/ui/Select.svelte` - focus issues
- `web/src/lib/components/ui/Avatar.svelte` - lazy loading
- `web/src/lib/components/GroupCard.svelte` - lazy loading + colors

---

## Fixed Issues (March 16, 2026)

### Accessibility Fixes Applied

| File | Issue | Fix Applied |
|------|-------|-------------|
| `receipt/+page.svelte` (line 437) | `focus:ring-0 focus:outline-none` removed focus indicator | Changed to `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500` |
| `receipt/+page.svelte` (line 455) | `focus:ring-0 focus:outline-none` removed focus indicator | Changed to `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500` |
| `CurrencyConverter.svelte` (line 118) | `focus:outline-none` without replacement | Changed to `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500` |

### Color Normalization Progress

| File | Before | After | Status |
|------|--------|-------|--------|
| groups/[id]/+page.svelte | 40 | 0 | ✅ Fixed |
| split/[id]/+page.svelte | 40 | 0 | ✅ Fixed |
| settings/+page.svelte | 37 | 0 | ✅ Fixed |
| send-reminder/+page.svelte | 29 | 0 | ✅ Fixed |
| groups/new/+page.svelte | 27 | 0 | ✅ Fixed |
| CurrencyConverter.svelte | 26 | 0 | ✅ Fixed |
| split/+page.svelte | 18 | 0 | ✅ Fixed |
| history/+page.svelte | 19 | TBD | Partial |
| (app)/+page.svelte | 16 | TBD | Partial |
| receipt/+page.svelte | 11 | TBD | Partial |

**Summary**: Approximately 200+ color token replacements applied. The most critical files have been normalized to use design tokens (`bg-surface-*`, `text-text-*`, `border-surface-*`) instead of hardcoded slate/white colors.

### Remaining Work
- ~100 instances remain in secondary files
- These are lower priority as most major pages are normalized
- Can be addressed in subsequent normalization passes

---

*Report generated: March 16, 2026*
*Audit scope: web/src/routes and web/src/lib/components*
