# API Contract: Permit Streamliner

**Accelerator**: 004-permit-streamliner  
**Agencies**: Governor's Office of Planning and Research (OPR), Housing & Community Development (HCD), Dept of Consumer Affairs (DCA)  
**Base URL**: `http://localhost:8004` (local), `https://permit-streamliner.azurewebsites.net` (prod)  
**Authentication**: Azure Entra ID Bearer Token (all endpoints except `/health`)  
**API Version**: v1  
**Date**: 2026-02-02

---

## Base Configuration

**Port**: 8004 (local development)  
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
    "azure_search": "available",
    "document_intelligence": "available",
    "blob_storage": "available",
    "redis": "connected"
  }
}
```

**Response** (503 Service Unavailable):
```json
{
  "status": "unhealthy",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "azure_openai": "unavailable"
  },
  "errors": ["Azure OpenAI endpoint not reachable"]
}
```

---

## Intake Endpoints

### POST /api/v1/intake/classify

Classify project type and extract entities from natural language description.

**Authentication**: Required (applicant or reviewer role)

**Request Body**:
```json
{
  "project_description": "I want to add a 500 square foot family room to the back of my house. It will be single story with a bathroom and electrical outlets.",
  "address": "1234 J Street, Sacramento, CA 95814"
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| project_description | string | Yes | Natural language description (max 2000 chars) |
| address | string | Yes | Project address |
| applicant_name | string | No | Name (encrypted at rest) |
| applicant_email | string | No | Email for notifications |
| applicant_phone | string | No | Phone number |

**Response** (200 OK):
```json
{
  "classification": {
    "project_type": "residential_addition",
    "confidence": 0.94,
    "extracted_entities": {
      "square_footage": 500,
      "stories": 1,
      "includes_bathroom": true,
      "includes_kitchen": false,
      "structural_changes": true
    }
  },
  "required_permits": [
    {
      "permit_type": "building",
      "name": "Residential Building Permit",
      "agency": "City of Sacramento - Building Division",
      "typical_timeline_days": 42,
      "estimated_fee_min": 1850.00,
      "estimated_fee_max": 2200.00
    },
    {
      "permit_type": "electrical",
      "name": "Electrical Permit",
      "agency": "City of Sacramento - Building Division",
      "typical_timeline_days": 30,
      "estimated_fee_min": 250.00,
      "estimated_fee_max": 400.00
    },
    {
      "permit_type": "plumbing",
      "name": "Plumbing Permit",
      "agency": "City of Sacramento - Building Division",
      "typical_timeline_days": 30,
      "estimated_fee_min": 300.00,
      "estimated_fee_max": 500.00
    }
  ],
  "total_estimated_timeline_days": 42,
  "total_estimated_fee_min": 2400.00,
  "total_estimated_fee_max": 3100.00,
  "next_steps": "Create an application to receive a personalized document checklist"
}
```

**Response** (200 OK) - low confidence:
```json
{
  "classification": {
    "project_type": "unknown",
    "confidence": 0.62,
    "message": "Your project description is complex and may require specialized permits. We recommend calling the permit counter at (916) 555-0100 for guidance."
  },
  "escalation_required": true,
  "contact_info": {
    "phone": "(916) 555-0100",
    "email": "permits@cityofsacramento.org",
    "hours": "Monday-Friday 8:00 AM - 4:00 PM"
  }
}
```

**Response** (400 Bad Request):
```json
{
  "error": "invalid_description",
  "message": "Project description is too short. Please provide more details about your project.",
  "min_length": 20
}
```

---

### POST /api/v1/applications

Create a new permit application.

**Authentication**: Required (applicant role)

**Request Body**:
```json
{
  "applicant": {
    "full_name": "Maria Martinez",
    "email": "maria@example.com",
    "phone": "916-555-1234",
    "business_name": "Martinez Construction LLC",
    "license_number": "CA-B-987654",
    "preferred_language": "es"
  },
  "project": {
    "description": "Adding 500 sq ft family room to single-family home",
    "type": "residential_addition",
    "address": "1234 J Street, Sacramento, CA 95814",
    "parcel_number": "006-0123-045",
    "jurisdiction": "City of Sacramento"
  }
}
```

**Response** (201 Created):
```json
{
  "application_id": "f7e6d5c4-b3a2-1098-7654-321fedcba098",
  "permit_number": "PRM-2026-000142",
  "status": "intake",
  "created_at": "2026-03-15T10:05:00Z",
  "checklist_url": "/api/v1/applications/f7e6d5c4-b3a2-1098-7654-321fedcba098/checklist"
}
```

---

### GET /api/v1/applications/{application_id}/checklist

Get personalized document checklist for application.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| application_id | UUID | Application identifier |

**Response** (200 OK):
```json
{
  "application_id": "f7e6d5c4-b3a2-1098-7654-321fedcba098",
  "permit_number": "PRM-2026-000142",
  "requirements": [
    {
      "requirement_id": "11111111-2222-3333-4444-555555555555",
      "permit_type": "building",
      "responsible_agency": "City of Sacramento - Building Division",
      "required_documents": [
        {
          "name": "Site Plan",
          "format": "PDF",
          "required": true,
          "description": "Must show property boundaries, existing structures, proposed addition location, setbacks from all property lines (min 5 feet side, 15 feet rear), and scale (1 inch = 20 feet or similar)"
        },
        {
          "name": "Architectural Drawings",
          "format": "PDF",
          "required": true,
          "description": "Floor plan, elevations (all 4 sides), roof plan, wall sections. Must be drawn to scale and include dimensions."
        },
        {
          "name": "Structural Calculations",
          "format": "PDF",
          "required": true,
          "description": "Signed and stamped by California licensed structural engineer (required for additions over 400 sq ft per Section R301.1.3)"
        }
      ],
      "estimated_processing_days": 42,
      "fee_estimate": 1850.00,
      "status": "pending"
    }
  ],
  "special_constraints": [
    {
      "type": "historic_district",
      "description": "Your property is in the Midtown Historic District. Additional Historic Preservation Commission review required (adds 30 days).",
      "additional_requirements": [
        "Historic preservation application form",
        "Exterior elevations showing compatibility with historic character"
      ]
    }
  ],
  "estimated_total_days": 72,
  "estimated_total_fee": 3200.00
}
```

---

## Document Endpoints

### POST /api/v1/documents/upload

Upload permit application document (site plan, architectural drawings, etc.).

**Authentication**: Required

**Request**: `multipart/form-data`

**Form Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| application_id | UUID | Yes | Parent application |
| requirement_id | UUID | No | Links to specific checklist item |
| filename | string | Yes | Original filename |
| file | binary | Yes | Max 50MB, PDF/PNG/JPG/TIFF |

**Example Request**:
```bash
curl -X POST http://localhost:8004/api/v1/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "application_id=f7e6d5c4-b3a2-1098-7654-321fedcba098" \
  -F "requirement_id=11111111-2222-3333-4444-555555555555" \
  -F "filename=site_plan.pdf" \
  -F "file=@site_plan.pdf"
```

**Response** (202 Accepted):
```json
{
  "document_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
  "extraction_status": "processing",
  "message": "Document uploaded successfully. Validation in progress.",
  "validation_url": "/api/v1/documents/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/validation"
}
```

---

### GET /api/v1/documents/{document_id}/validation

Check document validation status and results.

**Authentication**: Required

**Response** (200 OK) - validation complete:
```json
{
  "document_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
  "extraction_status": "completed",
  "extracted_data": {
    "lot_area_sqft": 6500,
    "existing_building_sqft": 1800,
    "proposed_addition_sqft": 500,
    "total_proposed_sqft": 2300,
    "stories": 2,
    "max_height_ft": 28,
    "front_setback_ft": 20,
    "rear_setback_ft": 15,
    "side_setback_left_ft": 5,
    "side_setback_right_ft": 5
  },
  "validation_results": {
    "lot_coverage": {
      "max": 0.50,
      "proposed": 0.354,
      "passed": true,
      "confidence": 0.92
    },
    "height": {
      "max_ft": 35,
      "proposed_ft": 28,
      "passed": true,
      "confidence": 0.88
    },
    "setback_front": {
      "min_ft": 15,
      "proposed_ft": 20,
      "passed": true,
      "confidence": 0.95
    },
    "setback_rear": {
      "min_ft": 10,
      "proposed_ft": 15,
      "passed": true,
      "confidence": 0.91
    }
  },
  "validation_passed": true,
  "overall_confidence": 0.92,
  "needs_review": false
}
```

**Response** (200 OK) - validation failed:
```json
{
  "document_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
  "extraction_status": "completed",
  "validation_results": {
    "setback_side": {
      "min_ft": 5,
      "proposed_ft": 3,
      "passed": false,
      "confidence": 0.87,
      "violation": "Proposed side setback (3 feet) is less than minimum required (5 feet). Variance or design modification required."
    }
  },
  "validation_passed": false,
  "needs_review": true,
  "corrective_actions": [
    "Revise site plan to show 5-foot minimum side setback",
    "Or apply for zoning variance (adds 60-90 days to timeline)"
  ]
}
```

---

## Zoning Endpoints

### GET /api/v1/zoning/check

Check zoning compliance for a property address.

**Authentication**: Required

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| address | string | Yes | Full property address |
| parcel_number | string | No | Assessor's Parcel Number (more precise than address) |

**Example Request**:
```
GET /api/v1/zoning/check?address=1234%20J%20Street,%20Sacramento,%20CA%2095814
```

**Response** (200 OK):
```json
{
  "address": "1234 J Street, Sacramento, CA 95814",
  "parcel_number": "006-0123-045",
  "jurisdiction": "City of Sacramento",
  "zoning": {
    "zone_code": "R-2A",
    "zone_name": "Low Density Residential",
    "overlay_zones": ["historic_district"],
    "permitted_uses": [
      "Single-family residential",
      "Two-family residential (duplex)",
      "Accessory dwelling unit (ADU)",
      "Home occupation"
    ],
    "restrictions": {
      "max_height_ft": 35,
      "max_stories": 2.5,
      "max_lot_coverage": 0.50,
      "min_lot_size_sqft": 5000,
      "setbacks": {
        "front_ft": 15,
        "rear_ft": 10,
        "side_ft": 5
      },
      "parking": {
        "required_spaces_per_unit": 2,
        "covered_spaces_required": true
      }
    }
  },
  "environmental_constraints": [
    {
      "type": "fema_flood_zone",
      "zone": "X",
      "description": "Area of minimal flood hazard (outside 100-year and 500-year floodplains)",
      "additional_requirements": []
    },
    {
      "type": "historic_district",
      "name": "Midtown Historic District",
      "description": "Properties must maintain historic character. Design review by Historic Preservation Commission required for exterior changes.",
      "additional_requirements": [
        "Historic preservation application",
        "Design guidelines compliance"
      ]
    }
  ],
  "data_source": "mock",
  "last_updated": "2026-01-15T00:00:00Z"
}
```

**Response** (404 Not Found):
```json
{
  "error": "parcel_not_found",
  "message": "Address not found in zoning database. Please verify address or contact Planning Department.",
  "contact": {
    "department": "City of Sacramento Planning Division",
    "phone": "(916) 555-0200"
  }
}
```

---

## Status Query Endpoints

### POST /api/v1/status/query

Natural language status query interface.

**Authentication**: Required (applicant who owns application, or reviewer)

**Request Body**:
```json
{
  "application_id": "f7e6d5c4-b3a2-1098-7654-321fedcba098",
  "query": "What's the status of my building permit?"
}
```

**Response** (200 OK):
```json
{
  "query": "What's the status of my building permit?",
  "response": "Your building permit application (PRM-2026-000142) is currently under plan review by the Building Division. Assigned reviewer: Maria Chen. The application was received on March 15, 2026 and is on track for decision by April 26, 2026 (30 business days). You are at Day 10 of 30 (33% complete). No additional information is needed at this time.",
  "application_status": "in_review",
  "current_stage": "Plan Review - Structural",
  "assigned_reviewer": "Maria Chen",
  "sla_status": "on_track",
  "days_elapsed": 10,
  "days_remaining": 20,
  "estimated_decision_date": "2026-04-26",
  "responded_at": "2026-03-25T14:30:00Z"
}
```

**Response** (200 OK) - corrections needed:
```json
{
  "query": "Why is my permit taking so long?",
  "response": "Your application requires corrections. On March 20, 2026, the plan reviewer requested: (1) Revised site plan showing 5-foot minimum side setback (currently shows 3 feet), and (2) Structural calculations for roof beam LVL-1 signed by licensed engineer. These corrections must be submitted within 30 days (by April 19, 2026) to avoid re-application fees. Once corrections are received, review will resume.",
  "application_status": "corrections_requested",
  "corrections": [
    {
      "item": "Site plan - side setback violation",
      "description": "Revise site plan to show 5-foot minimum side setback (currently shows 3 feet)",
      "deadline": "2026-04-19"
    },
    {
      "item": "Structural calculations missing engineer signature",
      "description": "Structural calculations for roof beam LVL-1 must be signed and stamped by California licensed structural engineer",
      "deadline": "2026-04-19"
    }
  ],
  "upload_url": "/api/v1/documents/upload",
  "responded_at": "2026-03-25T14:30:00Z"
}
```

---

## Routing & Review Endpoints (Reviewer/Admin Only)

### GET /api/v1/admin/workload

Get reviewer workload dashboard data.

**Authentication**: Required (reviewer or admin role)

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| agency | string | No | Filter by agency (e.g., "Building Division") |

**Response** (200 OK):
```json
{
  "reviewers": [
    {
      "reviewer_id": "emp-2847",
      "reviewer_name": "Maria Chen",
      "agency": "City of Sacramento - Building Division",
      "active_applications": 18,
      "pending_count": 5,
      "in_review_count": 10,
      "corrections_requested_count": 3,
      "avg_days_in_review": 12.3,
      "sla_at_risk_count": 2,
      "sla_breached_count": 0
    },
    {
      "reviewer_id": "emp-3921",
      "reviewer_name": "James Wong",
      "agency": "City of Sacramento - Building Division",
      "active_applications": 22,
      "pending_count": 8,
      "in_review_count": 12,
      "corrections_requested_count": 2,
      "avg_days_in_review": 14.7,
      "sla_at_risk_count": 4,
      "sla_breached_count": 1
    }
  ],
  "agency_summary": {
    "total_applications": 187,
    "avg_days_to_decision": 28.4,
    "sla_compliance_rate": 0.87
  }
}
```

---

### GET /api/v1/admin/sla-dashboard

Get SLA tracking dashboard.

**Authentication**: Required (admin role)

**Response** (200 OK):
```json
{
  "summary": {
    "total_active_applications": 187,
    "on_track": 142,
    "at_risk": 38,
    "breached": 7,
    "sla_compliance_rate": 0.85
  },
  "at_risk_applications": [
    {
      "application_id": "12345678-1234-1234-1234-123456789012",
      "permit_number": "PRM-2026-000089",
      "project_type": "commercial_tenant_improvement",
      "submitted_at": "2026-02-01T10:00:00Z",
      "sla_deadline": "2026-03-03",
      "days_remaining": 3,
      "assigned_reviewer": "James Wong",
      "current_stage": "Fire Department review",
      "priority": "high"
    }
  ],
  "breached_applications": [
    {
      "application_id": "87654321-4321-4321-4321-210987654321",
      "permit_number": "PRM-2026-000042",
      "project_type": "residential_addition",
      "submitted_at": "2026-01-15T10:00:00Z",
      "sla_deadline": "2026-02-14",
      "days_overdue": 12,
      "assigned_reviewer": "Maria Chen",
      "escalation_reason": "Awaiting structural engineer review - external delay",
      "priority": "urgent"
    }
  ]
}
```

---

## Error Response Standards

All errors follow this structure:

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {},
  "timestamp": "2026-03-15T10:30:00Z",
  "request_id": "req-xyz123"
}
```

**Common Error Codes**:
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `unauthorized` | 401 | Missing or invalid authentication |
| `forbidden` | 403 | Insufficient permissions |
| `not_found` | 404 | Resource doesn't exist |
| `validation_error` | 400 | Request validation failed |
| `invalid_file` | 400 | Invalid file format/size |
| `payload_too_large` | 413 | File exceeds 50MB limit |
| `rate_limit_exceeded` | 429 | Too many requests |
| `internal_error` | 500 | Server error |
| `service_unavailable` | 503 | Dependent service down |

---

## Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /api/v1/documents/upload | 20 requests | 5 minutes |
| POST /api/v1/intake/classify | 30 requests | 1 minute |
| POST /api/v1/status/query | 30 requests | 1 minute |
| GET /api/v1/zoning/check | 50 requests | 1 minute |
| All other endpoints | 100 requests | 1 minute |

---

## Mock Mode

When `USE_MOCK_SERVICES=true` (default for port 8004):

- **Zoning lookups**: Return data from `mock_data/zoning-mock-data.json`
- **Document validation**: Returns hardcoded validation results
- **Project classification**: Real GPT-4o (or template-based if Azure unavailable)
- **Environmental constraints**: Mock FEMA flood zones, CNDDB data

**No Azure credentials required for mock mode.**
