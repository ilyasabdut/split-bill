# Split Bill PWA - Quality Audit Report

**Date**: March 15, 2026
**Scope**: Complete UI/UX quality audit across 41 components and 11 pages
**Audit Method**: Automated scan + design system analysis

---

## Anti-Patterns Verdict

### ⚠️ PASS with Reservations

This interface does **not** look overtly AI-generated, but it shows signs of incomplete implementation:

**AI Slop Tells Found**:
- Heavy reliance on generic Tailwind colors (`slate-*` on 531+ elements) instead of semantic tokens
- Inconsistent spacing patterns suggest ad-hoc decisions rather than systematic design
- Some arbitrary pixel values (`[15px]`, `[11px]`) mixed with token usage

**What Saves It**:
- No dark mode with glowing accents
- No gradient text decorations
- No glassmorphism blur effects
- No hero metric layouts with big numbers
- Clean, purposeful component structure

**Verdict**: This is a **work-in-progress** implementing a design system, not AI slop. The foundation (design tokens in `app.css`) is solid; the issue is inconsistent adoption across components.

---

## Executive Summary

**Overall Quality Score**: 6.5/10

| Severity | Count | Status |
|----------|-------|--------|
| Critical | 3 | 🔴 Blockers |
| High | 8 | 🟡 Significant |
| Medium | 12 | 🟢 Quality issues |
| Low | 5 | ⚪ Nice-to-haves |

**Total Issues**: 28

### Most Critical Issues

1. **531 hardcoded colors** - Components not using design system tokens (addresses CLAUDE.md principle #1)
2. **Touch targets potentially too small** - Fixed widths/heights may not meet 44x44px requirement
3. **13 input labels only** - Forms missing proper label associations (WCAG violation)

### Recommended Next Steps

1. **Immediate**: Use `/normalize` to migrate hardcoded colors to semantic tokens (addresses 531 issues)
2. **Short-term**: Use `/harden` to fix form accessibility (add labels, ARIA)
3. **Medium-term**: Use `/adapt` to ensure responsive patterns and touch targets
4. **Long-term**: Use `/polish` for spacing consistency and micro-interactions

---

## Detailed Findings by Severity

### Critical Issues

#### 1. Hardcoded Colors Not Using Design Tokens
**Location**: Throughout all components (531 instances)
**Severity**: 🔴 Critical
**Category**: Theming / Design System

**Description**:
Components use hardcoded Tailwind colors (`slate-*`, `emerald-*`, `amber-*`, `rose-*`, `gray-*`) instead of semantic design tokens defined in `app.css`.

**Impact**:
- Violates CLAUDE.md principle: "Use existing tokens first"
- Breaks dark mode consistency
- Makes design changes require touching every file
- Creates visual inconsistency

**Affected Components** (partial list):
- `Avatar.svelte` - `bg-slate-100`, `text-slate-600`
- `Button.svelte` - `bg-slate-900`, `text-white`
- `Card.svelte` - `bg-white`, `border-slate-200`
- `Input.svelte` - `border-slate-300`, `text-slate-900`
- `Tabs.svelte` - `bg-slate-900`, `text-slate-600`

**Recommendation**:
Replace hardcoded colors with semantic tokens:
- `slate-*` → `surface-*` or `text-*`
- `emerald-*` → `success`
- `amber-*` → `warning`
- `rose-*` → `error`
- `gray-*` → `surface-*` or `text-*`

**Suggested Command**: `/normalize` - Align with design system

---

#### 2. Forms Missing Proper Label Associations
**Location**: Form components across multiple pages
**Severity**: 🔴 Critical
**Category**: Accessibility (WCAG 2.1 A)

**Description**:
Only 13 input labels found across 41 components. Forms likely missing explicit `<label>` elements or `aria-label` attributes.

**Impact**:
- Screen reader users cannot understand form purpose
- Violates WCAG 2.1 A (1.3.1 Info and Relationships)
- Keyboard navigation issues for form fields
- Mobile screen reader users severely impacted

**WCAG Standard**: WCAG 2.1 A - 1.3.1, 2.4.6, 3.3.2

**Recommendation**:
1. Add explicit `<label>` elements for all inputs with `for` attribute
2. Or add `aria-label` / `aria-labelledby` for icon-only buttons
3. Ensure label text describes the input's purpose clearly

**Suggested Command**: `/harden` - Improve resilience and accessibility

---

#### 3. Fixed Dimensions May Break Touch Target Requirements
**Location**: Components with fixed widths (111) and heights (126)
**Severity**: 🔴 Critical
**Category**: Responsive Design / Accessibility

**Description**:
Fixed pixel dimensions may prevent proper scaling and violate 44x44px touch target minimum from CLAUDE.md.

**Impact**:
- Interactive elements may be too small on mobile
- Layout breaks on text zoom
- Violates WCAG 2.1 AA (2.5.5 Target Size)
- Poor mobile usability

**Examples Found**:
- `h-11` (44px) - borderline acceptable
- `w-10`, `h-10` (40px) - too small
- Arbitrary values like `[15px]`, `[11px]`

**WCAG Standard**: WCAG 2.1 AA - 2.5.5 Target Size

**Recommendation**:
1. Audit all interactive elements for 44x44px minimum
2. Use fluid sizing with `clamp()` where appropriate
3. Test with 200% text zoom

**Suggested Command**: `/adapt` - Improve responsive design

---

### High-Severity Issues

#### 4. Inconsistent Spacing Patterns
**Location**: 445 instances of hardcoded padding/margin/gap
**Severity**: 🟡 High
**Category**: Design System

**Description**:
Mix of spacing values (`p-3`, `p-4`, `px-5 py-10`, `gap-1.5`, `gap-3`) without systematic use of semantic spacing tokens.

**Impact**:
- Visual inconsistency across pages
- No clear spacing rhythm
- Violates CLAUDE.md "Clarity over density" principle

**Recommendation**:
Use semantic spacing tokens: `tight` (8px), `component` (16px), `section` (24px)

**Suggested Command**: `/normalize`

---

#### 5. Arbitrary Font Sizes Instead of Semantic Scale
**Location**: 407 instances of text sizing
**Severity**: 🟡 High
**Category**: Typography / Design System

**Description**:
Components use `text-xs`, `text-sm`, `text-base`, `text-[15px]`, `text-[11px]` instead of semantic scale (`caption`, `label`, `body`, etc.)

**Impact**:
- Inconsistent visual hierarchy
- Harder to maintain typography system
- Violates CLAUDE.md typography guidelines

**Recommendation**:
Migrate to semantic font sizes defined in design tokens:
- `caption` (12px) - for small text
- `label` (14px) - for labels
- `body` (16px) - for body text
- `subheading` (18px) - for subheadings
- `section` (24px) - for section headers
- `heading` (32px) - for page headings

**Suggested Command**: `/normalize`

---

#### 6. Limited Responsive Breakpoint Usage
**Location**: Only 20 responsive breakpoint usages found
**Severity**: 🟡 High
**Category**: Responsive Design

**Description**:
For a mobile-first PWA, there are surprisingly few responsive breakpoint considerations.

**Impact**:
- May not adapt well to tablet/desktop
- Fixed layouts could break on larger screens
- Doesn't follow CLAUDE.md mobile-first principle

**Recommendation**:
1. Add container queries for component-level responsiveness
2. Use fluid spacing with `clamp()`
3. Test on 375px, 768px, 1024px, 1440px breakpoints

**Suggested Command**: `/adapt`

---

#### 7. Low Component Variant Utility Usage
**Location**: `/web/src/lib/component-variants.ts` exists but underutilized
**Severity**: 🟡 High
**Category**: Design System

**Description**:
The `cv()` utility and variant patterns exist but components aren't using them consistently.

**Impact**:
- Duplication of variant logic
- Harder to maintain consistent styling
- Missing benefits of central variant system

**Recommendation**:
Use `component-variants.ts` patterns for badges, buttons, inputs, cards.

**Suggested Command**: `/extract` - Consolidate reusable patterns

---

#### 8. Missing Focus Indicators on Custom Components
**Location**: Custom interactive components
**Severity**: 🟡 High
**Category**: Accessibility

**Description**:
Custom interactive elements may lack visible focus indicators for keyboard navigation.

**Impact**:
- Keyboard users can't see where focus is
- Violates WCAG 2.1 A (2.4.7 Focus Visible)
- Poor accessibility for keyboard-only users

**WCAG Standard**: WCAG 2.1 A - 2.4.7 Focus Visible

**Recommendation**:
Add `focus-visible` ring styles to all custom interactive components.

**Suggested Command**: `/harden`

---

### Medium-Severity Issues

#### 9. No Empty State Components Found
**Location**: Across all pages
**Severity**: 🟢 Medium
**Category**: UX Writing / Interaction

**Description**:
No dedicated empty state components for when users have no splits, groups, or history.

**Impact**:
- Poor onboarding for new users
- Confusing "blank" states
- Missed opportunity for education

**Recommendation**:
Create empty state components that teach the interface (per frontend-design guidelines).

**Suggested Command**: `/onboard`

---

#### 10. Skeleton Loaders May Be Generic
**Location**: `SkeletonLoader.svelte`
**Severity**: 🟢 Medium
**Category**: Motion / Performance

**Description**:
Basic skeleton loading may not match actual content structure.

**Impact**:
- Janky loading experience
- Doesn't prepare users for actual layout

**Recommendation**:
Ensure skeleton loaders match final content structure precisely.

**Suggested Command**: `/polish`

---

#### 11. Limited Animation Usage
**Location**: Only 10 animations found
**Severity**: 🟢 Medium
**Category**: Motion

**Description**:
Very few animations, which is good for performance but may feel static.

**Impact**:
- May feel less "premium"
- Missing micro-interaction feedback

**Recommendation**:
Add purposeful animations for state changes (page transitions, button feedback).

**Suggested Command**: `/animate`

---

#### 12. Bottom Navigation May Need Polish
**Location**: `BottomNav.svelte`
**Severity**: 🟢 Medium
**Category**: Interaction / Polish

**Description**:
Floating pill nav exists but may need active state refinement and touch feedback.

**Impact**:
- Navigation state unclear
- Touch feedback missing

**Recommendation**:
Add clear active states, touch feedback (scale), and smooth transitions.

**Suggested Command**: `/polish` or `/delight`

---

### Low-Severity Issues

#### 13. Offline Banner Implementation
**Location**: `OfflineBanner.svelte`
**Severity**: ⚪ Low
**Category**: Polish

**Description**:
Good feature, but check if dismissible and visually integrated.

**Recommendation**:
Ensure dismissible, non-intrusive, consistent with app design.

#### 14. Progress Component Usage
**Location**: `Progress.svelte`
**Severity**: ⚪ Low
**Category**: Performance

**Description**:
Check if using `value` attribute properly for ARIA.

**Recommendation**:
Ensure `aria-valuenow`, `aria-valuemin`, `aria-valuemax` set correctly.

#### 15. Error Boundary Implementation
**Location**: `ErrorBoundary.svelte`
**Severity**: ⚪ Low
**Category**: Resilience

**Description**:
Good pattern, ensure it provides recovery options.

**Recommendation**:
Add retry mechanisms and helpful error messages.

#### 16-20. Additional Minor Items
- Avatar component may need loading states
- Currency converter could use better formatting
- Loading spinner could be more distinctive
- Stat card may need better visual hierarchy
- Tabs component could use smoother transitions

---

## Patterns & Systemic Issues

### Recurring Problems

1. **Design Token Adoption Gap**
   - Tokens exist in `app.css` but inconsistent adoption
   - 531 hardcoded colors suggest "bolted-on" design system
   - **Pattern**: Components were built before tokens, migration incomplete

2. **Mobile-First Not Applied**
   - Only 1 explicit mobile-first pattern found
   - Fixed dimensions suggest desktop-first thinking
   - **Pattern**: Components built with fixed sizes, not fluid

3. **Form Accessibility Missing**
   - Only 13 labels for many form inputs
   - **Pattern**: Forms built without accessibility consideration

4. **Spacing Inconsistency**
   - 445 hardcoded spacing values
   - **Pattern**: Spacing decided per-component, not systematically

5. **Variant Utility Underutilized**
   - `component-variants.ts` exists but barely used
   - **Pattern**: Duplication instead of consolidation

---

## Positive Findings

### What's Working Well

1. ✅ **Modern Svelte 5 Usage**
   - Proper use of `$props`, `$derived`, `$state` runes
   - Current best practices

2. ✅ **Semantic HTML Foundation**
   - 67 semantic elements found
   - Good use of proper HTML tags

3. ✅ **Zero Performance Red Flags**
   - No images to optimize
   - No large imports
   - Minimal animations (no layout thrashing)
   - Small component sizes (18-217 lines)

4. ✅ **Design System Foundation Exists**
   - `app.css` has proper token structure
   - `component-variants.ts` provides patterns
   - Tailwind config properly configured
   - Dark mode supported via class strategy

5. ✅ **Good Component Structure**
   - Clear separation: UI components vs Layout components
   - Atomic design pattern (Avatar, Badge, Card as atoms)
   - Reusable components (Input, Select, Toggle)

6. ✅ **No AI Slop Anti-Patterns**
   - No gradient text
   - No glassmorphism
   - No hero metric layouts
   - No dark mode with glowing accents
   - Clean, purposeful design

7. ✅ **Accessibility Foundation**
   - 26 ARIA labels present
   - 65 buttons (proper button elements)
   - Focus styles defined in `app.css`

---

## Recommendations by Priority

### Immediate (This Sprint)

1. **`/normalize`** - Migrate hardcoded colors to design tokens
   - Addresses: 531 hardcoded color issues
   - Impact: Eliminates theming inconsistencies, enables dark mode
   - Estimated effort: 2-3 hours

2. **`/harden`** - Fix form accessibility
   - Addresses: Missing labels, ARIA issues
   - Impact: WCAG AA compliance, better screen reader support
   - Estimated effort: 1-2 hours

3. **`/harden`** - Ensure 44x44px touch targets
   - Addresses: Fixed dimensions, touch target issues
   - Impact: Mobile usability, WCAG compliance
   - Estimated effort: 1 hour

### Short-Term (Next Sprint)

4. **`/normalize`** - Migrate spacing to semantic tokens
   - Addresses: 445 hardcoded spacing issues
   - Impact: Visual consistency, clearer rhythm
   - Estimated effort: 2 hours

5. **`/normalize`** - Migrate typography to semantic scale
   - Addresses: 407 font size issues
   - Impact: Consistent hierarchy
   - Estimated effort: 1-2 hours

6. **`/adapt`** - Add responsive breakpoints
   - Addresses: Limited responsive patterns
   - Impact: Better tablet/desktop experience
   - Estimated effort: 2-3 hours

7. **`/harden`** - Add focus indicators to custom components
   - Addresses: Keyboard navigation
   - Impact: Accessibility for keyboard users
   - Estimated effort: 1 hour

### Medium-Term (Following Sprint)

8. **`/extract`** - Consolidate variant patterns
   - Addresses: Duplication, underutilized utilities
   - Impact: Easier maintenance, consistency
   - Estimated effort: 2 hours

9. **`/onboard`** - Create empty state components
   - Addresses: Missing empty states
   - Impact: Better onboarding, less confusion
   - Estimated effort: 3-4 hours

10. **`/polish`** - Refine spacing consistency
    - Addresses: Visual rhythm issues
    - Impact: More polished feel
    - Estimated effort: 2 hours

11. **`/animate`** - Add purposeful micro-interactions
    - Addresses: Static feel
    - Impact: More premium, responsive feel
    - Estimated effort: 2-3 hours

### Long-Term (Backlog)

12. **`/delight`** - Add delightful moments
    - Celebration animations, success states
    - Estimated effort: 4-6 hours

13. **`/polish`** - Skeleton loader refinement
    - Match actual content structure
    - Estimated effort: 1-2 hours

14. **`/polish`** - Bottom nav polish
    - Active states, touch feedback
    - Estimated effort: 1 hour

---

## Suggested Commands for Fixes

| Command | Purpose | Issues Addressed |
|---------|---------|------------------|
| `/normalize` | Align with design system | 531 colors + 445 spacing + 407 typography = 1,383 issues |
| `/harden` | Improve accessibility & resilience | Forms, ARIA, touch targets, focus indicators |
| `/adapt` | Improve responsive design | Breakpoints, fluid sizing, mobile-first |
| `/extract` | Consolidate reusable patterns | Variant utilities, component consolidation |
| `/onboard` | Design empty states & onboarding | Empty components, first-run experience |
| `/polish` | Final quality pass | Spacing, details, refinement |
| `/animate` | Add purposeful motion | Micro-interactions, state changes |
| `/delight` | Add moments of joy | Celebrations, delightful touches |

---

## Summary

This is a **well-structured codebase with a solid foundation** that needs consistency work. The design system exists but isn't fully adopted. The main work is **migration to tokens**, not building from scratch.

**Key Insight**: This is not AI slop—it's incomplete implementation of a design system.

**Recommended Approach**:
1. Run `/normalize` first (biggest impact)
2. Run `/harden` for accessibility blockers
3. Run `/adapt` for responsive concerns
4. Polish with `/animate`, `/delight`, `/onboard`

**Effort Estimate**: 15-20 hours to reach high quality across all dimensions.
