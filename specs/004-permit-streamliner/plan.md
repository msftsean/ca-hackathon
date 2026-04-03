# Implementation Plan: Permit Streamliner

**Branch**: `feature/004-permit-streamliner`  
**Date**: 2026-02-02  
**Spec**: [spec.md](./spec.md)  
**Agencies**: Governor's Office of Planning and Research (OPR), Housing & Community Development (HCD), Dept of Consumer Affairs (DCA)

---

## Summary

Build an AI-powered permit intake and status tracking agent that automates project classification, generates personalized permit checklists, validates document completeness, cross-references zoning/environmental/code requirements, and routes applications to appropriate reviewing agencies—all while maintaining transparency and SLA accountability.

**Core Features**:
1. Natural language project intake with intelligent permit type identification
2. Automated checklist generation based on project type, location, and scope
3. Document validation using Azure Document Intelligence (site plans, architectural drawings)
4. Zoning compliance checking against GIS data (mock mode)
5. Environmental constraint flagging (flood zones, endangered species, CEQA triggers)
6. Multi-agency routing with workflow dependencies and priority assignment
7. SLA-aware status tracking with natural language query interface
8. Reviewer workload dashboard with load balancing

**Key Constraints**:
- No final permit approval authority (plan reviewers retain decision-making)
- Mock zoning/GIS data for pilot (real integration Phase 2)
- 3-second max response time for status queries (95th percentile)
- WCAG 2.1 Level AA accessibility compliance
- Multi-language support (English, Spanish)
- SLA tracking with 80% threshold alerting

---

## Technical Context

### Language & Framework
- **Backend**: Python 3.11+, FastAPI 0.109+, Pydantic v2
- **Frontend**: React 18.2+, TypeScript 5.3+, Vite 5.x, Tailwind CSS 3.4+
- **AI/LLM**: Azure OpenAI (GPT-4o), Semantic Kernel for orchestration
- **Search**: Azure AI Search for regulatory knowledge base (building codes, permit requirements)
- **Document AI**: Azure Document Intelligence for plan validation
- **Auth**: Azure Entra ID, MSAL React library

### Dependencies
- **Backend**:
  - `fastapi` - API framework
  - `pydantic` v2 - Data validation and permit requirement models
  - `semantic-kernel` - AI orchestration for 3-agent pipeline
  - `azure-ai-formrecognizer` - Document Intelligence SDK
  - `azure-search-documents` - Azure AI Search client
  - `azure-identity` - Azure authentication
  - `azure-storage-blob` - Document storage
  - `python-dateutil` - SLA date calculations
  - `pytest`, `pytest-asyncio` - Testing

- **Frontend**:
  - `react`, `react-dom` - UI framework
  - `@msal/react` - Azure AD authentication
  - `@tanstack/react-query` - Server state management
  - `react-hook-form` - Form handling
  - `zod` - Client-side validation
  - `react-dropzone` - File upload
  - `recharts` - SLA tracking visualization
  - `i18next` - Internationalization (EN/ES)

- **External Services**:
  - Azure OpenAI API (GPT-4o for classification and status queries)
  - Azure AI Search (permit requirements, building codes, agency procedures)
  - Azure Document Intelligence (site plan and drawing validation)
  - Azure Blob Storage (application documents)
  - Azure Entra ID (authentication/authorization)

### Storage
- **Document Storage**: Azure Blob Storage with 1-hour signed URLs
- **Application Data**: PostgreSQL 15+ with indexes for SLA queries
- **Knowledge Base**: Azure AI Search with hybrid search (vector + keyword) for permit regulations
- **Cache**: Redis for frequent zoning lookups and agency routing rules

### Testing Strategy
- **Backend**: pytest with >85% coverage, permit identification accuracy tests
- **Frontend**: Vitest for unit tests, React Testing Library for components
- **E2E**: Playwright for application submission flows, status query scenarios
- **Accessibility**: axe DevTools automated scans, manual keyboard navigation testing
- **AI Evaluation**: 200-application gold standard dataset with expert validation
- **Load Testing**: Simulate 100 concurrent applicants during intake surge

### Platform
- **Development**: Docker Compose for local environment (FastAPI, React, PostgreSQL, Redis, Azure AI Search emulator)
- **Deployment**: Azure Container Apps via Azure Developer CLI (azd)
- **Infra**: Bicep templates for Azure resources (OpenAI, AI Search, Document Intelligence, Storage)
- **CI/CD**: GitHub Actions for lint, test, build, deploy
- **Monitoring**: Azure Application Insights for telemetry, custom SLA breach alerts

### Project Type
Full-stack AI agent accelerator with:
- Backend API service (Python/FastAPI)
- Frontend SPA (React/TypeScript)
- Azure AI service integration (OpenAI, AI Search, Document Intelligence)
- 3-agent pipeline: IntakeAgent (classify) → RequirementsAgent (checklist) → RoutingAgent (assign reviewers)
- Mock integrations for zoning GIS and agency systems

---

## Constitution Check

Reviewing against [California State AI Agent Constitution v2.0.0](../../shared/constitution.md):

### ✅ I. California Data Privacy & Security First
- **Compliance**: 
  - Applicant PII (name, address, phone) encrypted in database (FR-011)
  - No permit details released without applicant authentication
  - Audit logging for all application access (reviewers, admin)
  - CCPA/CPRA compliance for PII handling
- **Implementation**: Column-level encryption in PostgreSQL, RBAC for reviewer access, applicant auth via Azure Entra ID

### ✅ II. Accessibility & Multilingual Access (ADA & WCAG 2.1 AA)
- **Compliance**:
  - WCAG 2.1 AA compliance required (SC-009)
  - English and Spanish language support (FR-010)
  - Form labels with ARIA attributes, keyboard navigation
  - Clear explanations of permit requirements (8th-grade reading level)
  - Screen reader compatibility for status tracking
- **Implementation**: i18next for translations, axe accessibility testing, manual keyboard nav QA

### ✅ III. Equity & Bias Mitigation
- **Compliance**:
  - Consistent permit requirements regardless of applicant name, location (urban/rural), or project type
  - No assumptions about applicant technical knowledge (guided intake wizard)
  - Same document validation standards for all applicants
  - Load balancing ensures fair reviewer assignment (no favoritism)
- **Implementation**: Standardized Pydantic permit requirement models, bias testing across project types

### ✅ IV. Graceful Escalation
- **Compliance**:
  - Complex projects (multi-phase, contradictory regulations) escalate to senior planner (P1 scenario edge case)
  - Low confidence (<85%) in project classification triggers human review (FR-001)
  - CEQA analysis limited to preliminary screening, substantive review by qualified planners (risk mitigation)
  - Appeals and legal disputes escalated immediately (edge case: appeals filed)
- **Implementation**: Confidence thresholds in classification service, escalation flags in Application model, explicit disclaimers

### ✅ V. Auditability & Transparency
- **Compliance**:
  - All routing decisions logged with reasoning (FR-006)
  - SLA breaches tracked and reported for agency performance (FR-007)
  - Status query responses include responsible reviewer name and contact (FR-008)
  - Permit requirement sources cited (e.g., "per Section R301.1.3 of California Building Code")
- **Implementation**: AuditLog model with decision reasoning, transparent SLA dashboard for applicants

### ✅ Agent-Specific Boundaries
- **IntakeAgent**: Classifies project type, extracts entities (address, scope, project description)
- **RequirementsAgent**: Searches knowledge base for permit requirements, generates checklist
- **RoutingAgent**: Determines reviewing agencies, assigns priority, creates workflow dependencies
- **No Final Approval**: Agent explicitly disclaims plan reviewer authority for permit approval (per Prohibited Actions #2)

### ✅ Prohibited Actions Compliance
- ❌ Never promise outcomes → All checklists labeled "preliminary" pending reviewer validation
- ❌ Never provide legal advice → CEQA guidance marked "informational only, consult environmental planner"
- ❌ Never make assumptions about project → Guided questions to clarify scope
- ❌ Never discourage eligible applicants → Positive framing even for complex projects

### ✅ California-Specific Requirements
- **Breakthrough Project Directive**: Aligns with mandate to streamline permitting using AI
- **Envision 2026 Goal 5**: Supports seamless cross-agency experiences for permits
- **County Coordination**: Multi-agency routing includes county and state agencies (Fish & Wildlife, Water Board)
- **Housing Crisis**: Prioritizes residential permit processing to support housing production goals

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                           # FastAPI app initialization
│   ├── config.py                         # Azure service configs, SLA thresholds
│   ├── models/
│   │   ├── application.py                # PermitApplication, RequiredDocument models
│   │   ├── permit_type.py                # PermitType, ZoningCheck models
│   │   ├── routing.py                    # ReviewAssignment, AgencyWorkflow models
│   │   ├── audit.py                      # AuditLog model
│   │   └── enums.py                      # Status, ProjectType, Priority enums
│   ├── services/
│   │   ├── intake_agent.py               # IntakeAgent: project classification (GPT-4o)
│   │   ├── requirements_agent.py         # RequirementsAgent: checklist generation (AI Search RAG)
│   │   ├── routing_agent.py              # RoutingAgent: agency assignment, workflow creation
│   │   ├── document_validator.py         # Azure Document Intelligence for site plan validation
│   │   ├── zoning_service.py             # Mock zoning GIS lookup (Phase 2: real integration)
│   │   ├── environmental_service.py      # Environmental constraint checks (FEMA, CNDDB)
│   │   ├── sla_tracker.py                # SLA calculation, breach detection, notifications
│   │   ├── status_query.py               # Azure OpenAI for natural language status queries
│   │   └── knowledge_base.py             # Azure AI Search client for code lookup
│   ├── routers/
│   │   ├── applications.py               # POST /applications, GET /applications/{id}
│   │   ├── intake.py                     # POST /intake/classify, POST /intake/checklist
│   │   ├── documents.py                  # POST /documents/upload, POST /documents/validate
│   │   ├── status.py                     # POST /status/query (natural language)
│   │   ├── zoning.py                     # GET /zoning/check?address={address}
│   │   └── admin.py                      # GET /admin/sla-dashboard, GET /admin/workload
│   ├── middleware/
│   │   ├── auth.py                       # Azure Entra ID JWT validation
│   │   ├── rbac.py                       # Role-based access (applicant, reviewer, admin)
│   │   └── rate_limit.py                 # Rate limiting for public intake API
│   └── tests/
│       ├── test_intake_agent.py          # Project classification accuracy tests
│       ├── test_requirements_agent.py    # Checklist generation tests
│       ├── test_routing_agent.py         # Agency routing logic tests
│       ├── test_document_validator.py    # Site plan validation tests
│       ├── test_sla_tracker.py           # SLA calculation tests
│       └── fixtures/                     # Sample applications, site plans, zoning data

frontend/
├── src/
│   ├── App.tsx                           # MSAL authentication provider
│   ├── main.tsx                          # React root
│   ├── pages/
│   │   ├── IntakeWizard.tsx              # Step-by-step project intake form
│   │   ├── ChecklistView.tsx             # Display generated permit checklist
│   │   ├── DocumentUpload.tsx            # Upload site plans, drawings
│   │   ├── DocumentValidation.tsx        # Show validation results with confidence scores
│   │   ├── ApplicationStatus.tsx         # Natural language status query interface
│   │   ├── ReviewerDashboard.tsx         # Assigned applications, SLA tracking (staff only)
│   │   └── AdminDashboard.tsx            # SLA metrics, workload balancing (admin only)
│   ├── components/
│   │   ├── ProjectTypeSelector.tsx       # Visual project type selection
│   │   ├── AddressInput.tsx              # Address autocomplete with validation
│   │   ├── ChecklistItem.tsx             # Single checklist item with upload status
│   │   ├── SLAProgressBar.tsx            # Visual SLA timeline with color coding
│   │   ├── ZoningComplianceCard.tsx      # Display zoning check results
│   │   ├── RoutingFlowchart.tsx          # Visual workflow of reviewing agencies
│   │   └── LanguageToggle.tsx            # EN/ES language switcher
│   ├── hooks/
│   │   ├── useProjectClassification.ts   # Intake agent API call
│   │   ├── useChecklistGeneration.ts     # Requirements agent API call
│   │   ├── useDocumentValidation.ts      # Document validator API call
│   │   ├── useStatusQuery.ts             # Natural language status query
│   │   └── useZoningCheck.ts             # Zoning compliance API call
│   ├── api/
│   │   └── client.ts                     # Axios instance with MSAL token interceptor
│   ├── i18n/
│   │   ├── en.json                       # English translations (permit terms, UI)
│   │   ├── es.json                       # Spanish translations
│   │   └── index.ts                      # i18next configuration
│   └── tests/
│       ├── IntakeWizard.test.tsx         # Intake flow tests
│       ├── ChecklistView.test.tsx        # Checklist display tests
│       ├── ApplicationStatus.test.tsx    # Status query tests
│       └── a11y.test.tsx                 # Accessibility tests with axe

infra/
├── main.bicep                            # Azure resource orchestration
├── app/
│   ├── openai.bicep                      # Azure OpenAI GPT-4o deployment
│   ├── search.bicep                      # Azure AI Search service
│   ├── document-intelligence.bicep       # Azure AI Document Intelligence
│   └── storage.bicep                     # Blob storage for documents
└── modules/
    └── monitoring.bicep                  # Application Insights, SLA alerts

shared/
├── permit-requirements.json              # Permit type definitions, document requirements
├── zoning-mock-data.json                 # Mock zoning regulations by jurisdiction (pilot)
└── california-building-code-excerpts.md  # Key CBC sections for knowledge base seeding
```

---

## Complexity Tracking

### Phase 1: Natural Language Intake & Classification (Week 1-2)
**Estimated Complexity**: Medium  
**Tasks**:
- [ ] Create IntakeAgent service with Azure OpenAI GPT-4o
- [ ] Define project type taxonomy (15 types: residential_addition, new_residential, commercial_new, etc.)
- [ ] Implement project classification with confidence scoring
- [ ] Build entity extraction (address, square footage, stories, project cost estimate)
- [ ] Create guided intake wizard in React with project type selection
- [ ] Add AddressInput component with autocomplete
- [ ] Test classification accuracy on 200 historical permit applications (target ≥92% per SC-001)
- [ ] Implement low-confidence (<85%) escalation to human intake staff

**Risks**: Ambiguous project descriptions reduce accuracy (mitigation: clarifying questions, common templates)

---

### Phase 2: Requirements Agent & Checklist Generation (Week 2-3)
**Estimated Complexity**: High  
**Tasks**:
- [ ] Set up Azure AI Search index for permit requirements knowledge base
- [ ] Ingest permit type definitions from `permit-requirements.json`
- [ ] Ingest California Building Code excerpts (key sections: R301-R313 residential, 403-421 commercial)
- [ ] Implement RequirementsAgent with semantic search (RAG pattern)
- [ ] Create Pydantic models for PermitType, RequiredDocument
- [ ] Build checklist generation logic based on project type + address + scope
- [ ] Add fee estimation based on project valuation
- [ ] Create ChecklistView.tsx with expandable document requirements
- [ ] Test checklist completeness against 50 sample projects (target: all required permits identified)

**Risks**: Knowledge base incompleteness leads to missing permit types (mitigation: agency stakeholder review, iterative updates)

---

### Phase 3: Document Validation (Week 3-4)
**Estimated Complexity**: Medium  
**Tasks**:
- [ ] Implement document_validator.py using Azure Document Intelligence
- [ ] Create site plan validation logic (detect property boundaries, setbacks, scale, north arrow)
- [ ] Create architectural drawing validation (floor plan, elevations, room labels)
- [ ] Add confidence scoring (0.0-1.0) for each validation element
- [ ] Build DocumentUpload.tsx with react-dropzone
- [ ] Create DocumentValidation.tsx showing validation results with color-coded confidence
- [ ] Add corrections guidance for failed validations
- [ ] Test validation accuracy on 100 sample site plans (target ≥85% per SC-002)

**Risks**: Hand-drawn or poor-quality scans reduce accuracy (mitigation: provide upload guidelines, flag low confidence for manual review)

---

### Phase 4: Zoning Compliance & Environmental Checks (Week 4-5)
**Estimated Complexity**: High  
**Tasks**:
- [ ] Create zoning_service.py with mock GIS data lookup (from `zoning-mock-data.json`)
- [ ] Define ZoningCheck Pydantic model (zone_code, permitted_uses, height, setbacks, lot_coverage, parking)
- [ ] Implement compliance validation logic (compare proposed vs. allowed)
- [ ] Create environmental_service.py for constraint checking
- [ ] Integrate FEMA flood zone API (free public API)
- [ ] Mock CNDDB endangered species lookup (Phase 2: real integration requires CDFW access)
- [ ] Add CalFire wildfire hazard zone detection (free public GIS data)
- [ ] Build ZoningComplianceCard.tsx component with visual compliance indicators
- [ ] Test zoning validation on 50 addresses with known zoning (accuracy check)

**Risks**: Mock zoning data may not reflect real-world complexity (mitigation: document Phase 2 requirements, pilot with single jurisdiction)

---

### Phase 5: Multi-Agency Routing (Week 5-6)
**Estimated Complexity**: Medium  
**Tasks**:
- [ ] Create routing_agent.py with agency assignment logic
- [ ] Define routing rules (project type → reviewing agencies matrix)
- [ ] Implement priority assignment (high: life safety, medium: standard, low: minor)
- [ ] Add workflow dependencies (e.g., Planning approval before Building)
- [ ] Create ReviewAssignment model with assigned_at, due_date, status
- [ ] Implement load balancing algorithm (assign to reviewer with lowest pending count)
- [ ] Build RoutingFlowchart.tsx showing review workflow visually
- [ ] Add reviewer notification emails (assigned, approaching SLA deadline)
- [ ] Test routing logic on 30 sample applications (verify correct agencies assigned)

**Risks**: Complex multi-agency projects may have unclear routing (mitigation: escalation to coordinator for manual triage)

---

### Phase 6: SLA Tracking & Status Queries (Week 6-7)
**Estimated Complexity**: Medium  
**Tasks**:
- [ ] Implement sla_tracker.py with deadline calculation (business days, holidays)
- [ ] Add SLA thresholds by permit type (30 days building, 15 days OTC, 90 days CEQA)
- [ ] Create breach detection (80% threshold warning, 100% breach alert)
- [ ] Build status_query.py with Azure OpenAI natural language interface
- [ ] Implement RAG pattern for status responses (query application DB, format with GPT-4o)
- [ ] Create ApplicationStatus.tsx with chat-like interface
- [ ] Build SLAProgressBar.tsx with green/yellow/red color coding
- [ ] Add applicant notification system (email/SMS via SendGrid or Twilio)
- [ ] Test status query accuracy on 50 sample questions (target ≥95% per SC-006)

**Risks**: SLA calculations complex with holidays, reviewer unavailability (mitigation: use python-dateutil, document holiday schedule)

---

### Phase 7: Reviewer Dashboard & Admin Tools (Week 7)
**Estimated Complexity**: Low  
**Tasks**:
- [ ] Create ReviewerDashboard.tsx with assigned applications list
- [ ] Add filtering (status, priority, SLA status)
- [ ] Implement sorting (oldest first, approaching SLA, priority)
- [ ] Build AdminDashboard.tsx with agency-wide SLA metrics
- [ ] Add workload balancing view (applications per reviewer)
- [ ] Create SLA breach report export (CSV for management)
- [ ] Implement reviewer role in RBAC middleware
- [ ] Test dashboard performance with 500+ applications loaded

**Risks**: Slow dashboard with large datasets (mitigation: pagination, indexing, caching with Redis)

---

### Phase 8: Multi-Language & Accessibility (Week 8)
**Estimated Complexity**: Medium  
**Tasks**:
- [ ] Set up i18next with EN and ES translations
- [ ] Translate all UI strings, permit terminology, checklist descriptions
- [ ] Add ARIA labels to all form inputs, buttons, and interactive elements
- [ ] Implement keyboard navigation for document upload and checklist
- [ ] Test color contrast ratios (≥4.5:1 for normal text)
- [ ] Conduct screen reader testing (NVDA, JAWS)
- [ ] Run axe DevTools automated accessibility scan (target: zero critical violations per SC-009)
- [ ] Measure Spanish-language adoption (target ≥15% per SC-010)

**Risks**: Translation quality for technical permit terms (mitigation: professional translation service, agency review)

---

### Phase 9: Testing & QA (Week 9)
**Estimated Complexity**: Medium  
**Tasks**:
- [ ] Achieve >85% backend test coverage
- [ ] Write E2E Playwright tests for full application submission flow
- [ ] Conduct load testing (100 concurrent applicants submitting applications)
- [ ] Run OWASP ZAP security scan
- [ ] Validate permit identification accuracy ≥92% (SC-001)
- [ ] Validate document validation accuracy ≥85% (SC-002)
- [ ] Test SLA tracking with historical data (verify deadline calculations)
- [ ] User acceptance testing with pilot city staff (5 reviewers, 2 intake staff)

**Risks**: Load testing reveals performance issues (mitigation: optimize Azure AI Search queries, add Redis caching)

---

### Phase 10: Deployment & Monitoring (Week 10)
**Estimated Complexity**: Low  
**Tasks**:
- [ ] Deploy to Azure Container Apps via `azd up`
- [ ] Configure Application Insights with SLA breach alerts
- [ ] Set up custom dashboard for SC-001 through SC-010 metrics
- [ ] Create runbook for on-call support
- [ ] Train pilot city staff on intake wizard, reviewer dashboard, admin tools
- [ ] Launch to pilot city (10% of applications initially)
- [ ] Monitor CSAT ≥4.0/5.0 (SC-007) via post-approval survey
- [ ] Track processing time reduction (target 25% per SC-004)

**Risks**: Azure region outage affecting AI Search or OpenAI (mitigation: multi-region deployment plan, fallback to manual processing)

---

## Success Metrics Tracking

| Metric | Target | Measurement Method | Dashboard |
|--------|--------|-------------------|-----------|
| SC-001: Permit identification accuracy | ≥92% | Expert validation on 200-app sample | Monthly report |
| SC-002: Document validation accuracy | ≥85% | Gold standard 100 site plans | Weekly report |
| SC-003: Application completion rate | ≥75% (from 55% baseline) | Complete vs. corrections requested ratio | Real-time KPI |
| SC-004: Processing time reduction | 25% (45→34 days) | Average days from submission to decision | Monthly KPI |
| SC-005: SLA compliance rate | ≥85% (from 72% baseline) | Applications decided within SLA | Real-time dashboard |
| SC-006: Status query accuracy | ≥95% | Sample validation + latency monitoring | Weekly report |
| SC-007: User satisfaction | ≥4.0/5.0 CSAT | Post-approval survey | Real-time CSAT |
| SC-008: Staff efficiency gain | 50% time savings on intake/status | Before/after time-tracking survey | Quarterly survey |
| SC-009: Accessibility compliance | Zero critical violations | axe DevTools + manual testing | Pre-release checklist |
| SC-010: Spanish adoption | ≥15% of sessions | Language preference analytics | Monthly dashboard |

---

## Open Questions

1. **Pilot City Selection**: Which California city will participate in pilot? Need city with diverse permit types (residential, commercial, environmental), technical capacity for integration, and political will.

2. **Zoning Data Integration**: What GIS platform does pilot city use (Esri ArcGIS, QGIS, other)? API access requirements? Data refresh frequency?

3. **Building Code Updates**: How do agencies track California Building Code triennial updates? Who is responsible for knowledge base updates?

4. **Reviewer Workload Thresholds**: What is reasonable application load per reviewer? (e.g., 20 active applications, 5 new per week?)

5. **SLA Exceptions**: Do agencies have formal processes for SLA extensions (complex projects, applicant-caused delays)? How to document?

6. **Fee Calculation**: Permit fees vary widely by jurisdiction. Use standardized fee schedule or jurisdiction-specific? Integration with payment systems (Phase 2)?

7. **Multi-Jurisdiction Projects**: How to handle projects on city boundaries or requiring county approval (e.g., septic systems)? Coordinated routing?

8. **CEQA Threshold Determination**: Who makes final call on CEQA applicability? Agent provides screening only - need clear escalation path.

9. **Historical Permit Data**: Can pilot city provide 200+ historical applications with final decisions for AI training/validation?

10. **Appeal Process**: If applicant appeals denial or conditions, does agent play any role or fully separate workflow?

---

## Next Steps

1. **Week 1**: Kickoff meeting with OPR, HCD, DCA, pilot city representatives
2. **Week 1**: Provision Azure resources (OpenAI, AI Search, Document Intelligence, Storage) via Bicep
3. **Week 1-2**: Collect permit requirement documentation from pilot city, sample applications for testing
4. **Week 2**: Build and test IntakeAgent with project classification
5. **Week 3**: Seed Azure AI Search knowledge base with permit requirements, building code excerpts
6. **Week 4-5**: Implement document validation and zoning compliance checking
7. **Week 6**: Build routing logic and SLA tracking
8. **Week 7**: Develop reviewer and admin dashboards
9. **Week 8**: Multi-language and accessibility implementation
10. **Week 9**: QA, load testing, user acceptance testing with pilot city staff
11. **Week 10**: Pilot deployment, monitoring, and feedback collection
12. **Week 11+**: Iterate based on pilot feedback, plan Phase 2 (real GIS integration, fee payment, multi-city rollout)
