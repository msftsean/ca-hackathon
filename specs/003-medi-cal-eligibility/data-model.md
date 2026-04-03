# Data Model: Medi-Cal Eligibility Agent

**Feature**: Medi-Cal Eligibility Agent  
**Date**: 2026-02-02  
**Database**: PostgreSQL 15+ with column-level encryption for PII

---

## Entity Relationship Overview

```
Application (1) ──────< (N) Document
    │                        │
    │                        │
    ├──< (N) IncomeRecord ──┘
    │
    ├──< (N) EligibilityResult
    │
    └──< (N) AuditEntry

HouseholdMember (N) ──> (1) Application

FPLGuideline (lookup table, annual updates)
DocumentRequirement (lookup table, by program type)
```

---

## Core Entities

### Application

Primary entity representing a Medi-Cal eligibility application.

**Table**: `applications`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| application_id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| applicant_id | UUID | NOT NULL, INDEX | Links to secure constituent identity system (external) |
| status | VARCHAR(50) | NOT NULL, DEFAULT 'draft' | `draft`, `submitted`, `document_review`, `county_processing`, `pending_interview`, `approved`, `denied`, `withdrawn` |
| submitted_at | TIMESTAMP WITH TIME ZONE | NULL | When application was submitted to county (null if draft) |
| county | VARCHAR(50) | NOT NULL | California county of residence (1-58 counties, e.g., "Los Angeles", "Alameda") |
| program_type | VARCHAR(50) | NOT NULL | `magi_adult`, `magi_child`, `magi_parent_caretaker`, `aged_blind_disabled`, `medicare_savings_qmb`, `medicare_savings_slmb`, `pregnancy` |
| household_size | INTEGER | NOT NULL, CHECK (household_size > 0) | Number of people in tax filing household |
| fpl_percentage | NUMERIC(5,2) | NULL | Calculated MAGI income as % of Federal Poverty Level (e.g., 138.50 for 138.5% FPL) |
| estimated_decision_date | DATE | NULL | Submitted date + 45 days (standard processing time) |
| benefitscal_id | VARCHAR(100) | NULL, UNIQUE | ID returned by county BenefitsCal system after submission |
| language_preference | VARCHAR(10) | DEFAULT 'en' | ISO 639-1 code: `en`, `es`, `zh`, `vi`, `tl`, `ko` |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp (trigger on UPDATE) |

**Indexes**:
- `idx_applications_applicant_id` on `applicant_id`
- `idx_applications_status` on `status`
- `idx_applications_county_status` on `(county, status)` for county dashboards
- `idx_applications_submitted_at` on `submitted_at` for SLA tracking

**Encryption**:
- `applicant_id` column encrypted using PostgreSQL `pgcrypto` extension (AES-256)

**Example**:
```json
{
  "application_id": "a7f3c8e1-4b2d-4c9e-8f1a-3d5e6b7c8d9e",
  "applicant_id": "encrypted:xk92jf...",
  "status": "county_processing",
  "submitted_at": "2026-01-15T10:30:00Z",
  "county": "San Francisco",
  "program_type": "magi_adult",
  "household_size": 1,
  "fpl_percentage": 112.50,
  "estimated_decision_date": "2026-03-01",
  "benefitscal_id": "SF-2026-001234",
  "language_preference": "en",
  "created_at": "2026-01-10T14:20:00Z",
  "updated_at": "2026-01-15T10:30:00Z"
}
```

---

### Document

Represents uploaded income verification or supporting documents.

**Table**: `documents`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| document_id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| application_id | UUID | NOT NULL, FOREIGN KEY → applications(application_id) ON DELETE CASCADE | Parent application |
| document_type | VARCHAR(50) | NOT NULL | `w2`, `paystub`, `form_1040`, `schedule_c`, `schedule_se`, `ssa_1099`, `pension_statement`, `bank_statement`, `trust_document`, `other` |
| file_name | VARCHAR(255) | NOT NULL | Original uploaded file name |
| file_url | TEXT | NOT NULL | Signed Azure Blob Storage URL (1-hour expiration) |
| file_size_bytes | INTEGER | NOT NULL | File size for storage tracking |
| mime_type | VARCHAR(100) | NOT NULL | `application/pdf`, `image/jpeg`, `image/png`, `image/tiff` |
| extracted_data | JSONB | NULL | Structured OCR output (schema varies by document_type) |
| processing_status | VARCHAR(50) | NOT NULL, DEFAULT 'uploaded' | `uploaded`, `processing`, `extracted`, `failed`, `manual_review_required` |
| ocr_confidence | NUMERIC(3,2) | NULL, CHECK (ocr_confidence BETWEEN 0 AND 1) | Overall OCR confidence score (0.0-1.0, e.g., 0.94) |
| pii_detected | BOOLEAN | DEFAULT FALSE | Whether PII was detected during scanning |
| uploaded_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Upload timestamp |
| processed_at | TIMESTAMP WITH TIME ZONE | NULL | When OCR extraction completed |

**Indexes**:
- `idx_documents_application_id` on `application_id`
- `idx_documents_processing_status` on `processing_status`
- `idx_documents_type_application` on `(document_type, application_id)` for completeness checks

**Encryption**:
- `file_url` contains encrypted blob reference with customer-managed keys

**Example Extracted Data (W-2)**:
```json
{
  "document_id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
  "application_id": "a7f3c8e1-4b2d-4c9e-8f1a-3d5e6b7c8d9e",
  "document_type": "w2",
  "file_name": "W2_2025_ACME_Corp.pdf",
  "file_url": "https://dhcsstorage.blob.core.windows.net/documents/encrypted-blob-id?sv=2023...",
  "file_size_bytes": 245678,
  "mime_type": "application/pdf",
  "extracted_data": {
    "tax_year": 2025,
    "employer_name": "ACME Corporation",
    "employer_ein": "12-3456789",
    "employee_name": "REDACTED",  
    "employee_ssn": "REDACTED",
    "box_1_wages": 42500.00,
    "box_2_federal_tax_withheld": 3825.50,
    "box_16_state_wages_ca": 42500.00,
    "box_17_state_tax_withheld_ca": 1912.00,
    "confidence_scores": {
      "box_1": 0.98,
      "box_2": 0.96,
      "box_16": 0.97,
      "box_17": 0.94
    }
  },
  "processing_status": "extracted",
  "ocr_confidence": 0.96,
  "pii_detected": true,
  "uploaded_at": "2026-01-10T14:25:00Z",
  "processed_at": "2026-01-10T14:25:23Z"
}
```

**Example Extracted Data (Pay Stub)**:
```json
{
  "extracted_data": {
    "employer_name": "Tech Startup Inc",
    "employee_name": "REDACTED",
    "pay_period_start": "2025-12-16",
    "pay_period_end": "2025-12-31",
    "pay_date": "2026-01-05",
    "gross_pay_current": 3250.00,
    "gross_pay_ytd": 78000.00,
    "pay_frequency": "biweekly",
    "confidence_scores": {
      "gross_pay_current": 0.91,
      "gross_pay_ytd": 0.89
    }
  },
  "ocr_confidence": 0.90,
  "processing_status": "manual_review_required"
}
```

---

### IncomeRecord

Represents a single income source extracted or entered for an application.

**Table**: `income_records`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| income_id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| application_id | UUID | NOT NULL, FOREIGN KEY → applications(application_id) ON DELETE CASCADE | Parent application |
| source | VARCHAR(50) | NOT NULL | `wages`, `self_employment`, `social_security`, `ssi`, `pension`, `unemployment`, `child_support`, `rental`, `alimony`, `interest_dividends`, `other` |
| amount | NUMERIC(12,2) | NOT NULL, CHECK (amount >= 0) | Dollar amount (e.g., 42500.00) |
| frequency | VARCHAR(20) | NOT NULL | `annual`, `monthly`, `biweekly`, `weekly`, `hourly` |
| annualized_amount | NUMERIC(12,2) | NOT NULL | Calculated annual equivalent (e.g., hourly * 2080 hours) |
| verification_status | VARCHAR(50) | DEFAULT 'pending' | `pending`, `verified`, `disputed` |
| document_id | UUID | NULL, FOREIGN KEY → documents(document_id) ON DELETE SET NULL | Supporting document (null if self-reported) |
| is_countable_magi | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether income counts toward MAGI (e.g., child support excluded) |
| is_countable_non_magi | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether income counts for non-MAGI (SSI excluded) |
| recipient | VARCHAR(100) | NULL | Who receives income (applicant, spouse, dependent) |
| notes | TEXT | NULL | Additional context (e.g., "seasonal employment, 6 months/year") |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Record creation timestamp |

**Indexes**:
- `idx_income_records_application_id` on `application_id`
- `idx_income_records_source` on `source`

**Business Rules**:
- **Annualized Calculation**:
  - `hourly`: amount × 2080 (40 hrs/week × 52 weeks)
  - `weekly`: amount × 52
  - `biweekly`: amount × 26
  - `monthly`: amount × 12
  - `annual`: amount (no conversion)

- **MAGI Countable Income**: Excludes child support, SSI, foster care payments, student financial aid
- **Non-MAGI Countable Income**: Excludes SSI but includes most other sources

**Example**:
```json
{
  "income_id": "i9a8b7c6-d5e4-3f2g-1h0i-j9k8l7m6n5o4",
  "application_id": "a7f3c8e1-4b2d-4c9e-8f1a-3d5e6b7c8d9e",
  "source": "wages",
  "amount": 3250.00,
  "frequency": "biweekly",
  "annualized_amount": 84500.00,
  "verification_status": "verified",
  "document_id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
  "is_countable_magi": true,
  "is_countable_non_magi": true,
  "recipient": "applicant",
  "notes": null,
  "created_at": "2026-01-10T14:30:00Z"
}
```

---

### EligibilityResult

Stores preliminary eligibility determinations performed by the agent.

**Table**: `eligibility_results`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| result_id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| application_id | UUID | NOT NULL, FOREIGN KEY → applications(application_id) ON DELETE CASCADE | Parent application |
| program | VARCHAR(100) | NOT NULL | Program evaluated (e.g., "Medi-Cal MAGI Adult", "QMB Medicare Savings") |
| eligible | BOOLEAN | NOT NULL | Preliminary determination (true = likely eligible) |
| magi_income | NUMERIC(12,2) | NULL | Total MAGI income calculated |
| countable_assets | NUMERIC(12,2) | NULL | For non-MAGI pathways (seniors/disabled) |
| fpl_percentage | NUMERIC(5,2) | NOT NULL | Income as % of FPL (e.g., 138.50) |
| fpl_threshold | NUMERIC(5,2) | NOT NULL | Program threshold (e.g., 138.00 for Medi-Cal) |
| household_size | INTEGER | NOT NULL | Household size used for FPL lookup |
| determination_date | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | When screening was performed |
| methodology | VARCHAR(50) | NOT NULL | `magi`, `non_magi_ssi_linked`, `non_magi_1634`, `medicare_savings_qmb`, `medicare_savings_slmb` |
| explanation | TEXT | NOT NULL | Human-readable explanation for applicant |
| next_steps | TEXT | NOT NULL | What applicant should do next |
| agent_version | VARCHAR(20) | NOT NULL | Agent version for audit (e.g., "1.0.0") |

**Indexes**:
- `idx_eligibility_results_application_id` on `application_id`
- `idx_eligibility_results_program_eligible` on `(program, eligible)` for analytics

**Example**:
```json
{
  "result_id": "e1f2g3h4-i5j6-7k8l-9m0n-o1p2q3r4s5t6",
  "application_id": "a7f3c8e1-4b2d-4c9e-8f1a-3d5e6b7c8d9e",
  "program": "Medi-Cal MAGI Adult",
  "eligible": true,
  "magi_income": 18600.00,
  "countable_assets": null,
  "fpl_percentage": 112.50,
  "fpl_threshold": 138.00,
  "household_size": 1,
  "determination_date": "2026-01-10T15:00:00Z",
  "methodology": "magi",
  "explanation": "Based on your annual income of $18,600 and household size of 1, your income is 112.5% of the Federal Poverty Level. This is below the 138% FPL threshold for Medi-Cal, so you are likely eligible for no-cost Medi-Cal coverage.",
  "next_steps": "Please complete your application and upload all required income verification documents. Your county eligibility worker will review and make a final determination within 45 days.",
  "agent_version": "1.0.0"
}
```

---

### AuditEntry

HIPAA-compliant audit log for all system actions involving application data.

**Table**: `audit_entries` (append-only, no UPDATE or DELETE allowed)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| entry_id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| timestamp | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | When action occurred |
| action | VARCHAR(50) | NOT NULL | `document_upload`, `ocr_extraction`, `eligibility_screening`, `status_query`, `application_submit`, `data_access`, `application_create`, `application_update` |
| actor_id | VARCHAR(255) | NOT NULL | User ID or service account (e.g., "user:abc123", "service:ocr-worker") |
| actor_role | VARCHAR(50) | NOT NULL | `applicant`, `county_worker`, `dhcs_admin`, `system` |
| application_id | UUID | NULL, INDEX | Application affected (null for global actions) |
| document_id | UUID | NULL | Document affected (if applicable) |
| pii_detected | BOOLEAN | DEFAULT FALSE | Whether PII was in the accessed data |
| masked_data | JSONB | NULL | PII-masked version of data accessed (e.g., `{"ssn": "XXX-XX-1234"}`) |
| ip_address_hash | VARCHAR(64) | NOT NULL | SHA-256 hash of IP address (not stored in plaintext) |
| user_agent | TEXT | NULL | Browser/client user agent string |
| outcome | VARCHAR(50) | NOT NULL | `success`, `failure`, `unauthorized`, `rate_limited` |
| error_message | TEXT | NULL | Error details if outcome = failure |
| signature | VARCHAR(255) | NOT NULL | HMAC-SHA256 signature for tamper detection |

**Indexes**:
- `idx_audit_entries_application_id` on `application_id`
- `idx_audit_entries_timestamp` on `timestamp` DESC for recent log queries
- `idx_audit_entries_actor_id` on `actor_id` for user activity reports
- `idx_audit_entries_action` on `action` for action-specific analytics

**Constraints**:
- Append-only enforced via PostgreSQL trigger that prevents UPDATE and DELETE
- Signature verified on read using server-side secret key

**Signature Generation**:
```python
import hmac
import hashlib

def generate_signature(entry: AuditEntry, secret_key: str) -> str:
    """Generate HMAC-SHA256 signature for audit entry."""
    message = f"{entry.timestamp}|{entry.action}|{entry.actor_id}|{entry.application_id}"
    return hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
```

**Example**:
```json
{
  "entry_id": "audit-1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6",
  "timestamp": "2026-01-10T14:25:23Z",
  "action": "ocr_extraction",
  "actor_id": "service:document-intelligence",
  "actor_role": "system",
  "application_id": "a7f3c8e1-4b2d-4c9e-8f1a-3d5e6b7c8d9e",
  "document_id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
  "pii_detected": true,
  "masked_data": {
    "employee_ssn": "XXX-XX-6789",
    "employee_name": "John D****"
  },
  "ip_address_hash": "5a2e3f1b8c9d0e4f7a6b3c2d1e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f",
  "user_agent": "Azure-Document-Intelligence/1.0",
  "outcome": "success",
  "error_message": null,
  "signature": "3f8a2b1c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a"
}
```

---

## Supporting Entities

### HouseholdMember

Represents members of the applicant's tax filing household.

**Table**: `household_members`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| member_id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| application_id | UUID | NOT NULL, FOREIGN KEY → applications(application_id) ON DELETE CASCADE | Parent application |
| relationship | VARCHAR(50) | NOT NULL | `self`, `spouse`, `dependent_child`, `dependent_parent`, `other_dependent` |
| age | INTEGER | NOT NULL, CHECK (age >= 0 AND age <= 120) | Age in years |
| is_tax_dependent | BOOLEAN | NOT NULL | Whether person is claimed as tax dependent |
| applying_for_coverage | BOOLEAN | DEFAULT FALSE | Whether this member is also applying (family application) |
| has_disability | BOOLEAN | DEFAULT FALSE | For non-MAGI pathway eligibility |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Record creation timestamp |

**Note**: No PII (names, DOB) stored in this table. Age calculated from DOB at application time.

**Example**:
```json
{
  "member_id": "m1a2b3c4-d5e6-7f8g-9h0i-j1k2l3m4n5o6",
  "application_id": "a7f3c8e1-4b2d-4c9e-8f1a-3d5e6b7c8d9e",
  "relationship": "dependent_child",
  "age": 8,
  "is_tax_dependent": true,
  "applying_for_coverage": true,
  "has_disability": false,
  "created_at": "2026-01-10T14:30:00Z"
}
```

---

### FPLGuideline (Lookup Table)

Federal Poverty Level guidelines by household size and year.

**Table**: `fpl_guidelines`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| guideline_id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| year | INTEGER | NOT NULL, INDEX | Guideline year (2026, 2027, etc.) |
| household_size | INTEGER | NOT NULL, CHECK (household_size BETWEEN 1 AND 15) | Number of people in household |
| annual_amount | NUMERIC(10,2) | NOT NULL | FPL for this household size (e.g., 16512.00 for 1 person in 2026) |
| state | VARCHAR(2) | DEFAULT 'CA' | State code (California may have different thresholds) |
| effective_date | DATE | NOT NULL | When guideline takes effect |

**Unique Constraint**: `(year, household_size, state)`

**Example Data (2026 Federal Poverty Level for California)**:
```sql
INSERT INTO fpl_guidelines (year, household_size, annual_amount, effective_date) VALUES
(2026, 1, 16512.00, '2026-01-01'),
(2026, 2, 22278.00, '2026-01-01'),
(2026, 3, 28044.00, '2026-01-01'),
(2026, 4, 36312.00, '2026-01-01'),
(2026, 5, 42078.00, '2026-01-01'),
(2026, 6, 47844.00, '2026-01-01'),
(2026, 7, 53610.00, '2026-01-01'),
(2026, 8, 59376.00, '2026-01-01');
-- Add $5,766 for each additional person beyond 8
```

---

### DocumentRequirement (Lookup Table)

Required documents by program type for completeness validation.

**Table**: `document_requirements`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| requirement_id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| program_type | VARCHAR(50) | NOT NULL | `magi_adult`, `aged_blind_disabled`, etc. |
| income_source | VARCHAR(50) | NULL | `wages`, `self_employment`, etc. (null = required for all) |
| required_document_type | VARCHAR(50) | NOT NULL | `w2`, `paystub`, `form_1040`, etc. |
| description | TEXT | NOT NULL | Human-readable description for applicant |
| is_mandatory | BOOLEAN | DEFAULT TRUE | Whether document is required or optional |
| language_key | VARCHAR(100) | NOT NULL | i18n translation key (e.g., "docs.w2.description") |

**Example Data**:
```sql
INSERT INTO document_requirements (program_type, income_source, required_document_type, description, is_mandatory, language_key) VALUES
('magi_adult', 'wages', 'w2', 'Most recent W-2 form from your employer', TRUE, 'docs.w2.description'),
('magi_adult', 'wages', 'paystub', 'Two most recent pay stubs showing year-to-date earnings', TRUE, 'docs.paystub.description'),
('magi_adult', 'self_employment', 'form_1040', 'Most recent IRS Form 1040 (complete return)', TRUE, 'docs.form_1040.description'),
('magi_adult', 'self_employment', 'schedule_c', 'IRS Schedule C (Profit or Loss from Business)', TRUE, 'docs.schedule_c.description'),
('aged_blind_disabled', 'social_security', 'ssa_1099', 'Social Security Administration SSA-1099 or SSA-1042S', TRUE, 'docs.ssa_1099.description'),
('aged_blind_disabled', NULL, 'bank_statement', 'Most recent 3 months of bank statements for all accounts (for asset test)', TRUE, 'docs.bank_statement.description');
```

---

## Database Schema (PostgreSQL DDL)

```sql
-- Enable UUID generation and encryption extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Applications table
CREATE TABLE applications (
    application_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    applicant_id BYTEA NOT NULL,  -- Encrypted UUID
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    submitted_at TIMESTAMP WITH TIME ZONE,
    county VARCHAR(50) NOT NULL,
    program_type VARCHAR(50) NOT NULL,
    household_size INTEGER NOT NULL CHECK (household_size > 0),
    fpl_percentage NUMERIC(5,2),
    estimated_decision_date DATE,
    benefitscal_id VARCHAR(100) UNIQUE,
    language_preference VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_applications_applicant_id ON applications(applicant_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_county_status ON applications(county, status);
CREATE INDEX idx_applications_submitted_at ON applications(submitted_at);

-- Auto-update updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_applications_updated_at BEFORE UPDATE ON applications
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Documents table
CREATE TABLE documents (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_url TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    extracted_data JSONB,
    processing_status VARCHAR(50) NOT NULL DEFAULT 'uploaded',
    ocr_confidence NUMERIC(3,2) CHECK (ocr_confidence BETWEEN 0 AND 1),
    pii_detected BOOLEAN DEFAULT FALSE,
    uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_documents_application_id ON documents(application_id);
CREATE INDEX idx_documents_processing_status ON documents(processing_status);
CREATE INDEX idx_documents_type_application ON documents(document_type, application_id);

-- Income records table
CREATE TABLE income_records (
    income_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    source VARCHAR(50) NOT NULL,
    amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
    frequency VARCHAR(20) NOT NULL,
    annualized_amount NUMERIC(12,2) NOT NULL,
    verification_status VARCHAR(50) DEFAULT 'pending',
    document_id UUID REFERENCES documents(document_id) ON DELETE SET NULL,
    is_countable_magi BOOLEAN NOT NULL DEFAULT TRUE,
    is_countable_non_magi BOOLEAN NOT NULL DEFAULT TRUE,
    recipient VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_income_records_application_id ON income_records(application_id);
CREATE INDEX idx_income_records_source ON income_records(source);

-- Eligibility results table
CREATE TABLE eligibility_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    program VARCHAR(100) NOT NULL,
    eligible BOOLEAN NOT NULL,
    magi_income NUMERIC(12,2),
    countable_assets NUMERIC(12,2),
    fpl_percentage NUMERIC(5,2) NOT NULL,
    fpl_threshold NUMERIC(5,2) NOT NULL,
    household_size INTEGER NOT NULL,
    determination_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    methodology VARCHAR(50) NOT NULL,
    explanation TEXT NOT NULL,
    next_steps TEXT NOT NULL,
    agent_version VARCHAR(20) NOT NULL
);

CREATE INDEX idx_eligibility_results_application_id ON eligibility_results(application_id);
CREATE INDEX idx_eligibility_results_program_eligible ON eligibility_results(program, eligible);

-- Audit entries table (append-only)
CREATE TABLE audit_entries (
    entry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    action VARCHAR(50) NOT NULL,
    actor_id VARCHAR(255) NOT NULL,
    actor_role VARCHAR(50) NOT NULL,
    application_id UUID,
    document_id UUID,
    pii_detected BOOLEAN DEFAULT FALSE,
    masked_data JSONB,
    ip_address_hash VARCHAR(64) NOT NULL,
    user_agent TEXT,
    outcome VARCHAR(50) NOT NULL,
    error_message TEXT,
    signature VARCHAR(255) NOT NULL
);

CREATE INDEX idx_audit_entries_application_id ON audit_entries(application_id);
CREATE INDEX idx_audit_entries_timestamp ON audit_entries(timestamp DESC);
CREATE INDEX idx_audit_entries_actor_id ON audit_entries(actor_id);
CREATE INDEX idx_audit_entries_action ON audit_entries(action);

-- Prevent UPDATE and DELETE on audit_entries
CREATE OR REPLACE FUNCTION prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit entries are immutable (no UPDATE or DELETE allowed)';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_audit_update BEFORE UPDATE ON audit_entries
FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();

CREATE TRIGGER prevent_audit_delete BEFORE DELETE ON audit_entries
FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();

-- Household members table
CREATE TABLE household_members (
    member_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    relationship VARCHAR(50) NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 0 AND age <= 120),
    is_tax_dependent BOOLEAN NOT NULL,
    applying_for_coverage BOOLEAN DEFAULT FALSE,
    has_disability BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_household_members_application_id ON household_members(application_id);

-- FPL guidelines lookup table
CREATE TABLE fpl_guidelines (
    guideline_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    year INTEGER NOT NULL,
    household_size INTEGER NOT NULL CHECK (household_size BETWEEN 1 AND 15),
    annual_amount NUMERIC(10,2) NOT NULL,
    state VARCHAR(2) DEFAULT 'CA',
    effective_date DATE NOT NULL,
    UNIQUE (year, household_size, state)
);

CREATE INDEX idx_fpl_guidelines_year ON fpl_guidelines(year);

-- Document requirements lookup table
CREATE TABLE document_requirements (
    requirement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_type VARCHAR(50) NOT NULL,
    income_source VARCHAR(50),
    required_document_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    is_mandatory BOOLEAN DEFAULT TRUE,
    language_key VARCHAR(100) NOT NULL
);

CREATE INDEX idx_document_requirements_program ON document_requirements(program_type);
```

---

## Data Retention & Compliance

### HIPAA Retention Requirements
- **Audit Logs**: 7 years minimum (appended-only, no deletion)
- **Application Data**: 7 years after final determination or until applicant requests deletion
- **Documents**: 7 years in encrypted blob storage with automated lifecycle policy

### PII Encryption
- **At Rest**: AES-256 encryption for `applicant_id`, document blobs
- **In Transit**: TLS 1.3 for all API communications
- **Audit Logs**: PII masked in `masked_data` JSONB field (e.g., `"XXX-XX-1234"` for SSN)

### Right to Deletion (CCPA/CPRA)
- Applicant requests deletion via authenticated API endpoint
- Soft-delete with `deleted_at` timestamp (retain for audit compliance)
- Document blobs purged after 7-year retention period
- Audit logs preserved indefinitely with PII masking

---

## Migration Notes

### Phase 1 (Mock Mode)
- `benefitscal_id` will be generated by mock service (random UUID)
- `applicant_id` links to local test database (no real constituent identity)

### Phase 2 (Production Integration)
- Integrate with county BenefitsCal system for real `benefitscal_id`
- Link `applicant_id` to California statewide constituent identity system
- Add county-specific routing and SLA configuration tables
- Implement real-time status sync with county systems

---

## Example Queries

### Application Status Summary
```sql
SELECT 
    status,
    COUNT(*) as count,
    AVG(EXTRACT(EPOCH FROM (NOW() - submitted_at)) / 86400) as avg_days_pending
FROM applications
WHERE submitted_at IS NOT NULL
GROUP BY status;
```

### Applications Missing Required Documents
```sql
SELECT 
    a.application_id,
    a.county,
    a.program_type,
    array_agg(DISTINCT dr.required_document_type) as missing_docs
FROM applications a
CROSS JOIN document_requirements dr
LEFT JOIN documents d ON a.application_id = d.application_id 
    AND d.document_type = dr.required_document_type
WHERE a.status = 'document_review'
    AND a.program_type = dr.program_type
    AND dr.is_mandatory = TRUE
    AND d.document_id IS NULL
GROUP BY a.application_id, a.county, a.program_type;
```

### OCR Performance Metrics
```sql
SELECT 
    document_type,
    COUNT(*) as total_processed,
    AVG(ocr_confidence) as avg_confidence,
    SUM(CASE WHEN processing_status = 'manual_review_required' THEN 1 ELSE 0 END) as manual_review_count,
    AVG(EXTRACT(EPOCH FROM (processed_at - uploaded_at))) as avg_processing_seconds
FROM documents
WHERE processed_at IS NOT NULL
GROUP BY document_type;
```

### Eligibility Approval Rate by County
```sql
SELECT 
    a.county,
    COUNT(*) as total_determinations,
    SUM(CASE WHEN er.eligible = TRUE THEN 1 ELSE 0 END) as likely_eligible_count,
    ROUND(100.0 * SUM(CASE WHEN er.eligible = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) as approval_rate_pct
FROM applications a
JOIN eligibility_results er ON a.application_id = er.application_id
WHERE er.program = 'Medi-Cal MAGI Adult'
GROUP BY a.county
ORDER BY total_determinations DESC;
```

---

## API Response Examples

### GET /applications/{application_id}
```json
{
  "application_id": "a7f3c8e1-4b2d-4c9e-8f1a-3d5e6b7c8d9e",
  "status": "county_processing",
  "submitted_at": "2026-01-15T10:30:00Z",
  "county": "San Francisco",
  "program_type": "magi_adult",
  "household_size": 1,
  "fpl_percentage": 112.50,
  "estimated_decision_date": "2026-03-01",
  "language_preference": "en",
  "documents": [
    {
      "document_id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
      "document_type": "w2",
      "file_name": "W2_2025_ACME_Corp.pdf",
      "processing_status": "extracted",
      "ocr_confidence": 0.96,
      "uploaded_at": "2026-01-10T14:25:00Z"
    }
  ],
  "income_records": [
    {
      "income_id": "i9a8b7c6-d5e4-3f2g-1h0i-j9k8l7m6n5o4",
      "source": "wages",
      "amount": 3250.00,
      "frequency": "biweekly",
      "annualized_amount": 84500.00,
      "verification_status": "verified"
    }
  ],
  "eligibility_result": {
    "program": "Medi-Cal MAGI Adult",
    "eligible": true,
    "fpl_percentage": 112.50,
    "explanation": "Based on your annual income of $18,600...",
    "next_steps": "Please complete your application..."
  }
}
```
