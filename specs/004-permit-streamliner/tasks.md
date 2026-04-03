# Tasks: Permit Streamliner (004)

**Input**: Design documents from `/specs/004-permit-streamliner/`
**Prerequisites**: plan.md ✅, spec.md ✅, data-model.md ✅, contracts/ ✅
**Accelerator**: 004 — Permit Streamliner (OPR / HCD / DCA)
**Pipeline**: 3-agent (IntakeAgent → RouterAgent → ValidationAgent)

---

## Phase 1: Core Infrastructure

**Purpose**: Project scaffolding, configuration, domain models, and mock services

- [ ] **T-001** [S] **Settings & Configuration**
  Create `accelerators/004-permit-streamliner/backend/app/config.py` with pydantic-settings `Settings` class.
  - Env vars: `USE_MOCK_SERVICES`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `AZURE_SEARCH_ENDPOINT`, `LOG_LEVEL`
  - Default `USE_MOCK_SERVICES=true`
  - **Acceptance**: `Settings()` loads from `.env`; mock mode is default
  - **Complexity**: S

- [ ] **T-002** [S] **FastAPI App & Health Endpoint** *(depends on T-001)*
  Create `accelerators/004-permit-streamliner/backend/app/main.py` with FastAPI app.
  - CORS middleware
  - `GET /health` → `{"status": "ok", "accelerator": "004-permit-streamliner", "mode": "mock|live"}`
  - Lifespan handler
  - **Acceptance**: `uvicorn` starts; `/health` returns 200
  - **Complexity**: S

- [ ] **T-003** [P] [L] **Pydantic v2 Domain Models**
  Create `accelerators/004-permit-streamliner/backend/app/models.py` with all domain entities:
  - `Applicant` (id, name, email, phone, company, license_number)
  - `Application` (id, applicant_id, project_type: residential|commercial|environmental, description, address, parcel_number, status: intake|routing|review|approved|denied, created_at)
  - `PermitRequirement` (id, permit_type, agency, description, documents_required, estimated_timeline_days, fee)
  - `Document` (id, application_id, type: site_plan|environmental_review|structural_calc|title_report, status: pending|approved|rejected)
  - `RoutingDecision` (id, application_id, agencies: list, primary_agency, routing_reason, priority)
  - `SLATracking` (id, application_id, agency, sla_days, started_at, due_at, status: on_track|at_risk|overdue)
  - API request/response models
  - **Acceptance**: All models validate; status/type enums enforced
  - **Complexity**: L

- [ ] **T-004** [P] [M] **Mock Service with Realistic Data** *(depends on T-003)*
  Create `accelerators/004-permit-streamliner/backend/app/mock_service.py` with:
  - Sample permit applications (residential ADU, commercial tenant improvement, solar install, environmental)
  - Agency directory (OPR, HCD, DCA, local planning departments)
  - Permit requirement templates by project type
  - Zoning data (sample parcels with zoning designations)
  - SLA targets by agency and permit type
  - **Acceptance**: Mock returns realistic permit data; agency routing matches project type
  - **Complexity**: M

**Checkpoint**: Core infrastructure ready — app starts, models validate, mock data available

---

## Phase 2: Agent Pipeline

**Purpose**: Implement the 3-agent pipeline for permit intake, routing, and validation

- [ ] **T-005** [M] **IntakeAgent — Project Classification** *(depends on T-003, T-004)*
  Create `accelerators/004-permit-streamliner/backend/app/agents/intake_agent.py`:
  - Project type classification (residential, commercial, environmental, mixed-use)
  - Scope detection (new construction, renovation, change of use, addition)
  - Entity extraction: address, parcel_number, project_description, square_footage
  - Complexity scoring (simple/standard/complex)
  - Mock mode: rule-based; Live mode: Azure OpenAI
  - **Acceptance**: Classifies 5+ project descriptions correctly; complexity scored
  - **Complexity**: M

- [ ] **T-006** [M] **RouterAgent — Agency Routing & Priority** *(depends on T-005)*
  Create `accelerators/004-permit-streamliner/backend/app/agents/router_agent.py`:
  - Multi-agency routing based on project type and location
  - Primary vs. secondary agency determination
  - Priority: housing (SB 35) > public safety > commercial > environmental
  - Concurrent vs. sequential review detection
  - SLA assignment based on agency and complexity
  - **Acceptance**: Routes to correct agencies for 5+ project types; SLA assigned
  - **Complexity**: M

- [ ] **T-007** [M] **ValidationAgent — Checklist & Zoning** *(depends on T-006)*
  Create `accelerators/004-permit-streamliner/backend/app/agents/validation_agent.py`:
  - Document checklist generation based on project + agency requirements
  - Zoning compatibility check (mock zoning database)
  - Completeness validation (required docs present/missing)
  - Fee estimation based on project scope
  - Response with requirements and estimated timeline
  - **Acceptance**: Generates accurate checklists; zoning check returns valid/invalid; fees estimated
  - **Complexity**: M

- [ ] **T-008** [M] **Pipeline Orchestrator** *(depends on T-005, T-006, T-007)*
  Create `accelerators/004-permit-streamliner/backend/app/pipeline.py`:
  - Wire IntakeAgent → RouterAgent → ValidationAgent
  - Application state management
  - Error handling with fallbacks
  - Logging with correlation IDs
  - Mock/live mode switching
  - **Acceptance**: Full pipeline processes application end-to-end; state persists
  - **Complexity**: M

- [ ] **T-009** [M] **Intake API Endpoint** *(depends on T-008)*
  Create `accelerators/004-permit-streamliner/backend/app/routes.py`:
  - `POST /api/intake/classify` — classify project, return routing + checklist
  - `POST /api/applications` — create application with classification results
  - Request validation, error responses
  - **Acceptance**: Classification returns agencies + checklist; application created with status
  - **Complexity**: M

**Checkpoint**: MVP complete — permit intake, agency routing, and validation checklist work end-to-end in mock mode

---

### 🎯 MVP CUTLINE

> **Everything above this line constitutes the MVP.** The 3-agent pipeline handles permit project classification, multi-agency routing, document checklist generation, and zoning validation in mock mode. Applicants can describe their project and receive a clear permit roadmap.

---

## Phase 3: Domain Logic

**Purpose**: Application management, zoning checks, SLA tracking, and document validation

- [ ] **T-010** [M] **Application Checklist Endpoint** *(depends on T-008)*
  Add `GET /api/applications/{id}/checklist` to routes:
  - Return required documents with completion status
  - Agency-specific requirements broken out
  - Missing document highlighting
  - **Acceptance**: Checklist shows required/submitted/missing per agency
  - **Complexity**: M

- [ ] **T-011** [M] **Zoning Check Endpoint** *(depends on T-004)*
  Add `GET /api/zoning/check` to routes:
  - Accept parcel_number or address → return zoning designation
  - Compatibility check with proposed project type
  - Setback, height, lot coverage constraints
  - **Acceptance**: Returns zoning for valid parcels; compatibility result with constraints
  - **Complexity**: M

- [ ] **T-012** [M] **SLA Tracking Service** *(depends on T-009)*
  Create `accelerators/004-permit-streamliner/backend/app/services/sla_service.py`:
  - SLA timer creation per agency assignment
  - Status computation: on_track, at_risk (>75% elapsed), overdue
  - Dashboard data: applications by SLA status
  - **Acceptance**: SLA status computed correctly; at-risk threshold at 75%
  - **Complexity**: M

- [ ] **T-013** [S] **Application Status Endpoint** *(depends on T-009)*
  Add `GET /api/applications/{id}` and `GET /api/applications` to routes:
  - Application detail with SLA status per agency
  - List applications with filtering (status, type, agency)
  - **Acceptance**: Detail includes per-agency SLA; list supports filters
  - **Complexity**: S

---

## Phase 4: Testing & Evals

**Purpose**: Comprehensive testing, evaluation suite, and E2E validation

- [ ] **T-014** [P] [S] **Unit Tests — Health & Config**
  Create `accelerators/004-permit-streamliner/backend/tests/test_health.py`:
  - Health endpoint returns 200
  - Settings load defaults correctly
  - **Acceptance**: All tests pass
  - **Complexity**: S

- [ ] **T-015** [P] [M] **Unit Tests — Pipeline & Agents**
  Create `accelerators/004-permit-streamliner/backend/tests/test_pipeline.py`:
  - IntakeAgent classifies project types correctly
  - RouterAgent routes to correct agencies
  - ValidationAgent generates accurate checklists
  - Pipeline processes end-to-end application
  - **Acceptance**: 10+ test cases covering all agents
  - **Complexity**: M

- [ ] **T-016** [P] [S] **Unit Tests — Domain Models**
  Create `accelerators/004-permit-streamliner/backend/tests/test_models.py`:
  - All Pydantic models validate correct data
  - Status/type enums enforced
  - **Acceptance**: All models tested for valid and invalid inputs
  - **Complexity**: S

- [ ] **T-017** [M] **Eval Test Suite — Classification & Routing Accuracy**
  Create `accelerators/004-permit-streamliner/backend/tests/test_evals.py`:
  - 15+ eval cases: project description → expected classification + routing
  - Classification accuracy: ≥90%
  - Routing accuracy: ≥95% correct agency assignment
  - Checklist completeness validation
  - **Acceptance**: Eval suite runs; accuracy metrics reported
  - **Complexity**: M

- [ ] **T-018** [M] **Playwright E2E Tests**
  Create `accelerators/004-permit-streamliner/frontend/tests/e2e/permit.spec.ts`:
  - User describes project → receives classification + checklist
  - Application submission flow
  - Zoning check returns results
  - SLA dashboard displays correctly
  - **Acceptance**: E2E tests pass against dev server
  - **Complexity**: M

---

## Dependencies & Execution Order

```
T-001 → T-002 → T-005 → T-006 → T-007 → T-008 → T-009 (critical path)
T-001 → T-003 → T-004 (parallel with T-002)
T-008 → T-010
T-004 → T-011
T-009 → T-012, T-013
T-009 → T-014, T-015, T-016, T-017, T-018 (all tests parallel)
```

### Parallel Opportunities

- T-003 and T-002 can run in parallel
- T-010, T-011, T-012, T-013 can run in parallel after MVP
- All test tasks (T-014 through T-018) can run in parallel

---

## Notes

- All agents must comply with `shared/constitution.md` boundaries
- Permit data is public; PII limited to applicant contact info (CCPA/CPRA applies)
- Mock mode must work without Azure credentials
- SB 35 streamlining rules should be reflected in priority routing
- Breakthrough Project permitting modernization goals should be referenced
