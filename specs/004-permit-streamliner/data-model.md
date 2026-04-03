# Permit Streamliner — Data Model

**Accelerator**: 004-permit-streamliner
**Agencies**: OPR / HCD / DCA
**Version**: 1.0.0

---

## Entity Relationship Overview

```
┌─────────────────┐       ┌──────────────────────┐
│   applicants    │──1:N──│    applications       │
└─────────────────┘       └──────────────────────┘
                                │
                ┌───────────────┼───────────────────┐
                │               │                   │
           1:N  ▼          1:N  ▼              1:N  ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ permit_require-  │ │    documents     │ │ routing_decisions │
│ ments            │ └──────────────────┘ └──────────────────┘
└──────────────────┘                              │
                                             1:N  ▼
                                      ┌──────────────────┐
                                      │   sla_tracking    │
                                      └──────────────────┘

                          ┌──────────────────┐
                          │  audit_entries   │  (append-only)
                          └──────────────────┘
```

---

## Core Entities

### 1. `applicants`

Represents the permit applicant (individual or business).

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | |
| `full_name` | `TEXT` | NOT NULL, **ENCRYPTED** | pgcrypto AES-256 |
| `email` | `TEXT` | NOT NULL, **ENCRYPTED** | pgcrypto AES-256 |
| `phone` | `TEXT` | **ENCRYPTED** | pgcrypto AES-256 |
| `business_name` | `TEXT` | | Nullable for individuals |
| `license_number` | `TEXT` | | Contractor license if applicable |
| `preferred_language` | `TEXT` | DEFAULT `'en'` | `en`, `es` supported |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT `now()` | |

**Indexes**: `idx_applicants_email` (unique on encrypted hash), `idx_applicants_license`

**Example**:
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "full_name": "[ENCRYPTED]",
  "email": "[ENCRYPTED]",
  "phone": "[ENCRYPTED]",
  "business_name": "Martinez Construction LLC",
  "license_number": "CA-B-987654",
  "preferred_language": "es",
  "created_at": "2026-03-15T10:00:00Z"
}
```

---

### 2. `applications`

Core entity tracking a permit application through its lifecycle.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | |
| `applicant_id` | `UUID` | FK → `applicants.id`, NOT NULL | |
| `permit_number` | `TEXT` | UNIQUE, NOT NULL | Format: `PRM-YYYY-NNNNNN` |
| `project_description` | `TEXT` | NOT NULL | Natural language from intake |
| `project_type` | `TEXT` | NOT NULL | `residential_addition`, `commercial_new`, `demolition`, `business_license`, `professional_license`, `environmental_review` |
| `property_address` | `TEXT` | NOT NULL | |
| `parcel_number` | `TEXT` | | APN for property identification |
| `jurisdiction` | `TEXT` | NOT NULL | City/county jurisdiction |
| `status` | `TEXT` | NOT NULL, DEFAULT `'intake'` | See status workflow below |
| `estimated_fee` | `DECIMAL(10,2)` | | AI-estimated fee range low |
| `estimated_fee_high` | `DECIMAL(10,2)` | | AI-estimated fee range high |
| `estimated_days` | `INTEGER` | | Estimated processing days |
| `special_constraints` | `JSONB` | DEFAULT `'[]'` | `["historic_district", "coastal_zone", "flood_zone", "ceqa_trigger"]` |
| `submitted_at` | `TIMESTAMPTZ` | | When formally submitted |
| `decision_date` | `TIMESTAMPTZ` | | When approved/denied |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT `now()` | |

**Status Workflow**:
```
intake → checklist_generated → documents_pending → under_review → 
  → approved | denied | additional_info_required → under_review
```

**Indexes**:
- `idx_applications_permit_number` (unique)
- `idx_applications_status` (for queue queries)
- `idx_applications_applicant` (FK)
- `idx_applications_jurisdiction_status` (composite, for reviewer dashboards)

**Business Rules**:
- `permit_number` auto-generated on creation: `PRM-{year}-{sequence}`
- `estimated_days` calculated from `project_type` + `special_constraints` count
- Base estimates: residential_addition=42, commercial_new=90, business_license=30, professional_license=21
- Each special constraint adds 14–30 days (historic_district=30, ceqa_trigger=21, flood_zone=14)

**Example**:
```json
{
  "id": "f7e6d5c4-b3a2-1098-7654-321fedcba098",
  "applicant_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "permit_number": "PRM-2026-000142",
  "project_description": "Adding 400 sq ft second-story addition to single-family home in historic Midtown Sacramento district",
  "project_type": "residential_addition",
  "property_address": "1234 J Street, Sacramento, CA 95814",
  "parcel_number": "006-0123-045",
  "jurisdiction": "City of Sacramento",
  "status": "checklist_generated",
  "estimated_fee": 2800.00,
  "estimated_fee_high": 3500.00,
  "estimated_days": 72,
  "special_constraints": ["historic_district"],
  "submitted_at": null,
  "created_at": "2026-03-15T10:05:00Z"
}
```

---

### 3. `permit_requirements`

AI-generated checklist items for an application.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | |
| `application_id` | `UUID` | FK → `applications.id`, NOT NULL | |
| `permit_type` | `TEXT` | NOT NULL | `building`, `electrical`, `plumbing`, `mechanical`, `zoning`, `ceqa`, `fire`, `health`, `abc`, `sign` |
| `responsible_agency` | `TEXT` | NOT NULL | e.g., `HCD`, `DCA`, `OPR`, local jurisdiction |
| `required_documents` | `JSONB` | NOT NULL | List of document specs |
| `estimated_processing_days` | `INTEGER` | NOT NULL | |
| `fee_estimate` | `DECIMAL(10,2)` | | |
| `status` | `TEXT` | DEFAULT `'pending'` | `pending`, `documents_received`, `complete`, `waived` |
| `notes` | `TEXT` | | AI-generated guidance |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT `now()` | |

**Indexes**: `idx_permit_req_application` (FK), `idx_permit_req_status`

**Business Rules**:
- Requirements auto-generated based on `project_type` + `jurisdiction` + `special_constraints`
- A residential_addition always requires: `building`, `zoning`; conditionally `electrical`, `plumbing` based on scope
- Historic district triggers additional `zoning` review with preservation board
- CEQA triggers require `ceqa` permit type with OPR routing

**Example**:
```json
{
  "id": "11111111-2222-3333-4444-555555555555",
  "application_id": "f7e6d5c4-b3a2-1098-7654-321fedcba098",
  "permit_type": "building",
  "responsible_agency": "City of Sacramento - Building Division",
  "required_documents": [
    {"name": "Architectural Drawings", "format": "PDF", "required": true},
    {"name": "Structural Calculations", "format": "PDF", "required": true},
    {"name": "Site Plan", "format": "PDF", "required": true},
    {"name": "Title Report", "format": "PDF", "required": true}
  ],
  "estimated_processing_days": 42,
  "fee_estimate": 1850.00,
  "status": "pending",
  "notes": "Historic district overlay requires additional preservation board review. Allow 30 extra days."
}
```

---

### 4. `documents`

Uploaded files with AI extraction and validation results.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | |
| `application_id` | `UUID` | FK → `applications.id`, NOT NULL | |
| `requirement_id` | `UUID` | FK → `permit_requirements.id` | Links to specific requirement |
| `filename` | `TEXT` | NOT NULL | |
| `content_type` | `TEXT` | NOT NULL | MIME type |
| `storage_url` | `TEXT` | NOT NULL | Azure Blob Storage path |
| `file_size_bytes` | `BIGINT` | NOT NULL | |
| `extraction_status` | `TEXT` | DEFAULT `'pending'` | `pending`, `processing`, `completed`, `failed` |
| `extracted_data` | `JSONB` | | Azure Document Intelligence output |
| `validation_results` | `JSONB` | | Cross-reference check results |
| `validation_passed` | `BOOLEAN` | | Overall pass/fail |
| `uploaded_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT `now()` | |

**Indexes**: `idx_documents_application` (FK), `idx_documents_requirement` (FK), `idx_documents_extraction_status`

**Business Rules**:
- Max file size: 50MB per document
- Accepted formats: PDF, PNG, JPG, TIFF
- Azure Document Intelligence extracts: square footage, stories, setbacks, lot coverage, building heights
- Validation cross-references extracted values against zoning maximums for the parcel
- `validation_passed = false` blocks application submission with specific failure reasons

**Example**:
```json
{
  "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
  "application_id": "f7e6d5c4-b3a2-1098-7654-321fedcba098",
  "requirement_id": "11111111-2222-3333-4444-555555555555",
  "filename": "site_plan_1234_j_street.pdf",
  "content_type": "application/pdf",
  "storage_url": "https://capermits.blob.core.windows.net/docs/f7e6d5c4/site_plan.pdf",
  "file_size_bytes": 2457600,
  "extraction_status": "completed",
  "extracted_data": {
    "lot_area_sqft": 6500,
    "existing_building_sqft": 1800,
    "proposed_addition_sqft": 400,
    "total_proposed_sqft": 2200,
    "stories": 2,
    "max_height_ft": 28,
    "front_setback_ft": 20,
    "rear_setback_ft": 15
  },
  "validation_results": {
    "lot_coverage": {"max": 0.50, "proposed": 0.338, "passed": true},
    "height": {"max_ft": 35, "proposed_ft": 28, "passed": true},
    "setback_front": {"min_ft": 15, "proposed_ft": 20, "passed": true},
    "far": {"max": 0.60, "proposed": 0.338, "passed": true}
  },
  "validation_passed": true
}
```

---

### 5. `routing_decisions`

Multi-agency routing assignments for permit review.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | |
| `application_id` | `UUID` | FK → `applications.id`, NOT NULL | |
| `agency` | `TEXT` | NOT NULL | Assigned agency/department |
| `reviewer_id` | `TEXT` | | Assigned reviewer (if available) |
| `reviewer_name` | `TEXT` | | For transparency |
| `priority` | `TEXT` | DEFAULT `'normal'` | `low`, `normal`, `high`, `urgent` |
| `stage` | `TEXT` | NOT NULL | `queued`, `in_review`, `info_requested`, `approved`, `denied` |
| `sla_target_date` | `DATE` | NOT NULL | Calculated from routing + processing estimate |
| `sla_at_risk` | `BOOLEAN` | DEFAULT `false` | True when >80% of SLA consumed |
| `escalated` | `BOOLEAN` | DEFAULT `false` | True when SLA exceeded |
| `escalation_reason` | `TEXT` | | |
| `notes` | `TEXT` | | Reviewer notes |
| `routed_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT `now()` | |
| `completed_at` | `TIMESTAMPTZ` | | |

**Indexes**: `idx_routing_application` (FK), `idx_routing_agency_stage` (composite), `idx_routing_sla_at_risk`

**Business Rules**:
- `sla_target_date = routed_at + estimated_processing_days` from the permit requirement
- `sla_at_risk` flips to `true` when `days_elapsed / estimated_processing_days >= 0.80`
- `escalated` triggers supervisor notification when SLA exceeded
- Reviewer load balancing: new applications route to reviewer with fewest active `in_review` items
- An application may have multiple routing decisions (one per agency/permit type)

**Example**:
```json
{
  "id": "99999999-8888-7777-6666-555544443333",
  "application_id": "f7e6d5c4-b3a2-1098-7654-321fedcba098",
  "agency": "City of Sacramento - Building Division",
  "reviewer_id": "emp-2847",
  "reviewer_name": "Maria Chen",
  "priority": "normal",
  "stage": "in_review",
  "sla_target_date": "2026-05-26",
  "sla_at_risk": false,
  "escalated": false,
  "routed_at": "2026-03-20T08:00:00Z",
  "completed_at": null
}
```

---

### 6. `audit_entries`

Append-only audit log for compliance and transparency.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `BIGSERIAL` | PK | Monotonic sequence |
| `application_id` | `UUID` | FK → `applications.id` | Nullable for system events |
| `actor_type` | `TEXT` | NOT NULL | `system`, `applicant`, `reviewer`, `ai_agent` |
| `actor_id` | `TEXT` | NOT NULL | User ID or agent name |
| `action` | `TEXT` | NOT NULL | `application_created`, `checklist_generated`, `document_uploaded`, `validation_run`, `routed`, `status_changed`, `sla_alert`, `escalated`, `decision_made` |
| `details` | `JSONB` | | Action-specific payload |
| `ip_address` | `INET` | | Request origin |
| `hmac_signature` | `TEXT` | NOT NULL | HMAC-SHA256 for tamper detection |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT `now()` | Immutable |

**Indexes**: `idx_audit_application` (FK), `idx_audit_created_at` (for time-range queries), `idx_audit_action`

**Business Rules**:
- **Append-only**: No UPDATE or DELETE operations permitted
- HMAC computed over: `application_id + actor_id + action + details + created_at`
- Retained for minimum 7 years per California records retention
- Supports California Public Records Act queries (filtered by action type)

**Example**:
```json
{
  "id": 1042,
  "application_id": "f7e6d5c4-b3a2-1098-7654-321fedcba098",
  "actor_type": "ai_agent",
  "actor_id": "intake-agent-v1",
  "action": "checklist_generated",
  "details": {
    "project_type": "residential_addition",
    "permits_required": ["building", "zoning"],
    "special_constraints_detected": ["historic_district"],
    "estimated_days": 72,
    "confidence": 0.91
  },
  "hmac_signature": "sha256:a3f8c2d1e9b7...",
  "created_at": "2026-03-15T10:05:01Z"
}
```

---

## Security & Encryption Strategy

| Data Classification | Protection | Implementation |
|---------------------|-----------|----------------|
| Applicant PII (name, email, phone) | Column-level encryption | PostgreSQL pgcrypto AES-256-CBC |
| Property addresses | Plaintext (public record) | N/A |
| Documents | Encryption at rest | Azure Blob Storage SSE |
| Audit logs | Tamper-proof | HMAC-SHA256 signatures |
| API tokens | Vault-managed | Azure Key Vault |

## Mock Mode

When `USE_MOCK_SERVICES=true`:
- Document extraction returns hardcoded `extracted_data` from `mock_data/`
- Zoning validation uses `mock_data/zoning_rules.json`
- Reviewer assignment uses a static pool of 5 mock reviewers
- SLA calculations use accelerated timelines (days → minutes)
