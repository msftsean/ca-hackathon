# Tasks: BenefitsCal Navigator (001)

**Input**: Design documents from `/specs/001-benefitscal-navigator/`
**Prerequisites**: plan.md ✅, spec.md ✅, data-model.md ✅, contracts/ ✅
**Accelerator**: 001 — BenefitsCal Navigator (CDSS)
**Pipeline**: 3-agent (QueryAgent → RouterAgent → ActionAgent)

---

## Phase 1: Core Infrastructure

**Purpose**: Project scaffolding, configuration, domain models, and mock services

- [ ] **T-001** [S] **Settings & Configuration**
  Create `accelerators/001-benefitscal-navigator/backend/app/config.py` with pydantic-settings `Settings` class.
  - Env vars: `USE_MOCK_SERVICES`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_KEY`, `LOG_LEVEL`
  - Default `USE_MOCK_SERVICES=true` for local/hackathon dev
  - **Acceptance**: `Settings()` loads from `.env`; mock mode is default; all vars documented
  - **Complexity**: S

- [ ] **T-002** [S] **FastAPI App & Health Endpoint** *(depends on T-001)*
  Create `accelerators/001-benefitscal-navigator/backend/app/main.py` with FastAPI app.
  - CORS middleware (allow all origins in dev)
  - `GET /health` → `{"status": "ok", "accelerator": "001-benefitscal-navigator", "mode": "mock|live"}`
  - Lifespan handler for startup/shutdown
  - **Acceptance**: `uvicorn` starts; `/health` returns 200; CORS headers present
  - **Complexity**: S

- [ ] **T-003** [P] [M] **Pydantic v2 Domain Models**
  Create `accelerators/001-benefitscal-navigator/backend/app/models.py` with all domain entities:
  - `ConversationSession` (id, user_id, language, created_at, messages)
  - `Query` (text, intent, entities, language, timestamp)
  - `EligibilityProfile` (household_size, monthly_income, county, citizenship_status, age, disability_status)
  - `BenefitProgram` (id, name: CalFresh|CalWORKs|GeneralRelief|CAPI, description, requirements, max_benefit)
  - `PolicyDocument` (id, program, title, content, effective_date, source_url)
  - `ChatMessage` / `ChatResponse` for API request/response
  - **Acceptance**: All models validate with sample data; JSON serialization round-trips
  - **Complexity**: M

- [ ] **T-004** [P] [M] **Mock Service with Realistic Data** *(depends on T-003)*
  Create `accelerators/001-benefitscal-navigator/backend/app/mock_service.py` with:
  - Canned eligibility data for CalFresh, CalWORKs, General Relief, CAPI
  - FPL-based income thresholds per program
  - Sample policy documents (at least 3 per program)
  - Mock intent detection responses (eligibility_check, program_info, application_help, escalation)
  - Multi-language mock responses (English, Spanish, Chinese, Vietnamese, Tagalog, Korean, Armenian, Hmong)
  - **Acceptance**: Mock service returns realistic data for all 4 programs; no external calls needed
  - **Complexity**: M

**Checkpoint**: Core infrastructure ready — app starts, models validate, mock data available

---

## Phase 2: Agent Pipeline

**Purpose**: Implement the 3-agent pipeline for conversational eligibility Q&A

- [ ] **T-005** [M] **QueryAgent — Intent Detection & Entity Extraction** *(depends on T-003, T-004)*
  Create `accelerators/001-benefitscal-navigator/backend/app/agents/query_agent.py`:
  - Intent classification: eligibility_check, program_info, application_help, escalation, greeting
  - Entity extraction: program_name, household_size, income, county, language
  - PII filtering: mask SSN, DOB, address from logs
  - Language detection for 8 supported languages
  - Mock mode: pattern-matching; Live mode: Azure OpenAI
  - **Acceptance**: Correctly classifies 5+ sample queries; extracts entities; PII never in logs
  - **Complexity**: M

- [ ] **T-006** [M] **RouterAgent — Program Routing & Priority** *(depends on T-005)*
  Create `accelerators/001-benefitscal-navigator/backend/app/agents/router_agent.py`:
  - Route to correct benefit program(s) based on intent + entities
  - Multi-program eligibility (user may qualify for multiple)
  - Priority: crisis/escalation > eligibility_check > program_info > general
  - Escalation triggers: mentions of emergency, abuse, homelessness
  - County-specific routing when applicable
  - **Acceptance**: Routes to correct program(s) for 5+ scenarios; escalation triggers work
  - **Complexity**: M

- [ ] **T-007** [L] **ActionAgent — Response Generation with Citations** *(depends on T-006)*
  Create `accelerators/001-benefitscal-navigator/backend/app/agents/action_agent.py`:
  - Generate natural-language responses with policy citations
  - Eligibility pre-screening based on profile data
  - Response formatting: structured answers with next-steps
  - Citation format: `[PolicyDoc: {title}, §{section}]`
  - Multi-language response generation
  - Disclaimer: "This is not an official eligibility determination"
  - **Acceptance**: Responses include citations; pre-screening logic matches FPL thresholds; disclaimer present
  - **Complexity**: L

- [ ] **T-008** [M] **Pipeline Orchestrator** *(depends on T-005, T-006, T-007)*
  Create `accelerators/001-benefitscal-navigator/backend/app/pipeline.py`:
  - Wire QueryAgent → RouterAgent → ActionAgent
  - Session management (conversation context)
  - Error handling with graceful fallbacks
  - Logging with correlation IDs
  - Configurable mock/live mode via `USE_MOCK_SERVICES`
  - **Acceptance**: Full pipeline processes a query end-to-end; session state persists across turns; errors handled gracefully
  - **Complexity**: M

- [ ] **T-009** [M] **Chat API Endpoint** *(depends on T-008)*
  Create/update routes in `accelerators/001-benefitscal-navigator/backend/app/routes.py`:
  - `POST /api/chat` — send message, get response (with session management)
  - `POST /api/sessions` — create new conversation session
  - Request validation, error responses (400, 422, 500)
  - Rate limiting headers
  - **Acceptance**: `/api/chat` returns structured response with citations; sessions persist; validation errors return 422
  - **Complexity**: M

**Checkpoint**: MVP complete — conversational eligibility Q&A works end-to-end in mock mode

---

### 🎯 MVP CUTLINE

> **Everything above this line constitutes the MVP.** The agent pipeline handles conversational eligibility Q&A for CalFresh, CalWORKs, General Relief, and CAPI in mock mode. Users can ask questions and receive cited, multi-language responses.

---

## Phase 3: Domain Logic

**Purpose**: Domain-specific endpoints, pre-screening, and program data services

- [ ] **T-010** [M] **Pre-Screening Endpoint** *(depends on T-008)*
  Add `POST /api/prescreening` to routes:
  - Accept `EligibilityProfile` → return list of likely-eligible programs
  - FPL calculation logic (2024 thresholds)
  - Program-specific rules (CalFresh: 200% FPL gross, 100% net; CalWORKs: family with children; etc.)
  - **Acceptance**: Pre-screening returns correct programs for 5+ household profiles
  - **Complexity**: M

- [ ] **T-011** [S] **Programs Endpoint** *(depends on T-004)*
  Add `GET /api/programs` and `GET /api/programs/{program_id}` to routes:
  - Return program details, requirements, benefit amounts
  - Filter by county when query param provided
  - **Acceptance**: Returns all 4 programs; individual program detail includes requirements
  - **Complexity**: S

- [ ] **T-012** [M] **Multi-Language Support Service** *(depends on T-007)*
  Create `accelerators/001-benefitscal-navigator/backend/app/services/language_service.py`:
  - Language detection from user input
  - Response translation (mock: template-based; live: Azure Translator)
  - 8 supported languages: en, es, zh, vi, tl, ko, hy, hmn
  - **Acceptance**: Responses generated in detected language; language codes validated
  - **Complexity**: M

- [ ] **T-013** [M] **Escalation & Handoff Service** *(depends on T-006)*
  Create `accelerators/001-benefitscal-navigator/backend/app/services/escalation_service.py`:
  - Detect crisis keywords and escalation triggers
  - Generate handoff payload with conversation summary
  - County office routing (mock county directory)
  - **Acceptance**: Crisis keywords trigger escalation; handoff includes conversation context
  - **Complexity**: M

---

## Phase 4: Testing & Evals

**Purpose**: Comprehensive testing, evaluation suite, and E2E validation

- [ ] **T-014** [P] [S] **Unit Tests — Health & Config**
  Create `accelerators/001-benefitscal-navigator/backend/tests/test_health.py`:
  - Health endpoint returns 200
  - Settings load defaults correctly
  - Mock mode is default
  - **Acceptance**: All tests pass; coverage for config and health
  - **Complexity**: S

- [ ] **T-015** [P] [M] **Unit Tests — Pipeline & Agents**
  Create `accelerators/001-benefitscal-navigator/backend/tests/test_pipeline.py`:
  - QueryAgent classifies intents correctly
  - RouterAgent routes to correct programs
  - ActionAgent generates cited responses
  - Pipeline processes end-to-end query
  - **Acceptance**: 10+ test cases covering all agent behaviors
  - **Complexity**: M

- [ ] **T-016** [P] [S] **Unit Tests — Domain Models**
  Create `accelerators/001-benefitscal-navigator/backend/tests/test_models.py`:
  - All Pydantic models validate correct data
  - Models reject invalid data (negative income, missing required fields)
  - JSON serialization/deserialization round-trips
  - **Acceptance**: All models tested for valid and invalid inputs
  - **Complexity**: S

- [ ] **T-017** [M] **Eval Test Suite — Accuracy & Routing**
  Create `accelerators/001-benefitscal-navigator/backend/tests/test_evals.py`:
  - 20+ eval cases: query → expected intent + program routing
  - Accuracy threshold: ≥90% intent classification
  - Routing accuracy: ≥95% correct program selection
  - Response quality: citations present, disclaimer included
  - **Acceptance**: Eval suite runs in CI; accuracy metrics reported
  - **Complexity**: M

- [ ] **T-018** [M] **Playwright E2E Tests**
  Create `accelerators/001-benefitscal-navigator/frontend/tests/e2e/chat.spec.ts`:
  - User sends message → receives response
  - Multi-turn conversation maintains context
  - Pre-screening form submits and returns results
  - Language selector changes response language
  - **Acceptance**: E2E tests pass against running dev server
  - **Complexity**: M

---

## Dependencies & Execution Order

```
T-001 → T-002 → T-005 → T-006 → T-007 → T-008 → T-009 (critical path)
T-001 → T-003 → T-004 (parallel with T-002)
T-008 → T-010, T-013
T-004 → T-011
T-007 → T-012
T-009 → T-014, T-015, T-016, T-017, T-018 (all tests parallel)
```

### Parallel Opportunities

- T-003 and T-002 can run in parallel (different files)
- T-014, T-015, T-016 can all run in parallel (different test files)
- T-010, T-011, T-012, T-013 can run in parallel after MVP

---

## Notes

- All agents must comply with `shared/constitution.md` boundaries
- PII handling must follow CCPA/CPRA requirements
- Mock mode must work without any Azure credentials
- Responses must include EO N-12-23 compliance disclaimers
