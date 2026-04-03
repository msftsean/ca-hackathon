# Feature Specification: Permit Streamliner

**Branch**: `feature/004-permit-streamliner`  
**Date**: 2026-02-02  
**Status**: Draft  
**Agencies**: Governor's Office of Planning and Research (OPR), Housing & Community Development (HCD), Dept of Consumer Affairs (DCA)  
**Compliance**: Breakthrough Project Directive, Envision 2026 Goal 5, EO N-12-23

---

## Problem Statement

The Breakthrough Project mandates that every California state agency streamline permitting and licensing processes using AI. Currently, residents and businesses face:

**Construction Permits**: Multi-month delays for residential and commercial projects. Complex zoning, environmental (CEQA), and building code requirements create confusion and incomplete applications.

**Business Licenses**: Professional licensing (contractors, cosmetologists, real estate) with unclear requirements across 50+ licensing boards under DCA.

**Environmental Reviews**: CEQA compliance uncertainty delays housing and infrastructure projects critical to California's housing crisis.

**Applicants face**:
- Confusion about which permits are required for their project
- Incomplete applications rejected due to missing documents
- No visibility into processing status or SLA timelines
- Manual routing between agencies causing delays
- Contradictory guidance from different agencies

**Agencies face**:
- Manual intake and classification of permit applications
- High volume of incomplete applications requiring follow-up
- Coordination challenges across departments (planning, building, fire, environmental)
- SLA breach tracking requiring manual oversight
- Limited ability to provide proactive status updates

---

## User Scenarios

### P1: Intelligent Permit Application Intake

**As a** property owner planning a home addition  
**I want to** describe my project in natural language and receive a personalized permit checklist  
**So that** I can submit a complete application on the first try

**Acceptance Scenarios**:

```gherkin
Given I am planning a 500 sq ft single-story addition to my single-family home
When I describe my project as "Adding a 20x25 foot family room to the back of my house"
Then the system identifies I need:
  - Building permit (residential addition)
  - Electrical permit (new wiring)
  - Plumbing permit (if adding bathroom)
  - Zoning compliance check (setback requirements)
And generates a checklist with required documents:
  - Site plan showing property boundaries and setbacks
  - Architectural drawings (floor plan, elevations)
  - Structural calculations (if required by size)
  - Title deed or proof of ownership
And provides estimated timeline: 6-8 weeks
And estimates fees: $2,800-$3,500 based on project cost

Given I am opening a restaurant in an existing commercial space
When I describe "Opening a 2,500 sq ft Italian restaurant in downtown Sacramento"
Then the system identifies I need:
  - Business license (City of Sacramento)
  - Health permit (Sacramento County Environmental Health)
  - Building permit (tenant improvements)
  - Fire safety inspection
  - ABC license application (if serving alcohol)
  - Sign permit (if exterior signage)
And routes to multiple agencies with coordinated checklist
And flags CEQA exemption eligibility (existing space, no new construction)

Given my project is in a historic district
When I input the address
Then the system detects historic overlay zone
And adds Historic Preservation Commission review to requirements
And increases timeline estimate by 4-6 weeks
And provides link to design guidelines
```

---

### P2: Document Completeness Pre-Check

**As an** applicant submitting permit documents  
**I want** the system to validate my documents before official submission  
**So that** I avoid rejections and delays due to missing or incorrect documents

**Acceptance Scenarios**:

```gherkin
Given I am applying for a residential building permit
When I upload my site plan PDF
Then the system validates:
  - Property boundaries are shown
  - Setback dimensions are labeled
  - Proposed structure location is marked
  - Scale and north arrow are present
And provides confidence score for each requirement (e.g., 95% confident setbacks shown)
And flags if any required elements are missing

Given I upload architectural drawings
When the system processes the PDF
Then it extracts:
  - Total square footage of addition
  - Number of stories
  - Room designations (bedroom, bathroom, living, etc.)
  - Wall heights and roof pitch
And cross-references against zoning maximums (height limit, lot coverage)
And alerts if drawings indicate code violations

Given I am missing a required document (structural calculations)
When I attempt to submit my application
Then the system blocks submission
And highlights the missing document in red
And explains why it's required ("Additions over 400 sq ft require structural engineer certification per Section R301.1.3")
And offers to connect me with licensed engineers in my area

Given I upload documents for a project requiring CEQA review
When the system analyzes the project description
Then it determines CEQA exemption category (if applicable)
And generates preliminary environmental checklist
And flags potential environmental concerns (wetlands, endangered species habitat, wildfire hazard zones)
And provides guidance on environmental document requirements
```

---

### P3: Real-Time Status Tracking with SLA Monitoring

**As an** applicant with a pending permit  
**I want to** query my permit status in natural language and see SLA-aware progress  
**So that** I know when to expect a decision and can plan construction timeline

**Acceptance Scenarios**:

```gherkin
Given my building permit was submitted 15 days ago
When I ask "What's the status of my permit?"
Then the system responds:
  "Your building permit (BP-2026-001234) was received on January 10, 2026 and is currently under plan review. The typical processing time is 30 business days. Your application is on track, with an estimated decision date of February 20, 2026. A plan reviewer will contact you within 5 business days if additional information is needed."
And displays progress bar: 50% complete (15 of 30 days)
And shows current stage: "Plan Review - Structural" with reviewer name

Given my permit has been in review for 45 days (exceeding 30-day SLA)
When I check status
Then the system alerts me to the delay
And explains: "Your application is past the standard 30-day review period due to structural engineering review requiring additional calculations. A supervisor has been notified. Expected completion: February 28, 2026."
And provides escalation contact: "For urgent concerns, contact [Supervisor Name] at [phone]"
And logs SLA breach for agency performance tracking

Given I ask "When will the fire inspection happen?"
When my permit is approved but awaiting inspection
Then the system responds with inspection scheduling guidance
And provides available inspection slots if online scheduling is enabled
And explains: "Fire inspections are typically scheduled 2-3 business days after approval. You can schedule online or call [phone] Monday-Friday 8am-4pm."

Given my application requires corrections
When I ask about next steps
Then the system lists specific deficiencies:
  - "Corrected site plan showing 5-foot side setback (currently shows 3 feet)"
  - "Structural calculations for roof beam LVL-1 signed by licensed engineer"
And provides deadline: "Corrections must be submitted within 30 days to avoid re-application fees"
And offers upload link for revised documents
```

---

### P4: Cross-Reference Validation (Zoning, Environmental, Code)

**As a** permit reviewer  
**I want** the system to automatically check project compliance against zoning, environmental, and building code requirements  
**So that** I can focus on complex issues rather than routine validation

**Acceptance Scenarios**:

```gherkin
Given an applicant submits a project for 3-story mixed-use building
When the system cross-references against zoning data
Then it checks:
  - Zoning district: C-2 (General Commercial)
  - Max height allowed: 45 feet
  - Proposed height: 38 feet (COMPLIANT)
  - Max lot coverage: 85%
  - Proposed coverage: 78% (COMPLIANT)
  - Parking requirements: 1 space per 400 sq ft commercial + 1.5 per residential unit
  - Provided: 24 spaces, Required: 22 spaces (COMPLIANT)
And generates compliance summary report for reviewer

Given a project is located in a flood zone
When the system analyzes the parcel address
Then it detects FEMA flood zone designation: AE (100-year floodplain)
And flags requirements:
  - Elevation certificate required
  - Lowest floor must be at or above Base Flood Elevation
  - Flood insurance disclosure mandatory
And adds flood zone compliance to document checklist

Given a project triggers CEQA thresholds
When the proposed square footage exceeds exemption limits
Then the system identifies required environmental review type:
  - Initial Study (IS) required for 10,000-50,000 sq ft commercial
  - Environmental Impact Report (EIR) potentially required if significant impacts
And checks sensitive area databases:
  - California Natural Diversity Database (CNDDB) for endangered species
  - State Water Resources Control Board for water quality
  - CalFire hazard severity zones for wildfire risk
And generates preliminary environmental constraint map

Given a residential addition includes electrical work
When the system analyzes the project description
Then it validates California Electrical Code requirements:
  - GFCI outlets required in kitchen, bathrooms, garage
  - AFCI circuit breakers for living areas
  - Smoke alarms (interconnected, in each bedroom and hallway)
  - Carbon monoxide alarms if gas appliances present
And adds these items to inspection checklist
And flags if drawings don't show required safety devices
```

---

### P5: Automated Routing to Reviewing Agencies

**As a** permit intake coordinator  
**I want** applications automatically routed to the correct reviewing department and external agencies  
**So that** processing begins immediately without manual triage

**Acceptance Scenarios**:

```gherkin
Given a commercial building permit application is submitted
When the system analyzes project type and scope
Then it routes to:
  - Building Division (primary reviewer) - Priority: High
  - Fire Department (life safety review) - Priority: High
  - Public Works (site drainage, utilities) - Priority: Medium
  - Planning Department (zoning compliance) - Priority: Medium
And creates workflow with dependencies:
  - Planning must approve before Building can issue
  - Fire and Building can review in parallel
And assigns to available reviewers based on workload balancing

Given an application requires state-level environmental review
When CEQA triggers are detected
Then the system routes to:
  - California Department of Fish and Wildlife (if biological resources)
  - State Water Resources Control Board (if water quality impacts)
  - California Coastal Commission (if coastal zone project)
And generates state agency notification letters
And tracks response deadlines (30 days for state agency comments)

Given a contractor license application is submitted
When DCA receives the application
Then the system routes based on license type:
  - Contractors State License Board (CSLB) for general contractors
  - Board of Barbering and Cosmetology for cosmetology licenses
  - Bureau of Real Estate for real estate brokers
And validates completeness (exam scores, insurance, bond, experience verification)
And triggers background check workflow if criminal history questions answered yes

Given a project is in multiple jurisdictions (city + county)
When the address spans city limits boundary
Then the system identifies both jurisdictions
And creates coordinated review process
And alerts applicant: "Your project is in [City] but may require [County] approval for [reason, e.g., septic system outside city sewer service area]"
And provides both agencies' contact information
```

---

## Edge Cases

### Project Type Edge Cases

**Ambiguous Project Descriptions**  
- **Challenge**: Applicant describes "home improvement" without details  
- **Solution**: Ask clarifying questions (interior/exterior? square footage? structural changes?), provide common project type examples, offer phone consultation option

**Multi-Phase Projects**  
- **Challenge**: Large development with phased construction over years  
- **Solution**: Identify master permit + phase-specific permits, flag dependencies, create multi-year timeline, coordinate with planning's vesting tentative map process

**Emergency Repairs vs. Permits**  
- **Challenge**: Applicant needs emergency plumbing/electrical repair but asks about permit requirements  
- **Solution**: Detect urgency keywords ("leak", "no heat", "electrical fire"), provide emergency contact info, explain that safety repairs can begin immediately with post-work permits

**Projects Requiring Multiple License Types**  
- **Challenge**: General contractor + specialized trades (electrical, plumbing) all need separate licenses  
- **Solution**: Generate multi-license checklist, flag if applicant-listed contractor lacks required licenses, integrate with CSLB license verification API

### Zoning & Code Edge Cases

**Properties with Multiple Zoning Designations**  
- **Challenge**: Split-zoned parcels with different regulations on each portion  
- **Solution**: Detect split zoning, require site plan showing zone boundary, apply most restrictive regulations unless variance approved

**Grandfathered Non-Conforming Uses**  
- **Challenge**: Existing building doesn't meet current code but was legal when built  
- **Solution**: Flag non-conformity, escalate to planner for legal non-conforming determination, document historical permits in system

**Cumulative Code Changes During Review**  
- **Challenge**: Code update occurs during 30-day review period  
- **Solution**: Apply code version in effect at application submission date per "vested rights" principle, document code version in approval

**Conflicting Requirements (State vs. Local)**  
- **Challenge**: State housing law (e.g., SB 9 lot splits) conflicts with local zoning  
- **Solution**: Flag state preemption, provide guidance on ministerial approval requirements, escalate to city attorney if needed

### Environmental Review Edge Cases

**Categorical Exemption Disputes**  
- **Challenge**: Applicant claims CEQA exemption but community members dispute  
- **Solution**: Flag public interest keywords in comments, require environmental coordinator review, document exemption justification thoroughly

**Late Discovery of Hazardous Materials**  
- **Challenge**: Phase I Environmental Site Assessment reveals contamination after application submitted  
- **Solution**: Halt permit processing, require Phase II investigation, coordinate with DTSC (Dept of Toxic Substances Control), add remediation to requirements

**Tribal Consultation Requirements (AB 52)**  
- **Challenge**: Project may affect tribal cultural resources  
- **Solution**: Check California Historical Resources Information System (CHRIS), identify nearby tribal lands, trigger AB 52 consultation if within notification area, add 30-day tribal response period to timeline

### Process & Timeline Edge Cases

**Applicant Unresponsive to Correction Requests**  
- **Challenge**: 30-day correction deadline passes without resubmission  
- **Solution**: Auto-email reminders at 15 days, 25 days, expire application at 30 days with re-application notice, preserve submitted docs for 60 days

**Reviewer Workload Imbalance**  
- **Challenge**: One reviewer has 50 pending applications, others have 10  
- **Solution**: Load balancing algorithm assigns new apps to least-busy qualified reviewer, flag SLA breaches for supervisor redistribution, track reviewer performance metrics

**System Downtime During Submission**  
- **Challenge**: Applicant's submission fails due to server outage  
- **Solution**: Auto-save draft progress every 30 seconds, allow submission resume after reconnection, preserve original submission timestamp if outage documented

**Appeal Filed After Permit Denial**  
- **Challenge**: Applicant appeals denial, new review process begins  
- **Solution**: Create appeal workflow with separate timeline (15 business days for appeal hearing), preserve original application and denial rationale, assign to appeals board/hearing officer (outside agent scope - escalate)

---

## Requirements

### Functional Requirements

**FR-001**: Natural Language Project Intake  
The system shall accept project descriptions in natural language (English, Spanish) and classify project type using Azure OpenAI GPT-4o into categories: residential_addition, new_residential, commercial_new, commercial_tenant_improvement, demolition, grading, sign, fence, pool, solar, professional_license, business_license, environmental_review, variance, appeal.

**FR-002**: Permit Requirement Identification  
The system shall cross-reference project type, address, and scope against a knowledge base of permit requirements (building, electrical, plumbing, mechanical, fire, health, environmental, business license) and generate a personalized checklist with descriptions, required documents, estimated fees, and timelines.

**FR-003**: Zoning Compliance Validation  
The system shall integrate with parcel/zoning GIS data to retrieve zoning district, allowed uses, height limits, setback requirements, lot coverage maximums, and parking requirements. It shall validate proposed project parameters against these regulations and flag non-compliance or variance needs.

**FR-004**: Environmental Constraint Checking  
The system shall query California environmental databases (FEMA flood zones, CNDDB for endangered species, CHRIS for cultural resources, CalFire wildfire hazard zones, State Water Resources Control Board impaired waters) and flag potential CEQA triggers, exemption eligibility, or required mitigation measures.

**FR-005**: Document Completeness Validation  
The system shall use Azure Document Intelligence to analyze uploaded PDFs (site plans, architectural drawings, engineering reports) and validate presence of required elements (property boundaries, setbacks, room labels, structural stamps, title blocks with scale/date). Confidence scores ≥80% required, below threshold flags for human review.

**FR-006**: Automated Multi-Agency Routing  
The system shall route applications to appropriate reviewing departments (Building, Planning, Fire, Public Works, Environmental Health) and external agencies (state Fish & Wildlife, Water Board, Coastal Commission) based on project type and triggers. Routing includes priority assignment (high/medium/low) and workflow dependencies (e.g., Planning approval before Building).

**FR-007**: SLA Tracking & Breach Alerting  
The system shall track processing time against agency-specific SLAs (e.g., 30 business days for building permits, 15 days for over-the-counter permits, 90 days for CEQA review) and alert supervisors when applications approach 80% of SLA deadline. SLA breach logs shall be generated for performance reporting.

**FR-008**: Natural Language Status Queries  
The system shall respond to status queries in natural language (e.g., "When will my permit be ready?", "Why is my application taking so long?") using Azure OpenAI with RAG from application database. Responses include current stage, responsible reviewer, estimated completion date, and next steps required from applicant.

**FR-009**: Code Cross-Reference (Building, Fire, Electrical)  
The system shall maintain knowledge base of California Building Code (CBC), California Fire Code (CFC), California Electrical Code (CEC), and California Plumbing Code (CPC) requirements. It shall identify applicable code sections based on project type and flag common compliance items (GFCI outlets, smoke alarms, fire sprinklers, accessibility).

**FR-010**: Multi-Language Support  
The system shall provide user interface and generated checklists in English and Spanish per California Government Code §7290-7299.8. Natural language processing shall detect language preference from initial query.

**FR-011**: Applicant Notification System  
The system shall send automated notifications via email and SMS for status changes (application received, in review, corrections needed, approved, inspection scheduled). Notifications shall include application ID, next steps, and direct links to applicant portal.

**FR-012**: Reviewer Workload Dashboard  
The system shall provide agency staff with dashboard showing assigned applications, pending count, SLA status (green/yellow/red), and average days in review. Load balancing algorithm distributes new applications to reviewers with capacity.

---

## Key Entities

### PermitApplication
- **application_id** (UUID): Unique identifier  
- **applicant** (object): Name, email, phone (PII encrypted)  
- **project_type** (enum): Type of project/permit  
- **address** (object): Parcel address, APN (Assessor's Parcel Number)  
- **status** (enum): `draft`, `submitted`, `plan_review`, `corrections_requested`, `approved`, `denied`, `inspection_scheduled`, `permit_issued`  
- **submitted_at** (timestamp): Submission date  
- **sla_deadline** (date): Target decision date based on permit type  
- **estimated_decision_date** (date): Current estimate accounting for delays  

### RequiredDocument
- **document_type** (string): E.g., "Site Plan", "Architectural Drawings"  
- **description** (text): What document must contain  
- **required_for** (array): Permit types requiring this document  
- **status** (enum): `not_uploaded`, `uploaded`, `validated`, `corrections_needed`  
- **uploaded_at** (timestamp): Upload date  
- **validation_confidence** (decimal): 0.0-1.0 from AI validation  

### PermitType
- **type_id** (string): E.g., "BP" (Building Permit), "EL" (Electrical)  
- **name** (string): Full permit name  
- **agency** (string): Issuing department/agency  
- **requirements** (array): Required documents, inspections, fees  
- **typical_timeline** (integer): Days for standard processing  
- **fees** (object): Base fee + calculation method  
- **sla_days** (integer): Service level agreement timeframe  

### ZoningCheck
- **address** (string): Project address  
- **apn** (string): Assessor's Parcel Number  
- **zone_code** (string): E.g., "R-1" (Single Family Residential), "C-2" (Commercial)  
- **permitted_uses** (array): Allowed land uses in this zone  
- **restrictions** (object): Height, setbacks, lot coverage, parking  
- **status** (enum): `compliant`, `non_compliant`, `variance_required`, `pending_review`  
- **compliance_notes** (text): Specific issues or confirmations  

### ReviewAssignment
- **application_id** (UUID): Foreign key to PermitApplication  
- **agency** (string): E.g., "Building Division", "Fire Department"  
- **reviewer** (string): Assigned staff member (PII)  
- **assigned_at** (timestamp): Assignment date  
- **due_date** (date): When review must be completed  
- **status** (enum): `pending`, `in_progress`, `approved`, `corrections_requested`, `denied`  
- **comments** (text): Reviewer notes  
- **priority** (enum): `low`, `medium`, `high`, `urgent`  

---

## Success Criteria

**SC-001**: Permit Identification Accuracy  
System correctly identifies all required permits for a project with ≥92% accuracy when validated against experienced permit technician reviews (sample of 200 applications).

**SC-002**: Document Completeness Validation Accuracy  
AI validation of uploaded documents achieves ≥85% accuracy in detecting missing required elements (site plan validation study on 100 sample plans).

**SC-003**: Application Completion Rate Improvement  
Percentage of applications submitted complete on first try increases from baseline 55% to ≥75% within 6 months of deployment due to upfront checklist and validation.

**SC-004**: Average Processing Time Reduction  
Average time from application submission to decision reduced by 25% (from 45 days to ≤34 days for building permits) due to automated routing and SLA monitoring.

**SC-005**: SLA Compliance Rate  
Percentage of applications processed within SLA deadline increases from baseline 72% to ≥85% due to proactive breach alerting and workload balancing.

**SC-006**: Status Query Response Accuracy  
Natural language status query responses accurate ≥95% when compared to actual application status in database. Response latency <3 seconds for 95th percentile.

**SC-007**: User Satisfaction  
Applicant CSAT score ≥4.0/5.0 for permit intake and status tracking features (post-approval survey).

**SC-008**: Agency Staff Efficiency  
Permit reviewer time spent on manual intake triage and status inquiries reduced by 50% (measured via time-tracking survey before/after deployment).

**SC-009**: Accessibility Compliance  
Zero critical or serious accessibility violations detected by axe DevTools. WCAG 2.1 Level AA compliance verified.

**SC-010**: Multi-Language Adoption  
Spanish-language interface usage ≥15% of total sessions (reflecting California Spanish-speaking population with lower small business formation rates).

---

## Out of Scope

- Final permit approval authority (remains with licensed plan reviewers and building officials)
- On-site inspection scheduling and mobile inspection apps (separate system)
- Fee payment processing integration (Phase 2)
- Appeals hearing management and board packet generation
- Integration with CAD/GIS systems for automated zoning analysis (Phase 2 - pilot with mock zoning data)
- Cross-jurisdictional permit reciprocity (e.g., state license valid in all counties)
- Building permit plan set markup and redlining tools for reviewers
- Contractor license examination and testing (DCA CSLB responsibility)
- Business tax certificate issuance (separate finance department system)

---

## Dependencies

- Access to county/city parcel and zoning GIS data (mock data for pilot)
- California Building Code knowledge base (HTML/PDF scraping or API if available)
- Azure OpenAI API quota for GPT-4o (high volume during intake surges)
- Azure Document Intelligence quota for plan validation
- Azure AI Search index for regulatory knowledge base
- Sample permit applications and approved plan sets for validation testing
- Agency stakeholder review of permit requirement rules and workflows

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Zoning data outdated or incomplete | High - incorrect compliance guidance | Mock data for pilot, document data refresh requirements, flag low-confidence zoning determinations for manual verification |
| AI misclassifies complex projects | High - wrong permits identified | Confidence thresholds with human review <85%, feedback loop from reviewers corrects misclassifications, extensive testing on historical applications |
| Code requirements change frequently | Medium - stale guidance provided | Quarterly knowledge base updates, version tracking in responses, subscribe to California Building Standards Commission updates |
| Applicants lack technical knowledge to describe projects | High - poor project descriptions → wrong permits | Guided intake wizard with visual examples, "I don't know" option triggers phone consultation, common project templates (ADU, garage, room addition) |
| Agencies resist AI routing decisions | High - low adoption | Pilot with single agency (e.g., City of Sacramento Planning Dept), emphasize AI as triage tool not replacement, transparent routing logic with override capability |
| CEQA analysis too complex for AI | Critical - environmental violations | Scope limited to exemption screening and constraint flagging, all substantive CEQA review by qualified planners, disclaimer on preliminary analysis |

---

## Approval

- [ ] Governor's Office of Planning and Research (OPR) policy review
- [ ] Housing & Community Development (HCD) housing permit process validation
- [ ] Dept of Consumer Affairs (DCA) licensing requirements review
- [ ] California Building Officials (CALBO) code interpretation review
- [ ] Pilot city/county selection and MOU signed
- [ ] CDT security and accessibility review
- [ ] Privacy Impact Assessment (PIA) for PII handling (applicant names, addresses)
