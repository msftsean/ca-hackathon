# API Contracts: BenefitsCal Navigator Agent

**Feature**: BenefitsCal Navigator Agent  
**Version**: 1.0  
**Date**: 2026-02-02  
**Base URL**: `http://localhost:8001` (development), `https://benefitscal-navigator.azure.gov` (production)

## Overview

This document defines all HTTP endpoints for the BenefitsCal Navigator Agent backend API. All endpoints return JSON unless otherwise specified. Authentication is optional for public endpoints (chat, pre-screening) and required for county staff endpoints (escalation management).

---

## Health and Status Endpoints

### GET /health

Health check endpoint for monitoring and load balancer probes.

**Request**: None

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "benefitscal-navigator",
  "version": "1.0.0",
  "timestamp": "2026-02-02T14:30:00Z",
  "dependencies": {
    "azure_openai": "healthy",
    "azure_search": "healthy",
    "postgres": "healthy",
    "redis": "healthy"
  }
}
```

**Mock Mode Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "benefitscal-navigator",
  "version": "1.0.0",
  "timestamp": "2026-02-02T14:30:00Z",
  "dependencies": {
    "azure_openai": "mock",
    "azure_search": "mock",
    "postgres": "healthy",
    "redis": "mock"
  },
  "mock_mode": true
}
```

**Error Response** (503 Service Unavailable):
```json
{
  "status": "unhealthy",
  "service": "benefitscal-navigator",
  "errors": [
    "Azure OpenAI connection failed",
    "Redis connection timeout"
  ]
}
```

---

## Chat and Q&A Endpoints

### POST /chat

Process a natural language query about benefit programs.

**Authentication**: None (public endpoint)

**Request Headers**:
- `Content-Type: application/json`

**Request Body**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "What are the income limits for CalFresh for a family of 3?",
  "language": "en"
}
```

**Request Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | UUID | Yes | Session identifier (generated client-side or via POST /sessions) |
| `query` | String (max 2000 chars) | Yes | Natural language question |
| `language` | String (ISO 639-1) | No | Preferred response language. If not provided, auto-detected. Supported: en, es, zh, vi, tl, ko, hy, fa, ar |

**Response** (200 OK):
```json
{
  "query_id": "660e8400-e29b-41d4-a716-446655440111",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "For a family of 3 people in California, the gross monthly income limit for CalFresh is $2,495 (130% of the Federal Poverty Level). The net monthly income limit is $1,920 (100% FPL). These limits are updated annually. For more information, visit BenefitsCal.com.",
  "intent": "eligibility_question",
  "confidence": 0.95,
  "language": "en",
  "citations": [
    {
      "document_id": "770e8400-e29b-41d4-a716-446655440222",
      "citation": "CDSS CalFresh Manual Section 63-300.1",
      "relevance": 0.92,
      "url": "https://www.cdss.ca.gov/calfresh-manual/63-300"
    }
  ],
  "escalated": false,
  "processing_time_ms": 1850
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `query_id` | UUID | Unique identifier for this query (for audit logs) |
| `session_id` | UUID | Session identifier |
| `response` | String | Natural language response in requested language |
| `intent` | String (enum) | Classified intent: `eligibility_question`, `program_info`, `prescreening`, `application_status`, `escalation_request`, `crisis`, `unknown` |
| `confidence` | Float (0.0-1.0) | Agent confidence in response accuracy |
| `language` | String (ISO 639-1) | Language of response |
| `citations` | Array | Source documents used in response |
| `escalated` | Boolean | Whether this query triggered escalation to county staff |
| `processing_time_ms` | Integer | Time taken to generate response |

**Error Response** (400 Bad Request):
```json
{
  "error": "validation_error",
  "message": "query field is required",
  "details": {
    "field": "query",
    "constraint": "required"
  }
}
```

**Error Response** (429 Too Many Requests):
```json
{
  "error": "rate_limit_exceeded",
  "message": "Maximum 20 queries per minute per session",
  "retry_after_seconds": 30
}
```

**Error Response** (503 Service Unavailable):
```json
{
  "error": "service_unavailable",
  "message": "Azure OpenAI service temporarily unavailable. Please try again in a few moments."
}
```

---

### POST /sessions

Create a new conversation session.

**Authentication**: None (public endpoint)

**Request Headers**:
- `Content-Type: application/json`

**Request Body**:
```json
{
  "channel": "web",
  "language": "en",
  "county": "Los Angeles"
}
```

**Request Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `channel` | String (enum) | No | Interaction channel: `web`, `voice`. Default: `web` |
| `language` | String (ISO 639-1) | No | Preferred language. Default: `en` |
| `county` | String | No | California county (one of 58 counties) |

**Response** (201 Created):
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "started_at": "2026-02-02T14:30:00Z",
  "channel": "web",
  "language": "en",
  "county": "Los Angeles"
}
```

---

### GET /sessions/{session_id}

Retrieve conversation session details and query history.

**Authentication**: None for owner, required for county staff

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `session_id` | UUID | Session identifier |

**Response** (200 OK):
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "started_at": "2026-02-02T14:30:00Z",
  "ended_at": null,
  "channel": "web",
  "language": "en",
  "county": "Los Angeles",
  "escalated": false,
  "query_count": 3,
  "queries": [
    {
      "query_id": "660e8400-e29b-41d4-a716-446655440111",
      "timestamp": "2026-02-02T14:30:15Z",
      "query": "What are the income limits for CalFresh?",
      "response": "For a family of 3 people in California...",
      "intent": "eligibility_question",
      "confidence": 0.95
    }
  ]
}
```

**Error Response** (404 Not Found):
```json
{
  "error": "session_not_found",
  "message": "Session 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

---

## Eligibility Pre-Screening Endpoints

### POST /prescreening

Submit household information for preliminary eligibility determination.

**Authentication**: None (public endpoint)

**Request Headers**:
- `Content-Type: application/json`

**Request Body**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "household_size": 3,
  "monthly_income_total": 2200.00,
  "county": "Los Angeles",
  "has_senior_65plus": false,
  "has_disability": false,
  "has_child_under_18": true,
  "citizenship_status": "citizen",
  "currently_working": true
}
```

**Request Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | UUID | Yes | Session identifier |
| `household_size` | Integer (1-20) | Yes | Number of people in household |
| `monthly_income_total` | Decimal | Yes | Total household monthly income (USD) |
| `county` | String | Yes | California county (one of 58 counties) |
| `has_senior_65plus` | Boolean | No | Household includes someone 65+ (default: false) |
| `has_disability` | Boolean | No | Household includes someone with disability (default: false) |
| `has_child_under_18` | Boolean | No | Household includes child under 18 (default: false) |
| `citizenship_status` | String (enum) | No | `citizen`, `qualified_immigrant`, `mixed_status`, `prefer_not_to_say` (default: `prefer_not_to_say`) |
| `currently_working` | Boolean | No | Any household member employed (default: null) |

**Response** (200 OK):
```json
{
  "profile_id": "880e8400-e29b-41d4-a716-446655440333",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "results": {
    "calfresh": {
      "likely_eligible": true,
      "reason": "Gross income $2,200 is below limit $2,495 for household of 3",
      "income_limit_gross": 2495.00,
      "income_limit_net": 1920.00,
      "next_steps": "Apply at BenefitsCal.com",
      "confidence": 0.92
    },
    "calworks": {
      "likely_eligible": false,
      "reason": "Income exceeds CalWORKs limits for household of 3 with one child",
      "income_limit": 1473.00,
      "next_steps": "Contact Los Angeles County DPSS for case-by-case review",
      "confidence": 0.88
    },
    "general_relief": {
      "likely_eligible": false,
      "reason": "General Relief is for individuals without children",
      "next_steps": null,
      "confidence": 0.95
    },
    "capi": {
      "likely_eligible": false,
      "reason": "No household member 65+ or disabled",
      "next_steps": null,
      "confidence": 0.98
    }
  },
  "disclaimer": "This is a preliminary determination only. Actual eligibility is determined by your county welfare office. Apply at BenefitsCal.com for an official determination.",
  "processing_time_ms": 850
}
```

**Error Response** (400 Bad Request):
```json
{
  "error": "validation_error",
  "message": "household_size must be between 1 and 20",
  "details": {
    "field": "household_size",
    "value": 0,
    "constraint": "min: 1, max: 20"
  }
}
```

---

## Voice Interaction Endpoints

### POST /voice/session

Initiate a voice interaction session (WebRTC).

**Authentication**: None (public endpoint)

**Request Headers**:
- `Content-Type: application/json`

**Request Body**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "language": "en",
  "consent_recording": true
}
```

**Request Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | UUID | Yes | Parent conversation session ID |
| `language` | String (ISO 639-1) | No | Voice language (default: en) |
| `consent_recording` | Boolean | Yes | California two-party consent law requires explicit consent |

**Response** (201 Created):
```json
{
  "voice_session_id": "aa0e8400-e29b-41d4-a716-446655440444",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "webrtc_endpoint": "wss://benefitscal-navigator.azure.gov/voice/aa0e8400-e29b-41d4-a716-446655440444",
  "ice_servers": [
    {
      "urls": "stun:stun.azure.com:3478"
    }
  ],
  "ai_identification": "This is an AI agent. This conversation will be recorded. You may request a human agent at any time.",
  "created_at": "2026-02-02T14:35:00Z"
}
```

**Error Response** (400 Bad Request):
```json
{
  "error": "consent_required",
  "message": "consent_recording must be true per California two-party consent law"
}
```

**Mock Mode Note**: Voice endpoints return mock WebRTC configuration but do not establish actual voice connection in mock mode.

---

## Escalation and Ticket Endpoints

### POST /escalations

Create an escalation ticket to county staff.

**Authentication**: None for resident-initiated, required for county staff-initiated

**Request Headers**:
- `Content-Type: application/json`

**Request Body**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "escalation_reason": "low_confidence",
  "priority": "medium",
  "resident_contact_info": "jane.doe@example.com"
}
```

**Request Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | UUID | Yes | Session to escalate |
| `escalation_reason` | String (enum) | Yes | `low_confidence`, `crisis`, `fraud_allegation`, `policy_exception`, `cpra_request`, `constituent_request`, `unknown_intent` |
| `priority` | String (enum) | No | `emergency`, `urgent`, `high`, `medium`, `low` (default: auto-determined by escalation_reason) |
| `resident_contact_info` | String | No | Email or phone number for follow-up (PII-encrypted) |

**Response** (201 Created):
```json
{
  "ticket_id": "990e8400-e29b-41d4-a716-446655440444",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "escalation_reason": "low_confidence",
  "priority": "medium",
  "assigned_county": "Los Angeles",
  "status": "pending",
  "expected_resolution_time": "2 business days",
  "created_at": "2026-02-02T14:40:00Z"
}
```

---

### GET /escalations/{ticket_id}

Retrieve escalation ticket status.

**Authentication**: Required (county staff or ticket creator)

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `ticket_id` | UUID | Escalation ticket identifier |

**Response** (200 OK):
```json
{
  "ticket_id": "990e8400-e29b-41d4-a716-446655440444",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "escalation_reason": "low_confidence",
  "priority": "medium",
  "assigned_county": "Los Angeles",
  "status": "in_progress",
  "expected_resolution_time": "2 business days",
  "created_at": "2026-02-02T14:40:00Z",
  "resolved_at": null,
  "conversation_summary": "Resident asked about CalWORKs eligibility with special income situation. Agent confidence 65%."
}
```

**Error Response** (403 Forbidden):
```json
{
  "error": "forbidden",
  "message": "You do not have permission to view this escalation ticket"
}
```

---

## Program Information Endpoints

### GET /programs

List all benefit programs with basic information.

**Authentication**: None (public endpoint)

**Response** (200 OK):
```json
{
  "programs": [
    {
      "program_id": "calfresh",
      "program_name": "CalFresh",
      "description": "CalFresh helps low-income people and families buy groceries. CalFresh benefits are issued monthly on an Electronic Benefit Transfer (EBT) card.",
      "administering_agency": "California Department of Social Services (CDSS)",
      "county_administered": true,
      "application_url": "https://www.benefitscal.com",
      "contact_phone": "1-877-847-3663",
      "multilingual_support": {
        "es": "1-877-847-3663",
        "zh": "1-877-847-3663",
        "vi": "1-877-847-3663"
      }
    },
    {
      "program_id": "calworks",
      "program_name": "CalWORKs",
      "description": "CalWORKs provides temporary cash aid and services to families with children.",
      "administering_agency": "California Department of Social Services (CDSS)",
      "county_administered": true,
      "application_url": "https://www.benefitscal.com",
      "contact_phone": "1-877-847-3663"
    },
    {
      "program_id": "general_relief",
      "program_name": "General Relief",
      "description": "General Relief provides temporary financial assistance to low-income adults without children.",
      "administering_agency": "County Welfare Offices",
      "county_administered": true,
      "application_url": "https://www.benefitscal.com"
    },
    {
      "program_id": "capi",
      "program_name": "Cash Assistance Program for Immigrants (CAPI)",
      "description": "CAPI provides cash assistance to elderly, blind, or disabled non-citizens ineligible for SSI/SSP.",
      "administering_agency": "California Department of Social Services (CDSS)",
      "county_administered": true,
      "application_url": "https://www.benefitscal.com",
      "contact_phone": "1-877-847-3663"
    }
  ]
}
```

---

### GET /programs/{program_id}

Get detailed information about a specific benefit program.

**Authentication**: None (public endpoint)

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `program_id` | String | Program identifier: `calfresh`, `calworks`, `general_relief`, `capi` |

**Response** (200 OK):
```json
{
  "program_id": "calfresh",
  "program_name": "CalFresh",
  "description": "CalFresh helps low-income people and families buy groceries. CalFresh benefits are issued monthly on an Electronic Benefit Transfer (EBT) card.",
  "administering_agency": "California Department of Social Services (CDSS)",
  "county_administered": true,
  "income_limits": {
    "household_size_1": {
      "gross_monthly": 1580.00,
      "net_monthly": 1215.00
    },
    "household_size_2": {
      "gross_monthly": 2137.00,
      "net_monthly": 1644.00
    },
    "household_size_3": {
      "gross_monthly": 2495.00,
      "net_monthly": 1920.00
    }
  },
  "eligibility_requirements": [
    "California residency",
    "Income below limits",
    "Asset limits (not applicable to most households)",
    "Work requirements for able-bodied adults without dependents (ABAWD)"
  ],
  "application_url": "https://www.benefitscal.com",
  "contact_phone": "1-877-847-3663"
}
```

---

## County-Specific Endpoints

### GET /counties

List all California counties with contact information.

**Authentication**: None (public endpoint)

**Response** (200 OK):
```json
{
  "counties": [
    {
      "county_name": "Los Angeles",
      "dpss_phone": "1-866-613-3777",
      "dpss_website": "https://dpss.lacounty.gov",
      "languages_supported": ["en", "es", "zh", "vi", "ko", "hy", "fa", "ar"]
    },
    {
      "county_name": "San Diego",
      "dpss_phone": "1-866-262-9881",
      "dpss_website": "https://www.sandiegocounty.gov/hhsa/",
      "languages_supported": ["en", "es"]
    }
  ]
}
```

---

## Status Codes Summary

| Status Code | Meaning | Used For |
|-------------|---------|----------|
| **200 OK** | Success | GET requests returning data |
| **201 Created** | Resource created | POST /sessions, POST /escalations, POST /voice/session |
| **400 Bad Request** | Invalid request | Validation errors, missing required fields |
| **403 Forbidden** | Access denied | Attempting to access escalation ticket without permission |
| **404 Not Found** | Resource not found | Session or ticket does not exist |
| **429 Too Many Requests** | Rate limit exceeded | More than 20 queries/minute per session |
| **503 Service Unavailable** | Service degraded | Azure OpenAI outage, database connection failure |

---

## Authentication

**Public Endpoints** (no authentication required):
- GET /health
- POST /chat
- POST /sessions
- GET /sessions/{session_id} (resident can access own session)
- POST /prescreening
- POST /voice/session
- POST /escalations (resident-initiated)
- GET /programs
- GET /programs/{program_id}
- GET /counties

**Authenticated Endpoints** (Azure Entra ID required):
- GET /escalations/{ticket_id} (county staff only)
- County staff dashboard (future)

**Authentication Method**: Azure Entra ID (OAuth 2.0)
- Header: `Authorization: Bearer <token>`
- Token obtained via Azure Entra ID authentication flow

---

## Rate Limiting

- **Public endpoints**: 20 requests/minute per session_id
- **Authenticated endpoints**: 100 requests/minute per user
- Rate limit headers included in all responses:
  - `X-RateLimit-Limit: 20`
  - `X-RateLimit-Remaining: 15`
  - `X-RateLimit-Reset: 1643817600`

---

## CORS Configuration

- **Development**: `http://localhost:3000` (frontend dev server)
- **Production**: `https://benefitscal.ca.gov`, `https://www.benefitscal.com`
- **Methods**: GET, POST, OPTIONS
- **Headers**: Content-Type, Authorization

---

**Last Updated**: 2026-02-02  
**Next Review**: After pilot deployment (Q2 2026)
