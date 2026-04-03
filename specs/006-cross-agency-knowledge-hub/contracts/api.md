# API Contracts: Cross-Agency Knowledge Hub

**Feature**: `006-cross-agency-knowledge-hub`  
**Created**: 2024-12-19  
**Base URL**: `http://localhost:8006` (development), `https://knowledge-hub.ca.gov/api` (production)  
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
    "azure_ai_search": "healthy",
    "redis_cache": "healthy",
    "entra_id": "healthy"
  },
  "index_stats": {
    "total_documents": 102547,
    "total_agencies": 214,
    "last_indexed": "2024-12-19T09:00:00Z"
  }
}
```

**Response (503 Service Unavailable)**:
```json
{
  "status": "unhealthy",
  "timestamp": "2024-12-19T10:30:00Z",
  "services": {
    "database": "healthy",
    "azure_ai_search": "degraded",
    "redis_cache": "healthy",
    "entra_id": "healthy"
  },
  "error": "Azure AI Search latency above threshold (5.2s > 3s)"
}
```

---

### Search

#### POST /search

Execute federated search across agency knowledge bases with permission-aware filtering.

**Authentication**: Required

**Request Headers**:
| Header | Value | Required |
|--------|-------|----------|
| Authorization | Bearer {token} | Yes |
| Content-Type | application/json | Yes |

**Request Body**:
```json
{
  "query": "telework policy for HR department",
  "filters": {
    "agencies": ["CDT", "CalHR"],
    "document_types": ["policy", "procedure"],
    "classification": ["public", "internal"],
    "date_range": {
      "start": "2023-01-01",
      "end": "2024-12-31"
    }
  },
  "search_options": {
    "page": 1,
    "page_size": 20,
    "sort_by": "relevance",
    "include_cross_references": true,
    "include_experts": true,
    "highlight_terms": true
  }
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8006/search \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "telework policy",
    "filters": {
      "agencies": ["CDT"],
      "document_types": ["policy"]
    },
    "search_options": {
      "page": 1,
      "page_size": 20,
      "include_cross_references": true
    }
  }'
```

**Response (200 OK)**:
```json
{
  "query_id": "qry-660e8400-e29b-41d4-a716-446655440001",
  "query_text": "telework policy",
  "sanitized_query": "telework policy",
  "total_results": 47,
  "page": 1,
  "page_size": 20,
  "total_pages": 3,
  "response_time_ms": 842,
  "user_agency_scope": ["CDT", "GovOps"],
  "results": [
    {
      "document_id": "doc-550e8400-e29b-41d4-a716-446655440000",
      "title": "Remote Work and Telework Policy - Updated 2024",
      "agency_id": "CDT",
      "agency_name": "California Department of Technology",
      "document_type": "policy",
      "classification": "internal",
      "relevance_score": 0.94,
      "snippet": "...employees may <mark>telework</mark> up to 3 days per week subject to manager approval. All <mark>telework</mark> arrangements must comply with <mark>CDT Policy</mark> 2024-015...",
      "created_at": "2024-06-15T08:00:00Z",
      "last_modified_at": "2024-11-20T14:30:00Z",
      "source_url": "https://cdt.sharepoint.com/policies/telework-2024.pdf",
      "author": "Jane Smith",
      "author_email": "jane.smith@cdt.ca.gov",
      "cross_references": [
        {
          "document_id": "doc-660e8400-e29b-41d4-a716-446655440002",
          "title": "IT Security Requirements for Remote Work",
          "relationship_type": "references",
          "confidence_score": 88,
          "agency_name": "CDT"
        }
      ],
      "keywords": ["telework", "remote work", "hybrid work", "work from home", "flexible work"]
    },
    {
      "document_id": "doc-770e8400-e29b-41d4-a716-446655440003",
      "title": "CalHR Telework Guidelines - Master Agreement",
      "agency_id": "CalHR",
      "agency_name": "California Department of Human Resources",
      "document_type": "guideline",
      "classification": "public",
      "relevance_score": 0.87,
      "snippet": "...state agencies implementing <mark>telework</mark> programs must follow CalHR <mark>guidelines</mark> for equipment, workspace safety, and performance management...",
      "created_at": "2023-02-10T10:00:00Z",
      "last_modified_at": "2024-08-05T11:15:00Z",
      "source_url": "https://calhr.ca.gov/Documents/telework-guidelines.pdf",
      "cross_references": [
        {
          "document_id": "doc-550e8400-e29b-41d4-a716-446655440000",
          "title": "Remote Work and Telework Policy - Updated 2024",
          "relationship_type": "complements",
          "confidence_score": 75,
          "agency_name": "CDT"
        }
      ],
      "keywords": ["telework", "remote work", "CalHR", "state policy"]
    }
  ],
  "facets": {
    "agencies": [
      {"agency_id": "CDT", "agency_name": "CA Dept of Technology", "count": 23},
      {"agency_id": "CalHR", "agency_name": "CA Dept of Human Resources", "count": 12},
      {"agency_id": "GovOps", "agency_name": "Government Operations", "count": 8},
      {"agency_id": "DGS", "agency_name": "Dept of General Services", "count": 4}
    ],
    "document_types": [
      {"type": "policy", "count": 28},
      {"type": "guideline", "count": 11},
      {"type": "procedure", "count": 6},
      {"type": "memo", "count": 2}
    ],
    "classification": [
      {"level": "public", "count": 31},
      {"level": "internal", "count": 16}
    ]
  },
  "suggestions": {
    "did_you_mean": null,
    "related_queries": [
      "remote work policy",
      "work from home policy",
      "hybrid work guidelines",
      "flexible work arrangements"
    ]
  },
  "experts": [
    {
      "expert_id": "exp-880e8400-e29b-41d4-a716-446655440004",
      "name": "Jane Smith",
      "agency": "CDT",
      "expertise_areas": ["telework policy", "remote work", "HR compliance"],
      "document_count": 5,
      "relevance_score": 92,
      "availability": "available",
      "contact_methods": {
        "email": "jane.smith@cdt.ca.gov",
        "teams": "https://teams.microsoft.com/l/chat/0/0?users=jane.smith@cdt.ca.gov"
      }
    }
  ]
}
```

**Response (400 Bad Request)**:
```json
{
  "error": "Invalid query",
  "message": "Query text exceeds maximum length of 500 characters",
  "details": {
    "field": "query",
    "max_length": 500,
    "actual_length": 637
  }
}
```

**Status Codes**:
- `200 OK`: Search executed successfully
- `400 Bad Request`: Invalid query parameters or filters
- `401 Unauthorized`: Missing or invalid authentication token
- `422 Unprocessable Entity`: Query contains PII or prohibited content

---

#### GET /search/suggestions

Get auto-complete suggestions for search query.

**Authentication**: Required

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | Yes | Partial query text (min 2 chars) |
| limit | integer | No | Max suggestions (default: 10, max: 20) |

**Example Request**:
```bash
curl "http://localhost:8006/search/suggestions?q=tele&limit=5" \
  -H "Authorization: Bearer {token}"
```

**Response (200 OK)**:
```json
{
  "query": "tele",
  "suggestions": [
    {"text": "telework policy", "frequency": 487, "last_searched": "2024-12-19T09:15:00Z"},
    {"text": "telehealth services", "frequency": 203, "last_searched": "2024-12-18T16:30:00Z"},
    {"text": "telecommunications contract", "frequency": 145, "last_searched": "2024-12-17T11:00:00Z"},
    {"text": "telework agreement template", "frequency": 89, "last_searched": "2024-12-19T08:45:00Z"},
    {"text": "telephone system procurement", "frequency": 56, "last_searched": "2024-12-16T14:20:00Z"}
  ]
}
```

**Status Codes**:
- `200 OK`: Suggestions retrieved successfully
- `400 Bad Request`: Query too short (<2 characters)
- `401 Unauthorized`: Missing or invalid authentication token

---

### Document Access

#### GET /documents/{document_id}

Retrieve full document content with permission check.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| document_id | UUID | Document identifier from search results |

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| include_metadata | boolean | true | Include document metadata |
| include_access_log | boolean | false | Include recent access history (auditor role only) |

**Example Request**:
```bash
curl "http://localhost:8006/documents/doc-550e8400-e29b-41d4-a716-446655440000?include_metadata=true" \
  -H "Authorization: Bearer {token}"
```

**Response (200 OK)**:
```json
{
  "document_id": "doc-550e8400-e29b-41d4-a716-446655440000",
  "title": "Remote Work and Telework Policy - Updated 2024",
  "agency_id": "CDT",
  "agency_name": "California Department of Technology",
  "document_type": "policy",
  "classification": "internal",
  "content": "# Remote Work and Telework Policy\n\n## Purpose\nThis policy establishes guidelines...",
  "content_format": "markdown",
  "metadata": {
    "created_at": "2024-06-15T08:00:00Z",
    "last_modified_at": "2024-11-20T14:30:00Z",
    "author": "Jane Smith",
    "author_email": "jane.smith@cdt.ca.gov",
    "owner": "HR Division",
    "version": "2.1",
    "supersedes_document_id": "doc-440e8400-e29b-41d4-a716-446655440001",
    "review_date": "2025-06-15",
    "keywords": ["telework", "remote work", "hybrid work"],
    "file_format": "PDF",
    "word_count": 3542,
    "read_time_minutes": 15
  },
  "download_url": "https://cdt.sharepoint.com/policies/telework-2024.pdf",
  "access_granted": true,
  "access_justification": "User is member of CDT-Employees group"
}
```

**Response (403 Forbidden)**:
```json
{
  "error": "Access denied",
  "message": "User does not have permission to access this document",
  "details": {
    "document_id": "doc-550e8400-e29b-41d4-a716-446655440000",
    "required_permission": "CDT-Employees group membership or Auditor role",
    "user_agencies": ["GovOps", "DGS"],
    "document_classification": "internal"
  }
}
```

**Status Codes**:
- `200 OK`: Document retrieved successfully
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User lacks permission to access document
- `404 Not Found`: Document not found or deleted

---

### Cross-References

#### GET /documents/{document_id}/cross-references

Retrieve related documents with relationship analysis.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| document_id | UUID | Source document identifier |

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| relationship_types | string[] | all | Filter by type: `supersedes`, `references`, `complements`, `conflicts` |
| min_confidence | integer | 70 | Minimum confidence score (0-100) |
| limit | integer | 10 | Max cross-references returned |

**Example Request**:
```bash
curl "http://localhost:8006/documents/doc-550e8400-e29b-41d4-a716-446655440000/cross-references?min_confidence=75&limit=5" \
  -H "Authorization: Bearer {token}"
```

**Response (200 OK)**:
```json
{
  "document_id": "doc-550e8400-e29b-41d4-a716-446655440000",
  "document_title": "Remote Work and Telework Policy - Updated 2024",
  "total_cross_references": 8,
  "filtered_count": 5,
  "cross_references": [
    {
      "cross_reference_id": "xref-990e8400-e29b-41d4-a716-446655440005",
      "target_document_id": "doc-660e8400-e29b-41d4-a716-446655440002",
      "target_title": "IT Security Requirements for Remote Work",
      "target_agency": "CDT",
      "relationship_type": "references",
      "confidence_score": 92,
      "detection_method": "citation_parsing",
      "evidence": "Policy explicitly references 'IT Security Requirements (CDT-SEC-2024-008)' in Section 4.2",
      "created_at": "2024-11-21T10:00:00Z",
      "validated_by": null,
      "user_can_access": true
    },
    {
      "cross_reference_id": "xref-aa0e8400-e29b-41d4-a716-446655440006",
      "target_document_id": "doc-770e8400-e29b-41d4-a716-446655440003",
      "target_title": "CalHR Telework Guidelines - Master Agreement",
      "target_agency": "CalHR",
      "relationship_type": "complements",
      "confidence_score": 78,
      "detection_method": "embedding_similarity",
      "evidence": "Both documents address telework eligibility, manager approval, and performance expectations with similar language",
      "created_at": "2024-11-21T10:00:00Z",
      "validated_by": "jane.smith@cdt.ca.gov",
      "user_can_access": true
    },
    {
      "cross_reference_id": "xref-bb0e8400-e29b-41d4-a716-446655440007",
      "target_document_id": "doc-440e8400-e29b-41d4-a716-446655440001",
      "target_title": "Remote Work and Telework Policy - Version 1.0",
      "target_agency": "CDT",
      "relationship_type": "supersedes",
      "confidence_score": 100,
      "detection_method": "metadata_matching",
      "evidence": "Document metadata shows version 2.1 supersedes version 1.0 (document ID in supersedes_document_id field)",
      "created_at": "2024-06-15T08:00:00Z",
      "validated_by": "system",
      "user_can_access": true
    }
  ],
  "relationship_type_counts": {
    "supersedes": 1,
    "references": 3,
    "complements": 4,
    "conflicts": 0
  }
}
```

**Status Codes**:
- `200 OK`: Cross-references retrieved successfully
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Source document not found

---

### Expert Search

#### GET /experts

Search for subject matter experts by expertise area or name.

**Authentication**: Required

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | No | Search query (expertise area or name) |
| agency | string | No | Filter by agency ID |
| availability | string | No | Filter by availability: `available`, `busy`, `unavailable` |
| sort_by | string | No | Sort order: `relevance`, `document_count`, `name` (default: `relevance`) |
| page | integer | No | Page number (default: 1) |
| page_size | integer | No | Results per page (default: 20, max: 100) |

**Example Request**:
```bash
curl "http://localhost:8006/experts?q=telework&agency=CDT&availability=available" \
  -H "Authorization: Bearer {token}"
```

**Response (200 OK)**:
```json
{
  "total_experts": 12,
  "page": 1,
  "page_size": 20,
  "experts": [
    {
      "expert_id": "exp-880e8400-e29b-41d4-a716-446655440004",
      "name": "Jane Smith",
      "title": "HR Policy Manager",
      "agency": "CDT",
      "agency_name": "California Department of Technology",
      "expertise_areas": ["telework policy", "remote work", "HR compliance", "flexible work arrangements"],
      "bio": "15 years experience developing and implementing telework policies for state agencies. Led CDT's transition to hybrid work model in 2020.",
      "document_count": 8,
      "recent_documents": [
        {
          "document_id": "doc-550e8400-e29b-41d4-a716-446655440000",
          "title": "Remote Work and Telework Policy - Updated 2024",
          "created_at": "2024-06-15T08:00:00Z"
        }
      ],
      "relevance_score": 94,
      "availability": "available",
      "contact_methods": {
        "email": "jane.smith@cdt.ca.gov",
        "teams": "https://teams.microsoft.com/l/chat/0/0?users=jane.smith@cdt.ca.gov",
        "phone": null,
        "office": "915 Capitol Mall, Sacramento CA"
      },
      "last_active": "2024-12-19T09:30:00Z"
    }
  ]
}
```

**Status Codes**:
- `200 OK`: Experts retrieved successfully
- `400 Bad Request`: Invalid query parameters
- `401 Unauthorized`: Missing or invalid authentication token

---

#### POST /experts/{expert_id}/contact

Initiate contact with subject matter expert.

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| expert_id | UUID | Expert identifier |

**Request Body**:
```json
{
  "contact_method": "email",
  "subject": "Question about CDT telework policy",
  "context": {
    "search_query": "telework policy",
    "document_id": "doc-550e8400-e29b-41d4-a716-446655440000",
    "document_title": "Remote Work and Telework Policy - Updated 2024"
  }
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8006/experts/exp-880e8400-e29b-41d4-a716-446655440004/contact \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d @contact-request.json
```

**Response (200 OK)**:
```json
{
  "contact_id": "contact-cc0e8400-e29b-41d4-a716-446655440008",
  "expert_id": "exp-880e8400-e29b-41d4-a716-446655440004",
  "expert_name": "Jane Smith",
  "expert_email": "jane.smith@cdt.ca.gov",
  "contact_method": "email",
  "subject": "Question about CDT telework policy",
  "pre_filled_message": "Hi Jane,\n\nI found your document \"Remote Work and Telework Policy - Updated 2024\" while searching for \"telework policy\" and have a question.\n\n[Your question here]\n\nThank you,\n[Your Name]",
  "email_link": "mailto:jane.smith@cdt.ca.gov?subject=Question%20about%20CDT%20telework%20policy&body=...",
  "teams_link": "https://teams.microsoft.com/l/chat/0/0?users=jane.smith@cdt.ca.gov&message=...",
  "initiated_at": "2024-12-19T10:45:00Z",
  "audit_logged": true
}
```

**Response (429 Too Many Requests)**:
```json
{
  "error": "Rate limit exceeded",
  "message": "You have reached the maximum of 5 expert contacts per day",
  "details": {
    "limit": 5,
    "remaining": 0,
    "reset_at": "2024-12-20T00:00:00Z"
  }
}
```

**Status Codes**:
- `200 OK`: Contact initiated successfully (audit logged, no actual message sent)
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Expert not found
- `429 Too Many Requests`: User exceeded daily contact limit (5 per day)

---

### Audit Logging

#### GET /audit/logs

Query audit trail for search activity and document access.

**Authentication**: Required (auditor role or compliance officer role)

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| start_date | ISO 8601 date | 7 days ago | Start of date range |
| end_date | ISO 8601 date | now | End of date range |
| user_id | string | null | Filter by user email |
| event_type | string | null | Filter by event: `search`, `document_access`, `expert_contact` |
| agency | string | null | Filter by agency |
| page | integer | 1 | Page number |
| page_size | integer | 50 | Results per page (max 500) |

**Example Request**:
```bash
curl "http://localhost:8006/audit/logs?start_date=2024-12-01&event_type=document_access&agency=CDT" \
  -H "Authorization: Bearer {token}"
```

**Response (200 OK)**:
```json
{
  "total_records": 3489,
  "page": 1,
  "page_size": 50,
  "total_pages": 70,
  "logs": [
    {
      "log_id": "log-dd0e8400-e29b-41d4-a716-446655440009",
      "timestamp": "2024-12-19T10:30:00Z",
      "event_type": "document_access",
      "user_id": "john.doe@cdt.ca.gov",
      "user_agency": "CDT",
      "user_role": "employee",
      "document_id": "doc-550e8400-e29b-41d4-a716-446655440000",
      "document_title": "Remote Work and Telework Policy - Updated 2024",
      "document_agency": "CDT",
      "document_classification": "internal",
      "access_method": "search_result",
      "access_granted": true,
      "ip_address": "10.0.1.45",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
    },
    {
      "log_id": "log-ee0e8400-e29b-41d4-a716-446655440010",
      "timestamp": "2024-12-19T10:29:15Z",
      "event_type": "search",
      "user_id": "john.doe@cdt.ca.gov",
      "user_agency": "CDT",
      "sanitized_query": "telework policy",
      "result_count": 47,
      "response_time_ms": 842,
      "filters_applied": {
        "agencies": ["CDT"],
        "document_types": ["policy"]
      },
      "ip_address": "10.0.1.45"
    }
  ]
}
```

**Status Codes**:
- `200 OK`: Audit logs retrieved successfully
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User lacks auditor or compliance officer role

---

#### GET /audit/analytics

Get search analytics and usage metrics.

**Authentication**: Required (auditor role or admin role)

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| start_date | ISO 8601 date | 30 days ago | Start of date range |
| end_date | ISO 8601 date | now | End of date range |
| agency | string | null | Filter by agency |

**Example Request**:
```bash
curl "http://localhost:8006/audit/analytics?start_date=2024-11-01&end_date=2024-12-01" \
  -H "Authorization: Bearer {token}"
```

**Response (200 OK)**:
```json
{
  "period": {
    "start_date": "2024-11-01",
    "end_date": "2024-12-01",
    "days": 31
  },
  "search_metrics": {
    "total_searches": 45782,
    "unique_users": 3421,
    "avg_searches_per_user": 13.4,
    "zero_result_queries": 6847,
    "zero_result_rate": 0.15
  },
  "top_queries": [
    {"query": "telework policy", "count": 487},
    {"query": "procurement guidelines", "count": 392},
    {"query": "IT security requirements", "count": 311}
  ],
  "top_agencies": [
    {"agency": "CDT", "searches": 12458, "documents_accessed": 5632},
    {"agency": "CalHR", "searches": 8934, "documents_accessed": 4201},
    {"agency": "GovOps", "searches": 6723, "documents_accessed": 3012}
  ],
  "document_access_metrics": {
    "total_accesses": 28473,
    "unique_documents": 4892,
    "avg_accesses_per_document": 5.8
  },
  "expert_contact_metrics": {
    "total_contacts": 1247,
    "unique_experts": 89,
    "avg_contacts_per_expert": 14.0
  }
}
```

**Status Codes**:
- `200 OK`: Analytics retrieved successfully
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User lacks auditor or admin role

---

## Error Response Format

All error responses follow consistent JSON structure:

```json
{
  "error": "Error category",
  "message": "Human-readable error description",
  "details": {
    "field": "Specific field that caused error",
    "constraint": "Validation constraint violated"
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
- Audience: `api://knowledge-hub-api`
- Scopes: `Search.Read`, `Document.Read`, `Expert.Contact`, `Audit.Read`
- Roles: `employee`, `manager`, `auditor`, or `admin`

**Token Expiration**: 1 hour (refresh required)

**Permission Mapping**:
- **employee**: Basic search, document access (based on agency membership)
- **manager**: Same as employee + access to team's audit logs
- **auditor**: Full audit log access, analytics access, all documents (any classification)
- **admin**: All permissions + index management APIs

## Rate Limiting

| Endpoint Category | Rate Limit | Window |
|------------------|------------|--------|
| Search | 100 requests/minute | Per user |
| Document access | 200 requests/minute | Per user |
| Expert contact | 5 requests/day | Per user |
| Audit logs | 50 requests/minute | Per user |
| Analytics | 10 requests/minute | Per user |

**Rate Limit Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1703001600
```

## API Versioning

Current version: **v1** (included in base path)

Breaking changes will increment major version (v2, v3, etc.)

## Server-Sent Events (SSE) for Progressive Results

For large search queries, use SSE endpoint for progressive result streaming:

**Endpoint**: `GET /search/stream`

**Response** (text/event-stream):
```
data: {"type":"metadata","total_results":47,"query_id":"qry-..."}

data: {"type":"result","document":{"document_id":"doc-...","title":"...","relevance_score":0.94}}

data: {"type":"result","document":{"document_id":"doc-...","title":"...","relevance_score":0.89}}

data: {"type":"complete","results_sent":20,"has_more":true}
```

Use EventSource API in frontend to receive results in real-time.
