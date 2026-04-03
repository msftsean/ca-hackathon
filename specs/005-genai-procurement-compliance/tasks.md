# Tasks: GenAI Procurement Compliance (005)

**Input**: Design documents from `/specs/005-genai-procurement-compliance/`
**Prerequisites**: plan.md ✅, spec.md ✅, data-model.md ✅, contracts/ ✅
**Accelerator**: 005 — GenAI Procurement Compliance (CDT / DGS)
**Pipeline**: Single agent with rule evaluation engine (NO frontend)

---

## Phase 1: Core Infrastructure

**Purpose**: Project scaffolding, configuration, domain models, and mock services

- [ ] **T-001** [S] **Settings & Configuration**
  Create `accelerators/005-genai-procurement-compliance/backend/app/config.py` with pydantic-settings `Settings` class.
  - Env vars: `USE_MOCK_SERVICES`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `LOG_LEVEL`
  - Default `USE_MOCK_SERVICES=true`
  - **Acceptance**: `Settings()` loads from `.env`; mock mode is default
  - **Complexity**: S

- [ ] **T-002** [S] **FastAPI App & Health Endpoint** *(depends on T-001)*
  Create `accelerators/005-genai-procurement-compliance/backend/app/main.py` with FastAPI app.
  - CORS middleware
  - `GET /health` → `{"status": "ok", "accelerator": "005-genai-procurement-compliance", "mode": "mock|live"}`
  - Lifespan handler
  - **Acceptance**: `uvicorn` starts; `/health` returns 200
  - **Complexity**: S

- [ ] **T-003** [P] [L] **Pydantic v2 Domain Models**
  Create `accelerators/005-genai-procurement-compliance/backend/app/models.py` with all domain entities:
  - `VendorAttestation` (id, vendor_name, product_name, submission_date, attestation_version, raw_content, status: pending|analyzing|complete|failed)
  - `ComplianceRule` (id, rule_code, title, description, category: transparency|safety|privacy|fairness|accountability, source: EO_N_5_26|SB_53|NIST_AI_RMF, severity: critical|major|minor, evaluation_criteria)
  - `ComplianceResult` (id, attestation_id, rule_id, status: pass|fail|partial|not_applicable, score: 0-100, evidence, remediation_guidance)
  - `GapAnalysis` (id, attestation_id, overall_score: 0-100, category_scores: dict, critical_gaps: list, recommendations: list)
  - `AuditRecord` (id, attestation_id, action, actor, timestamp, details)
  - API request/response models
  - **Acceptance**: All models validate; score ranges enforced (0-100); severity/status enums work
  - **Complexity**: L

- [ ] **T-004** [P] [M] **Mock Service with Realistic Data** *(depends on T-003)*
  Create `accelerators/005-genai-procurement-compliance/backend/app/mock_service.py` with:
  - Compliance rule library (20+ rules from EO N-5-26, SB 53, NIST AI RMF)
  - Sample vendor attestations (3+: one passing, one failing, one partial)
  - NIST AI RMF cross-reference mappings (Govern, Map, Measure, Manage)
  - Pre-computed compliance results for sample attestations
  - Category-level scoring templates
  - **Acceptance**: Mock returns realistic compliance data; rules span all categories
  - **Complexity**: M

**Checkpoint**: Core infrastructure ready — app starts, models validate, compliance rules loaded

---

## Phase 2: Agent Pipeline

**Purpose**: Implement the compliance analysis engine for vendor attestation review

- [ ] **T-005** [M] **Attestation Parser** *(depends on T-003, T-004)*
  Create `accelerators/005-genai-procurement-compliance/backend/app/agents/attestation_parser.py`:
  - Parse uploaded attestation documents (text/PDF content extraction)
  - Section identification (transparency, safety, privacy, fairness, accountability)
  - Evidence extraction from attestation text
  - Normalize vendor responses to structured format
  - Mock mode: pattern-matching; Live mode: Azure OpenAI
  - **Acceptance**: Parses 3+ sample attestations; sections identified; evidence extracted
  - **Complexity**: M

- [ ] **T-006** [L] **Rule Evaluation Engine** *(depends on T-005)*
  Create `accelerators/005-genai-procurement-compliance/backend/app/agents/rule_engine.py`:
  - Evaluate attestation against each compliance rule
  - Per-rule scoring: pass (100), partial (25-75), fail (0), not_applicable
  - Evidence matching: map attestation sections to rule requirements
  - Remediation guidance generation for failed/partial rules
  - NIST AI RMF cross-referencing (map each rule to NIST functions)
  - **Acceptance**: Evaluates all rules; scores consistent; remediation provided for failures
  - **Complexity**: L

- [ ] **T-007** [M] **Gap Analysis Generator** *(depends on T-006)*
  Create `accelerators/005-genai-procurement-compliance/backend/app/agents/gap_analyzer.py`:
  - Aggregate per-rule results into overall compliance score (0-100)
  - Category-level scores (transparency, safety, privacy, fairness, accountability)
  - Critical gap identification (any critical-severity rule that fails)
  - Prioritized recommendations list
  - Executive summary generation
  - **Acceptance**: Overall score computed correctly; critical gaps highlighted; recommendations prioritized
  - **Complexity**: M

- [ ] **T-008** [M] **Pipeline Orchestrator** *(depends on T-005, T-006, T-007)*
  Create `accelerators/005-genai-procurement-compliance/backend/app/pipeline.py`:
  - Wire AttestationParser → RuleEngine → GapAnalyzer
  - Attestation state management (pending → analyzing → complete)
  - Error handling (partial analysis on failure)
  - Audit trail logging for every evaluation step
  - Mock/live mode switching
  - **Acceptance**: Full pipeline processes attestation end-to-end; audit trail complete; state transitions correct
  - **Complexity**: M

- [ ] **T-009** [M] **Attestation Upload & Analysis Endpoints** *(depends on T-008)*
  Create `accelerators/005-genai-procurement-compliance/backend/app/routes.py`:
  - `POST /api/attestations/upload` — upload vendor attestation document
  - `POST /api/attestations/{id}/analyze` — trigger compliance analysis
  - `GET /api/attestations/{id}/results` — retrieve analysis results + gap analysis
  - Request validation, error responses
  - **Acceptance**: Upload stores attestation; analysis returns results with scores; results include gap analysis
  - **Complexity**: M

**Checkpoint**: MVP complete — vendor attestation upload, compliance analysis, and gap reporting work end-to-end in mock mode

---

### 🎯 MVP CUTLINE

> **Everything above this line constitutes the MVP.** The compliance engine parses vendor AI attestations, evaluates against EO N-5-26 / SB 53 / NIST AI RMF rules, generates per-rule scores (0-100), identifies critical gaps, and provides remediation guidance. No frontend — API-only accelerator.

---

## Phase 3: Domain Logic

**Purpose**: Advanced compliance features, batch processing, and audit capabilities

- [ ] **T-010** [M] **Compliance Rule Management** *(depends on T-004)*
  Create `accelerators/005-genai-procurement-compliance/backend/app/services/rule_service.py`:
  - CRUD for compliance rules
  - Rule versioning (track rule changes over time)
  - Category filtering and search
  - Import/export rules as JSON
  - **Acceptance**: Rules can be added/updated/versioned; category filtering works
  - **Complexity**: M

- [ ] **T-011** [M] **Batch Attestation Processing** *(depends on T-008)*
  Create `accelerators/005-genai-procurement-compliance/backend/app/services/batch_service.py`:
  - Process multiple attestations in sequence
  - Comparative scoring across vendors
  - Batch status tracking
  - **Acceptance**: Multiple attestations processed; comparative report generated
  - **Complexity**: M

- [ ] **T-012** [S] **Audit Trail Endpoint** *(depends on T-009)*
  Add `GET /api/attestations/{id}/audit` to routes:
  - Return complete audit trail for an attestation
  - Filterable by action type and date range
  - **Acceptance**: Audit trail complete; all analysis steps recorded
  - **Complexity**: S

- [ ] **T-013** [M] **NIST AI RMF Mapping Service** *(depends on T-006)*
  Create `accelerators/005-genai-procurement-compliance/backend/app/services/nist_service.py`:
  - Map compliance results to NIST AI RMF functions (Govern, Map, Measure, Manage)
  - Generate NIST-aligned compliance report
  - Cross-reference matrix (CA rules ↔ NIST subcategories)
  - **Acceptance**: NIST mapping covers all rules; cross-reference matrix complete
  - **Complexity**: M

---

## Phase 4: Testing & Evals

**Purpose**: Comprehensive testing and evaluation suite (API-only, no E2E browser tests)

- [ ] **T-014** [P] [S] **Unit Tests — Health & Config**
  Create `accelerators/005-genai-procurement-compliance/backend/tests/test_health.py`:
  - Health endpoint returns 200
  - Settings load defaults correctly
  - **Acceptance**: All tests pass
  - **Complexity**: S

- [ ] **T-015** [P] [M] **Unit Tests — Pipeline & Rule Engine**
  Create `accelerators/005-genai-procurement-compliance/backend/tests/test_pipeline.py`:
  - Attestation parser extracts sections correctly
  - Rule engine evaluates rules accurately
  - Gap analyzer computes scores correctly
  - Pipeline processes end-to-end
  - **Acceptance**: 15+ test cases; all compliance categories covered
  - **Complexity**: M

- [ ] **T-016** [P] [S] **Unit Tests — Domain Models**
  Create `accelerators/005-genai-procurement-compliance/backend/tests/test_models.py`:
  - All Pydantic models validate correct data
  - Score ranges enforced (0-100)
  - Severity/status enums enforced
  - **Acceptance**: All models tested for valid and invalid inputs
  - **Complexity**: S

- [ ] **T-017** [M] **Eval Test Suite — Compliance Accuracy**
  Create `accelerators/005-genai-procurement-compliance/backend/tests/test_evals.py`:
  - 20+ eval cases: attestation content → expected rule results
  - Per-rule evaluation accuracy: ≥90%
  - Critical gap detection: 100% (must never miss a critical failure)
  - Scoring consistency across similar attestations
  - **Acceptance**: Eval suite runs; critical gap detection perfect
  - **Complexity**: M

- [ ] **T-018** [M] **API Integration Tests**
  Create `accelerators/005-genai-procurement-compliance/backend/tests/test_api.py`:
  - Upload → analyze → results flow works end-to-end
  - Invalid attestation handled gracefully
  - Concurrent analysis requests don't interfere
  - **Acceptance**: Integration tests pass; error handling verified
  - **Complexity**: M

---

## Dependencies & Execution Order

```
T-001 → T-002 → T-005 → T-006 → T-007 → T-008 → T-009 (critical path)
T-001 → T-003 → T-004 (parallel with T-002)
T-004 → T-010
T-008 → T-011
T-009 → T-012
T-006 → T-013
T-009 → T-014, T-015, T-016, T-017, T-018 (all tests parallel)
```

### Parallel Opportunities

- T-003 and T-002 can run in parallel
- T-010, T-011, T-012, T-013 can run in parallel after MVP
- All test tasks (T-014 through T-018) can run in parallel

---

## Notes

- **NO FRONTEND** — this accelerator is API-only
- All evaluation must comply with `shared/constitution.md`
- Compliance rules must reference specific EO N-5-26 sections
- Audit trail is mandatory for government procurement compliance
- Mock mode must work without Azure credentials
- Scoring must be deterministic for the same input (no AI variability in rule evaluation)
