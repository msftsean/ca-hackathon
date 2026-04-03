# Tasks: Wildfire Response Coordinator (002)

**Input**: Design documents from `/specs/002-wildfire-response-coordinator/`
**Prerequisites**: plan.md ✅, spec.md ✅, data-model.md ✅, contracts/ ✅
**Accelerator**: 002 — Wildfire Response Coordinator (CAL FIRE / Cal OES)
**Pipeline**: 4-agent (IncidentAgent → ResourceAgent → EvacuationAgent → CoordinationAgent)

---

## Phase 1: Core Infrastructure

**Purpose**: Project scaffolding, configuration, domain models, and mock services

- [ ] **T-001** [S] **Settings & Configuration**
  Create `accelerators/002-wildfire-response-coordinator/backend/app/config.py` with pydantic-settings `Settings` class.
  - Env vars: `USE_MOCK_SERVICES`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `AZURE_SEARCH_ENDPOINT`, `WEATHER_API_KEY`, `LOG_LEVEL`
  - Default `USE_MOCK_SERVICES=true`
  - **Acceptance**: `Settings()` loads from `.env`; mock mode is default
  - **Complexity**: S

- [ ] **T-002** [S] **FastAPI App & Health Endpoint** *(depends on T-001)*
  Create `accelerators/002-wildfire-response-coordinator/backend/app/main.py` with FastAPI app.
  - CORS middleware
  - `GET /health` → `{"status": "ok", "accelerator": "002-wildfire-response-coordinator", "mode": "mock|live"}`
  - Lifespan handler
  - **Acceptance**: `uvicorn` starts; `/health` returns 200; CORS headers present
  - **Complexity**: S

- [ ] **T-003** [P] [L] **Pydantic v2 Domain Models**
  Create `accelerators/002-wildfire-response-coordinator/backend/app/models.py` with all domain entities:
  - `Incident` (id, name, type, location_lat/lon, acres, containment_pct, cal_fire_unit, status, severity, created_at)
  - `Resource` (id, type: engine|crew|aircraft|dozer, agency, status: available|deployed|returning, location, capacity)
  - `EvacuationZone` (id, name, level: warning|order|shelter_in_place, population, geometry, shelters)
  - `WeatherCondition` (station_id, temp, humidity, wind_speed, wind_direction, red_flag_warning, fire_weather_watch)
  - `AgencyAssignment` (id, incident_id, agency: CAL_FIRE|Cal_OES|county|utility, role, resources_assigned)
  - `PSPSEvent` (id, utility, affected_area, start_time, end_time, customers_affected, status)
  - API request/response models for all endpoints
  - **Acceptance**: All models validate with sample data; enum constraints enforced
  - **Complexity**: L

- [ ] **T-004** [P] [M] **Mock Service with Realistic Data** *(depends on T-003)*
  Create `accelerators/002-wildfire-response-coordinator/backend/app/mock_service.py` with:
  - Sample incidents (3+ active wildfires across different CA regions)
  - Resource inventory (engines, crews, aircraft across 6 mutual aid regions)
  - Evacuation zones with population data
  - Weather conditions with red flag scenarios
  - PSPS event data (PG&E, SCE, SDG&E)
  - Mutual aid region mappings (Regions I–VI)
  - **Acceptance**: Mock returns realistic multi-agency incident data; no external calls
  - **Complexity**: M

**Checkpoint**: Core infrastructure ready — app starts, models validate, mock data available

---

## Phase 2: Agent Pipeline

**Purpose**: Implement the 4-agent pipeline for wildfire coordination

- [ ] **T-005** [M] **IncidentAgent — Situation Assessment** *(depends on T-003, T-004)*
  Create `accelerators/002-wildfire-response-coordinator/backend/app/agents/incident_agent.py`:
  - Incident intake and classification (severity: low/medium/high/extreme)
  - Location parsing (lat/lon, address, landmark)
  - Weather correlation (red flag warnings, wind conditions)
  - Incident timeline tracking
  - Mock mode: pattern-matching; Live mode: Azure OpenAI
  - **Acceptance**: Classifies severity for 5+ scenarios; weather correlation works
  - **Complexity**: M

- [ ] **T-006** [L] **ResourceAgent — Resource Allocation** *(depends on T-005)*
  Create `accelerators/002-wildfire-response-coordinator/backend/app/agents/resource_agent.py`:
  - Resource matching based on incident severity and type
  - Mutual aid region awareness (6 regions)
  - Resource availability checking
  - Multi-agency coordination (CAL FIRE, county, federal)
  - Allocation priority: life safety > property > environment
  - **Acceptance**: Allocates appropriate resources for 5+ incident types; respects mutual aid regions
  - **Complexity**: L

- [ ] **T-007** [L] **EvacuationAgent — Zone Planning** *(depends on T-005)*
  Create `accelerators/002-wildfire-response-coordinator/backend/app/agents/evacuation_agent.py`:
  - Evacuation zone determination based on fire spread models
  - Population impact estimation
  - Shelter capacity matching
  - Evacuation route planning (avoid fire path)
  - PSPS coordination (de-energized areas)
  - **Acceptance**: Generates evacuation zones with population counts; shelter assignments valid
  - **Complexity**: L

- [ ] **T-008** [M] **CoordinationAgent — Multi-Agency Orchestration** *(depends on T-006, T-007)*
  Create `accelerators/002-wildfire-response-coordinator/backend/app/agents/coordination_agent.py`:
  - Wire IncidentAgent → ResourceAgent + EvacuationAgent → CoordinationAgent
  - Multi-agency notification generation
  - Situation report (SITREP) compilation
  - ICS (Incident Command System) role tracking
  - Priority conflict resolution between agencies
  - **Acceptance**: Produces coordinated SITREP; agency assignments non-conflicting
  - **Complexity**: M

- [ ] **T-009** [M] **Incident API Endpoints** *(depends on T-008)*
  Create `accelerators/002-wildfire-response-coordinator/backend/app/routes.py`:
  - `POST /api/incidents` — report new incident, trigger pipeline
  - `GET /api/incidents` — list active incidents
  - `GET /api/incidents/{id}` — incident details with assignments
  - Request validation, error responses
  - **Acceptance**: Incident creation triggers full pipeline; list/detail endpoints work
  - **Complexity**: M

**Checkpoint**: MVP complete — wildfire incident intake, resource allocation, and evacuation planning work end-to-end in mock mode

---

### 🎯 MVP CUTLINE

> **Everything above this line constitutes the MVP.** The 4-agent pipeline handles wildfire incident reporting, resource allocation across mutual aid regions, evacuation zone planning, and multi-agency coordination in mock mode.

---

## Phase 3: Domain Logic

**Purpose**: Domain-specific endpoints for resources, evacuations, weather, and PSPS

- [ ] **T-010** [M] **Resource Allocation Endpoint** *(depends on T-008)*
  Add `POST /api/resources/allocate` to routes:
  - Accept incident_id + resource requirements → return allocation plan
  - Validate resource availability before allocation
  - Track deployed vs. available resources
  - **Acceptance**: Allocation respects availability; deployed resources marked unavailable
  - **Complexity**: M

- [ ] **T-011** [M] **Evacuation Zone Endpoint** *(depends on T-008)*
  Add `POST /api/evacuations/zones` and `GET /api/evacuations/zones/{incident_id}` to routes:
  - Create/update evacuation zones for an incident
  - Return zones with shelter assignments and population data
  - Zone level transitions (warning → order → all-clear)
  - **Acceptance**: Zones created with valid shelter assignments; level transitions logged
  - **Complexity**: M

- [ ] **T-012** [S] **Weather Endpoint** *(depends on T-004)*
  Add `GET /api/weather` and `GET /api/weather/{station_id}` to routes:
  - Return current conditions and fire weather alerts
  - Red flag warning detection
  - Mock: static weather data; Live: NWS API
  - **Acceptance**: Returns weather with red flag status; station lookup works
  - **Complexity**: S

- [ ] **T-013** [M] **PSPS Event Service** *(depends on T-004)*
  Create `accelerators/002-wildfire-response-coordinator/backend/app/services/psps_service.py`:
  - Track PSPS events by utility (PG&E, SCE, SDG&E)
  - Correlate PSPS with evacuation zones
  - Impact assessment (customers affected, critical facilities)
  - **Acceptance**: PSPS events correlated with incidents; impact counts accurate
  - **Complexity**: M

- [ ] **T-014** [M] **Mutual Aid Region Service** *(depends on T-006)*
  Create `accelerators/002-wildfire-response-coordinator/backend/app/services/mutual_aid_service.py`:
  - 6 CA mutual aid regions with county mappings
  - Cross-region resource request workflow
  - Resource sharing agreements tracking
  - **Acceptance**: Region lookup by county; cross-region requests generated correctly
  - **Complexity**: M

---

## Phase 4: Testing & Evals

**Purpose**: Comprehensive testing, evaluation suite, and E2E validation

- [ ] **T-015** [P] [S] **Unit Tests — Health & Config**
  Create `accelerators/002-wildfire-response-coordinator/backend/tests/test_health.py`:
  - Health endpoint returns 200
  - Settings load defaults correctly
  - **Acceptance**: All tests pass
  - **Complexity**: S

- [ ] **T-016** [P] [M] **Unit Tests — Pipeline & Agents**
  Create `accelerators/002-wildfire-response-coordinator/backend/tests/test_pipeline.py`:
  - IncidentAgent classifies severity correctly
  - ResourceAgent allocates appropriate resources
  - EvacuationAgent generates valid zones
  - CoordinationAgent produces SITREP
  - **Acceptance**: 12+ test cases covering all 4 agents
  - **Complexity**: M

- [ ] **T-017** [P] [S] **Unit Tests — Domain Models**
  Create `accelerators/002-wildfire-response-coordinator/backend/tests/test_models.py`:
  - All Pydantic models validate correct data
  - Enum constraints enforced (resource types, severity levels)
  - **Acceptance**: All models tested for valid and invalid inputs
  - **Complexity**: S

- [ ] **T-018** [M] **Eval Test Suite — Accuracy & Routing**
  Create `accelerators/002-wildfire-response-coordinator/backend/tests/test_evals.py`:
  - 15+ eval cases: incident → expected severity + resource allocation
  - Severity classification accuracy: ≥90%
  - Resource allocation appropriateness: ≥85%
  - Evacuation zone coverage validation
  - **Acceptance**: Eval suite runs; metrics reported
  - **Complexity**: M

- [ ] **T-019** [M] **Playwright E2E Tests**
  Create `accelerators/002-wildfire-response-coordinator/frontend/tests/e2e/incident.spec.ts`:
  - User reports incident → resources allocated
  - Evacuation zones displayed on map
  - SITREP generated and downloadable
  - **Acceptance**: E2E tests pass against dev server
  - **Complexity**: M

---

## Dependencies & Execution Order

```
T-001 → T-002 → T-005 → T-006 → T-008 → T-009 (critical path)
                  T-005 → T-007 → T-008 (parallel with T-006)
T-001 → T-003 → T-004 (parallel with T-002)
T-008 → T-010, T-011
T-004 → T-012, T-013
T-006 → T-014
T-009 → T-015, T-016, T-017, T-018, T-019 (all tests parallel)
```

### Parallel Opportunities

- T-003 and T-002 can run in parallel
- T-006 and T-007 can run in parallel (both depend on T-005)
- T-010, T-011, T-012, T-013, T-014 can run in parallel after MVP
- All test tasks (T-015 through T-019) can run in parallel

---

## Notes

- All agents must comply with `shared/constitution.md` boundaries
- Wildfire data must never include PII of residents
- Mock mode must work without any Azure credentials or weather APIs
- ICS terminology must be used consistently (IC, Operations, Logistics, etc.)
- Mutual aid regions follow CA OES standard definitions
