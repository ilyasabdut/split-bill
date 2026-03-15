# AI Coding Agent Guidelines

## Design Context

### Users
Young adults (18-35) splitting bills with friends, roommates, or partners. They use the app in casual social contexts—after meals, during trips, or managing shared household expenses. The job is to quickly and fairly split expenses without awkward money conversations.

### Brand Personality
Three words that define our brand voice:
1. **Efficient & trustworthy** - Gets the job done reliably, like a modern fintech app
2. **Friendly & playful** - Has personality and warmth, but not childish or chaotic
3. **Premium & polished** - Feels well-crafted with attention to detail

### Aesthetic Direction
**Minimalist with breathing room.** Think Swiss design influence, Japanese mobile apps, or modern fintech (Monzo, Revolut, Linear). Clean typography, generous whitespace, restrained color palette.

**Anti-references**: Dense dashboards, aggressive gradients, cluttered interfaces.

### Design Principles

1. **Clarity over density** - When in doubt, add more whitespace. Information should breathe.
2. **Confident simplicity** - Fewer elements, each purposeful. Don't add features "just in case."
3. **Subtle delight** - Micro-interactions and polish add premium feel, but never overwhelm.
4. **Trustworthy precision** - Numbers and financial data must be accurate, clear, and unambiguous.
5. **Mobile-first touch** - 44px minimum tap targets, proper safe areas, responsive layouts.

### Design System (Already Implemented)

**Location**: `/web/src/app.css` and `/web/tailwind.config.js`

**Colors**:
- Primary: `#0ea5e9` (Sky-500) - use for CTAs, active states, brand moments
- Status: `success`(#10b981), `warning`(#f59e0b), `error`(#ef4444), `info`(#0ea5e9)
- Surface: `surface-0`(white) through `surface-200`(gray-200) - backgrounds and borders
- Text: `text-primary` through `text-tertiary` - always use semantic tokens

**Typography**:
- Font: Plus Jakarta Sans (already loaded)
- Scale: `caption` → `label` → `body` → `subheading` → `section` → `heading` → `hero` → `display`
- Always use semantic font sizes, never arbitrary pixel values

**Spacing**:
- Base: 4px grid
- Use semantic: `tight`(8px), `component`(16px), `section`(24px)
- Generous gaps between sections (24-32px minimum)

**Radius**:
- sm: 12px, md: 16px, lg: 20px, xl: 24px, 2xl: 32px
- Cards and containers should use xl/2xl for that premium iOS feel

**Shadows**:
- `shadow-card` - for standard cards
- `shadow-elevated` - for floating elements, bottom nav
- `shadow-modal` - for overlays and dialogs

### When Designing

1. **Use existing tokens first** - Check `/web/src/app.css` before adding new values
2. **Import from component-variants.ts** - Badge, button, input patterns already defined
3. **Mobile-first** - Design for 375-430px width, then expand
4. **Touch targets** - Minimum 44x44px for all interactive elements
5. **Test dark mode** - Toggle class on `<html>` to verify

### Component Guidelines

- **Cards**: Use `bg-surface-0 shadow-card rounded-xl` with semantic padding
- **Buttons**: 48px min-height, 20px radius, primary or secondary variants
- **Inputs**: 48-60px height, clear labels, semantic error states
- **Badges**: Use semantic color variants from component-variants.ts
- **Icons**: 20-24px, light blue circular backgrounds for emphasis

### Accessibility

- Minimum contrast: 4.5:1 for normal text, 3:1 for large text
- All interactive elements: 44x44px minimum
- Focus states: `focus-visible` ring, 2px offset
- Semantic HTML: proper heading hierarchy, button/link distinctions
