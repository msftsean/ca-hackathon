# Implementation Plan: Cross-Agency Knowledge Hub

**Branch**: `006-cross-agency-knowledge-hub` | **Date**: 2024-12-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-cross-agency-knowledge-hub/spec.md`

## Summary

Permission-aware federated search system enabling state employees to discover documents, policies, and subject matter experts across 200+ California state agencies. System leverages Azure AI Search hybrid search (BM25 + semantic), Azure Entra ID for agency-scoped access control, cross-reference detection for policy alignment, expert routing for collaboration, and immutable audit logging for compliance with California Public Records Act.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5+ (frontend)  
**Primary Dependencies**: FastAPI, Pydantic v2, Azure AI Search SDK, Azure Entra ID (MSAL), Azure OpenAI SDK, React 18, Vite, Tailwind CSS  
**Storage**: Azure AI Search (document indices), async SQLite (audit logs, cross-references, expert profiles), Azure Blob Storage (document originals if needed)  
**Testing**: pytest (backend), vitest (frontend), Playwright (E2E)  
**Target Platform**: Linux containers (Docker), Azure Container Apps  
**Project Type**: Web application with federated search orchestration and permission-aware result filtering  
**Performance Goals**: <3 second search response time (p95), 500 concurrent users, <300ms permission check, progressive result rendering  
**Constraints**: WCAG 2.1 AA compliance, California Public Records Act audit requirements, Envision 2026 Goal 4 (cross-agency collaboration), zero unauthorized access  
**Scale/Scope**: 200+ state agencies, 100,000+ documents, 10,000+ state employees, 500 concurrent searches

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Security & Compliance Requirements** (Constitution-driven):
- ✅ Azure Entra ID authentication with agency-scoped group membership (primary authorization mechanism)
- ✅ Document-level classification enforcement (public, internal, confidential, restricted)
- ✅ Row-level security on search results based on user permissions (permission-aware filtering)
- ✅ TLS 1.3 for all data in transit
- ✅ Immutable audit logging with 7-year retention per California Public Records Act
- ✅ Zero unauthorized access requirement (enforced by permission cache + real-time validation)
- ✅ WCAG 2.1 AA accessibility for search interface and results display
- ✅ Query sanitization to prevent injection attacks and PII leakage in logs
- ✅ Audit trail supports CPRA requests (searchable, exportable, privacy-preserving)
- ✅ No PII storage in search queries (sanitized before logging)

**Regulatory Alignment**:
- Primary: California Public Records Act (audit logging, transparency)
- Secondary: Envision 2026 Goal 4 (cross-agency collaboration and knowledge sharing)
- Framework: California Information Practices Act (user privacy in audit logs)
- Governance: CDT Security Standards (access control, encryption, audit trails)

## Project Structure

### Documentation (this feature)

```text
specs/006-cross-agency-knowledge-hub/
├── spec.md              # Feature specification (COMPLETE)
├── plan.md              # This file (COMPLETE)
├── data-model.md        # Entity and relationship definitions (COMPLETE)
├── research.md          # Phase 0: Azure AI Search evaluation, permission model design
├── contracts/           # Phase 1: Search API contracts, permission schemas
├── quickstart.md        # Phase 1: Local dev setup, sample document indices
└── tasks.md             # Phase 2: Implementation tasks (generated separately)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── search_query.py             # SearchQuery entity
│   │   ├── document.py                 # Document entity
│   │   ├── agency_permission.py        # AgencyPermission entity
│   │   ├── cross_reference.py          # CrossReference entity
│   │   ├── expert.py                   # Expert entity
│   │   └── audit_log.py                # AuditLog entity
│   ├── services/
│   │   ├── search_orchestrator.py      # Federated search coordination
│   │   ├── permission_engine.py        # Agency-scoped access control
│   │   ├── result_filter.py            # Permission-aware result filtering
│   │   ├── cross_reference_detector.py # Document relationship analysis
│   │   ├── expert_finder.py            # Subject matter expert identification
│   │   ├── query_sanitizer.py          # Query sanitization and validation
│   │   ├── audit_logger.py             # Immutable audit trail
│   │   └── analytics_tracker.py        # Search analytics and metrics
│   ├── api/
│   │   ├── search_routes.py            # Search, faceting, suggestions endpoints
│   │   ├── document_routes.py          # Document retrieval, access control
│   │   ├── expert_routes.py            # Expert search, contact endpoints
│   │   ├── audit_routes.py             # Audit log query endpoints
│   │   └── admin_routes.py             # Index management, analytics
│   ├── storage/
│   │   ├── ai_search_client.py         # Azure AI Search client
│   │   ├── db_client.py                # Async SQLite client
│   │   └── blob_storage.py             # Azure Blob Storage (optional)
│   ├── auth/
│   │   ├── entra_id.py                 # Azure Entra ID integration
│   │   ├── permission_cache.py         # Permission caching (5-minute TTL)
│   │   └── rbac.py                     # Role-based access control
│   └── indexing/
│       ├── document_indexer.py         # Document ingestion to AI Search
│       ├── webhook_handler.py          # Document change notifications
│       └── batch_indexer.py            # Bulk document indexing
└── tests/
    ├── unit/
    │   ├── test_search_orchestrator.py
    │   ├── test_permission_engine.py
    │   ├── test_result_filter.py
    │   ├── test_cross_reference_detector.py
    │   └── test_query_sanitizer.py
    ├── integration/
    │   ├── test_search_workflow.py
    │   ├── test_permission_enforcement.py
    │   └── test_audit_trail.py
    └── contract/
        ├── test_search_api.py
        └── test_permission_contracts.py

frontend/
├── src/
│   ├── components/
│   │   ├── SearchBar.tsx               # Search input with suggestions
│   │   ├── SearchResults.tsx           # Result list with pagination
│   │   ├── ResultCard.tsx              # Individual result display
│   │   ├── FacetFilters.tsx            # Agency, type, date filters
│   │   ├── CrossReferences.tsx         # Related documents display
│   │   ├── ExpertCard.tsx              # Expert recommendation display
│   │   ├── DocumentPreview.tsx         # Document content preview
│   │   └── AuditLogViewer.tsx          # Audit log query interface
│   ├── pages/
│   │   ├── SearchHome.tsx              # Main search interface
│   │   ├── SearchResults.tsx           # Search results page
│   │   ├── DocumentDetail.tsx          # Document detail view
│   │   ├── ExpertDirectory.tsx         # Expert search interface
│   │   └── AuditDashboard.tsx          # Audit log dashboard (auditor role)
│   ├── services/
│   │   ├── search-api.ts               # Search API client
│   │   ├── document-api.ts             # Document API client
│   │   ├── expert-api.ts               # Expert API client
│   │   ├── audit-api.ts                # Audit API client
│   │   └── auth-service.ts             # MSAL + Entra ID client
│   ├── hooks/
│   │   ├── useSearch.ts                # Search state management
│   │   ├── usePermissions.ts           # User permission state
│   │   ├── useDocumentAccess.ts        # Document access control
│   │   └── useAuth.ts                  # Authentication state
│   └── utils/
│       ├── query-parser.ts             # Advanced query syntax parsing
│       ├── result-highlighter.ts       # Search term highlighting
│       └── analytics.ts                # Client-side analytics tracking
└── tests/
    ├── unit/
    │   └── components/
    ├── integration/
    │   └── workflows/
    └── e2e/
        └── playwright/
            ├── search-workflow.spec.ts
            ├── permission-enforcement.spec.ts
            ├── cross-reference.spec.ts
            └── expert-contact.spec.ts

shared/
├── schemas/
│   ├── document-schema.json            # Document entity schema
│   ├── permission-schema.json          # Permission entity schema
│   └── audit-log-schema.json           # Audit log entity schema
└── config/
    ├── agency-config.json              # Agency metadata (names, IDs, hierarchy)
    └── classification-levels.json      # Document classification definitions
```

**Structure Decision**: Web application architecture selected based on:
- User-facing search interface requiring React frontend
- Federated search orchestration requiring Python backend with Azure AI Search SDK
- Permission enforcement requiring centralized backend service (cannot trust client-side filtering)
- Separation of concerns between UI (React), search orchestration (FastAPI), and AI Search engine (Azure PaaS)
- Shared configuration for agency metadata and classification levels used by both frontend and backend

## Complexity Tracking

> **No constitution violations identified. Complexity justified by cross-agency security and compliance requirements.**

| Aspect | Justification | Simpler Alternative Rejected Because |
|--------|---------------|--------------------------------------|
| Permission-aware result filtering | CPRA and security requirements mandate users only see documents they're authorized to access; cannot return all results and filter client-side | Client-side filtering exposes unauthorized document metadata in API responses; creates security vulnerability |
| Hybrid search (BM25 + semantic) | Keyword search alone misses conceptually similar documents; semantic search alone lacks precision for exact matches; hybrid provides best of both | Pure keyword search (BM25) fails on synonym/paraphrase queries; pure semantic search fails on exact term matching |
| Permission caching (5-minute TTL) | Real-time Entra ID queries for every search request add 200-500ms latency; unacceptable for 3-second p95 target | No caching violates performance requirements; longer TTL (>5 minutes) creates security window for stale permissions |
| Immutable audit trail | California Public Records Act and security monitoring require tamper-proof event logging; UPDATE/DELETE operations prohibited | Mutable logs fail compliance requirements; cannot prove integrity for legal/forensic purposes |
| Cross-reference detection | State policy alignment and best practice sharing require identifying related documents across agencies; manual discovery is infeasible at 100k+ document scale | Manual cross-referencing by employees is time-prohibitive; misses hidden connections across agencies |
| Progressive result rendering | Federated search across 200+ agencies can have variable latency; blocking on slowest index violates 3-second p95 requirement | Synchronous wait for all agencies results in worst-case latency; poor user experience |
