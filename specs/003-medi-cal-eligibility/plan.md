# Implementation Plan: Medi-Cal Eligibility Agent

**Branch**: `feature/003-medi-cal-eligibility`  
**Date**: 2026-02-02  
**Spec**: [spec.md](./spec.md)  
**Agency**: Department of Health Care Services (DHCS)

---

## Summary

Build an AI-powered eligibility agent that automates income document extraction, performs preliminary Medi-Cal eligibility screening based on MAGI and non-MAGI rules, validates document completeness, and provides application status tracking—all while maintaining HIPAA compliance through comprehensive PII detection, encryption, and audit logging.

**Core Features**:
1. Document upload with Azure Document Intelligence OCR extraction
2. Income calculation and FPL comparison engine using Pydantic models
3. MAGI and non-MAGI eligibility screening
4. Document completeness validation with personalized checklists
5. Natural language status query interface
6. HIPAA-compliant audit trail with PII masking
7. Mock BenefitsCal integration layer

**Key Constraints**:
- HIPAA compliance mandatory for all data handling
- No final eligibility determination (county authority only)
- OCR confidence threshold ≥85% or flag for manual review
- All PII encrypted at rest (AES-256) and in transit (TLS 1.3)
- Multi-language support (EN, ES, ZH, VI, TL, KO)
- WCAG 2.1 Level AA accessibility compliance

---

## Technical Context

### Language & Framework
- **Backend**: Python 3.11+, FastAPI 0.109+, Pydantic v2
- **Frontend**: React 18.2+, TypeScript 5.3+, Vite 5.x, Tailwind CSS 3.4+
- **AI/LLM**: Azure OpenAI (GPT-4o), Semantic Kernel for orchestration
- **Document AI**: Azure Document Intelligence (Form Recognizer) for OCR
- **Auth**: Azure Entra ID, MSAL React library

### Dependencies
- **Backend**:
  - `fastapi` - API framework
  - `pydantic` v2 - Data validation and income calculation models
  - `semantic-kernel` - AI orchestration
  - `azure-ai-formrecognizer` - Document Intelligence SDK
  - `azure-identity` - Azure authentication
  - `azure-storage-blob` - Encrypted document storage
  - `cryptography` - PII encryption utilities
  - `python-jose` - JWT token handling
  - `pytest`, `pytest-asyncio` - Testing

- **Frontend**:
  - `react`, `react-dom` - UI framework
  - `@msal/react` - Azure AD authentication
  - `@tanstack/react-query` - Server state management
  - `react-hook-form` - Form handling
  - `zod` - Client-side validation
  - `react-dropzone` - File upload
  - `recharts` - Income visualization
  - `i18next` - Internationalization

- **External Services**:
  - Azure Document Intelligence API (OCR)
  - Azure OpenAI API (GPT-4o for status queries)
  - Azure Blob Storage (encrypted document storage)
  - Azure Entra ID (authentication/authorization)

### Storage
- **Document Storage**: Azure Blob Storage with encryption at rest, signed URLs with 1-hour expiration
- **Application Data**: PostgreSQL 15+ with encrypted columns for PII
- **Audit Logs**: Append-only table with cryptographic signing, 7-year retention
- **Session State**: Redis for temporary upload progress tracking

### Testing Strategy
- **Backend**: pytest with >85% coverage, HIPAA compliance test suite
- **Frontend**: Vitest for unit tests, React Testing Library for components
- **E2E**: Playwright for document upload flows, status query scenarios
- **Accessibility**: axe DevTools automated scans, manual screen reader testing
- **Security**: OWASP ZAP scans, penetration testing for PII exposure
- **OCR Validation**: Gold standard dataset of 200 sample documents with manual review

### Platform
- **Development**: Docker Compose for local environment (FastAPI, React, PostgreSQL, Redis)
- **Deployment**: Azure Container Apps via Azure Developer CLI (azd)
- **Infra**: Bicep templates for Azure resources (Document Intelligence, OpenAI, Storage, etc.)
- **CI/CD**: GitHub Actions for lint, test, build, deploy
- **Monitoring**: Azure Application Insights for telemetry, Log Analytics for audit logs

### Project Type
Full-stack AI agent accelerator with:
- Backend API service (Python/FastAPI)
- Frontend SPA (React/TypeScript)
- Azure AI service integration (Document Intelligence, OpenAI)
- HIPAA-compliant data handling
- Mock integration layer for county systems

---

## Constitution Check

Reviewing against [California State AI Agent Constitution v2.0.0](../../shared/constitution.md):

### ✅ I. California Data Privacy & Security First
- **Compliance**: 
  - All PII (SSN, DOB, address) masked in audit logs (FR-006)
  - Identity verification required before releasing application status (P4 scenario)
  - HIPAA-compliant encryption at rest and in transit (FR-001)
  - Audit trail for all data access with RBAC (FR-007)
- **Implementation**: Pydantic models with `@field_validator` for PII detection, Azure RBAC for document access, cryptographic signing of audit logs

### ✅ II. Accessibility & Multilingual Access (ADA & WCAG 2.1 AA)
- **Compliance**:
  - WCAG 2.1 AA compliance required (FR-012)
  - Multi-language support for EN/ES/ZH/VI/TL/KO (FR-010)
  - Form labels with ARIA attributes, keyboard navigation
  - 8th-grade reading level for eligibility explanations
- **Implementation**: i18next for translations, React Testing Library with axe integration, manual screen reader QA

### ✅ III. Equity & Bias Mitigation
- **Compliance**:
  - Consistent processing for all income sources (wages, self-employment, benefits)
  - No language assumes employment status or housing situation
  - Same OCR quality thresholds for all applicants
  - County office kiosk access for applicants without devices (risk mitigation)
- **Implementation**: Standardized Pydantic eligibility rules applied uniformly, bias testing across demographic groups

### ✅ IV. Graceful Escalation
- **Compliance**:
  - OCR confidence <85% triggers manual review flag (FR-002)
  - Complex cases (special needs trusts, immigration status) escalate to county (P6 scenario)
  - Crisis language in status queries routes to human support
  - Clear explanation when agent cannot provide final determination
- **Implementation**: Confidence score thresholds in OCR service, escalation flags in Application model, explicit "preliminary determination only" messaging

### ✅ V. Auditability & Transparency
- **Compliance**:
  - All actions logged with timestamp, actor, application_id, action type (FR-007)
  - Cryptographic signing for tamper detection
  - 7-year retention per HIPAA requirements
  - Support for CPRA requests and algorithmic accountability reviews
- **Implementation**: AuditEntry model with immutable append-only storage, HMAC-SHA256 signing, JSON export API for compliance officers

### ✅ Agent-Specific Boundaries
- **QueryAgent**: Classifies income document types, extracts entities (income amounts, employers), detects PII
- **ActionAgent**: Searches eligibility rules knowledge base, creates preliminary determination, formats responses with DHCS citations
- **No Final Determination**: Agent explicitly disclaims county authority for final eligibility approval (per Prohibited Actions #2)

### ✅ Prohibited Actions Compliance
- ❌ Never provide medical advice → Scope limited to Medi-Cal eligibility only
- ❌ Never promise outcomes → All determinations labeled "preliminary" pending county review
- ❌ Never store SSNs unencrypted → Column-level encryption in PostgreSQL
- ❌ Never discourage eligible applicants → Positive framing ("likely eligible" vs "probably not")
- ❌ Never make assumptions about immigration status → Route to county for verification

### ✅ California-Specific Requirements
- **Multilingual Support**: i18next with 6 languages, language detection from browser settings
- **County Coordination**: Application model includes county field, routing to 58 county BenefitsCal instances (mock mode)
- **SB 75 All Kids Coverage**: Edge case handling for immigration status changes, state-funded program information

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                      # FastAPI app initialization
│   ├── config.py                    # Azure service configs, feature flags
│   ├── models/
│   │   ├── application.py           # Application, Document, IncomeRecord Pydantic models
│   │   ├── eligibility.py           # EligibilityResult, FPLGuidelines models
│   │   ├── audit.py                 # AuditEntry model with signing
│   │   └── enums.py                 # Status, DocumentType, IncomeSource enums
│   ├── services/
│   │   ├── document_intelligence.py # Azure Document Intelligence OCR
│   │   ├── ocr_parsers.py           # W-2, pay stub, Form 1040 structured extractors
│   │   ├── income_calculator.py     # Annualized income, MAGI calculation
│   │   ├── eligibility_engine.py    # FPL comparison, MAGI/non-MAGI rules
│   │   ├── pii_detector.py          # Regex + NER for SSN, DOB, medical info
│   │   ├── document_validator.py    # Completeness check, quality validation
│   │   ├── audit_service.py         # Audit log creation with cryptographic signing
│   │   ├── status_query.py          # Azure OpenAI integration for NL status queries
│   │   └── benefitscal_mock.py      # Mock integration layer for county system
│   ├── routers/
│   │   ├── applications.py          # POST /applications, GET /applications/{id}
│   │   ├── documents.py             # POST /documents/upload, GET /documents/{id}/extract
│   │   ├── eligibility.py           # POST /eligibility/screen
│   │   ├── status.py                # POST /status/query (natural language)
│   │   └── audit.py                 # GET /audit/logs (admin only)
│   ├── middleware/
│   │   ├── auth.py                  # Azure Entra ID JWT validation
│   │   ├── rbac.py                  # Role-based access control
│   │   └── pii_logging.py           # Ensure no PII in application logs
│   └── tests/
│       ├── test_ocr_parsers.py      # OCR extraction accuracy tests
│       ├── test_eligibility.py      # MAGI/non-MAGI rule tests
│       ├── test_pii_detector.py     # PII detection coverage tests
│       ├── test_hipaa_compliance.py # HIPAA audit trail tests
│       └── fixtures/                # Sample W-2s, pay stubs (synthetic data)

frontend/
├── src/
│   ├── App.tsx                      # MSAL authentication provider
│   ├── main.tsx                     # React root
│   ├── pages/
│   │   ├── ApplicationForm.tsx      # Application creation and household info
│   │   ├── DocumentUpload.tsx       # Drag-and-drop file upload with preview
│   │   ├── IncomeReview.tsx         # Review extracted income data
│   │   ├── EligibilityResult.tsx    # Display preliminary determination
│   │   ├── StatusTracker.tsx        # Natural language status query interface
│   │   └── DocumentChecklist.tsx    # Completeness validation display
│   ├── components/
│   │   ├── FileUploader.tsx         # react-dropzone wrapper
│   │   ├── OCRExtractedData.tsx     # Side-by-side document/data view
│   │   ├── IncomeSourceForm.tsx     # Add/edit income sources
│   │   ├── FPLCalculator.tsx        # FPL % visualization
│   │   ├── LanguageSelector.tsx     # i18next language switcher
│   │   └── AccessibleForm.tsx       # WCAG-compliant form wrapper
│   ├── hooks/
│   │   ├── useDocumentUpload.ts     # Upload mutation with progress
│   │   ├── useEligibilityScreen.ts  # Eligibility screening query
│   │   └── useStatusQuery.ts        # Natural language status query
│   ├── api/
│   │   └── client.ts                # Axios instance with MSAL token interceptor
│   ├── i18n/
│   │   ├── en.json                  # English translations
│   │   ├── es.json                  # Spanish translations
│   │   └── index.ts                 # i18next configuration
│   └── tests/
│       ├── DocumentUpload.test.tsx  # Upload flow tests
│       ├── EligibilityResult.test.tsx # Result display tests
│       └── a11y.test.tsx            # Accessibility tests with axe

infra/
├── main.bicep                       # Azure resource orchestration
├── app/
│   ├── document-intelligence.bicep  # Azure AI Document Intelligence
│   ├── openai.bicep                 # Azure OpenAI GPT-4o deployment
│   ├── storage.bicep                # Blob storage with encryption
│   └── postgres.bicep               # Azure Database for PostgreSQL
└── modules/
    └── monitoring.bicep             # Application Insights, Log Analytics

shared/
└── fpl-guidelines-2026.json         # Federal Poverty Level thresholds by household size
```

---

## Complexity Tracking

### Phase 1: Document Upload & OCR Extraction (Week 1-2)
**Estimated Complexity**: Medium  
**Tasks**:
- [ ] Set up Azure Document Intelligence resource via Bicep
- [ ] Implement document upload API with Azure Blob Storage integration
- [ ] Create OCR parser for W-2 (Boxes 1, 2, 16, 17)
- [ ] Create OCR parser for pay stub (custom layout detection)
- [ ] Implement confidence score threshold logic (85%)
- [ ] Build frontend DocumentUpload.tsx with react-dropzone
- [ ] Add PII detection service (SSN regex: `\d{3}-\d{2}-\d{4}`)
- [ ] Write OCR accuracy tests with gold standard dataset

**Risks**: Azure Document Intelligence may struggle with handwritten documents (mitigation: clear upload guidelines)

---

### Phase 2: Income Calculation Engine (Week 2-3)
**Estimated Complexity**: High  
**Tasks**:
- [ ] Define Pydantic models for IncomeRecord with validation
- [ ] Implement annualized income calculation (hourly → annual, biweekly → annual)
- [ ] Create MAGI income calculator per 42 CFR 435.603 (excludes: child support, SSI)
- [ ] Build FPL comparison logic with 2026 thresholds
- [ ] Implement non-MAGI asset calculation for seniors/disabled
- [ ] Create IncomeSourceForm.tsx React component
- [ ] Build FPL percentage visualization with recharts
- [ ] Write unit tests for all income calculation scenarios

**Risks**: MAGI rules complex with many exceptions (mitigation: extensive test coverage, DHCS rule validation)

---

### Phase 3: Eligibility Screening (Week 3-4)
**Estimated Complexity**: High  
**Tasks**:
- [ ] Implement eligibility_engine.py with MAGI pathways (adult, child, parent/caretaker)
- [ ] Add non-MAGI eligibility logic (SSI-linked, 1634 status, Medicare Savings Programs)
- [ ] Create household composition validation
- [ ] Implement eligibility result explanation generator (Semantic Kernel)
- [ ] Build EligibilityResult.tsx with clear pass/fail messaging
- [ ] Add alternative coverage suggestions (Covered California)
- [ ] Test against 100 synthetic application scenarios
- [ ] Validate 88% accuracy target against county determinations (sample data)

**Risks**: Edge cases (self-employment deductions, household disputes) may reduce accuracy (mitigation: flag for manual review)

---

### Phase 4: Document Completeness Validation (Week 4)
**Estimated Complexity**: Medium  
**Tasks**:
- [ ] Create document requirement rules engine (program type → required docs)
- [ ] Implement document quality validation (OCR confidence, recency, legibility)
- [ ] Build personalized checklist generator
- [ ] Add DocumentChecklist.tsx with upload status tracking
- [ ] Implement document expiration detection (W-2 must be current tax year)
- [ ] Add multi-document validation (Form 1040 + Schedule C for self-employment)
- [ ] Write completeness validation tests

**Risks**: Requirements vary by county (mitigation: centralized rule configuration, county override option)

---

### Phase 5: Status Tracking with Natural Language (Week 5)
**Estimated Complexity**: Medium  
**Tasks**:
- [ ] Implement status query API with Azure OpenAI GPT-4o
- [ ] Create Semantic Kernel prompt for status translation
- [ ] Add application status workflow (draft → submitted → county_processing → approved/denied)
- [ ] Build StatusTracker.tsx with chat interface
- [ ] Implement identity verification before releasing sensitive status
- [ ] Add SLA tracking (45-day standard processing time)
- [ ] Test with 50 sample status queries
- [ ] Measure <2 second response time (SC-008)

**Risks**: Users may ask questions beyond status (mitigation: scope limiting in prompt, escalation trigger)

---

### Phase 6: HIPAA Compliance & Audit Trail (Week 5-6)
**Estimated Complexity**: High  
**Tasks**:
- [ ] Implement audit_service.py with cryptographic signing (HMAC-SHA256)
- [ ] Create append-only AuditEntry table with PostgreSQL
- [ ] Add column-level encryption for PII in Application table
- [ ] Implement PII masking in audit logs (e.g., "John D****" for names)
- [ ] Build RBAC middleware (applicant, county_worker, dhcs_admin roles)
- [ ] Add audit log export API for compliance officers
- [ ] Run HIPAA compliance test suite (100% pass required)
- [ ] Conduct penetration testing for PII exposure
- [ ] Complete Privacy Impact Assessment (PIA)

**Risks**: PII detection false negatives could leak data (mitigation: multi-layer detection with regex + NER, manual audit sampling)

---

### Phase 7: Mock BenefitsCal Integration (Week 6)
**Estimated Complexity**: Low  
**Tasks**:
- [ ] Define BenefitsCal JSON payload schema
- [ ] Implement benefitscal_mock.py with application submission endpoint
- [ ] Add county routing logic (58 counties)
- [ ] Create submission confirmation with tracking number
- [ ] Build queue and retry logic for system downtime
- [ ] Add integration test suite
- [ ] Document API contract for real integration (Phase 2)

**Risks**: Actual BenefitsCal API may differ from mock (mitigation: early stakeholder review of schema)

---

### Phase 8: Multi-Language & Accessibility (Week 7)
**Estimated Complexity**: Medium  
**Tasks**:
- [ ] Set up i18next with language files (EN, ES, ZH, VI, TL, KO)
- [ ] Translate all UI strings and eligibility explanations
- [ ] Add ARIA labels to all form inputs and buttons
- [ ] Implement keyboard navigation for document upload
- [ ] Test color contrast ratios (≥4.5:1 for normal text)
- [ ] Conduct screen reader testing (NVDA, JAWS)
- [ ] Run axe DevTools automated accessibility scan
- [ ] Measure Spanish-language adoption (target ≥18% per SC-009)

**Risks**: Translation quality for complex eligibility terms (mitigation: DHCS-certified translators, community review)

---

### Phase 9: Testing & QA (Week 8)
**Estimated Complexity**: Medium  
**Tasks**:
- [ ] Achieve >85% backend test coverage
- [ ] Write E2E Playwright tests for all user journeys
- [ ] Conduct load testing (500 concurrent uploads)
- [ ] Run OWASP ZAP security scan
- [ ] Validate OCR accuracy ≥92% (SC-002)
- [ ] Test eligibility screening accuracy ≥88% (SC-010)
- [ ] Measure document processing speed <30 seconds (SC-001)
- [ ] User acceptance testing with DHCS stakeholders

**Risks**: Performance issues with large PDF uploads (mitigation: 10MB file size limit, async processing)

---

### Phase 10: Deployment & Monitoring (Week 8)
**Estimated Complexity**: Low  
**Tasks**:
- [ ] Deploy to Azure Container Apps via `azd up`
- [ ] Configure Application Insights alerts (error rate, latency)
- [ ] Set up Log Analytics for audit log queries
- [ ] Create monitoring dashboard (uploads, eligibility screens, status queries)
- [ ] Document runbook for on-call support
- [ ] Train county eligibility workers on system usage
- [ ] Launch to pilot county (10% of applications)
- [ ] Measure CSAT ≥4.2/5.0 (SC-006)

**Risks**: Azure region outage affecting Document Intelligence (mitigation: multi-region deployment plan)

---

## Success Metrics Tracking

| Metric | Target | Measurement Method | Dashboard |
|--------|--------|-------------------|-----------|
| SC-001: Document processing speed | <30 sec for 95% | Application Insights custom metric | Azure Dashboard |
| SC-002: OCR accuracy | ≥92% average confidence | Gold standard validation dataset | Weekly report |
| SC-003: Application completion | ≥85% (from 68% baseline) | Submitted vs. draft applications ratio | Monthly KPI |
| SC-004: Processing time reduction | ≤27 min (40% reduction) | County worker survey + time tracking | Quarterly survey |
| SC-005: HIPAA compliance | 100% audit pass rate | Monthly compliance audit | Compliance portal |
| SC-006: User satisfaction | ≥4.2/5.0 CSAT | Post-interaction survey | Real-time CSAT |
| SC-007: Accessibility | Zero critical violations | axe DevTools + manual testing | Pre-release checklist |
| SC-008: Status query accuracy | ≥98% accuracy, <2 sec latency | Sample validation + App Insights | Weekly report |
| SC-009: Spanish adoption | ≥18% of sessions | Language preference analytics | Monthly dashboard |
| SC-010: Eligibility accuracy | ≥88% match to county final | 500-case validation sample | 6-month study |

---

## Open Questions

1. **Document Intelligence Quota**: What is the API call quota for Document Intelligence in the DHCS Azure subscription? Need to plan for peak load (redetermination surges).

2. **BenefitsCal API Specification**: Does BenefitsCal have a documented API, or will integration require county IT coordination? Timeline for production integration?

3. **FPL Update Process**: Who is responsible for updating FPL thresholds annually in January? Need admin UI or manual config update?

4. **County Pilot Selection**: Which county will participate in pilot testing? Need county with diverse applicant demographics and technical capacity.

5. **PII Detection Coverage**: Should we use Azure AI Language NER in addition to regex for PII detection? Cost vs. accuracy tradeoff.

6. **Non-MAGI Asset Verification**: How do counties currently verify bank account balances? Can we integrate with financial institution APIs or require manual upload only?

7. **Appeals Integration**: If preliminary determination is disputed, how does the appeal workflow integrate with existing county processes?

8. **Multilingual OCR**: Does Azure Document Intelligence support OCR for Spanish-language documents, or do we need language-specific models?

---

## Next Steps

1. **Week 1**: Kickoff meeting with DHCS stakeholders, county eligibility supervisors, and CDT security team
2. **Week 1**: Provision Azure resources (Document Intelligence, OpenAI, Storage, PostgreSQL) via Bicep
3. **Week 1**: Collect sample document library (W-2s, pay stubs, tax returns) with DHCS privacy approval
4. **Week 2**: Implement Phase 1 (document upload + OCR) and validate OCR accuracy on samples
5. **Week 3**: Build income calculation engine and validate against DHCS test cases
6. **Week 4-5**: Develop eligibility screening and status tracking
7. **Week 6**: Complete HIPAA compliance implementation and initiate security review
8. **Week 7**: Multi-language and accessibility implementation
9. **Week 8**: QA, pilot deployment, and county worker training
10. **Week 9+**: Monitor pilot metrics, iterate based on feedback, plan Phase 2 (production BenefitsCal integration)
