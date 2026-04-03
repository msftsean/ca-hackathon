# Tasks: Medi-Cal Eligibility Agent (003)

**Input**: Design documents from `/specs/003-medi-cal-eligibility/`
**Prerequisites**: plan.md ✅, spec.md ✅, data-model.md ✅, contracts/ ✅
**Accelerator**: 003 — Medi-Cal Eligibility Agent (DHCS)
**Pipeline**: 3-agent (QueryAgent → RouterAgent → ActionAgent)

---

## Phase 1: Core Infrastructure

**Purpose**: Project scaffolding, configuration, domain models, and mock services

- [ ] **T-001** [S] **Settings & Configuration**
  Create `accelerators/003-medi-cal-eligibility/backend/app/config.py` with pydantic-settings `Settings` class.
  - Env vars: `USE_MOCK_SERVICES`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `AZURE_DOC_INTELLIGENCE_ENDPOINT`, `AZURE_DOC_INTELLIGENCE_KEY`, `LOG_LEVEL`
  - Default `USE_MOCK_SERVICES=true`
  - **Acceptance**: `Settings()` loads from `.env`; mock mode is default
  - **Complexity**: S

- [ ] **T-002** [S] **FastAPI App & Health Endpoint** *(depends on T-001)*
  Create `accelerators/003-medi-cal-eligibility/backend/app/main.py` with FastAPI app.
  - CORS middleware
  - `GET /health` → `{"status": "ok", "accelerator": "003-medi-cal-eligibility", "mode": "mock|live"}`
  - Lifespan handler
  - **Acceptance**: `uvicorn` starts; `/health` returns 200
  - **Complexity**: S

- [ ] **T-003** [P] [L] **Pydantic v2 Domain Models**
  Create `accelerators/003-medi-cal-eligibility/backend/app/models.py` with all domain entities:
  - `Application` (id, applicant_name, household_members, status: draft|submitted|under_review|approved|denied, created_at)
  - `EligibilityProfile` (age, household_size, monthly_income, income_type, county, citizenship_status, pregnancy_status, disability_status, current_coverage)
  - `Document` (id, application_id, type: pay_stub|tax_return|id_card|residency_proof, file_url, ocr_status, extracted_data)
  - `IncomeRecord` (source, amount, frequency: weekly|biweekly|monthly|annual, verified: bool, document_id)
  - `BenefitProgram` (id, name: MediCal|MediCalExpansion|MCAP|MinorConsent, fpl_threshold, age_range, description)
  - `ScreeningResult` / `ApplicationResponse` for API
  - **Acceptance**: All models validate with sample data; status enums enforced
  - **Complexity**: L

- [ ] **T-004** [P] [M] **Mock Service with Realistic Data** *(depends on T-003)*
  Create `accelerators/003-medi-cal-eligibility/backend/app/mock_service.py` with:
  - 2024 Federal Poverty Level (FPL) thresholds by household size
  - MAGI income calculation rules
  - Sample applications in various statuses
  - Mock OCR results for document types (pay stubs, tax returns)
  - Medi-Cal program variants (traditional, expansion, MCAP, Minor Consent)
  - County-specific data (all 58 CA counties)
  - **Acceptance**: Mock returns realistic eligibility data; FPL thresholds accurate for 2024
  - **Complexity**: M

**Checkpoint**: Core infrastructure ready — app starts, models validate, mock data available

---

## Phase 2: Agent Pipeline

**Purpose**: Implement the 3-agent pipeline for eligibility screening and document processing

- [ ] **T-005** [M] **QueryAgent — Intent Detection & Entity Extraction** *(depends on T-003, T-004)*
  Create `accelerators/003-medi-cal-eligibility/backend/app/agents/query_agent.py`:
  - Intent classification: eligibility_screen, document_upload, status_check, program_info, income_verify
  - Entity extraction: income, household_size, age, county, citizenship, pregnancy
  - PII filtering: mask SSN, DOB, addresses from logs
  - Mock mode: pattern-matching; Live mode: Azure OpenAI
  - **Acceptance**: Correctly classifies 5+ sample queries; PII never logged
  - **Complexity**: M

- [ ] **T-006** [M] **RouterAgent — Program Routing & Priority** *(depends on T-005)*
  Create `accelerators/003-medi-cal-eligibility/backend/app/agents/router_agent.py`:
  - Route to Medi-Cal program variant based on profile
  - MAGI vs. non-MAGI pathway detection
  - Multi-program eligibility (may qualify for multiple)
  - Priority: emergency/pregnant > children > adults > expansion
  - **Acceptance**: Routes to correct program for 5+ profiles; MAGI pathway detected
  - **Complexity**: M

- [ ] **T-007** [L] **ActionAgent — Eligibility Determination & Response** *(depends on T-006)*
  Create `accelerators/003-medi-cal-eligibility/backend/app/agents/action_agent.py`:
  - MAGI income calculation (gross → adjusted → MAGI)
  - FPL percentage computation by household size
  - Program eligibility determination with explanation
  - Document checklist generation based on program
  - Response with next steps and required documents
  - Disclaimer: "This is a preliminary screening, not an official determination"
  - **Acceptance**: MAGI calculation correct for 5+ scenarios; FPL percentages accurate; disclaimer present
  - **Complexity**: L

- [ ] **T-008** [M] **Pipeline Orchestrator** *(depends on T-005, T-006, T-007)*
  Create `accelerators/003-medi-cal-eligibility/backend/app/pipeline.py`:
  - Wire QueryAgent → RouterAgent → ActionAgent
  - Application state management
  - Error handling with fallbacks
  - Logging with correlation IDs
  - Mock/live mode switching
  - **Acceptance**: Full pipeline processes screening request end-to-end; errors handled gracefully
  - **Complexity**: M

- [ ] **T-009** [M] **Core API Endpoints** *(depends on T-008)*
  Create `accelerators/003-medi-cal-eligibility/backend/app/routes.py`:
  - `POST /api/applications` — create new application
  - `POST /api/eligibility/screen` — submit profile for screening
  - `POST /api/status/query` — check application status
  - Request validation, error responses (400, 422, 500)
  - **Acceptance**: Screening returns eligibility result; application CRUD works; validation errors return 422
  - **Complexity**: M

**Checkpoint**: MVP complete — eligibility screening with MAGI calculation works end-to-end in mock mode

---

### 🎯 MVP CUTLINE

> **Everything above this line constitutes the MVP.** The 3-agent pipeline handles Medi-Cal eligibility screening with MAGI methodology, FPL calculations, and program routing in mock mode. Users can submit profiles and receive preliminary eligibility determinations.

---

## Phase 3: Domain Logic

**Purpose**: Document processing, income verification, and advanced eligibility features

- [ ] **T-010** [L] **Document Upload & OCR Endpoint** *(depends on T-008)*
  Add `POST /api/documents/upload` to routes:
  - Accept document upload (PDF, image)
  - Mock: return pre-built OCR results; Live: Azure Document Intelligence
  - Extract income data from pay stubs, tax returns
  - Document type classification
  - **Acceptance**: Document upload stores file; OCR extracts income data; type classified
  - **Complexity**: L

- [ ] **T-011** [M] **Income Verification Service** *(depends on T-010)*
  Create `accelerators/003-medi-cal-eligibility/backend/app/services/income_service.py`:
  - Reconcile self-reported income with OCR-extracted data
  - Annualize income from various frequencies (weekly, biweekly, monthly)
  - Flag discrepancies between reported and documented income
  - **Acceptance**: Income annualization correct; discrepancies flagged when >10% variance
  - **Complexity**: M

- [ ] **T-012** [M] **FPL Calculation Service** *(depends on T-004)*
  Create `accelerators/003-medi-cal-eligibility/backend/app/services/fpl_service.py`:
  - 2024 FPL thresholds (48 contiguous states + AK + HI)
  - Household size adjustments (1–8+ members)
  - Program-specific FPL percentages (138% Medi-Cal, 213% children, 322% pregnant)
  - **Acceptance**: FPL calculations match federal guidelines; all household sizes covered
  - **Complexity**: M

- [ ] **T-013** [S] **Application Status Tracking** *(depends on T-009)*
  Enhance application status tracking:
  - Status transitions: draft → submitted → under_review → approved/denied
  - Status history with timestamps
  - Missing document notifications
  - **Acceptance**: Status transitions enforced; history tracked; missing docs identified
  - **Complexity**: S

---

## Phase 4: Testing & Evals

**Purpose**: Comprehensive testing, evaluation suite, and E2E validation

- [ ] **T-014** [P] [S] **Unit Tests — Health & Config**
  Create `accelerators/003-medi-cal-eligibility/backend/tests/test_health.py`:
  - Health endpoint returns 200
  - Settings load defaults correctly
  - **Acceptance**: All tests pass
  - **Complexity**: S

- [ ] **T-015** [P] [M] **Unit Tests — Pipeline & Agents**
  Create `accelerators/003-medi-cal-eligibility/backend/tests/test_pipeline.py`:
  - QueryAgent classifies intents correctly
  - RouterAgent routes to correct Medi-Cal programs
  - ActionAgent performs MAGI calculations correctly
  - Pipeline processes end-to-end screening
  - **Acceptance**: 12+ test cases; MAGI edge cases covered
  - **Complexity**: M

- [ ] **T-016** [P] [S] **Unit Tests — Domain Models**
  Create `accelerators/003-medi-cal-eligibility/backend/tests/test_models.py`:
  - All Pydantic models validate correct data
  - Status enum constraints enforced
  - Income frequency conversions work
  - **Acceptance**: All models tested for valid and invalid inputs
  - **Complexity**: S

- [ ] **T-017** [M] **Eval Test Suite — Eligibility Accuracy**
  Create `accelerators/003-medi-cal-eligibility/backend/tests/test_evals.py`:
  - 20+ eval cases: profile → expected eligibility determination
  - MAGI calculation accuracy: 100% (deterministic)
  - Program routing accuracy: ≥95%
  - Edge cases: zero income, self-employment, multiple income sources
  - **Acceptance**: Eval suite runs; all deterministic calculations pass
  - **Complexity**: M

- [ ] **T-018** [M] **Playwright E2E Tests**
  Create `accelerators/003-medi-cal-eligibility/frontend/tests/e2e/eligibility.spec.ts`:
  - User submits eligibility profile → receives determination
  - Document upload flow → OCR results displayed
  - Application status check works
  - **Acceptance**: E2E tests pass against dev server
  - **Complexity**: M

---

## Dependencies & Execution Order

```
T-001 → T-002 → T-005 → T-006 → T-007 → T-008 → T-009 (critical path)
T-001 → T-003 → T-004 (parallel with T-002)
T-008 → T-010 → T-011
T-004 → T-012
T-009 → T-013
T-009 → T-014, T-015, T-016, T-017, T-018 (all tests parallel)
```

### Parallel Opportunities

- T-003 and T-002 can run in parallel
- T-010, T-012, T-013 can start in parallel after MVP
- All test tasks (T-014 through T-018) can run in parallel

---

## Notes

- All agents must comply with `shared/constitution.md` boundaries
- PHI/PII handling must follow HIPAA and CCPA/CPRA requirements
- MAGI calculations must be deterministic (no AI variability)
- Mock mode must work without Azure credentials or Document Intelligence
- Income thresholds must use current-year FPL guidelines
