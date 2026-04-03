# Feature Specification: Medi-Cal Eligibility Agent

**Branch**: `feature/003-medi-cal-eligibility`  
**Date**: 2026-02-02  
**Status**: Draft  
**Agency**: Department of Health Care Services (DHCS)  
**Compliance**: HIPAA, EO N-12-23, DHCS Privacy Requirements

---

## Problem Statement

The California Medi-Cal program serves over 15 million enrollees, making it the nation's largest Medicaid program. Annual eligibility redeterminations and new applicant processing create massive paperwork surges that overwhelm county eligibility workers. The introduction of new asset tests for seniors and disabled individuals in 2026 adds additional complexity to the determination process.

Applicants face:
- Multi-week processing delays for income verification
- Confusion about required documentation
- Lack of real-time application status visibility
- Language barriers in understanding eligibility criteria
- High rejection rates due to incomplete documentation

County eligibility workers face:
- Manual data entry from W-2s, pay stubs, and tax returns
- Complex MAGI and non-MAGI rule application
- HIPAA compliance requirements for all data handling
- Audit trail documentation requirements
- Backlog management with limited staffing

---

## User Scenarios

### P1: Document Upload & Income Extraction

**As an** applicant or county eligibility worker  
**I want to** upload income verification documents and have data automatically extracted  
**So that** I can reduce manual data entry errors and processing time

**Acceptance Scenarios**:

```gherkin
Given I am a Medi-Cal applicant with a W-2 form
When I upload the W-2 PDF to the eligibility agent
Then the system extracts employer name, gross wages, federal income tax withheld
And displays the extracted data for my verification
And flags any PII detected in the document
And stores the document securely with encryption

Given I am uploading a pay stub with multiple income sources
When the system processes the document
Then it identifies year-to-date earnings, pay period, and employer
And calculates annualized income based on pay frequency
And requests clarification if document quality is poor

Given I upload a document in Spanish
When the system performs OCR extraction
Then it correctly extracts data from the Spanish-language document
And displays extracted values in both Spanish and English
```

---

### P2: MAGI-Based Eligibility Pre-Screening

**As an** applicant  
**I want to** receive a preliminary eligibility determination based on my income  
**So that** I can understand my likelihood of qualifying before completing the full application

**Acceptance Scenarios**:

```gherkin
Given I am a single adult with $18,000 annual income in California
When I request eligibility pre-screening
Then the system calculates my income as 109% of FPL (2026 FPL: $16,512)
And determines I am likely eligible for Medi-Cal
And explains that final determination requires county verification
And provides next steps for completing the application

Given I am a family of 4 with $72,000 annual income
When the system evaluates MAGI-based eligibility
Then it calculates income as 198% of FPL (2026 FPL for family of 4: $36,312)
And determines I exceed MAGI Medi-Cal thresholds
And suggests alternative coverage options (Covered California with subsidies)
And logs the screening with masked income data

Given my income changed mid-year due to job loss
When I provide documentation of both employment periods
Then the system uses current monthly income for screening
And applies the correct prospective income methodology
And flags the application for priority processing
```

---

### P3: Document Completeness Validation

**As an** applicant  
**I want to** know if my documentation package is complete before submission  
**So that** I can avoid application delays due to missing documents

**Acceptance Scenarios**:

```gherkin
Given I am applying for Medi-Cal with self-employment income
When the system reviews my uploaded documents
Then it identifies I need Schedule C, Schedule SE, and Form 1040
And flags that I only uploaded Form 1040
And provides a checklist of missing documents with descriptions
And allows me to upload additional documents before final submission

Given I am a senior applying with pension and Social Security income
When the document completeness check runs
Then it verifies I provided SSA-1099 and pension statement
And confirms asset documentation is required for non-MAGI pathway
And generates a personalized document checklist
And estimates my application will be ready for county review

Given I upload documents that are expired or illegible
When the system validates document quality
Then it flags the W-2 as from tax year 2023 (too old for 2026 application)
And requests current year income documentation
And identifies pages with OCR confidence below 85% threshold
And prompts me to re-upload clearer versions
```

---

### P4: Application Status Tracking via Natural Language

**As an** applicant  
**I want to** check my application status using natural language questions  
**So that** I can get updates without calling the county office

**Acceptance Scenarios**:

```gherkin
Given my application was submitted 10 days ago
When I ask "What is the status of my Medi-Cal application?"
Then the system retrieves my application by identity verification
And responds with "Your application was received on [date] and is under county review. Typical processing time is 45 days. Your estimated decision date is [date]."
And provides my application ID for reference
And offers to send status updates via SMS or email

Given my application requires additional documentation
When I ask about my application status
Then the system alerts me that a document request was sent 5 days ago
And lists the specific missing documents
And provides an upload link with deadline information
And warns that missing the deadline may delay processing

Given my application was approved
When I check status
Then the system confirms approval and effective coverage date
And explains how to use my Medi-Cal coverage
And provides my Beneficiary ID number (BIC)
And offers to connect me with a health plan enrollment specialist
```

---

### P5: HIPAA-Compliant Audit Trail

**As a** DHCS compliance officer  
**I want** all data access and eligibility determinations logged with PII masking  
**So that** we maintain HIPAA compliance and support audits

**Acceptance Scenarios**:

```gherkin
Given an eligibility worker accesses an application
When the system logs the access event
Then it records timestamp, worker ID, application ID, and action
And masks all PII (name, SSN, address) in the audit log
And includes reason for access and duration of session
And stores logs in tamper-evident format with cryptographic signing

Given a data breach investigation is initiated
When the compliance team queries audit logs
Then they can trace all access to a specific application
And identify who viewed documents and when
And determine if unauthorized access occurred
And export logs in standard HIPAA audit format

Given automated PII detection runs on uploaded documents
When the system identifies SSN, date of birth, or medical info
Then it logs the PII detection event without storing the actual PII
And applies appropriate encryption and access controls
And flags high-risk documents for manual review
And generates compliance report for DHCS oversight
```

---

### P6: Non-MAGI Evaluation for Seniors/Disabled

**As a** senior or disabled applicant  
**I want** the system to evaluate my eligibility under non-MAGI rules including asset tests  
**So that** I can determine eligibility for programs like Medicare Savings Programs

**Acceptance Scenarios**:

```gherkin
Given I am 68 years old applying for a Medicare Savings Program
When I provide asset documentation (bank statements, investment accounts)
Then the system calculates countable assets excluding primary residence
And compares to $4,000 individual / $6,000 couple limits (2026 thresholds)
And evaluates income under 138% FPL for QMB eligibility
And determines preliminary eligibility for Qualified Medicare Beneficiary program
And routes to county for final asset verification

Given I am disabled with Social Security Disability Income (SSDI)
When the system evaluates my eligibility
Then it applies SSI-linked Medi-Cal methodology
And excludes SSDI from countable income per federal rules
And identifies I may qualify for both Medicare and Medi-Cal
And generates a specialized checklist for dual eligibles
And connects me to Health Insurance Counseling and Advocacy Program (HICAP)

Given I have a special needs trust
When I upload trust documentation
Then the system identifies it as an exempt asset
And flags for manual review by county eligibility specialist
And logs the complex case for expedited human review
And provides estimated timeline for specialized determinations
```

---

## Edge Cases

### Document Processing Edge Cases

**Handwritten W-2s or Pay Stubs**  
- **Challenge**: OCR accuracy drops significantly on handwritten forms  
- **Solution**: Flag low-confidence extractions, prompt for typed/employer-issued documents, offer phone assistance

**Multi-Page Tax Returns (100+ pages)**  
- **Challenge**: Processing time and cost for Document Intelligence API  
- **Solution**: Request specific pages only (1040, Schedules A/B/C/SE), implement page limit warnings, batch processing

**Income in Foreign Currency**  
- **Challenge**: Need exchange rates and tax treaty considerations  
- **Solution**: Request IRS Form 2555 for foreign earned income, integrate with current exchange rate API, flag for manual review

**Self-Employment with Irregular Income**  
- **Challenge**: Annualized income calculations may not reflect current ability to pay  
- **Solution**: Use most recent 3-month average if lower than annual, document methodology in determination

### Eligibility Logic Edge Cases

**Income Volatility (Gig Economy Workers)**  
- **Challenge**: Monthly income varies significantly (ride-share, delivery drivers)  
- **Solution**: Use 3-month rolling average, request platform earnings statements (Uber/Lyft), apply reasonably predictable income rules

**Recent Immigration Status Changes**  
- **Challenge**: Five-year bar for some LPRs, but California covers income-eligible regardless of status for emergency/pregnancy services  
- **Solution**: Route to county for immigration status verification, provide state-funded program information, comply with SB 75 All Kids coverage

**Household Composition Disputes**  
- **Challenge**: Applicant disagrees with tax filer household definition  
- **Solution**: Allow non-filer declaration, document alternative household composition, flag for county review per MAGI regulations

**Aging Out of Parent Coverage**  
- **Challenge**: Young adults turning 26 mid-year losing parent's insurance  
- **Solution**: Detect qualifying life event, expedite processing (10-day turnaround), backdate coverage to loss date if eligible

### HIPAA & Privacy Edge Cases

**Document Contains Third-Party PII**  
- **Challenge**: W-2 includes employer EIN, tax return includes spouse SSN  
- **Solution**: Redact non-applicant SSNs before storage, log all PII detections, apply minimum necessary standard

**Subpoena for Application Records**  
- **Challenge**: Law enforcement or legal requests for protected health information  
- **Solution**: Route to DHCS legal counsel, require proper legal process, log all requests, notify applicant per HIPAA requirements

**Minor Applicant with Non-Custodial Parent Request**  
- **Challenge**: Parent without legal custody requests child's application status  
- **Solution**: Verify custodial parent consent, route to county for custody determination, escalate to DHCS if dispute

### Technical Edge Cases

**BenefitsCal System Downtime**  
- **Challenge**: Cannot submit application to county system  
- **Solution**: Queue applications locally with encryption, auto-retry every 15 minutes, notify applicant of delay, maintain 72-hour local queue

**OCR Extraction Contradicts Applicant-Entered Data**  
- **Challenge**: W-2 shows $32,000 but applicant entered $28,000  
- **Solution**: Flag discrepancy, request confirmation, show extracted vs. entered side-by-side, log correction

**Application Submitted to Wrong County**  
- **Challenge**: Applicant moved mid-process  
- **Solution**: Detect county change via address update, transfer application to correct county, notify both counties, preserve original submission date

---

## Requirements

### Functional Requirements

**FR-001**: Document Upload & Storage  
The system shall accept PDF, JPG, PNG, and TIFF formats for income verification documents with maximum 10MB per file and 50MB per application package. Files must be encrypted at rest using AES-256 and in transit using TLS 1.3.

**FR-002**: OCR Extraction via Azure Document Intelligence  
The system shall use Azure Document Intelligence to extract structured data from W-2s (Box 1, 2, 16, 17), pay stubs (gross pay, YTD earnings, employer, pay period), and Form 1040 (Lines 1, 8, 9, 11). Extraction confidence scores below 85% shall trigger manual review flags.

**FR-003**: Income Calculation Engine  
The system shall calculate annualized income from various sources (wages, self-employment, Social Security, pensions, unemployment, child support) using Pydantic models implementing MAGI and non-MAGI methodologies per 42 CFR 435.603.

**FR-004**: Federal Poverty Level (FPL) Comparison  
The system shall compare calculated MAGI to current FPL guidelines (updated annually) and determine eligibility for Medi-Cal (138% FPL), Medicare Savings Programs (QMB: 100%, SLMB: 120%, QI: 135%), and Covered California subsidies (400% FPL cap).

**FR-005**: Document Completeness Validation  
The system shall generate personalized checklists based on income sources declared and program type (MAGI Medi-Cal, Aged/Blind/Disabled, Medicare Savings Programs, pregnancy, children). Required documents shall include IRS Form 4506-C for tax transcript verification.

**FR-006**: PII Detection & HIPAA Compliance  
The system shall detect and mask SSN (XXX-XX-1234), date of birth, medical record numbers, and diagnosis codes using regex and NER models. All PII access requires authentication with role-based access control (RBAC) and audit logging.

**FR-007**: Audit Trail with Cryptographic Signing  
The system shall log all actions (document upload, data extraction, eligibility screening, status queries) with timestamp, user ID, IP address (hashed), and action outcome. Logs shall be immutable and cryptographically signed for tamper detection.

**FR-008**: Application Status API  
The system shall provide RESTful API for status queries with authentication via Azure Entra ID. Status responses shall include stage (received, document review, county processing, pending interview, approved, denied), estimated completion date, and next actions required.

**FR-009**: BenefitsCal Integration (Mock Mode)  
The system shall implement a mock integration layer for submitting completed applications to BenefitsCal (county eligibility system) with JSON payload containing applicant demographics, income sources, household composition, and uploaded document URLs.

**FR-010**: Multi-Language Support  
The system shall provide user interface and extracted data presentation in English, Spanish, Chinese (Simplified), Vietnamese, Tagalog, and Korean per California Government Code §7290-7299.8.

**FR-011**: Asset Test Evaluation (Non-MAGI)  
The system shall calculate countable assets for seniors/disabled applicants by summing checking accounts, savings accounts, stocks/bonds, and property (excluding primary residence, one vehicle, burial funds up to $1,500). Asset limits: $4,000 individual, $6,000 couple (2026 California thresholds).

**FR-012**: Accessibility Compliance  
The system shall meet WCAG 2.1 Level AA standards including keyboard navigation, screen reader compatibility, color contrast ratios ≥4.5:1, and form field labels with ARIA attributes.

---

## Key Entities

### Application
- **application_id** (UUID): Unique identifier  
- **applicant_id** (UUID): Links to constituent identity (stored in secure system)  
- **status** (enum): `draft`, `submitted`, `document_review`, `county_processing`, `pending_interview`, `approved`, `denied`, `withdrawn`  
- **submitted_at** (timestamp): Application submission date  
- **county** (string): County of residence (1-58 California counties)  
- **program_type** (enum): `magi_adult`, `magi_child`, `aged_blind_disabled`, `medicare_savings`, `pregnancy`  
- **fpl_percentage** (decimal): Calculated income as % of FPL  
- **created_at**, **updated_at** (timestamps)

### Document
- **document_id** (UUID): Unique identifier  
- **application_id** (UUID): Foreign key to Application  
- **document_type** (enum): `w2`, `paystub`, `form_1040`, `schedule_c`, `ssa_1099`, `pension_statement`, `bank_statement`, `other`  
- **file_url** (string): Encrypted blob storage URL  
- **extracted_data** (JSON): Structured data from OCR  
- **processing_status** (enum): `uploaded`, `processing`, `extracted`, `failed`, `manual_review_required`  
- **ocr_confidence** (decimal): 0.0-1.0 confidence score  
- **uploaded_at** (timestamp)

### IncomeRecord
- **income_id** (UUID): Unique identifier  
- **application_id** (UUID): Foreign key to Application  
- **source** (enum): `wages`, `self_employment`, `social_security`, `pension`, `unemployment`, `child_support`, `rental`, `other`  
- **amount** (decimal): Dollar amount  
- **frequency** (enum): `annual`, `monthly`, `biweekly`, `weekly`, `hourly`  
- **verification_status** (enum): `pending`, `verified`, `disputed`  
- **document_id** (UUID): Links to supporting Document  
- **is_countable** (boolean): Per MAGI/non-MAGI rules

### EligibilityResult
- **result_id** (UUID): Unique identifier  
- **application_id** (UUID): Foreign key to Application  
- **program** (string): Program evaluated (e.g., "Medi-Cal MAGI Adult")  
- **eligible** (boolean): Preliminary determination  
- **magi_income** (decimal): Total MAGI income calculated  
- **fpl_percentage** (decimal): % of Federal Poverty Level  
- **household_size** (integer): Tax filer household size  
- **determination_date** (timestamp)  
- **methodology** (enum): `magi`, `non_magi_ssi`, `non_magi_1634`, `medicare_savings`  
- **notes** (text): Explanation for applicant

### AuditEntry
- **entry_id** (UUID): Unique identifier  
- **timestamp** (timestamp): Action occurred time  
- **action** (enum): `document_upload`, `ocr_extraction`, `eligibility_screening`, `status_query`, `application_submit`, `data_access`  
- **actor_id** (string): User ID or system service account  
- **actor_role** (enum): `applicant`, `county_worker`, `dhcs_admin`, `system`  
- **application_id** (UUID): Affected application  
- **pii_detected** (boolean): Whether PII was in accessed data  
- **masked_data** (JSON): PII-masked version of data accessed  
- **ip_address_hash** (string): SHA-256 hash of IP address  
- **signature** (string): Cryptographic signature for tamper detection

---

## Success Criteria

**SC-001**: Document Processing Speed  
95% of uploaded documents processed and OCR-extracted within 30 seconds. Measured via Azure Application Insights performance metrics.

**SC-002**: OCR Accuracy  
Average OCR confidence score ≥92% for W-2s and pay stubs. W-2 Box 1 (wages) extraction accuracy ≥95% when validated against manual review sample.

**SC-003**: Application Completion Rate  
Document completeness validation increases application completion rate from baseline 68% to ≥85% within 3 months of deployment.

**SC-004**: Processing Time Reduction  
Average county eligibility worker processing time per application reduced by 40% (from 45 minutes to ≤27 minutes) due to pre-populated income data.

**SC-005**: HIPAA Compliance  
100% of PII access logged with actor identification. Zero HIPAA violations or unauthorized data disclosures. Monthly compliance audit pass rate 100%.

**SC-006**: User Satisfaction  
Applicant satisfaction score (CSAT) ≥4.2/5.0 for document upload and status tracking features. Measured via post-interaction survey.

**SC-007**: Accessibility Compliance  
Zero critical or serious accessibility violations detected by axe DevTools automated testing. Manual screen reader testing passes 100% of user journeys.

**SC-008**: Status Query Accuracy  
Status query responses accurate ≥98% when compared to BenefitsCal system of record. Latency <2 seconds for 95th percentile queries.

**SC-009**: Multi-Language Adoption  
Spanish-language interface usage ≥18% of total sessions (reflecting California Spanish-speaking population ~28% with lower digital access rates).

**SC-010**: Eligibility Screening Accuracy  
Preliminary eligibility determinations match final county determinations ≥88% of cases (measured on 500-case validation sample over 6 months).

---

## Out of Scope

- Final eligibility determination authority (remains with county eligibility workers)
- Direct integration with BenefitsCal production system (Phase 2)
- Automated interview scheduling (Phase 2)
- Renewal processing (separate accelerator)
- Provider network integration or health plan selection
- Benefit card issuance or claims processing
- Integration with CalFresh, CalWORKs, or other social services (separate agents)
- Appeals process management (separate workflow)

---

## Dependencies

- Azure Document Intelligence API quota and regional availability
- DHCS data classification and security approval
- County stakeholder feedback on BenefitsCal integration requirements
- FPL guidelines updated by HHS annually (typically January)
- Sample document library for OCR model training/validation
- Azure Entra ID tenant for authentication and RBAC

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| OCR fails on poor quality documents | High - applicant frustration, delays | Provide image quality guidelines, real-time upload feedback, phone assistance option |
| HIPAA violation due to PII exposure | Critical - legal liability, public trust | Comprehensive PII detection, encryption, RBAC, penetration testing, privacy impact assessment |
| FPL thresholds change mid-development | Medium - incorrect eligibility screening | Externalize FPL table as config, implement version control, add admin update UI |
| County workers distrust AI-extracted data | High - low adoption | Show OCR confidence scores, side-by-side view with document, allow easy corrections, training program |
| Applicants lack devices for document upload | High - equity concerns | Provide county office kiosk access, mail-in with scanning service, community partner support |

---

## Approval

- [ ] DHCS Privacy Officer review and approval
- [ ] CDT security and compliance review
- [ ] County eligibility supervisor feedback incorporated
- [ ] Accessibility audit scheduled
- [ ] Privacy Impact Assessment (PIA) completed
