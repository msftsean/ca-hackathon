# Tasks: Cross-Agency Knowledge Hub (006)

**Input**: Design documents from `/specs/006-cross-agency-knowledge-hub/`
**Prerequisites**: plan.md ✅, spec.md ✅, data-model.md ✅, contracts/ ✅
**Accelerator**: 006 — Cross-Agency Knowledge Hub (GovOps)
**Pipeline**: Search orchestrator (federated search with permission-aware access control)

---

## Phase 1: Core Infrastructure

**Purpose**: Project scaffolding, configuration, domain models, and mock services

- [ ] **T-001** [S] **Settings & Configuration**
  Create `accelerators/006-cross-agency-knowledge-hub/backend/app/config.py` with pydantic-settings `Settings` class.
  - Env vars: `USE_MOCK_SERVICES`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_KEY`, `LOG_LEVEL`
  - Default `USE_MOCK_SERVICES=true`
  - **Acceptance**: `Settings()` loads from `.env`; mock mode is default
  - **Complexity**: S

- [ ] **T-002** [S] **FastAPI App & Health Endpoint** *(depends on T-001)*
  Create `accelerators/006-cross-agency-knowledge-hub/backend/app/main.py` with FastAPI app.
  - CORS middleware
  - `GET /health` → `{"status": "ok", "accelerator": "006-cross-agency-knowledge-hub", "mode": "mock|live"}`
  - Lifespan handler
  - **Acceptance**: `uvicorn` starts; `/health` returns 200
  - **Complexity**: S

- [ ] **T-003** [P] [L] **Pydantic v2 Domain Models**
  Create `accelerators/006-cross-agency-knowledge-hub/backend/app/models.py` with all domain entities:
  - `SearchQuery` (id, query_text, user_id, agency_id, filters: dict, include_cross_refs: bool, timestamp)
  - `Document` (id, title, content_summary, agency_id, classification: public|internal|confidential, tags, published_date, source_url, relevance_score)
  - `AgencyPermission` (id, user_id, agency_id, access_level: read|write|admin, granted_at, expires_at)
  - `CrossReference` (id, source_doc_id, target_doc_id, relationship_type: references|supersedes|implements|conflicts, confidence_score, detected_by)
  - `Expert` (id, name, agency_id, specializations: list, contact_email, availability_status)
  - `SearchResult` / `SearchResponse` for API
  - **Acceptance**: All models validate; classification and access_level enums enforced
  - **Complexity**: L

- [ ] **T-004** [P] [M] **Mock Service with Realistic Data** *(depends on T-003)*
  Create `accelerators/006-cross-agency-knowledge-hub/backend/app/mock_service.py` with:
  - Sample documents across 10+ agencies (policy memos, guidelines, reports)
  - Agency permission matrix (user → agency access mappings)
  - Pre-computed cross-references between related documents
  - Expert directory with specializations
  - Mock search index with relevance scoring
  - **Acceptance**: Mock returns permission-filtered results; cross-references included
  - **Complexity**: M

**Checkpoint**: Core infrastructure ready — app starts, models validate, mock data available

---

## Phase 2: Agent Pipeline

**Purpose**: Implement the federated search orchestrator with permission-aware access control

- [ ] **T-005** [M] **Search Query Processor** *(depends on T-003, T-004)*
  Create `accelerators/006-cross-agency-knowledge-hub/backend/app/agents/query_processor.py`:
  - Query parsing and intent detection (keyword search, semantic search, expert lookup)
  - Filter extraction (agency, date range, classification, document type)
  - Query expansion (synonyms, related terms for government jargon)
  - User context resolution (who is searching, their permissions)
  - Mock mode: keyword matching; Live mode: Azure OpenAI + Azure AI Search
  - **Acceptance**: Parses 5+ query types; filters extracted; user context resolved
  - **Complexity**: M

- [ ] **T-006** [M] **Permission Filter Engine** *(depends on T-005)*
  Create `accelerators/006-cross-agency-knowledge-hub/backend/app/agents/permission_engine.py`:
  - Resolve user's agency permissions before search
  - Filter results by access level (public always visible, internal/confidential gated)
  - Cross-agency access enforcement (user sees only permitted agencies)
  - Audit log for access attempts (including denied)
  - **Acceptance**: Unauthorized documents never returned; audit log records all access attempts
  - **Complexity**: M

- [ ] **T-007** [M] **Federated Search Engine** *(depends on T-006)*
  Create `accelerators/006-cross-agency-knowledge-hub/backend/app/agents/search_engine.py`:
  - Search across multiple agency document stores
  - Relevance scoring and result ranking
  - Cross-reference detection between result documents
  - Result deduplication (same doc in multiple indices)
  - Snippet generation with keyword highlighting
  - **Acceptance**: Returns ranked, deduplicated results; cross-references detected; snippets generated
  - **Complexity**: M

- [ ] **T-008** [M] **Pipeline Orchestrator** *(depends on T-005, T-006, T-007)*
  Create `accelerators/006-cross-agency-knowledge-hub/backend/app/pipeline.py`:
  - Wire QueryProcessor → PermissionFilter → FederatedSearch
  - Result aggregation and formatting
  - Error handling (partial results on index failure)
  - Logging with correlation IDs
  - Mock/live mode switching
  - **Acceptance**: Full pipeline returns permission-filtered, ranked results; partial failure handled
  - **Complexity**: M

- [ ] **T-009** [M] **Search API Endpoint** *(depends on T-008)*
  Create `accelerators/006-cross-agency-knowledge-hub/backend/app/routes.py`:
  - `POST /api/search` — federated search with filters and permissions
  - `GET /api/documents/{id}` — document detail (permission-gated)
  - Request validation, error responses
  - Pagination support (offset + limit)
  - **Acceptance**: Search returns filtered results; document detail gated; pagination works
  - **Complexity**: M

**Checkpoint**: MVP complete — federated search with permission-aware filtering works end-to-end in mock mode

---

### 🎯 MVP CUTLINE

> **Everything above this line constitutes the MVP.** The search orchestrator handles federated search across agencies with permission-aware filtering, relevance ranking, and cross-reference detection in mock mode. Users can search and receive only the documents they're authorized to view.

---

## Phase 3: Domain Logic

**Purpose**: Expert routing, cross-references, advanced search, and agency management

- [ ] **T-010** [M] **Expert Routing Endpoint** *(depends on T-008)*
  Add `GET /api/experts` and `GET /api/experts/{id}` to routes:
  - Search experts by specialization and agency
  - Availability status filtering
  - Expertise relevance matching to search queries
  - **Acceptance**: Expert search returns relevant results; availability filtered
  - **Complexity**: M

- [ ] **T-011** [M] **Cross-Reference Detection Endpoint** *(depends on T-007)*
  Add `POST /api/search/cross-references` to routes:
  - Given a document, find all cross-referenced documents
  - Relationship type classification (references, supersedes, implements, conflicts)
  - Confidence scoring for detected references
  - **Acceptance**: Cross-references detected with relationship types; confidence scored
  - **Complexity**: M

- [ ] **T-012** [M] **Agency Permission Management Service** *(depends on T-006)*
  Create `accelerators/006-cross-agency-knowledge-hub/backend/app/services/permission_service.py`:
  - CRUD for agency permissions
  - Permission expiration handling
  - Bulk permission grants (all users in an agency)
  - Permission audit report
  - **Acceptance**: Permissions created/revoked; expiration enforced; audit available
  - **Complexity**: M

- [ ] **T-013** [S] **Document Metadata Service** *(depends on T-004)*
  Create `accelerators/006-cross-agency-knowledge-hub/backend/app/services/document_service.py`:
  - Document classification management
  - Tag management and search
  - Document freshness tracking (stale document alerts)
  - **Acceptance**: Classification updated; tags searchable; stale documents flagged
  - **Complexity**: S

---

## Phase 4: Testing & Evals

**Purpose**: Comprehensive testing, evaluation suite, and E2E validation

- [ ] **T-014** [P] [S] **Unit Tests — Health & Config**
  Create `accelerators/006-cross-agency-knowledge-hub/backend/tests/test_health.py`:
  - Health endpoint returns 200
  - Settings load defaults correctly
  - **Acceptance**: All tests pass
  - **Complexity**: S

- [ ] **T-015** [P] [M] **Unit Tests — Pipeline & Search**
  Create `accelerators/006-cross-agency-knowledge-hub/backend/tests/test_pipeline.py`:
  - Query processor parses queries correctly
  - Permission filter blocks unauthorized documents
  - Search engine returns ranked results
  - Pipeline processes end-to-end query
  - **Acceptance**: 12+ test cases; permission enforcement verified
  - **Complexity**: M

- [ ] **T-016** [P] [S] **Unit Tests — Domain Models**
  Create `accelerators/006-cross-agency-knowledge-hub/backend/tests/test_models.py`:
  - All Pydantic models validate correct data
  - Access level and classification enums enforced
  - **Acceptance**: All models tested for valid and invalid inputs
  - **Complexity**: S

- [ ] **T-017** [M] **Eval Test Suite — Search & Permissions**
  Create `accelerators/006-cross-agency-knowledge-hub/backend/tests/test_evals.py`:
  - 15+ eval cases: query + user → expected filtered results
  - Permission enforcement: 100% (must never leak unauthorized docs)
  - Search relevance: top-3 results include expected document ≥80% of time
  - Cross-reference detection accuracy: ≥85%
  - **Acceptance**: Permission enforcement perfect; relevance acceptable
  - **Complexity**: M

- [ ] **T-018** [M] **Playwright E2E Tests**
  Create `accelerators/006-cross-agency-knowledge-hub/frontend/tests/e2e/search.spec.ts`:
  - User searches → receives filtered results
  - Document detail view works
  - Expert search returns relevant experts
  - Cross-references displayed for documents
  - **Acceptance**: E2E tests pass against dev server
  - **Complexity**: M

---

## Dependencies & Execution Order

```
T-001 → T-002 → T-005 → T-006 → T-007 → T-008 → T-009 (critical path)
T-001 → T-003 → T-004 (parallel with T-002)
T-008 → T-010
T-007 → T-011
T-006 → T-012
T-004 → T-013
T-009 → T-014, T-015, T-016, T-017, T-018 (all tests parallel)
```

### Parallel Opportunities

- T-003 and T-002 can run in parallel
- T-010, T-011, T-012, T-013 can run in parallel after MVP
- All test tasks (T-014 through T-018) can run in parallel

---

## Notes

- All search must comply with `shared/constitution.md` boundaries
- Permission enforcement is **security-critical** — must never leak unauthorized documents
- Access control must comply with CCPA/CPRA and agency data sharing agreements
- Mock mode must work without Azure credentials or Azure AI Search
- Cross-agency search must respect inter-agency data sharing MOUs
- 200+ agencies expected at scale — mock data should represent diversity
