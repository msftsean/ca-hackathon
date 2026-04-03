# API Contract: Medi-Cal Eligibility Agent

**Accelerator**: 003-medi-cal-eligibility  
**Agency**: Department of Health Care Services (DHCS)  
**Base URL**: `http://localhost:8003` (local), `https://medi-cal-eligibility.azurewebsites.net` (prod)  
**Authentication**: Azure Entra ID Bearer Token (all endpoints except `/health`)  
**API Version**: v1  
**Date**: 2026-02-02

---

## Base Configuration

**Port**: 8003 (local development)  
**Content-Type**: `application/json` (all requests/responses)  
**Authentication Header**: `Authorization: Bearer <jwt_token>`  
**CORS**: Enabled for `http://localhost:5173` (frontend dev server)

---

## Health & Status Endpoints

### GET /health

Health check endpoint for monitoring and container orchestration.

**Authentication**: None required

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-15T10:30:00Z",
  "services": {
    "database": "connected",
    "azure_openai": "available",
    "document_intelligence": "available",
    "blob_storage": "available",
    "redis": "connected"
  }
}
```

**Response** (503 Service Unavailable) - if any service down:
```json
{
  "status": "unhealthy",
  "version": "1.0.0",
  "timestamp": "2026-01-15T10:30:00Z",
  "services": {
    "database": "connected",
    "azure_openai": "unavailable",
    "document_intelligence": "available",
    "blob_storage": "available",
    "redis": "connected"
  },
  "errors": ["Azure OpenAI endpoint not reachable"]
}
```

---

## Application Endpoints

### POST /api/v1/applications

Create a new Medi-Cal eligibility application.

**Authentication**: Required (applicant or county_worker role)

**Request Body**:
```json
{
  "applicant_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "county": "San Francisco",
  "program_type": "magi_adult",
  "household_size": 1,
  "language_preference": "en"
}
```

**Request Schema**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| applicant_id | UUID | Yes | Must exist in identity system | Secure constituent ID |
| county | string | Yes | One of 58 CA counties | County of residence |
| program_type | string | Yes | `magi_adult`, `magi_child`, `aged_blind_disabled`, `medicare_savings_qmb`, `pregnancy` | Program applying for |
| household_size | integer | Yes | > 0 | Tax filing household size |
| language_preference | string | No | `en`, `es`, `zh`, `vi`, `tl`, `ko` | Default: `en` |

**Response** (201 Created):
```json
{
  "application_id": "a7f3c8e1-4b2d-4c9e-8f1a-3d5e6b7c8d9e",
  "status": "draft",
  "created_at": "2026-01-10T14:20:00Z",
  "estimated_decision_date": null,
  "next_steps": [
    "Upload income verification documents (W-2, pay stubs, etc.)",
    "Complete household composition",
    "Submit application for county review"
  ]
}
```

**Response** (400 Bad Request):
```json
{
  "error": "validation_error",
  "message": "Invalid county name",
  "details": {
    "field": "county",
    "value": "San Fransisco",
    "allowed_values": ["San Francisco", "Los Angeles", ...]
  }
}
```

**Response** (401 Unauthorized):
```json
{
  "error": "unauthorized",
  "message": "Bearer token missing or invalid"
}
```

---

### GET /api/v1/applications/{application_id}

Retrieve application details.

**Authentication**: Required (applicant who owns it, or county_worker, or dhcs_admin)

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| application_id | UUID | Application identifier |

**Response** (200 OK):
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
  "benefitscal_id": "SF-2026-001234",
  "created_at": "2026-01-10T14:20:00Z",
  "updated_at": "2026-01-15T10:30:00Z",
  "documents": [
    {
      "document_id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
      "document_type": "w2",
      "processing_status": "extracted",
      "ocr_confidence": 0.96,
      "uploaded_at": "2026-01-10T14:25:00Z"
    }
  ],
  "income_records": [
    {
      "income_id": "i9a8b7c6-d5e4-3f2g-1h0i-j9k8l7m6n5o4",
      "source": "wages",
      "annualized_amount": 84500.00,
      "verification_status": "verified"
    }
  ]
}
```

**Response** (403 Forbidden):
```json
{
  "error": "forbidden",
  "message": "You do not have permission to access this application"
}
```

**Response** (404 Not Found):
```json
{
  "error": "not_found",
  "message": "Application not found"
}
```

---

## Document Endpoints

### POST /api/v1/documents/upload

Upload income verification document with automatic OCR extraction.

**Authentication**: Required (applicant or county_worker)

**Request**: `multipart/form-data`

**Form Fields**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| application_id | UUID | Yes | Must exist | Parent application |
| document_type | string | Yes | `w2`, `paystub`, `form_1040`, `schedule_c`, `ssa_1099`, `bank_statement`, `other` | Document category |
| file | binary | Yes | Max 10MB, PDF/JPG/PNG/TIFF | Document file |

**Example Request** (curl):
```bash
curl -X POST http://localhost:8003/api/v1/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "application_id=a7f3c8e1-4b2d-4c9e-8f1a-3d5e6b7c8d9e" \
  -F "document_type=w2" \
  -F "file=@W2_2025.pdf"
```

**Response** (202 Accepted) - async processing started:
```json
{
  "document_id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
  "processing_status": "processing",
  "message": "Document uploaded successfully. OCR extraction in progress.",
  "status_url": "/api/v1/documents/d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a/extraction"
}
```

**Response** (400 Bad Request):
```json
{
  "error": "invalid_file",
  "message": "File size exceeds 10MB limit",
  "max_size_bytes": 10485760
}
```

**Response** (413 Payload Too Large):
```json
{
  "error": "payload_too_large",
  "message": "File exceeds maximum upload size"
}
```

---

### GET /api/v1/documents/{document_id}/extraction

Check OCR extraction status and retrieve results.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| document_id | UUID | Document identifier |

**Response** (200 OK) - extraction complete:
```json
{
  "document_id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
  "processing_status": "extracted",
  "ocr_confidence": 0.96,
  "pii_detected": true,
  "extracted_data": {
    "tax_year": 2025,
    "employer_name": "ACME Corporation",
    "box_1_wages": 42500.00,
    "box_2_federal_tax_withheld": 3825.50,
    "box_16_state_wages_ca": 42500.00,
    "confidence_scores": {
      "box_1": 0.98,
      "box_2": 0.96
    }
  },
  "processed_at": "2026-01-10T14:25:23Z",
  "needs_review": false
}
```

**Response** (200 OK) - still processing:
```json
{
  "document_id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
  "processing_status": "processing",
  "message": "OCR extraction in progress. Check back in a few seconds.",
  "estimated_completion": "2026-01-10T14:25:30Z"
}
```

**Response** (200 OK) - manual review required:
```json
{
  "document_id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
  "processing_status": "manual_review_required",
  "ocr_confidence": 0.72,
  "extracted_data": {
    "box_1_wages": 42500.00,
    "confidence_scores": {
      "box_1": 0.72
    }
  },
  "needs_review": true,
  "review_reason": "OCR confidence below 85% threshold. Please verify extracted data or upload clearer document."
}
```

---

## Eligibility Endpoints

### POST /api/v1/eligibility/screen

Perform preliminary eligibility screening based on income and household data.

**Authentication**: Required

**Request Body**:
```json
{
  "application_id": "a7f3c8e1-4b2d-4c9e-8f1a-3d5e6b7c8d9e",
  "income_records": [
    {
      "source": "wages",
      "amount": 3250.00,
      "frequency": "biweekly"
    }
  ],
  "household_size": 1,
  "program": "Medi-Cal MAGI Adult"
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| application_id | UUID | Yes | Application being screened |
| income_records | array | Yes | List of income sources |
| household_size | integer | Yes | Tax filing household size |
| program | string | Yes | Program to evaluate eligibility for |

**Response** (200 OK) - eligible:
```json
{
  "result_id": "e1f2g3h4-i5j6-7k8l-9m0n-o1p2q3r4s5t6",
  "eligible": true,
  "program": "Medi-Cal MAGI Adult",
  "magi_income": 84500.00,
  "fpl_percentage": 512.00,
  "fpl_threshold": 138.00,
  "household_size": 1,
  "methodology": "magi",
  "explanation": "Based on your annual income of $84,500 and household size of 1, your income is 512% of the Federal Poverty Level. This exceeds the 138% FPL threshold for no-cost Medi-Cal. You may qualify for subsidized coverage through Covered California.",
  "next_steps": "Visit CoveredCA.com to explore subsidized health insurance options. You may be eligible for tax credits to reduce premiums.",
  "determination_date": "2026-01-10T15:00:00Z",
  "disclaimer": "This is a preliminary screening only. Final eligibility determination will be made by your county eligibility worker."
}
```

**Response** (200 OK) - eligible:
```json
{
  "result_id": "e1f2g3h4-i5j6-7k8l-9m0n-o1p2q3r4s5t6",
  "eligible": true,
  "program": "Medi-Cal MAGI Adult",
  "magi_income": 18600.00,
  "fpl_percentage": 112.50,
  "fpl_threshold": 138.00,
  "household_size": 1,
  "methodology": "magi",
  "explanation": "Based on your annual income of $18,600 and household size of 1, your income is 112.5% of the Federal Poverty Level. This is below the 138% FPL threshold for Medi-Cal, so you are likely eligible for no-cost Medi-Cal coverage.",
  "next_steps": "Please complete your application and upload all required income verification documents. Your county eligibility worker will review and make a final determination within 45 days.",
  "determination_date": "2026-01-10T15:00:00Z",
  "disclaimer": "This is a preliminary screening only. Final eligibility determination will be made by your county eligibility worker."
}
```

**Response** (400 Bad Request):
```json
{
  "error": "missing_income",
  "message": "At least one income record is required for eligibility screening"
}
```

---

## Status Query Endpoints

### POST /api/v1/status/query

Natural language status query interface powered by Azure OpenAI.

**Authentication**: Required (applicant who owns application, or county_worker, or dhcs_admin)

**Request Body**:
```json
{
  "application_id": "a7f3c8e1-4b2d-4c9e-8f1a-3d5e6b7c8d9e",
  "query": "What is the status of my application?"
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| application_id | UUID | Yes | Application to query |
| query | string | Yes | Natural language question (max 500 chars) |

**Response** (200 OK):
```json
{
  "query": "What is the status of my application?",
  "response": "Your Medi-Cal application (ID: a7f3...8d9e) was received on January 15, 2026 and is currently under county review. The typical processing time is 45 days. Your estimated decision date is March 1, 2026. Your application is on track and no additional information is needed at this time. You will receive an email when a decision is made.",
  "application_status": "county_processing",
  "estimated_decision_date": "2026-03-01",
  "days_since_submission": 10,
  "days_remaining": 35,
  "responded_at": "2026-01-25T14:30:00Z"
}
```

**Response** (200 OK) - additional info needed:
```json
{
  "query": "When will I get my results?",
  "response": "Your application requires additional documentation. On January 20, 2026, we sent you a request for your most recent pay stub showing year-to-date earnings. Please upload this document within 30 days (by February 19, 2026) to avoid processing delays. Your estimated decision date will be calculated once the document is received.",
  "application_status": "document_review",
  "missing_documents": [
    "Most recent pay stub (must show YTD earnings)"
  ],
  "deadline": "2026-02-19",
  "responded_at": "2026-01-25T14:30:00Z"
}
```

**Response** (400 Bad Request):
```json
{
  "error": "query_too_long",
  "message": "Query exceeds 500 character limit",
  "max_length": 500
}
```

**Response** (403 Forbidden):
```json
{
  "error": "forbidden",
  "message": "You do not have permission to query this application"
}
```

---

## Audit Endpoints (Admin Only)

### GET /api/v1/audit/logs

Retrieve audit logs for compliance and HIPAA oversight.

**Authentication**: Required (dhcs_admin role only)

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| application_id | UUID | No | Filter by application |
| action | string | No | Filter by action type (`document_upload`, `eligibility_screening`, etc.) |
| start_date | ISO date | No | Start of date range |
| end_date | ISO date | No | End of date range |
| limit | integer | No | Max results (default: 100, max: 1000) |

**Example Request**:
```
GET /api/v1/audit/logs?application_id=a7f3c8e1-4b2d-4c9e-8f1a-3d5e6b7c8d9e&limit=50
```

**Response** (200 OK):
```json
{
  "total": 127,
  "limit": 50,
  "offset": 0,
  "logs": [
    {
      "entry_id": "audit-001",
      "timestamp": "2026-01-10T14:20:00Z",
      "action": "application_create",
      "actor_id": "user:applicant-123",
      "actor_role": "applicant",
      "application_id": "a7f3c8e1-4b2d-4c9e-8f1a-3d5e6b7c8d9e",
      "outcome": "success",
      "pii_detected": false,
      "signature": "sha256:a3f8c2d1..."
    },
    {
      "entry_id": "audit-002",
      "timestamp": "2026-01-10T14:25:00Z",
      "action": "document_upload",
      "actor_id": "user:applicant-123",
      "actor_role": "applicant",
      "application_id": "a7f3c8e1-4b2d-4c9e-8f1a-3d5e6b7c8d9e",
      "document_id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
      "outcome": "success",
      "pii_detected": true,
      "masked_data": {
        "document_type": "w2",
        "file_name": "W2_2025_ACME_Corp.pdf"
      },
      "signature": "sha256:b4e9d3f2..."
    }
  ]
}
```

**Response** (403 Forbidden):
```json
{
  "error": "forbidden",
  "message": "Admin role required to access audit logs"
}
```

---

## Error Response Standards

All error responses follow this structure:

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    "field": "specific_field_if_applicable",
    "additional_context": "..."
  },
  "timestamp": "2026-01-10T14:30:00Z",
  "request_id": "req-a1b2c3d4"
}
```

**Common Error Codes**:
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `unauthorized` | 401 | Missing or invalid authentication token |
| `forbidden` | 403 | Valid token but insufficient permissions |
| `not_found` | 404 | Resource does not exist |
| `validation_error` | 400 | Request body validation failed |
| `invalid_file` | 400 | Uploaded file invalid (format, size, etc.) |
| `payload_too_large` | 413 | Request body exceeds size limit |
| `rate_limit_exceeded` | 429 | Too many requests from client |
| `internal_error` | 500 | Server-side error |
| `service_unavailable` | 503 | Dependent service (Azure OpenAI, Document Intelligence) down |

---

## Rate Limits

| Endpoint | Limit | Window | Scope |
|----------|-------|--------|-------|
| POST /api/v1/documents/upload | 10 requests | 1 minute | Per applicant |
| POST /api/v1/eligibility/screen | 20 requests | 1 minute | Per applicant |
| POST /api/v1/status/query | 30 requests | 1 minute | Per applicant |
| All other endpoints | 100 requests | 1 minute | Per applicant |

**Rate Limit Response** (429 Too Many Requests):
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many document upload requests. Please wait 60 seconds before retrying.",
  "retry_after_seconds": 42,
  "limit": 10,
  "window": "1 minute"
}
```

---

## Mock Mode

When running with `USE_MOCK_SERVICES=true`, all endpoints function normally but:

- **OCR Extraction**: Returns hardcoded W-2 data from `mock_data/sample_w2.json`
- **Eligibility Screening**: Uses real calculation logic with mock income data
- **BenefitsCal Submission**: Returns mock tracking number `SF-2026-MOCK-{timestamp}`
- **Status Queries**: Azure OpenAI calls replaced with template responses

**Mock mode is enabled by default for ports 8003 and requires no Azure credentials.**
