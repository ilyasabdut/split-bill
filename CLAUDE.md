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

### Design System (Superdesign)

**Location**: `/web/src/app.css` and `/web/tailwind.config.js`

#### Color System

**Primary Brand Colors**:
- `brand-500`: `#0ea5e9` - Primary CTAs, active states, brand moments
- `brand-600`: `#0284c7` - Hover states
- `brand-50`: `#f0f9ff` - Light brand backgrounds

**Status Colors**:
- `success`: `#10b981` (emerald-500) - Paid, settled, completed
- `warning`: `#f59e0b` (amber-500) - Pending, unpaid
- `error`: `#ef4444` (rose-500) - Failed, deleted
- `info`: `#0ea5e9` (sky-500) - Helper states

**Semantic Background Pairs** (for icon containers, badges, stat cards):
- `bg-sky-100 text-sky-700` - Brand/primary icons
- `bg-emerald-100 text-emerald-700` - Success states
- `bg-amber-100 text-amber-700` - Warning states
- `bg-rose-100 text-rose-700` - Error states
- `bg-indigo-100 text-indigo-600` - Info/helper states
- `bg-violet-100 text-violet-600` - Group categories
- `bg-pink-100 text-pink-600` - Group categories
- `bg-orange-100 text-orange-500` - Template categories

**Surface Colors**:
- `surface-0`: White - Primary card background
- `surface-50`: `slate-50` - Subtle backgrounds
- `surface-100`: `slate-100` - Dividers, borders
- `surface-200`: `slate-200` - Secondary borders

#### Typography

**Font Family**: Plus Jakarta Sans (loaded via Fontshare)

**Semantic Scale** (use these, never arbitrary pixels):
- `caption`: 0.75rem (12px) - Metadata, timestamps
- `label`: 0.875rem (14px) - Secondary labels
- `body`: 1rem (16px) - Body text
- `subheading`: 1.125rem (18px) - Section titles
- `section`: 1.25rem (20px) - Subsection headers
- `heading`: 1.5rem (24px) - Page headers
- `hero`: 2rem (32px) - Hero titles
- `display`: 2.5rem (40px) - Display headlines

**Custom Sizes** (when semantic scale isn't enough):
- `[10px]` - Tiny badges, labels
- `[11px]` - Small metadata
- `[12px]` - Compact labels
- `[14px]` - Small body text
- `[22px]` - Large headings
- `[32px]` - Hero numbers

**Font Weights**:
- `medium` (500) - Emphasized body text
- `semibold` (600) - Buttons, labels
- `bold` (700) - Headers, emphasis
- `exabold` (800) - Numbers, hero text

**Text Utilities**:
- `tracking-tight` - Headlines for premium feel
- `uppercase tracking-wider` - Small headers, badges
- `tabular-nums` - Financial data
- `text-balance` - Headings for better wrap

#### Border Radius

**Standard Values**:
- `rounded-xl`: 0.75rem (12px) - Small elements, inputs
- `rounded-2xl`: 1rem (16px) - Buttons, icon containers
- `rounded-3xl`: 1.5rem (24px) - **Primary card radius** - Use this for most cards
- `rounded-full`: Fully rounded - Pills, badges, avatars

**Custom**:
- `xl2`: 1.25rem (20px) - Available in Tailwind config

#### Shadows

**Standard**:
- `shadow-card` - Default card elevation
- `shadow-md` - Medium elevation (buttons, cards)
- `shadow-elevated` - Floating elements, bottom nav
- `shadow-modal` - Overlays and dialogs
- `shadow-lg` - High elevation (hero cards)

**Colored Shadows** (for brand moments):
- `shadow-[0_0_15px_rgba(14,165,233,0.5)]` - Brand glow effect
- `shadow-brand-500/20` - Subtle brand shadow
- `shadow-brand-500/30` - Stronger brand shadow

#### Spacing

**Base Grid**: 4px

**Semantic Spacing**:
- `tight`: 8px - Compact gaps
- `component`: 16px - Element spacing
- `section`: 24px - Section spacing (minimum between sections)

**Mobile Safe Areas**:
- `pt-14` - Header clearance with notch
- `pb-[120px]` - Content above floating bottom nav
- `pb-[34px]` - Content above compact nav
- `pt-safe`, `pb-safe`, `px-safe` - Dynamic safe area insets

### Component Pattern Library

#### 1. Card Section Pattern
```html
<section class="rounded-3xl bg-white shadow-md border border-slate-200 p-5">
  <!-- Content -->
</section>
```

**Variants**:
- Hero card: Add `relative overflow-hidden` for decorative backgrounds
- Glassmorphism: `bg-white/60 border border-white/50 backdrop-blur-sm`
- Dark card: `bg-slate-900 text-white shadow-lg`

#### 2. Icon Container Pattern
```html
<div class="h-11 w-11 rounded-2xl bg-sky-100 text-sky-700 flex items-center justify-center">
  <iconify-icon icon="lucide:icon-name" class="text-xl"></iconify-icon>
</div>
```

**Variants**:
- Large icon: `h-14 w-14 rounded-3xl bg-brand-50 border border-brand-500/20`
- Small icon: `h-8 w-8 rounded-xl`
- Brand colored: `bg-brand-500 shadow-md` (with white icon)

#### 3. Status Badge Pattern
```html
<span class="rounded-full bg-emerald-100 text-emerald-800 px-2 py-1 text-[10px] font-bold uppercase tracking-wide">
  Paid
</span>
```

**Variants**:
- Unpaid: `bg-amber-100 text-amber-800`
- Paid: `bg-emerald-100 text-emerald-800`
- Error: `bg-rose-100 text-rose-800`

#### 4. Pill Button Pattern
```html
<button class="h-[38px] px-5 rounded-full bg-slate-100 text-slate-700 font-semibold hover:bg-slate-200 active:scale-95 transition-transform">
  Button Label
</button>
```

**Variants**:
- Primary pill: `bg-brand-500 text-white shadow-md`
- Currency selector: Add circular flag with `w-4 h-4 rounded-full bg-white shadow-sm`

#### 5. Floating Bottom Navigation Pattern
```html
<nav class="bg-white border border-slate-200 shadow-xl rounded-[28px] px-3 py-2 mx-auto max-w-2xl">
  <!-- Nav items -->
</nav>
```

**Nav Item**:
```html
<a class="min-h-[44px] rounded-2xl bg-brand-50 text-brand-600 flex flex-col items-center justify-center gap-1 py-2 active:scale-[0.99]">
  <iconify-icon icon="lucide:icon" class="text-xl"></iconify-icon>
  <span class="text-[12px] font-semibold">Label</span>
</a>
```

#### 6. Avatar System Pattern
```html
<div class="h-7 w-7 rounded-full bg-sky-200 border-2 border-white flex items-center justify-center">
  <span class="text-[10px] font-bold text-sky-800">M</span>
</div>
```

**Stacked Avatars**: `flex -space-x-2` for overlapping effect

#### 7. Horizontal Scroll Pattern
```html
<div class="flex gap-3 overflow-x-auto pb-4 -mx-4 px-4 scrollbar-hide">
  <!-- Scrollable items -->
</div>
```

**Classes**:
- `scrollbar-hide` utility defined in app.css
- `gap-3` between items
- `-mx-4 px-4` for full-width bleed

#### 8. Decorative Background Pattern
```html
<div class="pointer-events-none absolute inset-0 overflow-hidden">
  <div class="absolute -top-24 -right-20 h-72 w-72 rounded-full bg-brand-500/15 blur-2xl"></div>
  <div class="absolute top-28 -left-24 h-72 w-72 rounded-full bg-emerald-400/10 blur-2xl"></div>
  <div class="absolute bottom-40 -right-24 h-72 w-72 rounded-full bg-amber-400/10 blur-2xl"></div>
</div>
```

**Use**: Hero sections, featured cards for depth and premium feel

### Interactive States

**Press Feedback** (critical for mobile feel):
- `active:scale-[0.99]` - Standard press (buttons, cards)
- `active:scale-[0.98]` - Stronger press (large cards)
- `active:scale-95` - Light press (small elements)
- `active:opacity-70` - Alternative feedback

**Hover States** (desktop):
- `hover:bg-brand-50` - Subtle highlight
- `group-hover:bg-brand-50` - Parent group hover
- `hover:bg-slate-200` - Secondary elements

**Transitions**:
- `transition-transform` - Scale animations
- `transition-colors` - Color changes
- `transition-all` - Both (use sparingly for performance)
- Custom durations: `transition-medium` (200ms), `transition-slow` (300ms)

### When Designing

1. **Use existing tokens first** - Check `/web/src/app.css` before adding new values
2. **Import from component-variants.ts** - Badge, button, input patterns already defined
3. **Mobile-first** - Design for 375-430px width, then expand
4. **Touch targets** - Minimum 44x44px for all interactive elements (`min-h-[44px]`, `h-11`)
5. **Test dark mode** - Toggle class on `<html>` to verify
6. **Use rounded-3xl for cards** - Primary card radius for premium iOS feel
7. **Add press feedback** - Always include `active:scale-[0.99]` on interactive elements
8. **Safe areas for headers** - Use `pt-14` for notch clearance
9. **Padding for floating nav** - Use `pb-[120px]` on main content
10. **Semantic color pairs** - Match icon container bg/text colors from the pairs list

### Component Guidelines

**Cards**:
- Primary: `rounded-3xl bg-white shadow-md border border-slate-200 p-5`
- Hero: Add `relative overflow-hidden` with decorative blurred circles
- Glassmorphism: `bg-white/60 border border-white/50 backdrop-blur-sm rounded-2xl`

**Buttons**:
- Primary: `h-12 min-h-[44px] rounded-2xl bg-brand-500 shadow-md active:scale-[0.99] transition-transform`
- Secondary: `h-12 min-h-[44px] rounded-2xl bg-white border border-slate-200 shadow-md active:scale-[0.99]`
- Pill: `h-[38px] px-5 rounded-full bg-slate-100 font-semibold active:scale-95`

**Icon Containers**:
- Standard: `h-11 w-11 rounded-2xl bg-sky-100 text-sky-700 flex items-center justify-center`
- Brand: `h-11 w-11 rounded-2xl bg-brand-500 shadow-md flex items-center justify-center` (white icon)
- Large: `h-14 w-14 rounded-3xl bg-brand-50 border border-brand-500/20`

**Inputs**: 48-60px height, clear labels, semantic error states

**Badges**:
- Status pill: `rounded-full bg-emerald-100 text-emerald-800 px-2 py-1 text-[10px] font-bold uppercase tracking-wide`
- Use semantic background/text color pairs

**Avatars**:
- Standard: `h-7 w-7 rounded-full bg-sky-200 border-2 border-white flex items-center justify-center`
- Stacked: `flex -space-x-2` for overlap effect

**Horizontal Scrolling**:
- Container: `flex gap-3 overflow-x-auto pb-4 -mx-4 px-4 scrollbar-hide`
- Items: `shrink-0` to prevent compression

**Bottom Navigation**:
- Container: `bg-white border border-slate-200 shadow-xl rounded-[28px] px-3 py-2`
- Active item: `min-h-[44px] rounded-2xl bg-brand-50 text-brand-600 active:scale-[0.99]`

### Accessibility

- Minimum contrast: 4.5:1 for normal text, 3:1 for large text
- All interactive elements: 44x44px minimum (`min-h-[44px]`, `h-11`)
- Focus states: `focus-visible` ring, 2px offset
- Semantic HTML: proper heading hierarchy, button/link distinctions
- Safe area insets: `pt-safe`, `pb-safe`, `px-safe` for mobile devices
- Screen reader only: `.sr-only` utility for hidden labels
