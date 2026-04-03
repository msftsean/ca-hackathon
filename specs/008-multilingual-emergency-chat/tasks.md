# Tasks: Multilingual Emergency Chatbot (008)

**Input**: Design documents from `/specs/008-multilingual-emergency-chat/`
**Prerequisites**: plan.md ✅, spec.md ✅, data-model.md ✅, contracts/ ✅
**Accelerator**: 008 — Multilingual Emergency Chatbot (Cal OES)
**Pipeline**: Single agent (lightweight, low-latency)

---

## Phase 1: Core Infrastructure

**Purpose**: Project scaffolding, configuration, domain models, and mock services

- [ ] **T-001** [S] **Settings & Configuration**
  Create `accelerators/008-multilingual-emergency-chat/backend/app/config.py` with pydantic-settings `Settings` class.
  - Env vars: `USE_MOCK_SERVICES`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `AZURE_TRANSLATOR_KEY`, `AZURE_TRANSLATOR_REGION`, `LOG_LEVEL`
  - Default `USE_MOCK_SERVICES=true`
  - **Acceptance**: `Settings()` loads from `.env`; mock mode is default
  - **Complexity**: S

- [ ] **T-002** [S] **FastAPI App & Health Endpoint** *(depends on T-001)*
  Create `accelerators/008-multilingual-emergency-chat/backend/app/main.py` with FastAPI app.
  - CORS middleware
  - `GET /health` → `{"status": "ok", "accelerator": "008-multilingual-emergency-chat", "mode": "mock|live"}`
  - Lifespan handler
  - Low-latency focus: minimal middleware chain
  - **Acceptance**: `uvicorn` starts; `/health` returns 200; response time <50ms
  - **Complexity**: S

- [ ] **T-003** [P] [M] **Pydantic v2 Domain Models**
  Create `accelerators/008-multilingual-emergency-chat/backend/app/models.py` with all domain entities:
  - `EmergencyAlert` (id, type: wildfire|earthquake|flood|tsunami|hazmat, severity: advisory|watch|warning|emergency, title, description, affected_area, issued_at, expires_at, source_agency)
  - `EvacuationOrder` (id, zone_name, level: warning|order|shelter_in_place, routes: list, shelters: list, issued_at)
  - `Shelter` (id, name, address, capacity, current_occupancy, amenities: list, accessibility: bool, pet_friendly: bool, lat, lon)
  - `AirQualityReport` (id, station_name, aqi_value, aqi_category: good|moderate|unhealthy_sensitive|unhealthy|very_unhealthy|hazardous, pm25, primary_pollutant, forecast_tomorrow, measured_at)
  - `TranslationCache` (source_text_hash, source_lang, target_lang, translated_text, cached_at, ttl_seconds)
  - `ChatMessage` / `ChatResponse` for API
  - **Acceptance**: All models validate; severity/AQI enums enforced
  - **Complexity**: M

- [ ] **T-004** [P] [M] **Mock Service with Realistic Data** *(depends on T-003)*
  Create `accelerators/008-multilingual-emergency-chat/backend/app/mock_service.py` with:
  - Active emergency alerts (wildfire, earthquake advisory, flood watch)
  - Evacuation zones with routes and shelter assignments
  - Shelter directory (10+ shelters with capacity/occupancy)
  - AQI data for major CA regions (Bay Area, LA, Sacramento, Central Valley)
  - Pre-translated responses in 10 most common CA languages
  - **Acceptance**: Mock returns realistic emergency data; translations available; no external calls
  - **Complexity**: M

**Checkpoint**: Core infrastructure ready — app starts, models validate, mock data available

---

## Phase 2: Agent Pipeline

**Purpose**: Implement the single-agent emergency chatbot with translation

- [ ] **T-005** [M] **Emergency Chat Agent — Intent & Response** *(depends on T-003, T-004)*
  Create `accelerators/008-multilingual-emergency-chat/backend/app/agents/emergency_agent.py`:
  - Intent classification: alert_check, evacuation_info, shelter_find, aqi_check, general_emergency
  - Entity extraction: location, emergency_type, language preference
  - Response generation with emergency-appropriate urgency
  - Safety-first responses (always include emergency numbers: 911, 2-1-1)
  - Mock mode: template-based; Live mode: Azure OpenAI
  - **Acceptance**: Classifies 5+ emergency queries; safety info always included
  - **Complexity**: M

- [ ] **T-006** [M] **Translation Service** *(depends on T-005)*
  Create `accelerators/008-multilingual-emergency-chat/backend/app/agents/translation_service.py`:
  - Language detection from user input
  - Response translation to detected/requested language
  - Translation caching (avoid re-translating common phrases)
  - 70+ language support target (mock: 10 pre-translated; live: Azure Translator)
  - Low-bandwidth mode: shorter responses, essential info only
  - **Acceptance**: Detects language; translations cached; low-bandwidth mode reduces response size
  - **Complexity**: M

- [ ] **T-007** [M] **Emergency Data Aggregator** *(depends on T-004)*
  Create `accelerators/008-multilingual-emergency-chat/backend/app/agents/data_aggregator.py`:
  - Aggregate alerts, evacuations, shelters, AQI into unified response
  - Location-based filtering (nearest shelters, local alerts)
  - Alert priority sorting (emergency > warning > watch > advisory)
  - Data freshness tracking (stale alert detection)
  - **Acceptance**: Aggregates data correctly; location filtering works; stale alerts flagged
  - **Complexity**: M

- [ ] **T-008** [M] **Pipeline Orchestrator** *(depends on T-005, T-006, T-007)*
  Create `accelerators/008-multilingual-emergency-chat/backend/app/pipeline.py`:
  - Wire EmergencyAgent + TranslationService + DataAggregator
  - Low-latency optimization (<500ms target response time)
  - Error handling (emergency fallback: always return safety info)
  - Logging with correlation IDs (no PII)
  - Mock/live mode switching
  - **Acceptance**: Pipeline processes query <500ms; fallback always includes 911; errors never hide safety info
  - **Complexity**: M

- [ ] **T-009** [M] **Chat API Endpoint** *(depends on T-008)*
  Create `accelerators/008-multilingual-emergency-chat/backend/app/routes.py`:
  - `POST /api/chat` — emergency chat with auto-language detection
  - Request validation, error responses
  - SMS-compatible response format option
  - **Acceptance**: Chat returns translated response; SMS format available; validation works
  - **Complexity**: M

**Checkpoint**: MVP complete — multilingual emergency chat with alerts, shelters, and AQI works end-to-end in mock mode

---

### 🎯 MVP CUTLINE

> **Everything above this line constitutes the MVP.** The single-agent chatbot handles emergency queries in multiple languages, providing alerts, evacuation info, shelter locations, and air quality data. SMS-compatible responses and translation caching support low-bandwidth access.

---

## Phase 3: Domain Logic

**Purpose**: Domain-specific endpoints for alerts, evacuations, shelters, and AQI

- [ ] **T-010** [M] **Alert Management Endpoint** *(depends on T-007)*
  Add `POST /api/alerts` and `GET /api/alerts` to routes:
  - Create/list emergency alerts
  - Filter by type, severity, location, active status
  - Alert expiration handling
  - **Acceptance**: Alerts created/listed; filters work; expired alerts excluded by default
  - **Complexity**: M

- [ ] **T-011** [M] **Evacuation Status Endpoint** *(depends on T-007)*
  Add `POST /api/evacuation-status` to routes:
  - Query evacuation status by location or zone
  - Return routes, shelters, and current level
  - Level change history
  - **Acceptance**: Returns evacuation status with routes and shelters; history tracked
  - **Complexity**: M

- [ ] **T-012** [S] **Shelter Directory Endpoint** *(depends on T-004)*
  Add `POST /api/shelters` and `GET /api/shelters` to routes:
  - List shelters with capacity and occupancy
  - Filter by accessibility, pet-friendly, location proximity
  - Real-time occupancy updates (mock: static)
  - **Acceptance**: Shelter list filterable; occupancy shown; accessibility data present
  - **Complexity**: S

- [ ] **T-013** [S] **Air Quality Endpoint** *(depends on T-004)*
  Add `POST /api/aqi` and `GET /api/aqi` to routes:
  - AQI data by location/station
  - Health recommendations based on AQI category
  - Tomorrow's forecast
  - **Acceptance**: AQI returned with health guidance; forecast available
  - **Complexity**: S

- [ ] **T-014** [M] **SMS Gateway Integration** *(depends on T-009)*
  Create `accelerators/008-multilingual-emergency-chat/backend/app/services/sms_service.py`:
  - SMS-formatted response generation (160 char limit awareness)
  - Multi-part SMS handling for longer responses
  - Essential-info-only mode for SMS
  - Mock: log SMS; Live: Twilio/Azure Communication Services
  - **Acceptance**: SMS responses ≤160 chars or properly segmented; essential info preserved
  - **Complexity**: M

---

## Phase 4: Testing & Evals

**Purpose**: Comprehensive testing, evaluation suite, and E2E validation

- [ ] **T-015** [P] [S] **Unit Tests — Health & Config**
  Create `accelerators/008-multilingual-emergency-chat/backend/tests/test_health.py`:
  - Health endpoint returns 200
  - Settings load defaults correctly
  - **Acceptance**: All tests pass
  - **Complexity**: S

- [ ] **T-016** [P] [M] **Unit Tests — Pipeline & Agent**
  Create `accelerators/008-multilingual-emergency-chat/backend/tests/test_pipeline.py`:
  - Emergency agent classifies intents correctly
  - Translation service detects and translates
  - Data aggregator filters by location
  - Pipeline processes end-to-end
  - Response always includes safety info (911)
  - **Acceptance**: 12+ test cases; safety info always present
  - **Complexity**: M

- [ ] **T-017** [P] [S] **Unit Tests — Domain Models**
  Create `accelerators/008-multilingual-emergency-chat/backend/tests/test_models.py`:
  - All Pydantic models validate correct data
  - AQI category/severity enums enforced
  - Translation cache TTL logic works
  - **Acceptance**: All models tested for valid and invalid inputs
  - **Complexity**: S

- [ ] **T-018** [M] **Eval Test Suite — Response Quality & Latency**
  Create `accelerators/008-multilingual-emergency-chat/backend/tests/test_evals.py`:
  - 15+ eval cases: emergency query → expected response type
  - Safety info always present: 100%
  - Response latency: <500ms in mock mode
  - Translation accuracy: verified for 10 languages
  - SMS format compliance
  - **Acceptance**: Safety info perfect; latency within threshold
  - **Complexity**: M

- [ ] **T-019** [M] **Playwright E2E Tests**
  Create `accelerators/008-multilingual-emergency-chat/frontend/tests/e2e/emergency.spec.ts`:
  - User asks about alerts → receives translated response
  - Shelter finder returns nearby results
  - AQI check returns readings with guidance
  - Language selector works
  - **Acceptance**: E2E tests pass against dev server
  - **Complexity**: M

---

## Dependencies & Execution Order

```
T-001 → T-002 → T-005 → T-006, T-007 → T-008 → T-009 (critical path)
T-001 → T-003 → T-004 (parallel with T-002)
T-007 → T-010, T-011
T-004 → T-012, T-013
T-009 → T-014
T-009 → T-015, T-016, T-017, T-018, T-019 (all tests parallel)
```

### Parallel Opportunities

- T-003 and T-002 can run in parallel
- T-006 and T-007 can run in parallel (both depend on different inputs)
- T-010, T-011, T-012, T-013, T-014 can run in parallel after MVP
- All test tasks (T-015 through T-019) can run in parallel

---

## Notes

- All agents must comply with `shared/constitution.md` boundaries
- **Emergency safety info (911, 2-1-1) must NEVER be omitted** from responses
- Low-latency is critical — emergency responses must be fast
- Translation caching reduces repeated API calls for common phrases
- SMS mode must work for users without internet/smartphone access
- Mock mode must work without Azure credentials, Translator API, or SMS gateway
- AQI health guidance must follow EPA standards
