# Data Model: GenAI Procurement Compliance Checker

**Feature**: `005-genai-procurement-compliance`  
**Created**: 2024-12-19  
**Purpose**: Entity definitions and relationships for vendor AI attestation compliance analysis system

## Core Entities

### VendorAttestation

Represents uploaded vendor AI attestation document submitted during procurement process.

**Attributes**:
- `attestation_id` (UUID, primary key): Unique identifier for attestation
- `vendor_name` (str, required): Legal name of vendor submitting attestation
- `vendor_contact` (str, optional): Primary contact email for vendor
- `procurement_id` (str, required): Reference to procurement cycle/RFP ID
- `submitted_by` (str, required): Email of user who uploaded document (typically procurement officer)
- `submitted_at` (datetime, required): Timestamp of document upload
- `document_url` (str, required): Azure Blob Storage path to original document
- `document_hash` (str, required): SHA-256 hash for integrity verification
- `file_format` (enum: PDF, DOCX): Original document format
- `file_size_bytes` (int, required): File size for quota management
- `page_count` (int, optional): Number of pages (extracted during parsing)
- `status` (enum, required): Processing status - `uploaded`, `parsing`, `analyzing`, `complete`, `failed`, `requires_human_review`
- `analysis_started_at` (datetime, optional): When automated analysis began
- `analysis_completed_at` (datetime, optional): When automated analysis finished
- `assigned_to` (str, optional): Procurement officer assigned to review
- `created_at` (datetime, required): Record creation timestamp
- `updated_at` (datetime, required): Record last update timestamp
- `version` (int, default: 1): Version number for attestation updates
- `previous_version_id` (UUID, optional): Link to previous version if attestation was resubmitted
- `metadata` (JSON, optional): Additional document metadata (author, creation date, software)

**Relationships**:
- One-to-many with `ComplianceResult`: Each attestation has multiple compliance results (one per rule)
- One-to-one with `GapAnalysis`: Each attestation has one aggregated gap analysis
- One-to-many with `AuditRecord`: Each attestation generates multiple audit events
- One-to-one with `ProcurementDecision`: Each attestation may have final procurement decision

**Indexes**:
- Primary: `attestation_id`
- Secondary: `vendor_name`, `procurement_id`, `status`, `submitted_at`
- Composite: `(procurement_id, vendor_name)` for vendor comparison within procurement cycle

**Security**:
- Row-level security based on `procurement_id` - users can only access attestations for procurements they're assigned to
- Document URL requires signed SAS token with 1-hour expiration
- Soft delete only (mark as `deleted_at` rather than removing record) for audit compliance

---

### ComplianceRule

Represents individual compliance requirement from EO N-5-26, SB 53, or NIST AI RMF.

**Attributes**:
- `rule_id` (str, primary key): Unique identifier (e.g., `EO-N-5-26-001`, `SB-53-BIAS-001`, `NIST-RMF-GOVERN-1.1`)
- `source` (enum, required): Regulation source - `EO_N_5_26`, `SB_53`, `NIST_AI_RMF`, `CDT_GENAI_GUIDELINES`
- `category` (str, required): Requirement category (e.g., `content_safety`, `bias_governance`, `civil_rights`, `transparency`)
- `requirement_text` (str, required): Full text of compliance requirement
- `requirement_summary` (str, required): Brief summary for UI display (max 100 chars)
- `severity` (enum, required): Gap severity level - `critical`, `high`, `medium`, `low`
- `evaluation_guidance` (str, required): Instructions for AI model on how to evaluate this requirement
- `evidence_keywords` (list[str], optional): Keywords that indicate compliance (e.g., ["bias testing", "fairness audit"])
- `remediation_template` (str, optional): Suggested language vendor should include to satisfy requirement
- `legal_citation` (str, optional): Full legal citation with section number
- `effective_date` (date, required): When this requirement became effective
- `sunset_date` (date, optional): When requirement expires (if applicable)
- `parent_rule_id` (str, optional): Parent requirement if this is sub-requirement
- `requires_human_review` (bool, default: False): Flag for rules that always need human verification
- `version` (int, default: 1): Rule version for requirement updates
- `created_at` (datetime, required): Rule creation timestamp
- `updated_at` (datetime, required): Rule last update timestamp
- `metadata` (JSON, optional): Additional rule configuration (regex patterns, threshold values)

**Relationships**:
- One-to-many with `ComplianceResult`: Each rule generates results across multiple attestations
- Self-referential: `parent_rule_id` creates hierarchy for complex requirements

**Indexes**:
- Primary: `rule_id`
- Secondary: `source`, `category`, `severity`, `effective_date`
- Full-text: `requirement_text` for rule search

**Data Loading**:
- Rules loaded from `shared/compliance-rules/*.json` files at application startup
- Updated via admin API when regulations change (creates new version, preserves historical rules)

---

### ComplianceResult

Represents analysis outcome for specific compliance rule applied to specific vendor attestation.

**Attributes**:
- `result_id` (UUID, primary key): Unique identifier for result
- `attestation_id` (UUID, foreign key, required): Reference to vendor attestation
- `rule_id` (str, foreign key, required): Reference to compliance rule
- `status` (enum, required): Compliance status - `compliant`, `non_compliant`, `partial`, `unclear`, `not_applicable`
- `confidence_score` (float, 0.0-1.0, required): AI model confidence in this assessment
- `evidence_excerpts` (list[str], optional): Relevant text passages from attestation supporting this result
- `evidence_page_numbers` (list[int], optional): Page numbers where evidence was found
- `gap_description` (str, optional): Explanation of what is missing or insufficient (if non-compliant/partial)
- `ai_reasoning` (str, required): AI model's explanation of how it reached this conclusion
- `model_version` (str, required): Azure OpenAI model version used (e.g., `gpt-4o-2024-05-13`)
- `human_override` (bool, default: False): Whether human reviewer overrode AI assessment
- `human_override_by` (str, optional): Email of reviewer who performed override
- `human_override_at` (datetime, optional): When override occurred
- `human_override_reason` (str, optional): Justification for override (required if `human_override = True`)
- `final_status` (enum, required): Final compliance status after any human override (defaults to `status`)
- `analyzed_at` (datetime, required): When this result was generated
- `metadata` (JSON, optional): Additional analysis metadata (token count, processing time)

**Relationships**:
- Many-to-one with `VendorAttestation`: Each attestation has many compliance results
- Many-to-one with `ComplianceRule`: Each rule generates results for many attestations

**Indexes**:
- Primary: `result_id`
- Secondary: `attestation_id`, `rule_id`, `status`, `final_status`
- Composite: `(attestation_id, rule_id)` unique constraint - one result per rule per attestation
- Filter: `confidence_score < 0.85` for flagging low-confidence results

**Business Rules**:
- If `confidence_score < 0.85`, attestation status automatically set to `requires_human_review`
- `human_override_reason` mandatory when `human_override = True` (enforced at API layer)
- `final_status` is immutable after `ProcurementDecision` is recorded

---

### GapAnalysis

Represents aggregated compliance assessment for vendor attestation, summarizing all gaps and generating overall score.

**Attributes**:
- `analysis_id` (UUID, primary key): Unique identifier for gap analysis
- `attestation_id` (UUID, foreign key, unique, required): Reference to vendor attestation
- `overall_score` (float, 0-100, required): Severity-weighted compliance score
- `total_rules_evaluated` (int, required): Number of compliance rules checked
- `compliant_count` (int, required): Number of fully compliant results
- `non_compliant_count` (int, required): Number of non-compliant results
- `partial_count` (int, required): Number of partially compliant results
- `unclear_count` (int, required): Number of unclear results (requires human review)
- `not_applicable_count` (int, required): Number of N/A results
- `critical_gaps` (list[str], required): List of rule_ids with critical severity gaps
- `high_gaps` (list[str], required): List of rule_ids with high severity gaps
- `medium_gaps` (list[str], required): List of rule_ids with medium severity gaps
- `low_gaps` (list[str], required): List of rule_ids with low severity gaps
- `risk_level` (enum, required): Overall risk assessment - `disqualifying`, `high_risk`, `medium_risk`, `low_risk`, `acceptable`
- `remediation_guidance` (list[dict], required): Structured remediation recommendations (rule_id, gap, suggested_language)
- `sb_53_triggered` (bool, required): Whether SB 53 automated decision system requirements apply
- `sb_53_obligations` (list[str], optional): Additional SB 53 requirements if triggered
- `nist_ai_rmf_tier` (enum, optional): NIST risk tier - `tier_1`, `tier_2`, `tier_3`, `tier_4`
- `nist_ai_rmf_justification` (str, optional): Explanation for NIST tier classification
- `cross_reference_notes` (str, optional): Notes on overlapping requirements satisfied by single evidence
- `human_review_required` (bool, default: False): Flag for attestations needing human expert review
- `human_review_reasons` (list[str], optional): Reasons why human review is required
- `generated_at` (datetime, required): When gap analysis was generated
- `metadata` (JSON, optional): Additional analysis metadata (processing time, model versions)

**Relationships**:
- One-to-one with `VendorAttestation`: Each attestation has one gap analysis
- Aggregates data from multiple `ComplianceResult` records

**Indexes**:
- Primary: `analysis_id`
- Unique: `attestation_id`
- Secondary: `overall_score`, `risk_level`, `human_review_required`

**Scoring Algorithm**:
```
Severity weights: critical = 10, high = 5, medium = 2, low = 1
Max possible deductions = sum(all rule severities)
Actual deductions = sum(gap severities for non_compliant + partial*0.5 rules)
Overall score = max(0, 100 - (actual_deductions / max_deductions * 100))
```

**Risk Level Mapping**:
- `disqualifying`: Any critical gap OR score < 50
- `high_risk`: Score 50-69 OR 3+ high gaps
- `medium_risk`: Score 70-84
- `low_risk`: Score 85-94
- `acceptable`: Score 95-100 AND no critical/high gaps

---

### AuditRecord

Represents immutable log entry for all system actions, creating complete audit trail for compliance and oversight.

**Attributes**:
- `record_id` (UUID, primary key): Unique identifier for audit record
- `event_type` (enum, required): Type of event - `attestation_uploaded`, `analysis_started`, `analysis_completed`, `result_overridden`, `decision_made`, `report_generated`, `document_accessed`, `user_login`, `user_logout`
- `user_id` (str, required): Azure Entra ID user identifier (email or object ID)
- `user_role` (enum, required): Role at time of action - `procurement_officer`, `compliance_officer`, `auditor`, `admin`
- `ip_address` (str, required): IPv4/IPv6 address of request origin
- `user_agent` (str, optional): Browser/client user agent string
- `action` (str, required): Human-readable description of action (e.g., "Uploaded vendor attestation for RFP-2024-001")
- `resource_type` (enum, required): Type of resource affected - `attestation`, `compliance_result`, `gap_analysis`, `decision`, `report`, `audit_log`
- `resource_id` (str, required): Identifier of affected resource (attestation_id, result_id, etc.)
- `attestation_id` (UUID, optional): Reference to attestation if action relates to specific attestation
- `previous_value` (JSON, optional): Previous state of resource before action (for updates)
- `new_value` (JSON, optional): New state of resource after action (for creates/updates)
- `decision_rationale` (str, optional): Required for `decision_made` events
- `timestamp` (datetime, required): When event occurred (microsecond precision)
- `success` (bool, required): Whether action completed successfully
- `error_message` (str, optional): Error details if `success = False`
- `record_hash` (str, required): SHA-256 hash of record content for tamper detection
- `previous_record_hash` (str, optional): Hash of previous audit record (creates blockchain-like chain)
- `metadata` (JSON, optional): Additional context (session ID, correlation ID, request duration)

**Relationships**:
- Many-to-one with `VendorAttestation`: Audit records reference attestations
- Self-referential: `previous_record_hash` links to prior record

**Indexes**:
- Primary: `record_id`
- Secondary: `user_id`, `event_type`, `timestamp`, `attestation_id`, `resource_id`
- Composite: `(user_id, timestamp)` for user activity timeline
- Composite: `(attestation_id, timestamp)` for attestation history

**Immutability**:
- No UPDATE or DELETE operations permitted via API
- Database triggers prevent direct modification
- Record hash verification detects any database-level tampering
- Retention: 7 years per California public records requirements

**Chain Integrity**:
```
record_hash = SHA256(event_type + user_id + timestamp + action + resource_id + previous_record_hash)
```
Any modification breaks the hash chain, enabling tamper detection.

---

### ProcurementDecision

Represents final procurement officer recommendation for vendor attestation, creating binding decision record.

**Attributes**:
- `decision_id` (UUID, primary key): Unique identifier for decision
- `attestation_id` (UUID, foreign key, unique, required): Reference to vendor attestation
- `procurement_id` (str, required): Reference to procurement cycle/RFP ID
- `decision_type` (enum, required): Final recommendation - `approve`, `reject`, `request_clarification`, `escalate`
- `decided_by` (str, required): Email of procurement officer making decision
- `decided_at` (datetime, required): When decision was made
- `justification` (str, required): Detailed rationale for decision (min 100 chars)
- `compliance_score` (float, 0-100, required): Overall score from GapAnalysis at time of decision
- `risk_level` (enum, required): Risk level from GapAnalysis at time of decision
- `critical_gaps` (list[str], required): Critical gaps from GapAnalysis (frozen snapshot)
- `approved_with_conditions` (bool, default: False): Whether approval includes requirements
- `conditions` (list[str], optional): Specific conditions vendor must satisfy (if `approved_with_conditions = True`)
- `clarification_requests` (list[str], optional): Specific questions for vendor (if `decision_type = request_clarification`)
- `escalation_reason` (str, optional): Why decision was escalated (if `decision_type = escalate`)
- `escalated_to` (str, optional): Email of supervisor/legal counsel (if escalated)
- `approval_chain` (list[dict], optional): History of approvals for multi-level decisions (user, timestamp, approval)
- `final_decision` (bool, default: True): Whether this is the final decision (False if escalated)
- `superseded_by` (UUID, optional): Reference to decision that supersedes this one (if escalated)
- `created_at` (datetime, required): Decision record creation timestamp
- `metadata` (JSON, optional): Additional decision context (committee vote, legal review notes)

**Relationships**:
- One-to-one with `VendorAttestation`: Each attestation has at most one final decision
- Self-referential: `superseded_by` links to superseding decision
- Many-to-many with `AuditRecord`: Decision events generate audit records

**Indexes**:
- Primary: `decision_id`
- Unique: `attestation_id` (enforced only when `final_decision = True`)
- Secondary: `procurement_id`, `decision_type`, `decided_by`, `decided_at`

**Business Rules**:
- `justification` must be at least 100 characters (enforced at API layer)
- If `decision_type = reject` and `critical_gaps` is empty, requires admin override
- If `decision_type = approve` and `risk_level = disqualifying`, requires approval_chain with supervisor approval
- Decision is immutable once `final_decision = True` (creates new version if correction needed)
- Automated email notifications to vendor on `approve`, `reject`, or `request_clarification`

---

### Expert (Optional - for future expert routing feature)

Represents subject matter expert or compliance reviewer available for consultation.

**Attributes**:
- `expert_id` (UUID, primary key): Unique identifier for expert
- `user_id` (str, unique, required): Azure Entra ID user identifier
- `full_name` (str, required): Expert's full name
- `email` (str, required): Contact email
- `agency` (str, required): State agency affiliation
- `role` (str, required): Job title or role
- `expertise_areas` (list[str], required): Areas of expertise (e.g., ["AI ethics", "procurement law", "cybersecurity"])
- `certifications` (list[str], optional): Relevant certifications (e.g., ["CISSP", "California Bar"])
- `availability_status` (enum, required): Current availability - `available`, `busy`, `out_of_office`, `unavailable`
- `max_concurrent_reviews` (int, default: 5): Maximum attestations expert can review simultaneously
- `current_review_count` (int, default: 0): Number of active reviews assigned
- `total_reviews_completed` (int, default: 0): Lifetime review count
- `average_review_time_hours` (float, optional): Average time to complete review
- `contact_preference` (enum, default: email): Preferred contact method - `email`, `teams`, `phone`
- `phone` (str, optional): Phone number for urgent consultation
- `created_at` (datetime, required): Expert record creation timestamp
- `updated_at` (datetime, required): Expert record last update timestamp
- `metadata` (JSON, optional): Additional expert information (biography, publications)

**Relationships**:
- Many-to-many with `VendorAttestation`: Experts can be assigned to review multiple attestations

**Indexes**:
- Primary: `expert_id`
- Unique: `user_id`, `email`
- Secondary: `agency`, `availability_status`
- Full-text: `expertise_areas` for expert search

---

## Entity Relationships Summary

```
VendorAttestation (1) ──── (many) ComplianceResult
VendorAttestation (1) ──── (1) GapAnalysis
VendorAttestation (1) ──── (many) AuditRecord
VendorAttestation (1) ──── (0..1) ProcurementDecision
VendorAttestation (many) ──── (many) Expert [via assignment table]

ComplianceRule (1) ──── (many) ComplianceResult
ComplianceRule (0..1) ──── (many) ComplianceRule [self-referential parent-child]

AuditRecord (0..1) ──── (1) AuditRecord [self-referential hash chain]

ProcurementDecision (0..1) ──── (1) ProcurementDecision [self-referential superseded_by]
```

## Data Retention & Lifecycle

**Retention Policies**:
- `VendorAttestation`: 7 years (California public records requirement)
- `ComplianceResult`: 7 years (tied to attestation lifecycle)
- `GapAnalysis`: 7 years (tied to attestation lifecycle)
- `AuditRecord`: 7 years minimum, permanent recommended for forensic capability
- `ProcurementDecision`: 7 years (tied to attestation lifecycle)
- `ComplianceRule`: Permanent (historical rules preserved for past analyses)
- `Expert`: Active while user is state employee, archived on separation

**Lifecycle States**:
1. `VendorAttestation.status = uploaded` → Initial upload complete
2. `VendorAttestation.status = parsing` → Document parsing in progress
3. `VendorAttestation.status = analyzing` → Compliance analysis in progress
4. `VendorAttestation.status = complete` → Analysis complete, ready for review
5. `VendorAttestation.status = requires_human_review` → Low confidence or critical gaps
6. `ProcurementDecision` created → Final recommendation recorded
7. After 7 years → Archived to cold storage (Azure Archive tier)

## Security & Compliance

**Encryption**:
- At rest: AES-256 for all database fields and Azure Blob Storage documents
- In transit: TLS 1.3 for all API communications
- Sensitive fields: Additional application-level encryption for `justification`, `decision_rationale`

**Access Control**:
- Row-level security on `VendorAttestation` by `procurement_id` assignment
- Role-based access:
  - `procurement_officer`: Read/write attestations assigned to them, create decisions
  - `compliance_officer`: Read all attestations, read-only compliance rules
  - `auditor`: Read-only all entities, full audit log access
  - `admin`: Full access to compliance rules, user management

**Audit Requirements**:
- All CREATE, UPDATE operations generate `AuditRecord`
- All document downloads generate `document_accessed` audit event
- Failed authentication attempts logged to `AuditRecord`
- Audit log integrity verified via hash chain on application startup

**Data Classification**:
- `VendorAttestation.document_url`: Confidential (procurement sensitive)
- `ComplianceResult.evidence_excerpts`: Confidential (vendor proprietary information)
- `ProcurementDecision.justification`: Confidential (internal deliberation)
- `AuditRecord`: Public record (subject to CPRA requests, with PII redaction)
- `ComplianceRule`: Public (derived from public laws/regulations)
