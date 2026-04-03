# Tasks: EDD Claims Assistant (007)

**Input**: Design documents from `/specs/007-edd-claims-assistant/`
**Prerequisites**: plan.md ✅, spec.md ✅, data-model.md ✅, contracts/ ✅
**Accelerator**: 007 — EDD Claims Assistant (EDD)
**Pipeline**: 3-agent (QueryAgent → RouterAgent → ActionAgent)

---

## Phase 1: Core Infrastructure

**Purpose**: Project scaffolding, configuration, domain models, and mock services

- [ ] **T-001** [S] **Settings & Configuration**
  Create `accelerators/007-edd-claims-assistant/backend/app/config.py` with pydantic-settings `Settings` class.
  - Env vars: `USE_MOCK_SERVICES`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `AZURE_SEARCH_ENDPOINT`, `LOG_LEVEL`
  - Default `USE_MOCK_SERVICES=true`
  - **Acceptance**: `Settings()` loads from `.env`; mock mode is default
  - **Complexity**: S

- [ ] **T-002** [S] **FastAPI App & Health Endpoint** *(depends on T-001)*
  Create `accelerators/007-edd-claims-assistant/backend/app/main.py` with FastAPI app.
  - CORS middleware
  - `GET /health` → `{"status": "ok", "accelerator": "007-edd-claims-assistant", "mode": "mock|live"}`
  - Lifespan handler
  - **Acceptance**: `uvicorn` starts; `/health` returns 200
  - **Complexity**: S

- [ ] **T-003** [P] [L] **Pydantic v2 Domain Models**
  Create `accelerators/007-edd-claims-assistant/backend/app/models.py` with all domain entities:
  - `Claim` (id, claimant_id, claim_type, status: filed|pending|approved|denied|appealing, weekly_benefit_amount, claim_start_date, claim_end_date)
  - `ClaimType` (id, name: UI|DI|PFL, description, eligibility_requirements, max_duration_weeks, max_benefit_amount)
  - `EligibilityAssessment` (id, claim_type, base_period_wages, quarterly_earnings: list[4], meets_wage_requirement: bool, estimated_weekly_benefit, eligible: bool, reasons: list)
  - `SupportTicket` (id, claimant_id, issue_type, description, status: open|in_progress|resolved|escalated, created_at)
  - `PolicyArticle` (id, claim_type, title, content, effective_date, ui_code_section)
  - `DocumentChecklist` (id, claim_type, required_docs: list, submitted_docs: list, missing_docs: list)
  - `ChatMessage` / `ChatResponse` for API
  - **Acceptance**: All models validate; claim status/type enums enforced
  - **Complexity**: L

- [ ] **T-004** [P] [M] **Mock Service with Realistic Data** *(depends on T-003)*
  Create `accelerators/007-edd-claims-assistant/backend/app/mock_service.py` with:
  - Sample claims (UI, DI, PFL) in various statuses
  - 2024 benefit calculation rules (UI: high quarter ÷ 26; DI: highest quarter; PFL: 60-70% of wages)
  - Base period wage data samples
  - Policy articles for each claim type
  - Document checklists by claim type (ID, SSN card, wage records, medical cert for DI, bonding docs for PFL)
  - Mock identity verification responses
  - **Acceptance**: Mock returns realistic claim data; benefit calculations based on actual EDD formulas
  - **Complexity**: M

**Checkpoint**: Core infrastructure ready — app starts, models validate, mock data available

---

## Phase 2: Agent Pipeline

**Purpose**: Implement the 3-agent pipeline for claims support

- [ ] **T-005** [M] **QueryAgent — Intent Detection & Entity Extraction** *(depends on T-003, T-004)*
  Create `accelerators/007-edd-claims-assistant/backend/app/agents/query_agent.py`:
  - Intent classification: claim_status, eligibility_check, document_help, file_claim, appeal_info, general_info
  - Entity extraction: claim_type (UI/DI/PFL), claim_id, date_range, wage_info
  - PII filtering: mask SSN, claimant IDs from logs
  - Identity verification check (has user been verified?)
  - Mock mode: pattern-matching; Live mode: Azure OpenAI
  - **Acceptance**: Correctly classifies 5+ sample queries; entities extracted; PII filtered
  - **Complexity**: M

- [ ] **T-006** [M] **RouterAgent — Claim Type Routing & Priority** *(depends on T-005)*
  Create `accelerators/007-edd-claims-assistant/backend/app/agents/router_agent.py`:
  - Route to correct claim type handler (UI, DI, PFL)
  - Priority: identity_issue > claim_status > eligibility > document_help > general
  - Escalation triggers: fraud mention, appeal deadline approaching, overpayment notice
  - Multi-claim detection (user may have UI + DI)
  - **Acceptance**: Routes correctly for 5+ scenarios; escalation triggers work
  - **Complexity**: M

- [ ] **T-007** [L] **ActionAgent — Claims Response & Benefit Calculation** *(depends on T-006)*
  Create `accelerators/007-edd-claims-assistant/backend/app/agents/action_agent.py`:
  - Claim status lookup and formatting
  - Eligibility pre-screening with benefit estimation
  - UI benefit calculation: highest quarter wages ÷ 26 (capped)
  - DI/PFL benefit calculation: 60-70% of wages
  - Document checklist generation per claim type
  - Policy citations (UI Code sections)
  - Disclaimer: "This is informational only, not an official EDD determination"
  - **Acceptance**: Benefit calculations match EDD formulas; citations included; disclaimer present
  - **Complexity**: L

- [ ] **T-008** [M] **Pipeline Orchestrator** *(depends on T-005, T-006, T-007)*
  Create `accelerators/007-edd-claims-assistant/backend/app/pipeline.py`:
  - Wire QueryAgent → RouterAgent → ActionAgent
  - Session management with identity verification state
  - Error handling with fallbacks
  - Logging with correlation IDs
  - Mock/live mode switching
  - **Acceptance**: Full pipeline processes claim query end-to-end; identity state persists
  - **Complexity**: M

- [ ] **T-009** [M] **Chat API Endpoint** *(depends on T-008)*
  Create `accelerators/007-edd-claims-assistant/backend/app/routes.py`:
  - `POST /api/chat` — conversational claims support
  - Request validation, error responses
  - Session management (identity verification state)
  - **Acceptance**: Chat returns structured response; sessions work; validation errors return 422
  - **Complexity**: M

**Checkpoint**: MVP complete — conversational claims support for UI/DI/PFL works end-to-end in mock mode

---

### 🎯 MVP CUTLINE

> **Everything above this line constitutes the MVP.** The 3-agent pipeline handles conversational claims support for UI, DI, and PFL, including claim status lookup, eligibility pre-screening, benefit estimation, and document checklists in mock mode.

---

## Phase 3: Domain Logic

**Purpose**: Domain-specific endpoints for claims status, eligibility, and document checklists

- [ ] **T-010** [M] **Claim Status Endpoint** *(depends on T-008)*
  Add `POST /api/claim-status` to routes:
  - Accept claim_id + identity verification → return claim status detail
  - Status history with dates and actions
  - Next steps and required actions
  - **Acceptance**: Returns claim status with history; identity required before access
  - **Complexity**: M

- [ ] **T-011** [M] **Eligibility Pre-Screening Endpoint** *(depends on T-007)*
  Add `POST /api/eligibility` to routes:
  - Accept wage data + claim type → return eligibility assessment
  - Base period calculation
  - Weekly benefit amount estimation
  - Qualification reasons (met/not met)
  - **Acceptance**: Eligibility result with benefit estimate; base period correctly computed
  - **Complexity**: M

- [ ] **T-012** [S] **Document Checklist Endpoint** *(depends on T-004)*
  Add `POST /api/document-checklist` to routes:
  - Accept claim_type → return required documents
  - Track submitted vs. missing documents
  - Per-document instructions and acceptable formats
  - **Acceptance**: Checklist complete for all 3 claim types; instructions provided
  - **Complexity**: S

- [ ] **T-013** [M] **Identity Verification Service** *(depends on T-004)*
  Create `accelerators/007-edd-claims-assistant/backend/app/services/identity_service.py`:
  - Mock identity verification flow (knowledge-based questions)
  - Session-level verification state (verified/unverified)
  - Verification required before claim status access
  - **Acceptance**: Verification flow works; unverified users blocked from claim data
  - **Complexity**: M

---

## Phase 4: Testing & Evals

**Purpose**: Comprehensive testing, evaluation suite, and E2E validation

- [ ] **T-014** [P] [S] **Unit Tests — Health & Config**
  Create `accelerators/007-edd-claims-assistant/backend/tests/test_health.py`:
  - Health endpoint returns 200
  - Settings load defaults correctly
  - **Acceptance**: All tests pass
  - **Complexity**: S

- [ ] **T-015** [P] [M] **Unit Tests — Pipeline & Agents**
  Create `accelerators/007-edd-claims-assistant/backend/tests/test_pipeline.py`:
  - QueryAgent classifies claim intents correctly
  - RouterAgent routes to correct claim type
  - ActionAgent calculates benefits correctly
  - Pipeline processes end-to-end claim query
  - **Acceptance**: 12+ test cases; benefit calculation edge cases covered
  - **Complexity**: M

- [ ] **T-016** [P] [S] **Unit Tests — Domain Models**
  Create `accelerators/007-edd-claims-assistant/backend/tests/test_models.py`:
  - All Pydantic models validate correct data
  - Claim status/type enums enforced
  - Benefit amount ranges validated
  - **Acceptance**: All models tested for valid and invalid inputs
  - **Complexity**: S

- [ ] **T-017** [M] **Eval Test Suite — Claims Accuracy**
  Create `accelerators/007-edd-claims-assistant/backend/tests/test_evals.py`:
  - 20+ eval cases: query → expected intent + claim type routing
  - Benefit calculation accuracy: 100% (deterministic)
  - Intent classification accuracy: ≥90%
  - Escalation trigger detection: 100%
  - **Acceptance**: Eval suite runs; deterministic calculations perfect
  - **Complexity**: M

- [ ] **T-018** [M] **Playwright E2E Tests**
  Create `accelerators/007-edd-claims-assistant/frontend/tests/e2e/claims.spec.ts`:
  - User asks about claim status → response received
  - Eligibility screening flow works
  - Document checklist displayed
  - Multi-turn conversation maintains context
  - **Acceptance**: E2E tests pass against dev server
  - **Complexity**: M

---

## Dependencies & Execution Order

```
T-001 → T-002 → T-005 → T-006 → T-007 → T-008 → T-009 (critical path)
T-001 → T-003 → T-004 (parallel with T-002)
T-008 → T-010
T-007 → T-011
T-004 → T-012, T-013
T-009 → T-014, T-015, T-016, T-017, T-018 (all tests parallel)
```

### Parallel Opportunities

- T-003 and T-002 can run in parallel
- T-010, T-011, T-012, T-013 can run in parallel after MVP
- All test tasks (T-014 through T-018) can run in parallel

---

## Notes

- All agents must comply with `shared/constitution.md` boundaries
- PII handling is critical — SSN, claimant IDs must never be logged (CCPA/CPRA)
- Benefit calculations must be deterministic and match official EDD formulas
- Identity verification required before any claim-specific data access
- Mock mode must work without Azure credentials
- UI Code sections must be accurately referenced in citations
