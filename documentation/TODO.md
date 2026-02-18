# Project TODO & Roadmap

## Overview

This document tracks active development tasks, technical debt, and future roadmap for the Split Bill application.

**Last Updated**: February 18, 2026
**Current Phase**: Maintenance & Enhancement
**Status**: Production Ready with SuperDesign UI

---

## Quick Navigation

- [Active Tasks](#active-tasks) - Currently in progress
- [Completed](#completed) - Recently completed work
- [Backlog](#backlog) - Prioritized upcoming work
- [Technical Debt](#technical-debt) - Refactoring and improvements

---

## Active Tasks

### 🔥 High Priority

- [ ] **TEST-001**: Expand test coverage to 90%+
  - **Status**: In Progress
  - **Current**: ~50% coverage
  - **Target**: >90%

### 📋 Medium Priority

- [ ] **DOC-001**: Update architecture docs for SvelteKit frontend
  - **Status**: Open
  - **Details**: Reflect new PWA frontend architecture

### 📝 Low Priority

- [ ] **FEAT-001**: Add ProgressCircle component
- [ ] **FEAT-002**: Add animation polish to UI transitions

---

## Completed

### February 2026

- [x] **SuperDesign UI Implementation**: All 6 pages complete (25/25 checks pass)
  - Dashboard, History, Create Split, Receipt, Settings, Split Detail
- [x] **Loading state fixes**: Resolved stuck loading in Receipt and Settings pages
- [x] **UI Components**: LoadingSpinner, SkeletonLoader created
- [x] **Documentation cleanup**: Removed outdated markdown files

### January 2026

- [x] **SvelteKit Migration**: Migrated from Streamlit to SvelteKit PWA
- [x] **Offline-first architecture**: IndexedDB, Background Sync
- [x] **Backend database**: PostgreSQL with SQLAlchemy
- [x] **API extensions**: Currency, Groups, Templates, Payments, Analytics

---

## Backlog

### Phase 10: Advanced Features 🚀

#### Analytics & Business Intelligence

- [ ] **FEAT-101**: Add usage analytics dashboard
  - Track popular items, average split size, peak usage times
  - Export data to CSV/JSON
  - Visual charts and graphs

- [ ] **FEAT-102**: Implement receipt history
  - Store processed receipts per user (if auth added)
  - Search and filter past splits
  - Re-run calculations on historical data

#### Advanced OCR & AI Features

- [ ] **FEAT-201**: Support multiple receipt formats
  - Restaurant receipts
  - Grocery receipts
  - Gas station receipts
  - International receipts (different currencies)

- [ ] **FEAT-202**: Manual receipt correction UI
  - Allow users to edit OCR mistakes
  - Add missing items
  - Adjust extracted prices
  - Save corrections for ML training

- [ ] **FEAT-203**: Multi-language OCR support
  - Spanish receipts
  - French receipts
  - Chinese receipts
  - Configurable language per request

- [ ] **FEAT-204**: Item categorization
  - Auto-categorize items (Food, Drinks, Tax, etc.)
  - Spending insights by category
  - Category-based splitting rules

#### Social & Collaboration Features

- [ ] **FEAT-301**: Real-time collaboration
  - WebSocket support for live updates
  - Multiple users editing same split
  - Conflict resolution

- [ ] **FEAT-302**: Comments on splits
  - Add notes to shared splits
  - @mentions for people
  - Notification system

- [ ] **FEAT-303**: Payment integration
  - Venmo integration
  - PayPal integration
  - Generate payment links
  - Track payment status

#### User Experience

- [ ] **FEAT-401**: Mobile app (React Native/Flutter)
  - Native mobile experience
  - Camera integration for quick capture
  - Push notifications

- [ ] **FEAT-402**: Offline mode
  - Process receipts without internet
  - Queue for later upload
  - Local storage of splits

- [ ] **FEAT-403**: Dark/light theme toggle
  - User preference persistence
  - System theme detection
  - Smooth transitions

- [ ] **FEAT-404**: Keyboard shortcuts
  - Quick navigation between steps
  - Hotkeys for common actions
  - Accessibility improvements

#### Enterprise Features

- [ ] **FEAT-501**: Multi-currency support
  - Currency detection from receipt
  - Real-time exchange rates
  - Multi-currency splits

- [ ] **FEAT-502**: User accounts and authentication
  - JWT-based auth
  - OAuth (Google, Apple)
  - User profiles
  - Split history per user

- [ ] **FEAT-503**: Groups and recurring splits
  - Create friend groups
  - Save group configurations
  - Recurring bill templates
  - Group expense reports

- [ ] **FEAT-504**: Webhook integrations
  - Zapier integration
  - Custom webhooks
  - Event notifications

### Phase 11: Performance & Scale ⚡

- [ ] **PERF-101**: Implement distributed rate limiting
  - Move from in-memory to Redis-based
  - Support horizontal scaling

- [ ] **PERF-102**: Add database layer
  - PostgreSQL for structured data
  - Migrate from MinIO JSON to proper DB
  - Query optimization

- [ ] **PERF-103**: CDN integration
  - CloudFlare or AWS CloudFront
  - Image optimization
  - Global edge caching

- [ ] **PERF-104**: Background job processing
  - Celery for async tasks
  - OCR queue management
  - Retry logic for failed jobs

### Phase 12: Security & Compliance 🔒

- [ ] **SEC-101**: Implement proper user authentication
  - JWT with refresh tokens
  - Password hashing (bcrypt)
  - Session management

- [ ] **SEC-102**: Add audit logging
  - Track all data access
  - Immutable audit trail
  - Compliance reporting

- [ ] **SEC-103**: Data retention policies
  - Automatic data deletion
  - GDPR compliance
  - User data export

- [ ] **SEC-104**: Penetration testing
  - Security audit
  - Vulnerability assessment
  - Fix critical issues

---

## Technical Debt

### Code Quality

- [ ] **DEBT-001**: Fix LSP/type errors
  - **File**: api/src/main.py
  - **Issues**:
    - Line 559: bytes | None type mismatch
    - Line 565: bytes | None type mismatch
  - **Priority**: High
  - **Effort**: Small

- [ ] **DEBT-002**: Add comprehensive type hints
  - **Scope**: All service files
  - **Priority**: Medium
  - **Effort**: Medium
  - **Details**: Currently partial typing in some modules

- [ ] **DEBT-003**: Refactor large functions
  - **File**: api/src/main.py
  - **Functions**:
    - calculate_split_endpoint (lines 400-497)
    - upload_receipt (lines 527-583)
  - **Priority**: Medium
  - **Effort**: Medium

### Testing

- [ ] **DEBT-101**: Achieve >80% test coverage
  - **Current**: ~5% (only test_sample.py)
  - **Target**: >80%
  - **Priority**: High
  - **Effort**: Large

- [ ] **DEBT-102**: Add integration tests
  - API endpoint testing
  - OCR service mocking
  - Redis integration tests
  - MinIO integration tests

- [ ] **DEBT-103**: Add end-to-end tests
  - Full user workflow
  - Browser automation (Playwright)
  - Critical path testing

### Infrastructure

- [ ] **DEBT-201**: Improve error handling
  - Custom exception classes
  - Consistent error responses
  - Better error messages

- [ ] **DEBT-202**: Add logging correlation IDs
  - Request tracing
  - Distributed logging
  - Debug support

- [ ] **DEBT-203**: Optimize Docker images
  - Multi-stage builds
  - Smaller image sizes
  - Security scanning

---

## Phase History

### ✅ Phase 1: Modular Architecture & Code Quality

**Status**: Complete
**Date**: Completed

**Deliverables**:
- [x] Created modular architecture with clear separation of concerns
- [x] Implemented pre-commit hooks
- [x] Enhanced Makefile with development commands
- [x] Fixed duplicate functions
- [x] Improved code organization

**Outcome**: Professional, maintainable codebase

### ✅ Phase 2: Security Hardening

**Status**: Complete
**Date**: Completed

**Deliverables**:
- [x] API Key authentication with Bearer tokens
- [x] Comprehensive rate limiting (10/30/100 requests per minute)
- [x] Security headers (CSP, XSS Protection, Frame Options)
- [x] Input validation middleware (10MB request limit)

**Outcome**: Enterprise-grade security

### ✅ Phase 3: Performance & Caching

**Status**: Complete
**Date**: Completed

**Deliverables**:
- [x] Redis caching integration
- [x] Intelligent cache strategies (1hr/30min/24hr TTL)
- [x] Graceful Redis fallbacks
- [x] 3-5x performance improvement

**Outcome**: 70-90% cache hit rates

### ✅ Phase 4: Production Integration

**Status**: Complete
**Date**: Completed

**Deliverables**:
- [x] Unified API architecture
- [x] Modern FastAPI patterns (APIRouter)
- [x] Docker and Makefile updates
- [x] Comprehensive documentation

**Outcome**: Production-ready application

### ✅ Phase 5: Frontend Integration & Testing

**Status**: Complete
**Date**: Completed

**Deliverables**:
- [x] Streamlit frontend integration
- [x] End-to-end workflow testing
- [x] Error handling improvements
- [x] Production testing validation

**Outcome**: Full frontend-backend integration

### ✅ Phase 6: Testing & Quality Assurance

**Status**: Complete
**Date**: Completed

**Deliverables**:
- [x] Test framework setup (pytest)
- [x] Sample tests created
- [x] Code quality tools (Black, isort, Ruff, MyPy)
- [x] Pre-commit hooks

**Outcome**: Automated quality gates

### ✅ Phase 7: Monitoring & Observability

**Status**: Complete
**Date**: Completed

**Deliverables**:
- [x] Health check endpoints
- [x] Metrics collection
- [x] Structured logging
- [x] Monitoring data tracking

**Outcome**: Production observability

### ✅ Phase 8: User Experience Enhancements

**Status**: Complete
**Date**: Completed

**Deliverables**:
- [x] Mobile-responsive design
- [x] Accessibility compliance (WCAG 2.1 AA)
- [x] Dark theme
- [x] Keyboard navigation
- [x] Error handling improvements

**Outcome**: Enterprise-grade UX

### ✅ Phase 9: Recent Fixes & Improvements

**Status**: Complete
**Date**: Completed

**Deliverables**:
- [x] Fixed Streamlit configuration issues
- [x] Fixed API endpoint 404 errors
- [x] Streamlined UI (removed light mode toggle)
- [x] Enhanced API router structure

**Outcome**: Stable, polished application

---

## Roadmap

### Short Term (Next 3 Months)

**Focus**: Stability and core improvements

1. **Fix technical debt**
   - Resolve type errors
   - Achieve 80% test coverage
   - Improve error handling

2. **Documentation**
   - Complete all architecture docs
   - API versioning strategy
   - Deployment runbooks

3. **Monitoring**
   - Prometheus metrics
   - Alerting setup
   - Performance dashboards

### Medium Term (3-6 Months)

**Focus**: Feature expansion

1. **Core features**
   - Manual receipt correction
   - Receipt history
   - Multi-currency support

2. **User experience**
   - Mobile app (MVP)
   - Offline mode
   - Payment integration (Venmo)

3. **Scale**
   - Database migration
   - Distributed rate limiting
   - Background jobs

### Long Term (6-12 Months)

**Focus**: Platform and enterprise

1. **Platform**
   - User accounts and auth
   - Groups and recurring splits
   - Webhook integrations

2. **Enterprise**
   - Team management
   - Advanced analytics
   - Compliance features

3. **AI/ML**
   - Improved OCR accuracy
   - Auto-categorization
   - Spending insights

---

## Task Template

When adding new tasks, use this format:

```markdown
- [ ] **TASK-ID**: Brief description
  - **Assigned**: @username or TBD
  - **Status**: Open | In Progress | Blocked | Complete
  - **Priority**: Critical | High | Medium | Low
  - **Effort**: Small | Medium | Large
  - **Impact**: Description of business/technical impact
  - **Dependencies**: List of blocking tasks
  - **Details**: Detailed description
  - **Acceptance Criteria**:
    - [ ] Criterion 1
    - [ ] Criterion 2
```

---

## Contributing

### How to Pick Up Tasks

1. Comment on the task with "Taking this"
2. Update status to "In Progress"
3. Create a feature branch: `git checkout -b feature/TASK-ID`
4. Work on the task
5. Run quality checks: `make check-all`
6. Submit PR with task ID in title: "[TASK-001] Fix type errors"

### Task Priority Guide

- **Critical**: Blocking production, security issue, or data loss risk
- **High**: Significant user impact or technical debt
- **Medium**: Nice to have, improvements
- **Low**: Future ideas, exploratory

### Definition of Done

- [ ] Code implemented and tested
- [ ] All quality checks pass (`make check-all`)
- [ ] Documentation updated
- [ ] PR reviewed and approved
- [ ] Deployed to staging
- [ ] Tested in staging environment

---

## Recent Updates

### February 2026

- **Added**: Comprehensive documentation (ARCHITECTURE.md, API.md, TODO.md, etc.)
- **Identified**: Type errors in main.py (API-001)
- **Identified**: Need for expanded test coverage (TEST-001)

---

## Related Documents

- [Architecture Overview](ARCHITECTURE.md) - System architecture
- [API Documentation](API.md) - API reference
- [Development Guide](DEVELOPMENT.md) - Development setup
- [Operations Guide](OPERATIONS.md) - Deployment and monitoring
- [Architecture Decisions](ADR/) - Design decision records
