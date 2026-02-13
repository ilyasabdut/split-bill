# Architecture Decision Records (ADR)

This directory contains Architecture Decision Records (ADRs) that document significant architectural decisions made in the Split Bill project.

## What is an ADR?

An Architecture Decision Record (ADR) captures an important architectural decision made along with its context and consequences. ADRs help teams:

- Understand why decisions were made
- Onboard new team members faster
- Avoid revisiting decisions unnecessarily
- Document the evolution of the system

## ADR Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [001](001-fastapi-framework.md) | FastAPI as Backend Framework | ✅ Accepted | 2026-02 |
| [002](002-redis-caching.md) | Redis for Caching | ✅ Accepted | 2026-02 |
| [003](003-minio-storage.md) | MinIO for Object Storage | ✅ Accepted | 2026-02 |
| [004](004-streamlit-frontend.md) | Streamlit for Frontend | ✅ Accepted | 2026-02 |
| [005](005-openrouter-ocr.md) | OpenRouter for OCR | ✅ Accepted | 2026-02 |
| [006](006-api-key-authentication.md) | API Key Authentication | ✅ Accepted | 2026-02 |
| [007](007-docker-containerization.md) | Docker for Containerization | ✅ Accepted | 2026-02 |

## Status Legend

- **Proposed**: Under discussion, not yet decided
- **Accepted**: Decision made and implemented
- **Deprecated**: Decision no longer relevant
- **Superseded**: Replaced by a newer ADR

## Creating New ADRs

Use the [template](template.md) when creating new ADRs:

1. Copy `template.md` to `XXX-short-title.md`
2. Fill in all sections
3. Set status to "Proposed"
4. Create PR for review
5. After acceptance, update status to "Accepted"

## Related Documentation

- [Architecture Overview](../ARCHITECTURE.md)
- [Development Guide](../DEVELOPMENT.md)
- [TODO/Roadmap](../TODO.md)

---

**Note**: ADRs are immutable once accepted. If a decision changes, create a new ADR that supersedes the old one.
