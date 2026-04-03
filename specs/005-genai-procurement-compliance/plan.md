# Implementation Plan: GenAI Procurement Compliance Checker

**Branch**: `005-genai-procurement-compliance` | **Date**: 2024-12-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-genai-procurement-compliance/spec.md`

## Summary

Automated vendor AI attestation review system that analyzes procurement documents against California EO N-5-26 requirements, generates severity-weighted compliance scores, performs gap analysis with SB 53 and NIST AI RMF cross-referencing, and maintains immutable audit trail. System leverages Azure OpenAI for document analysis, Semantic Kernel for rule evaluation, and FastAPI backend with React frontend for procurement officer workflow.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5+ (frontend)  
**Primary Dependencies**: FastAPI, Pydantic v2, Semantic Kernel, pypdf, python-docx, Azure OpenAI SDK, React 18, Vite, Tailwind CSS  
**Storage**: Azure Blob Storage (attestation documents), async SQLite (audit logs, compliance rules cache), Azure AI Search (document indexing)  
**Testing**: pytest (backend), vitest (frontend), Playwright (E2E)  
**Target Platform**: Linux containers (Docker), Azure Container Apps  
**Project Type**: Web application with document processing pipeline and AI-powered compliance analysis  
**Performance Goals**: <5 minute analysis for 95% of documents (50 pages), 50 concurrent analyses, <300ms API response time  
**Constraints**: WCAG 2.1 AA compliance, 7-year audit retention, NIST AI RMF governance, EO N-12-23 transparency requirements  
**Scale/Scope**: 200+ state agencies, 500-1000 vendor attestations per year, 50-100 concurrent procurement officers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Security & Compliance Requirements** (Constitution-driven):
- ✅ Azure Entra ID authentication with role-based access control (procurement officer, compliance officer, auditor roles)
- ✅ AES-256 encryption at rest for vendor attestation documents (sensitive procurement data)
- ✅ TLS 1.3 for all data in transit
- ✅ Immutable audit logging with 7-year retention per California public records requirements
- ✅ AI transparency labeling per EO N-12-23 (all AI-generated analysis tagged with confidence scores and model version)
- ✅ Human oversight requirement (procurement officers can override AI findings with mandatory justification)
- ✅ NIST AI RMF compliance (risk classification, documentation, governance)
- ✅ WCAG 2.1 AA accessibility for all reports and UI components
- ✅ No PII storage (vendor attestations may contain company information but not individual PII)
- ✅ California Public Records Act compliance (audit trail supports CPRA requests)

**Regulatory Alignment**:
- Primary: Executive Order N-5-26 (GenAI Procurement Requirements)
- Secondary: Senate Bill 53 (Automated Decision Systems)
- Framework: NIST AI Risk Management Framework
- Governance: Executive Order N-12-23 (GenAI Governance)
- Data: California Public Records Act, Envision 2026 Goal 4

## Project Structure

### Documentation (this feature)

```text
specs/005-genai-procurement-compliance/
├── spec.md              # Feature specification (COMPLETE)
├── plan.md              # This file (COMPLETE)
├── data-model.md        # Entity and relationship definitions (COMPLETE)
├── research.md          # Phase 0: Compliance rule research, document parsing evaluation
├── contracts/           # Phase 1: API contracts, compliance rule schemas
├── quickstart.md        # Phase 1: Local dev setup, sample attestations
└── tasks.md             # Phase 2: Implementation tasks (generated separately)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── vendor_attestation.py       # VendorAttestation entity
│   │   ├── compliance_rule.py          # ComplianceRule entity
│   │   ├── compliance_result.py        # ComplianceResult entity
│   │   ├── gap_analysis.py             # GapAnalysis entity
│   │   ├── audit_record.py             # AuditRecord entity
│   │   └── procurement_decision.py     # ProcurementDecision entity
│   ├── services/
│   │   ├── document_parser.py          # pypdf + python-docx integration
│   │   ├── compliance_analyzer.py      # Semantic Kernel rule evaluation
│   │   ├── scoring_engine.py           # Severity-weighted scoring
│   │   ├── gap_analyzer.py             # Gap identification and remediation
│   │   ├── cross_reference.py          # SB 53 + NIST AI RMF cross-check
│   │   ├── report_generator.py         # PDF/DOCX report export
│   │   └── audit_logger.py             # Immutable audit trail
│   ├── api/
│   │   ├── attestation_routes.py       # Upload, analyze, retrieve endpoints
│   │   ├── compliance_routes.py        # Score, gap analysis endpoints
│   │   ├── report_routes.py            # Report generation endpoints
│   │   └── audit_routes.py             # Audit log query endpoints
│   ├── storage/
│   │   ├── blob_storage.py             # Azure Blob Storage client
│   │   ├── db_client.py                # Async SQLite client
│   │   └── search_client.py            # Azure AI Search client
│   └── auth/
│       ├── entra_id.py                 # Azure Entra ID integration
│       └── rbac.py                     # Role-based access control
└── tests/
    ├── unit/
    │   ├── test_document_parser.py
    │   ├── test_compliance_analyzer.py
    │   ├── test_scoring_engine.py
    │   └── test_gap_analyzer.py
    ├── integration/
    │   ├── test_attestation_workflow.py
    │   ├── test_compliance_pipeline.py
    │   └── test_audit_trail.py
    └── contract/
        ├── test_api_contracts.py
        └── test_compliance_rules.py

frontend/
├── src/
│   ├── components/
│   │   ├── AttestationUpload.tsx       # Document upload UI
│   │   ├── ComplianceScorecard.tsx     # Score visualization
│   │   ├── GapAnalysisTable.tsx        # Gap results display
│   │   ├── VendorComparison.tsx        # Side-by-side comparison
│   │   ├── ReportExport.tsx            # Report generation controls
│   │   └── AuditLogViewer.tsx          # Audit trail display
│   ├── pages/
│   │   ├── Dashboard.tsx               # Main procurement dashboard
│   │   ├── AttestationDetail.tsx       # Single attestation analysis view
│   │   ├── ComparisonView.tsx          # Multi-vendor comparison
│   │   └── AuditLog.tsx                # Audit log query interface
│   ├── services/
│   │   ├── attestation-api.ts          # Attestation API client
│   │   ├── compliance-api.ts           # Compliance API client
│   │   ├── report-api.ts               # Report API client
│   │   └── auth-service.ts             # MSAL + Entra ID client
│   └── hooks/
│       ├── useAttestation.ts           # Attestation state management
│       ├── useCompliance.ts            # Compliance state management
│       └── useAuth.ts                  # Authentication state
└── tests/
    ├── unit/
    │   └── components/
    ├── integration/
    │   └── workflows/
    └── e2e/
        └── playwright/
            ├── attestation-upload.spec.ts
            ├── compliance-analysis.spec.ts
            └── audit-trail.spec.ts

shared/
├── compliance-rules/
│   ├── eo-n-5-26-rules.json           # EO N-5-26 requirement definitions
│   ├── sb-53-rules.json               # SB 53 requirement definitions
│   └── nist-ai-rmf-rules.json         # NIST AI RMF criteria
└── schemas/
    ├── attestation-schema.json         # Attestation entity schema
    ├── compliance-result-schema.json   # Result entity schema
    └── audit-record-schema.json        # Audit record schema
```

**Structure Decision**: Web application architecture selected based on:
- User-facing procurement officer workflow requiring React frontend
- Document processing and AI analysis requiring Python backend with Semantic Kernel
- Separation of concerns between UI (React), business logic (FastAPI services), and AI (Semantic Kernel + Azure OpenAI)
- Shared compliance rules stored in `/shared` for consistency across backend rules engine and frontend display

## Complexity Tracking

> **No constitution violations identified. All complexity is justified by regulatory requirements.**

| Aspect | Justification | Simpler Alternative Rejected Because |
|--------|---------------|--------------------------------------|
| Immutable audit trail | California Public Records Act + procurement accountability requirements mandate complete, tamper-proof event logging | Mutable database logs insufficient for legal compliance and fraud prevention |
| Multi-framework compliance (EO N-5-26 + SB 53 + NIST) | Vendors must comply with overlapping state and federal AI regulations; single-framework analysis misses critical requirements | Single-regulation check creates legal liability; CDT legal counsel requires comprehensive coverage |
| Severity-weighted scoring | Different compliance gaps have vastly different risk levels; unweighted scoring obscures critical failures | Simple pass/fail or unweighted scoring fails to prioritize disqualifying gaps vs. minor issues |
| Human-in-the-loop override | EO N-12-23 mandates human decision-making authority; AI cannot make final procurement decisions | Fully automated decisions violate state AI governance policy and procurement law |
| Document parsing (pypdf + python-docx) | Vendor attestations arrive in various formats; must handle both digital-native and scanned PDFs | Single parser insufficient; OCR may be needed for scanned documents (to be evaluated in research phase) |
