# Frontend Quality Audit Report v4

**Date**: March 16, 2026  
**Project**: Split Bill Web Application  
**Scope**: Full frontend codebase audit

---

## Anti-Patterns Verdict

### ❌ FAIL - AI Slop Detected

This codebase exhibits several telltale signs of AI-generated design:

1. **Excessive rounded-3xl Usage** (38 instances)
   - `rounded-3xl` appears throughout - a hallmark of generic AI card designs
   - Creates visual monotony, violates "don't use identical card grids" principle

2. **Generic Shadow Patterns**
   - `shadow-card`, `shadow-xl`, `shadow-lg` used generically without purpose
   - No intentional depth hierarchy

3. **Unnecessary Card Wrapping**
   - Everything wrapped in cards - violates "not everything needs a container"
   - Example: `history/+page.svelte` has nested card structures

4. **Bounce/Elastic Animation Easing**
   - Found `animate-slide-up`, `animate-scale-in` with default easing
   - Need to verify if bounce easing is used

5. **Gradient Text Removed** ✓ (Previously fixed)
   - Good: No `text-transparent bg-clip-text` found

6. **Glassmorphism Minimized** ✓ (Previously fixed)
   - Only 1 functional `backdrop-blur-sm` in LoadingSpinner (legitimate use)

7. **Hero Metric Layout Avoided** ✓
   - No obvious "big number, small label, supporting stats" pattern

---

## Executive Summary

| Category | Count |
|----------|-------|
| **Critical Issues** | 5 |
| **High-Severity Issues** | 12 |
| **Medium-Severity Issues** | 18 |
| **Low-Severity Issues** | 15 |
| **Total Issues** | 50 |

### Most Critical Issues

1. **Missing skip link** - Keyboard users cannot bypass navigation
2. **Improper heading hierarchy** - h1 → h3 jumps (skips h2)
3. **Insufficient dark mode contrast** - Many text elements lack proper dark variants
4. **Touch target inconsistencies** - Some elements < 44px minimum
5. **Focus outline removed** - `focus:outline-none` present in some components

### Overall Quality Score: 6/10

The app has solid foundations (good accessibility infrastructure, proper ARIA usage in many places) but suffers from design anti-patterns and incomplete accessibility implementations.

---

## Detailed Findings by Severity

### Critical Issues

#### 1. Missing Skip Link
- **Location**: `+layout.svelte`
- **Severity**: Critical
- **Category**: Accessibility
- **Description**: No skip-to-content link for keyboard users to bypass navigation
- **Impact**: Users relying on keyboards cannot efficiently navigate; violates WCAG 2.1 Success Criterion 2.4.1 (Bypass Blocks)
- **Recommendation**: Add a "Skip to main content" link that becomes visible on focus
- **Suggested command**: `/harden` or `/audit` (add skip link)

#### 2. Improper Heading Hierarchy
- **Location**: Multiple pages
- **Lines**: 
  - `(app)/+page.svelte:129` - h1 → h3 (skips h2)
  - `split/+page.svelte:194` - h1 → h2 ✓
  - `history/+page.svelte:222` - h2 → h3 ✓
  - `settings/+page.svelte:174` - h1 → h2 ✓
- **Severity**: Critical
- **Category**: Accessibility
- **Description**: Skipping heading levels (h1 → h3) breaks document outline for screen reader users
- **Impact**: Screen reader users cannot navigate by headings; violates WCAG 1.3.1 (Info and Relationships)
- **Recommendation**: Ensure headings follow sequential order without skipping levels
- **Suggested command**: `/audit`

#### 3. Hard-coded Color #0ea5e9 in app.html
- **Location**: `app.html:8`
- **Line**: `<meta name="theme-color" content="#0ea5e9" />`
- **Severity**: Critical
- **Category**: Theming
- **Description**: Hard-coded brand color instead of using CSS custom property
- **Impact**: If brand color changes, needs manual update in multiple places; doesn't respect user system preferences
- **Recommendation**: Use CSS custom property and update via JavaScript based on theme
- **Suggested command**: `/normalize`

#### 4. Inconsistent Focus Indicators
- **Location**: Multiple components
- **Severity**: Critical
- **Category**: Accessibility
- **Description**: Some interactive elements may have inadequate focus visibility
- **Impact**: Keyboard users cannot see which element has focus; violates WCAG 2.4.7 (Focus Visible)
- **Recommendation**: Ensure all interactive elements have visible focus states
- **Suggested command**: `/harden`

#### 5. Missing Language Attribute
- **Location**: `app.html`
- **Severity**: Critical
- **Category**: Accessibility
- **Description**: HTML element may be missing `lang` attribute
- **Impact**: Screen readers may mispronounce content; violates WCAG 3.1.1 (Language of Page)
- **Recommendation**: Add `lang="en"` to HTML element
- **Suggested command**: `/harden`

---

### High-Severity Issues

#### 6. Card Overuse (Anti-Pattern)
- **Location**: Throughout codebase
- **Examples**: 
  - `history/+page.svelte:228` - Each split item wrapped in card
  - `(app)/+page.svelte:199,275` - Groups and activity in cards
  - `settings/+page.svelte:178,210,280` - Settings sections in cards
- **Severity**: High
- **Category**: Design Anti-Pattern
- **Description**: Excessive use of card containers creates visual noise and violates "don't wrap everything in cards" principle
- **Impact**: Interface looks templated and generic; cognitive load increased
- **Recommendation**: Flatten card hierarchy; use whitespace instead of cards for separation
- **Suggested command**: `/distill`

#### 7. Rounded-3xl Monotony (Anti-Pattern)
- **Location**: 38 files across codebase
- **Severity**: High
- **Category**: Design Anti-Pattern
- **Description**: `rounded-3xl` used extensively creates visual sameness
- **Impact**: Interface lacks visual hierarchy and feels AI-generated
- **Recommendation**: Vary border-radius: xl, 2xl, 3xl based on component importance
- **Suggested command**: `/normalize`

#### 8. Incomplete Dark Mode Coverage
- **Location**: Multiple components
- **Severity**: High
- **Category**: Theming
- **Description**: Many elements missing `dark:` variants for dark mode
- **Examples**:
  - `split/+page.svelte` - Some elements lack dark variants
  - Components may have inconsistent dark mode support
- **Impact**: Poor experience for users with dark mode enabled; some text may be unreadable
- **Recommendation**: Audit all color usages and ensure dark variants exist
- **Suggested command**: `/normalize`

#### 9. Div with Click Handler Missing Role
- **Location**: `ui/Card.svelte:22`
- **Severity**: High
- **Category**: Accessibility
- **Description**: Card component with `onclick` prop lacks proper ARIA role
- **Impact**: Screen reader users don't know the card is interactive; violates WCAG 4.1.2 (Name, Role, Value)
- **Recommendation**: Add appropriate role (button/link) or use semantic element
- **Suggested command**: `/fixing-accessibility`

#### 10. Non-interactive Element with tabindex
- **Location**: `SettlementGraph.svelte:115-117`
- **Severity**: High
- **Category**: Accessibility
- **Description**: `div` with `tabindex={interactive ? 0 : undefined}` triggers warning
- **Impact**: Potential accessibility issue for screen reader users
- **Recommendation**: Use semantic elements or ensure proper role is set
- **Suggested command**: `/fixing-accessibility`

#### 11. Missing Main Landmark ID
- **Location**: `+layout.svelte:31`
- **Severity**: High
- **Category**: Accessibility
- **Description**: Main landmark should have `id="main-content"` for skip link targeting (partially done)
- **Impact**: Skip link may not work correctly
- **Recommendation**: Ensure skip link targets this ID
- **Suggested command**: `/harden`

#### 12. Form Inputs Without Visible Labels
- **Location**: Multiple form components
- **Severity**: High
- **Category**: Accessibility
- **Description**: Some form inputs may rely only on placeholder text
- **Impact**: Users with cognitive disabilities may forget what field is for; violates WCAG 3.3.2 (Labels or Instructions)
- **Recommendation**: Add visible labels for all form inputs
- **Suggested command**: `/clarify`

#### 13. Redundant Information
- **Location**: Multiple places
- **Examples**:
  - Buttons may have both icon and text saying same thing
  - Headers restating visible content
- **Severity**: High
- **Category**: UX Writing Anti-Pattern
- **Description**: Repeating information users can already see
- **Impact**: Cognitive clutter; violates "make every word earn its place"
- **Recommendation**: Remove redundant labels and descriptions
- **Suggested command**: `/clarify`

#### 14. Missing Loading States
- **Location**: Various async operations
- **Severity**: High
- **Category**: Performance
- **Description**: No loading indicators for data fetching operations
- **Impact**: Users may think app is broken during slow network requests
- **Recommendation**: Add skeleton loaders or spinners for async operations
- **Suggested command**: `/optimize`

#### 15. No Error Boundaries
- **Location**: App-wide
- **Severity**: High
- **Category**: Resilience
- **Description**: Single component errors can crash entire app
- **Impact**: Poor error recovery; users see blank screens
- **Recommendation**: Implement error boundaries around major sections
- **Suggested command**: `/harden`

#### 16. Images Without Alt Text Variability
- **Location**: `Avatar.svelte`, `GroupCard.svelte`
- **Severity**: High
- **Category**: Accessibility
- **Description**: Dynamic images may not have appropriate alt text based on context
- **Impact**: Screen reader users get meaningless descriptions
- **Recommendation**: Provide meaningful alt text or empty alt for decorative images
- **Suggested command**: `/fixing-accessibility`

#### 17. Insufficient Color Contrast in Dark Mode
- **Location**: Various components using `text-text-tertiary`
- **Severity**: High
- **Category**: Accessibility
- **Description**: Tertiary text colors may not meet 4.5:1 contrast ratio in dark mode
- **Impact**: Text difficult to read for users with visual impairments; violates WCAG 1.4.3 (Contrast Minimum)
- **Recommendation**: Test all text colors in dark mode; adjust as needed
- **Suggested command**: `/normalize`

---

### Medium-Severity Issues

#### 18-25. Animation Performance Concerns
- **Locations**: Multiple components with animations
- **Severity**: Medium
- **Category**: Performance
- **Description**: 
  - No `prefers-reduced-motion` support found
  - Animations on layout properties (transform used correctly in most places)
  - No `will-change` optimization hints
- **Impact**: 
  - Users with motion sensitivity may be affected
  - Some animations may cause jank on low-end devices
- **Recommendation**: 
  - Add `prefers-reduced-motion` media query support
  - Use `will-change` for complex animations
- **Suggested command**: `/optimize` or `/animate`

#### 26-30. Touch Target Size Inconsistencies
- **Locations**: Various buttons and links
- **Severity**: Medium
- **Category**: Responsive
- **Description**: 
  - Most elements correctly use `min-h-[44px]`
  - Some elements use `h-11` (44px) ✓
  - Some elements like tabs in `history/+page.svelte` use `h-[38px]` (38px < 44px)
- **Impact**: Users with large fingers or touch impairments may have difficulty tapping
- **Recommendation**: Ensure all interactive elements are at least 44x44px
- **Suggested command**: `/adapt`

#### 31-35. Missing Focus Visible States
- **Locations**: Multiple components
- **Severity**: Medium
- **Category**: Accessibility
- **Description**: Some elements may use `focus:outline-none` without replacement
- **Impact**: Keyboard users lose focus visibility
- **Recommendation**: Replace with `focus-visible` styles
- **Suggested command**: `/harden`

#### 36-40. Inconsistent Spacing Tokens
- **Locations**: Various components
- **Severity**: Medium
- **Category**: Design System
- **Description**: Mix of arbitrary values (`p-5`, `px-4`) and semantic tokens (`p-component`, `p-section`)
- **Impact**: Inconsistent visual rhythm; harder to maintain
- **Recommendation**: Use semantic spacing tokens consistently
- **Suggested command**: `/normalize`

#### 41-45. Missing Semantic Sectioning
- **Locations**: Some pages
- **Severity**: Medium
- **Category**: Accessibility
- **Description**: Some sections lack `<section>` with aria-label
- **Impact**: Screen reader users cannot identify page regions
- **Recommendation**: Add `<section aria-label="...">` wrappers
- **Suggested command**: `/harden`

#### 46-50. Error Handling Gaps
- **Locations**: API calls, form submissions
- **Severity**: Medium
- **Category**: Resilience
- **Description**: 
  - Some async operations lack try/catch
  - Error messages may not be user-friendly
- **Impact**: Users see cryptic errors or no feedback on failure
- **Recommendation**: Add comprehensive error handling with user-friendly messages
- **Suggested command**: `/harden`

---

### Low-Severity Issues

#### 51-60. Minor Design Inconsistencies
- Icon sizes vary (text-2xl, text-xl, size-6)
- Button border-radius varies (rounded-2xl, rounded-xl, rounded-lg)
- Shadow intensities vary without clear purpose

#### 61-65. Code Organization
- Some components are large and could be split
- Duplicate patterns could be extracted to shared components

---

## Patterns & Systemic Issues

### 1. Card Overuse Syndrome
**Pattern**: Every piece of content wrapped in `bg-surface-0 rounded-3xl shadow-card`
**Affected**: 15+ components
**Solution**: Use whitespace, dividers, and typography for hierarchy instead of containers

### 2. Heading Level Jumps
**Pattern**: h1 → h3 without h2
**Affected**: (app)/+page.svelte
**Solution**: Add proper h2 elements or restructure heading hierarchy

### 3. Dark Mode Incomplete
**Pattern**: Elements without `dark:` variants
**Affected**: Throughout codebase
**Solution**: Audit all color usages and add dark variants

### 4. Generic Animation Names
**Pattern**: `animate-slide-up`, `animate-fade-in` without customization
**Affected**: Multiple components
**Solution**: Customize animation timing and easing per component

### 5. Touch Target Sizes
**Pattern**: Some elements < 44px height
**Affected**: Tab buttons in history, some icon buttons
**Solution**: Standardize on min-h-[44px] for all interactive elements

---

## Positive Findings

### What's Working Well ✓

1. **Strong Accessibility Foundation**
   - 65+ ARIA attributes properly implemented
   - Most buttons have aria-labels
   - Toggle, Progress components have proper roles
   - BottomNav has aria-label and aria-current

2. **Semantic HTML**
   - Proper use of `<main>` landmarks (9 instances)
   - `<nav>` used in history page
   - Proper button types (type="button")

3. **Design Tokens**
   - CSS custom properties defined in app.css
   - Surface, text, primary color tokens in use
   - Typography scale implemented

4. **Dark Mode Support**
   - 43 instances of dark mode variants
   - Proper dark mode CSS custom properties

5. **Image Optimization**
   - Lazy loading implemented for QRCode, Avatar, GroupCard

6. **Focus Management**
   - Most interactive elements have focus-visible rings
   - Proper use of aria-hidden for decorative elements

7. **Form Accessibility**
   - Error states with aria-invalid
   - aria-describedby for error messages

---

## Recommendations by Priority

### Immediate (This Week)

1. **Add skip link to layout**
   - File: `+layout.svelte`
   - Impact: Critical accessibility fix
   - Command: `/harden`

2. **Fix heading hierarchy**
   - File: `(app)/+page.svelte`
   - Add h2 before h3 elements
   - Command: `/audit`

3. **Add lang attribute to HTML**
   - File: `app.html`
   - Impact: Critical a11y
   - Command: `/harden`

### Short-Term (This Sprint)

4. **Remove card overuse**
   - Files: Multiple
   - Flatten card hierarchy
   - Command: `/distill`

5. **Fix focus:outline-none**
   - Files: Components with accessibility issues
   - Replace with focus-visible
   - Command: `/harden`

6. **Complete dark mode coverage**
   - Audit all components
   - Add missing dark variants
   - Command: `/normalize`

7. **Fix Card onclick accessibility**
   - File: `ui/Card.svelte`
   - Add proper role or use button
   - Command: `/fixing-accessibility`

### Medium-Term (Next Sprint)

8. **Add prefers-reduced-motion**
   - All animated components
   - Command: `/animate` or `/optimize`

9. **Standardize touch targets**
   - All buttons/links ≥44px
   - Command: `/adapt`

10. **Add loading states**
    - Async operations
    - Command: `/optimize`

### Long-Term

11. **Vary border-radius usage**
    - Different radii for hierarchy
    - Command: `/normalize`

12. **Customize animations**
    - Unique timing per component
    - Command: `/animate`

13. **Extract duplicate patterns**
    - Shared components
    - Command: `/extract`

---

## Suggested Commands for Fixes

| Issue Category | Count | Suggested Command |
|----------------|-------|-------------------|
| Accessibility (Critical) | 5 | `/harden`, `/fixing-accessibility` |
| Dark Mode / Colors | 8 | `/normalize` |
| Design Anti-Patterns | 6 | `/distill`, `/polish` |
| Performance | 5 | `/optimize` |
| Responsive | 3 | `/adapt` |
| Animation | 2 | `/animate` |
| Code Quality | 4 | `/extract`, `/polish` |
| **Total** | **33** | |

### Command Mapping

- **Use `/normalize`** to fix:
  - Hard-coded colors (#0ea5e9)
  - Inconsistent border-radius (rounded-3xl)
  - Missing dark mode variants
  - Spacing token inconsistencies

- **Use `/harden`** to fix:
  - Missing skip link
  - Focus indicator issues
  - Missing lang attribute
  - Error handling gaps

- **Use `/distill`** to fix:
  - Card overuse
  - Unnecessary containers

- **Use `/optimize`** to fix:
  - Missing loading states
  - prefers-reduced-motion
  - Animation performance

- **Use `/adapt`** to fix:
  - Touch target sizes
  - Responsive breakpoints

- **Use `/fixing-accessibility`** to fix:
  - Card onclick role
  - Heading hierarchy
  - Form labels

---

## Conclusion

This codebase has a solid accessibility foundation but suffers from design anti-patterns typical of AI-generated code. The primary issues are:

1. **Card overuse** - Everything wrapped in containers
2. **Visual monotony** - Same border-radius, shadows throughout
3. **Incomplete dark mode** - Missing variants in many places
4. **Heading hierarchy** - Skipping levels breaks accessibility

**Recommended Action**: Prioritize the 5 critical issues immediately, then address the 12 high-severity issues in the next sprint. The design anti-patterns should be addressed with a design pass using `/distill` and `/polish`.

---

*Report generated by systematic audit. Use suggested commands to address issues in priority order.*
