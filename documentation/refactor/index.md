  Design Summary

  Framework: Svelte 5 + TypeScript + SvelteKit
  - Smallest bundles, best mobile performance
  - Mature PWA tooling (Vite + vite-plugin-pwa)
  - Built-in routing and reactive state

  Key Features:
  1. Mobile-first UX - Bottom navigation bar, thumb-friendly touch targets (44x44px minimum)
  2. Full offline mode - View splits, create calculations, queue OCR uploads
  3. Background Sync API - Receipt uploads process automatically when connection returns
  4. Performance targets - < 3s load time, < 200KB initial bundle

  Migration Strategy: Parallel development - keep Streamlit running while building SvelteKit in /web directory

  Implementation: 5 phases over ~10 weeks, from foundation to advanced features

  The plan preserves your excellent async FastAPI backend with minimal changes while completely replacing the Streamlit
  frontend.

⏺ User approved Claude's plan
  ⎿  Plan saved to: ~/.claude/plans/adaptive-pondering-lagoon.md · /plan to edit
     Mobile-First PWA Redesign: Split-Bill Application

     Date: 2026-02-13
     Status: Design Complete - Awaiting Approval

     ---
     Context

     The current Split-Bill application uses Streamlit for the frontend, which limits mobile experience, PWA
     capabilities, and performance optimization potential. This redesign aims to create a modern, mobile-first
     Progressive Web App with full offline capabilities, native-like UX, and production-grade performance.

     Current State:
     - Frontend: Streamlit 1.45.0 (Python) - server-rendered, limited mobile support
     - Backend: FastAPI 0.115.12 (fully async, well-architected) - keep this
     - Cache: Redis 7.x with async operations - keep and extend
     - AI: OpenRouter API for OCR - keep this integration
     - PWA Features: None currently

     Design Goals:
     1. Native-like mobile experience (installable, push notifications, offline-first)
     2. Performance optimization (code splitting, intelligent caching, <3s load time)
     3. Modern tech stack migration (Svelte 5 + TypeScript)
     4. Full offline mode with Background Sync API for OCR receipts

     ---
     Recommended Approach

     Framework: Svelte 5 + TypeScript + SvelteKit

     This combination provides:
     - Smallest bundle sizes (compiled-away reactivity)
     - Best-in-class mobile performance
     - Built-in routing and SSR capabilities
     - Mature PWA tooling (Vite + vite-plugin-pwa)
     - Excellent TypeScript support

     Alternative Considered:
     - React + Vite: Larger ecosystem but heavier bundles
     - Vue 3: Good reactivity but Svelte 5 is more performant
     - Next.js: Over-engineered for this use case, SvelteKit is lighter

     ---
     Architecture Overview

     New Directory Structure

     web/                              # New SvelteKit frontend
     ├── src/
     │   ├── lib/
     │   │   ├── components/
     │   │   │   ├── ui/              # Reusable UI components (Button, Card, Input...)
     │   │   │   ├── layout/           # AppShell, BottomNav, OfflineBanner
     │   │   │   └── features/         # Feature-specific (receipt/, split/, share/)
     │   │   ├── stores/              # Reactive state (receipt, split, offline, auth)
     │   │   ├── services/
     │   │   │   ├── api/             # API client wrappers
     │   │   │   ├── offline/          # Background sync queue, IndexedDB wrapper
     │   │   │   └── image/           # Client-side compression, validation
     │   │   └── utils/               # Currency, validation, math, share
     │   └── routes/                  # File-based routing
     │       ├── (app)/                # Main app layout with bottom navigation
     │       ├── receipt/               # Upload/capture receipt
     │       ├── split/[id]/            # View/edit split
     │       └── history/               # Split history
     ├── static/                       # PWA icons, manifest
     └── service-worker.ts             # Background sync and caching

     app/                             # EXISTING Streamlit (keep during migration)
     api/                             # EXISTING FastAPI (keep, minimal changes)

     Mobile-First Navigation (Bottom Tab Bar)

     ┌─────────────────────────────────┐
     │         Header/Title          │
     ├─────────────────────────────────┤
     │                                 │
     │        Main Content             │
     │       (Scrollable)              │
     │                                 │
     ├─────────────────────────────────┤
     │  📸  |  💰  |  📋  |  ⚙️    │
     │ Home |Split |History|Settings │
     └─────────────────────────────────┘

     Tech Stack Summary
     ┌────────────┬──────────────────────────────┬─────────┐
     │ Component  │          Technology          │ Version │
     ├────────────┼──────────────────────────────┼─────────┤
     │ Framework  │ Svelte 5 + TypeScript        │ latest  │
     ├────────────┼──────────────────────────────┼─────────┤
     │ Build Tool │ Vite                         │ 6.x     │
     ├────────────┼──────────────────────────────┼─────────┤
     │ PWA Plugin │ vite-plugin-pwa              │ 0.21+   │
     ├────────────┼──────────────────────────────┼─────────┤
     │ Router     │ SvelteKit                    │ 2.x     │
     ├────────────┼──────────────────────────────┼─────────┤
     │ State      │ Svelte Stores (runes mode)   │ Native  │
     ├────────────┼──────────────────────────────┼─────────┤
     │ Forms      │ Felte                        │ 2.x     │
     ├────────────┼──────────────────────────────┼─────────┤
     │ UI         │ Skeleton UI (Tailwind-based) │ 2.x     │
     └────────────┴──────────────────────────────┴─────────┘
     ---
     Key Design Decisions

     1. Service Worker Strategy
     ┌────────────────┬───────────────────────────────┬──────────────────────────────┐
     │   Asset Type   │           Strategy            │          Rationale           │
     ├────────────────┼───────────────────────────────┼──────────────────────────────┤
     │ App Shell      │ CacheFirst (network fallback) │ Instant load                 │
     ├────────────────┼───────────────────────────────┼──────────────────────────────┤
     │ API Responses  │ NetworkFirst (cache fallback) │ Fresh data                   │
     ├────────────────┼───────────────────────────────┼──────────────────────────────┤
     │ Receipt Images │ StaleWhileRevalidate          │ Fast display                 │
     ├────────────────┼───────────────────────────────┼──────────────────────────────┤
     │ OCR Requests   │ NetworkOnly + Background Sync │ Always fresh, queued offline │
     └────────────────┴───────────────────────────────┴──────────────────────────────┘
     Critical: Background Sync API for OCR receipts - when offline, uploads are queued and processed when connection
     returns. User gets notification when complete.

     2. Offline Capability

     Full offline mode for:
     - Viewing previously loaded splits and receipts
     - Creating and calculating splits (client-side math)
     - Queueing receipt uploads for background sync

     Online required for:
     - OCR receipt processing (queues automatically when offline)
     - Initial data fetch
     - Saving new splits to server

     UI: Persistent offline banner showing queued actions count

     3. API Integration

     Keep existing FastAPI endpoints unchanged:
     - POST /receipts/upload - OCR processing
     - POST /splits/calculate - Split calculation
     - GET /splits/view/{id} - Shared split view
     - GET /health - Health check

     New API client features:
     - Type-safe request/response handling
     - Request deduplication (idempotency keys)
     - Optimistic UI updates with rollback on error
     - Automatic offline queueing

     4. Idempotency & Async Patterns

     Enhance existing backend patterns:
     - SHA256-based cache keys (already in api/src/core/cache.py)
     - Extend TTL for PWA caching strategies
     - Add idempotency request headers for duplicate detection

     Client-side:
     - Request deduplication manager prevents duplicate concurrent requests
     - Optimistic updates with automatic rollback
     - Background sync queue with automatic retry

     5. Authentication (Future Enhancement)

     Phase 1 (Current): Keep existing API key in environment variable

     Phase 2 (Production): Implement proper auth
     - HTTP-only cookies with CSRF tokens
     - Or WebAuthn/FIDO2 for passwordless biometric auth

     ---
     Critical Implementation Files

     New Frontend Files
     ┌─────────────────────────────────────┬────────────────────────────────────────┐
     │                File                 │                Purpose                 │
     ├─────────────────────────────────────┼────────────────────────────────────────┤
     │ web/src/routes/(app)/+layout.svelte │ Main app layout with bottom navigation │
     ├─────────────────────────────────────┼────────────────────────────────────────┤
     │ web/src/lib/stores/split.ts         │ Core split state management            │
     ├─────────────────────────────────────┼────────────────────────────────────────┤
     │ web/src/lib/stores/offline.ts       │ Online/offline state & detection       │
     ├─────────────────────────────────────┼────────────────────────────────────────┤
     │ web/src/lib/services/api/client.ts  │ Type-safe API client base              │
     ├─────────────────────────────────────┼────────────────────────────────────────┤
     │ web/src/service-worker.ts           │ Background sync, caching strategies    │
     ├─────────────────────────────────────┼────────────────────────────────────────┤
     │ web/src/routes/split/+page.svelte   │ Main split creation wizard             │
     ├─────────────────────────────────────┼────────────────────────────────────────┤
     │ vite.config.ts                      │ PWA configuration, Workbox strategies  │
     └─────────────────────────────────────┴────────────────────────────────────────┘
     Backend Files (Minimal Changes)
     ┌───────────────────────┬────────────────────────────────────────────┐
     │         File          │                  Changes                   │
     ├───────────────────────┼────────────────────────────────────────────┤
     │ api/src/core/cache.py │ Extend TTL for PWA patterns (optional)     │
     ├───────────────────────┼────────────────────────────────────────────┤
     │ api/src/main.py       │ No changes required (API is well-designed) │
     └───────────────────────┴────────────────────────────────────────────┘
     ---
     Performance Targets
     ┌──────────────────────────┬─────────┬─────────┐
     │          Metric          │ Target  │ Maximum │
     ├──────────────────────────┼─────────┼─────────┤
     │ First Contentful Paint   │ < 1.5s  │ 2s      │
     ├──────────────────────────┼─────────┼─────────┤
     │ Largest Contentful Paint │ < 2.5s  │ 3s      │
     ├──────────────────────────┼─────────┼─────────┤
     │ Time to Interactive      │ < 3s    │ 5s      │
     ├──────────────────────────┼─────────┼─────────┤
     │ Initial JS Bundle        │ < 100KB │ 200KB   │
     ├──────────────────────────┼─────────┼─────────┤
     │ Total Initial Load       │ < 150KB │ 250KB   │
     └──────────────────────────┴─────────┴─────────┘
     Optimization Techniques:
     - Route-based code splitting (automatic in SvelteKit)
     - Lazy loading for heavy components (QR code generator)
     - Client-side image compression before upload
     - Critical CSS inlining for above-fold content

     ---
     Implementation Phases

     Phase 1: Foundation (Weeks 1-2)

     - Initialize SvelteKit project with TypeScript
     - Configure Vite, Tailwind CSS, PWA plugin
     - Set up project structure and basic routing
     - Implement API client base class
     - Create receipt upload flow
     - Test OCR integration

     Phase 2: Core Features (Weeks 3-4)

     - Implement split calculation UI
     - Add person management and item assignment
     - Add tax/tip adjustment
     - Implement local storage (IndexedDB)
     - Basic offline detection and indicators
     - Share link generation

     Phase 3: Offline-First (Weeks 5-6)

     - Implement Background Sync API
     - Create offline queue system
     - Client-side split calculation
     - Service worker strategies
     - Offline indicators and testing
     - Push notification support

     Phase 4: Polish & Performance (Weeks 7-8)

     - Bundle optimization and code splitting
     - Image optimization pipeline
     - Loading states and error boundaries
     - Performance testing and optimization
     - Accessibility audit (WCAG 2.1 AA)

     Phase 5: Advanced Features (Weeks 9-10)

     - WebAuthn biometric authentication (optional)
     - Enhanced security headers
     - Rate limiting (client-side)
     - Feature flags system
     - Onboarding flow

     ---
     Migration Strategy

     Parallel Development (Recommended):
     - Keep existing Streamlit app functional during development
     - Build new SvelteKit frontend in /web directory
     - Run both in parallel via Docker Compose
     - Gradual traffic redirect via feature flags

     Cutover Plan:
     - Week 1-4: Parallel development, internal testing
     - Week 5-6: Beta testing at /web route
     - Week 7-8: Gradual rollout (10% → 50% → 100%)
     - Week 9-10: Full migration, deprecate Streamlit

     ---
     Risk Mitigation
     ┌───────────────────────────────┬──────────────────────────────────────────────┐
     │             Risk              │                  Mitigation                  │
     ├───────────────────────────────┼──────────────────────────────────────────────┤
     │ Background Sync not supported │ Fallback to manual sync on next online event │
     ├───────────────────────────────┼──────────────────────────────────────────────┤
     │ IndexedDB quota exceeded      │ Implement LRU eviction, data cleanup         │
     ├───────────────────────────────┼──────────────────────────────────────────────┤
     │ OCR API downtime              │ Queue requests, clear error messaging        │
     ├───────────────────────────────┼──────────────────────────────────────────────┤
     │ iOS PWA limitations           │ Extensive iOS testing, provide fallbacks     │
     ├───────────────────────────────┼──────────────────────────────────────────────┤
     │ Scope creep                   │ Strict phase boundaries, MVP mindset         │
     └───────────────────────────────┴──────────────────────────────────────────────┘
     ---
     Verification Plan

     Performance Testing

     - Run Lighthouse audit (target: 90+ all categories)
     - Test on real devices (iOS Safari, Chrome Mobile)
     - Bundle size analysis (target: < 200KB initial)
     - API response time < 500ms (p95)

     Functionality Testing

     - Receipt upload and OCR processing
     - Split calculation end-to-end
     - Offline mode: view existing splits
     - Offline mode: queue receipt upload
     - Background sync triggers when online
     - Share link generation and viewing
     - PWA install and launch from home screen

     Compatibility Testing

     - iOS 15+ Safari
     - Android Chrome
     - Desktop Chrome/FireFox/Safari
     - Screen reader accessibility

     ---
     Next Steps

     Upon approval:

     1. Invoke superpowers:writing-plans skill to create detailed implementation plan
     2. Create /web directory and initialize SvelteKit project
     3. Set up Vite, PWA plugin, and project structure
     4. Begin Phase 1 implementation tasks

     ---
     References

     Existing Files to Reference:
     - api/src/main.py:1 - Existing FastAPI endpoints (keep as-is)
     - api/src/core/cache.py:1 - Current caching patterns (extend for PWA)
     - api/src/services/openrouter_ocr.py:1 - Async OCR service (reuse directly)

     2026 PWA Trends (from research):
     - Mobile-first is now standard, not optional
     - Background Sync API for offline operations
     - WebAuthn/FIDO2 for biometric authentication
     - Code splitting, lazy loading, intelligent caching
     - Progressive enhancement for older devices
