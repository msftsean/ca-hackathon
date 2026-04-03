# API Contracts: GenAI Procurement Compliance Checker

**Feature**: `005-genai-procurement-compliance`  
**Created**: 2024-12-19  
**Base URL**: `http://localhost:8005` (development), `https://procurement-compliance.ca.gov/api` (production)  
**Authentication**: Azure Entra ID Bearer token (all endpoints except `/health`)

## API Endpoints

### Health & Status

#### GET /health

Health check endpoint for monitoring and load balancer probes.

**Authentication**: None required

**Request Parameters**: None

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "timestamp": "2024-12-19T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "azure_openai": "healthy",
    "blob_storage": "healthy"
  }
}
```

**Response (503 Service Unavailable)**:
```json
{
  "status": "unhealthy",
  "timestamp": "2024-12-19T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "azure_openai": "degraded",
    "blob_storage": "healthy"
  },
  "error": "Azure OpenAI API quota exceeded"
}
```

---

### Attestation Management

#### POST /attestations/upload

Upload vendor AI attestation document for analysis.

**Authentication**: Required (procurement officer or compliance officer role)

**Request Headers**:
| Header | Value | Required |
|--------|-------|----------|
| Authorization | Bearer {token} | Yes |
| Content-Type | multipart/form-data | Yes |

**Request Body (multipart/form-data)**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | File | Yes | PDF or DOCX attestation document (max 50MB) |
| vendor_name | string | Yes | Legal name of vendor |
| vendor_contact | string | No | Vendor contact email |
| procurement_id | string | Yes | RFP or procurement cycle ID |
| assigned_to | string | No | Email of assigned procurement officer |

**Example Request**:
```bash
curl -X POST http://localhost:8005/attestations/upload \
  -H "Authorization: Bearer {token}" \
  -F "file=@vendor-acme-attestation.pdf" \
  -F "vendor_name=Acme AI Corporation" \
  -F "vendor_contact=compliance@acme-ai.com" \
  -F "procurement_id=RFP-2024-CDT-001" \
  -F "assigned_to=john.doe@state.ca.gov"
```

**Response (201 Created)**:
```json
{
  "attestation_id": "550e8400-e29b-41d4-a716-446655440000",
  "vendor_name": "Acme AI Corporation",
  "vendor_contact": "compliance@acme-ai.com",
  "procurement_id": "RFP-2024-CDT-001",
  "file_format": "PDF",
  "file_size_bytes": 2458624,
  "page_count": 42,
  "submitted_by": "jane.smith@state.ca.gov",
  "submitted_at": "2024-12-19T10:30:00Z",
  "status": "uploaded",
  "document_url": "https://storage.blob.core.windows.net/attestations/550e8400.pdf?sas=...",
  "analysis_url": "/attestations/550e8400-e29b-41d4-a716-446655440000/analyze"
}
```

**Response (400 Bad Request)**:
```json
{
  "error": "Invalid file format",
  "message": "Only PDF and DOCX files are supported. Received: application/zip",
  "supported_formats": ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
}
```

**Response (413 Payload Too Large)**:
```json
{
  "error": "File too large",
  "message": "File size 62,914,560 bytes exceeds maximum 52,428,800 bytes (50 MB)",
  "max_size_bytes": 52428800
}
```

**Status Codes**:
- `201 Created`: Attestation uploaded successfully
- `400 Bad Request`: Invalid file format, missing required fields, or validation failure
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User lacks procurement officer or compliance officer role
- `413 Payload Too Large`: File exceeds 50MB limit
- `422 Unprocessable Entity`: Duplicate attestation (same vendor + procurement_id)

---

#### POST /attestations/{attestation_id}/analyze

Initiate compliance analysis for uploaded attestation.

**Authentication**: Required (procurement officer or compliance officer role)

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| attestation_id | UUID | Attestation identifier from upload response |

**Request Body**: None

**Example Request**:
```bash
curl -X POST http://localhost:8005/attestations/550e8400-e29b-41d4-a716-446655440000/analyze \
  -H "Authorization: Bearer {token}"
```

**Response (202 Accepted)**:
```json
{
  "attestation_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "analyzing",
  "analysis_started_at": "2024-12-19T10:35:00Z",
  "estimated_completion": "2024-12-19T10:40:00Z",
  "progress_url": "/attestations/550e8400-e29b-41d4-a716-446655440000/analysis-status",
  "stream_url": "/attestations/550e8400-e29b-41d4-a716-446655440000/analysis-stream"
}
```

**Response (409 Conflict)**:
```json
{
  "error": "Analysis already in progress",
  "message": "Attestation 550e8400-e29b-41d4-a716-446655440000 is currently being analyzed",
  "status": "analyzing",
  "started_at": "2024-12-19T10:30:00Z"
}
```

**Status Codes**:
- `202 Accepted`: Analysis initiated successfully
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Attestation not found
- `409 Conflict`: Analysis already in progress or already completed

---

#### GET /attestations/{attestation_id}/analysis-status

Get current analysis progress and status.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| attestation_id | UUID | Attestation identifier |

**Example Request**:
```bash
curl http://localhost:8005/attestations/550e8400-e29b-41d4-a716-446655440000/analysis-status \
  -H "Authorization: Bearer {token}"
```

**Response (200 OK) - In Progress**:
```json
{
  "attestation_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "analyzing",
  "progress_percentage": 65,
  "current_stage": "Evaluating SB 53 cross-references",
  "stages_completed": ["Document parsing", "EO N-5-26 analysis"],
  "stages_remaining": ["NIST AI RMF classification", "Gap analysis", "Report generation"],
  "started_at": "2024-12-19T10:35:00Z",
  "estimated_completion": "2024-12-19T10:40:00Z"
}
```

**Response (200 OK) - Completed**:
```json
{
  "attestation_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "complete",
  "progress_percentage": 100,
  "current_stage": "Analysis complete",
  "started_at": "2024-12-19T10:35:00Z",
  "completed_at": "2024-12-19T10:39:23Z",
  "results_url": "/attestations/550e8400-e29b-41d4-a716-446655440000/results"
}
```

**Status Codes**:
- `200 OK`: Status retrieved successfully
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Attestation not found

---

#### GET /attestations/{attestation_id}/results

Retrieve compliance analysis results.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| attestation_id | UUID | Attestation identifier |

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| include_evidence | boolean | true | Include evidence excerpts in results |
| severity_filter | string | all | Filter by severity: `all`, `critical`, `high`, `medium`, `low` |

**Example Request**:
```bash
curl "http://localhost:8005/attestations/550e8400-e29b-41d4-a716-446655440000/results?include_evidence=true" \
  -H "Authorization: Bearer {token}"
```

**Response (200 OK)**:
```json
{
  "attestation_id": "550e8400-e29b-41d4-a716-446655440000",
  "vendor_name": "Acme AI Corporation",
  "procurement_id": "RFP-2024-CDT-001",
  "analysis_completed_at": "2024-12-19T10:39:23Z",
  "overall_score": 78,
  "compliance_summary": {
    "total_rules": 18,
    "compliant": 12,
    "partial": 4,
    "non_compliant": 2,
    "unclear": 0
  },
  "severity_breakdown": {
    "critical_gaps": 0,
    "high_gaps": 1,
    "medium_gaps": 3,
    "low_gaps": 2
  },
  "eo_n_5_26_results": [
    {
      "rule_id": "EO-N-5-26-001",
      "requirement_summary": "Content safety and harmful content filtering",
      "status": "compliant",
      "confidence_score": 92,
      "evidence": "Vendor implements Azure OpenAI content filters at severity level 2 for hate, sexual, violence, and self-harm categories.",
      "severity": "critical"
    },
    {
      "rule_id": "EO-N-5-26-007",
      "requirement_summary": "Bias testing and fairness evaluation",
      "status": "partial",
      "confidence_score": 68,
      "evidence": "Vendor mentions bias testing but does not provide methodology, metrics, or test results.",
      "severity": "high",
      "gap_description": "Insufficient detail on bias testing methodology and results"
    }
  ],
  "sb_53_applicable": true,
  "sb_53_trigger_reason": "System makes automated decisions affecting eligibility for public benefits",
  "nist_ai_rmf_tier": 3,
  "nist_ai_rmf_justification": "High-risk system: affects legal/financial rights, serves vulnerable population",
  "gap_analysis_url": "/attestations/550e8400-e29b-41d4-a716-446655440000/gaps",
  "report_generation_url": "/attestations/550e8400-e29b-41d4-a716-446655440000/reports"
}
```

**Status Codes**:
- `200 OK`: Results retrieved successfully
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Attestation not found
- `425 Too Early`: Analysis not yet complete (status != `complete`)

---

#### GET /attestations/{attestation_id}/gaps

Retrieve detailed gap analysis with remediation guidance.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| attestation_id | UUID | Attestation identifier |

**Example Request**:
```bash
curl http://localhost:8005/attestations/550e8400-e29b-41d4-a716-446655440000/gaps \
  -H "Authorization: Bearer {token}"
```

**Response (200 OK)**:
```json
{
  "attestation_id": "550e8400-e29b-41d4-a716-446655440000",
  "vendor_name": "Acme AI Corporation",
  "overall_score": 78,
  "risk_level": "medium",
  "disqualifying_gaps": false,
  "gaps": [
    {
      "rule_id": "EO-N-5-26-007",
      "requirement_summary": "Bias testing and fairness evaluation",
      "severity": "high",
      "gap_description": "Insufficient detail on bias testing methodology and results",
      "current_evidence": "Vendor mentions bias testing but does not provide methodology, metrics, or test results.",
      "remediation_guidance": "Provide detailed bias testing methodology including: (1) test datasets used, (2) demographic categories evaluated, (3) fairness metrics calculated (e.g., demographic parity, equalized odds), (4) test results with pass/fail thresholds, (5) remediation actions for identified biases.",
      "remediation_complexity": "medium",
      "estimated_effort": "4-8 hours to document existing testing or 2-4 weeks to conduct comprehensive bias evaluation"
    },
    {
      "rule_id": "EO-N-5-26-012",
      "requirement_summary": "Civil rights impact assessment",
      "severity": "medium",
      "gap_description": "No civil rights impact assessment provided",
      "current_evidence": null,
      "remediation_guidance": "Submit civil rights impact assessment addressing: (1) protected classes potentially affected, (2) disparate impact analysis, (3) accommodation for disabilities, (4) language access provisions, (5) mitigation strategies.",
      "remediation_complexity": "high",
      "estimated_effort": "2-4 weeks with legal counsel review"
    }
  ],
  "next_steps": [
    "Address 1 high-severity gap to improve score above 85 (vendor acceptance threshold)",
    "Request additional documentation from vendor for partial compliance items",
    "Schedule follow-up call with vendor to clarify bias testing methodology"
  ]
}
```

**Status Codes**:
- `200 OK`: Gap analysis retrieved successfully
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Attestation not found

---

### Vendor Comparison

#### POST /compare

Compare multiple vendor attestations side-by-side.

**Authentication**: Required (procurement officer or compliance officer role)

**Request Body**:
```json
{
  "procurement_id": "RFP-2024-CDT-001",
  "attestation_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001",
    "770e8400-e29b-41d4-a716-446655440002"
  ],
  "comparison_criteria": ["overall_score", "critical_gaps", "high_gaps", "sb_53_compliance", "nist_tier"]
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8005/compare \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d @comparison-request.json
```

**Response (200 OK)**:
```json
{
  "procurement_id": "RFP-2024-CDT-001",
  "compared_at": "2024-12-19T11:00:00Z",
  "vendors": [
    {
      "attestation_id": "550e8400-e29b-41d4-a716-446655440000",
      "vendor_name": "Acme AI Corporation",
      "overall_score": 78,
      "rank": 2,
      "critical_gaps": 0,
      "high_gaps": 1,
      "medium_gaps": 3,
      "low_gaps": 2,
      "sb_53_applicable": true,
      "nist_tier": 3,
      "recommendation": "Request additional bias testing documentation"
    },
    {
      "attestation_id": "660e8400-e29b-41d4-a716-446655440001",
      "vendor_name": "BetaTech Solutions",
      "overall_score": 92,
      "rank": 1,
      "critical_gaps": 0,
      "high_gaps": 0,
      "medium_gaps": 1,
      "low_gaps": 1,
      "sb_53_applicable": true,
      "nist_tier": 3,
      "recommendation": "Meets all critical requirements, proceed to contract negotiation"
    },
    {
      "attestation_id": "770e8400-e29b-41d4-a716-446655440002",
      "vendor_name": "GammaAI Inc",
      "overall_score": 58,
      "rank": 3,
      "critical_gaps": 1,
      "high_gaps": 3,
      "medium_gaps": 2,
      "low_gaps": 1,
      "sb_53_applicable": true,
      "nist_tier": 4,
      "recommendation": "Disqualify - critical civil rights compliance gap"
    }
  ],
  "comparison_summary": "BetaTech Solutions has highest compliance score (92) with no critical or high-severity gaps. GammaAI Inc has disqualifying critical gap and should be excluded. Acme AI Corporation is viable pending bias testing documentation."
}
```

**Status Codes**:
- `200 OK`: Comparison generated successfully
- `400 Bad Request`: Invalid attestation IDs or attestations from different procurement cycles
- `401 Unauthorized`: Missing or invalid authentication token

---

### Report Generation

#### POST /attestations/{attestation_id}/reports

Generate gap analysis report in PDF or DOCX format.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| attestation_id | UUID | Attestation identifier |

**Request Body**:
```json
{
  "format": "pdf",
  "report_type": "gap_analysis",
  "include_remediation": true,
  "include_evidence": true,
  "watermark": "CONFIDENTIAL - PROCUREMENT REVIEW",
  "recipient_name": "John Doe, Procurement Officer",
  "purpose": "Vendor evaluation for RFP-2024-CDT-001"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8005/attestations/550e8400-e29b-41d4-a716-446655440000/reports \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d @report-request.json
```

**Response (200 OK)**:
```json
{
  "report_id": "880e8400-e29b-41d4-a716-446655440003",
  "attestation_id": "550e8400-e29b-41d4-a716-446655440000",
  "format": "pdf",
  "report_type": "gap_analysis",
  "generated_at": "2024-12-19T11:05:00Z",
  "generated_by": "jane.smith@state.ca.gov",
  "file_size_bytes": 1245632,
  "download_url": "https://storage.blob.core.windows.net/reports/880e8400.pdf?sas=...",
  "expires_at": "2024-12-19T12:05:00Z"
}
```

**Status Codes**:
- `200 OK`: Report generated successfully
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Attestation not found
- `422 Unprocessable Entity`: Invalid format or report_type

---

### Audit Logging

#### GET /audit/logs

Query audit trail for compliance and security monitoring.

**Authentication**: Required (auditor role or compliance officer role)

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| start_date | ISO 8601 date | 7 days ago | Start of date range |
| end_date | ISO 8601 date | now | End of date range |
| user_id | string | null | Filter by user email |
| attestation_id | UUID | null | Filter by attestation |
| action_type | string | null | Filter by action: `upload`, `analyze`, `access`, `decision` |
| page | integer | 1 | Page number for pagination |
| page_size | integer | 50 | Results per page (max 500) |

**Example Request**:
```bash
curl "http://localhost:8005/audit/logs?start_date=2024-12-01&user_id=jane.smith@state.ca.gov&action_type=decision" \
  -H "Authorization: Bearer {token}"
```

**Response (200 OK)**:
```json
{
  "total_records": 127,
  "page": 1,
  "page_size": 50,
  "total_pages": 3,
  "logs": [
    {
      "record_id": "audit-990e8400-e29b-41d4-a716-446655440004",
      "timestamp": "2024-12-19T11:30:00Z",
      "user_id": "jane.smith@state.ca.gov",
      "user_role": "procurement_officer",
      "action_type": "decision",
      "attestation_id": "550e8400-e29b-41d4-a716-446655440000",
      "decision_type": "request_clarification",
      "decision_rationale": "Vendor bias testing methodology insufficient, requested additional documentation",
      "ip_address": "10.0.1.45",
      "record_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
  ]
}
```

**Status Codes**:
- `200 OK`: Audit logs retrieved successfully
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User lacks auditor or compliance officer role

---

## Error Response Format

All error responses follow consistent JSON structure:

```json
{
  "error": "Error category (e.g., 'Validation failed', 'Not found')",
  "message": "Human-readable error description",
  "details": {
    "field": "Specific field that caused error (if applicable)",
    "constraint": "Validation constraint violated (if applicable)"
  },
  "request_id": "req-123456789",
  "timestamp": "2024-12-19T10:30:00Z"
}
```

## Authentication

All endpoints except `/health` require Azure Entra ID authentication.

**Request Header**:
```
Authorization: Bearer {access_token}
```

**Token Requirements**:
- Audience: `api://procurement-compliance-api`
- Scopes: `Attestation.Read`, `Attestation.Write`, `Audit.Read`
- Roles: `procurement_officer`, `compliance_officer`, or `auditor`

**Token Expiration**: 1 hour (refresh required)

## Rate Limiting

| Endpoint Category | Rate Limit | Window |
|------------------|------------|--------|
| Upload | 10 requests/minute | Per user |
| Analysis | 5 requests/minute | Per user |
| Query (GET) | 100 requests/minute | Per user |
| Report generation | 20 requests/hour | Per user |
| Audit logs | 50 requests/minute | Per user |

**Rate Limit Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1703001600
```

## API Versioning

Current version: **v1** (included in base path)

Breaking changes will increment major version (v2, v3, etc.)
