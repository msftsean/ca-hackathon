# API Contract: EDD Claims Assistant (007)

**Service**: EDD Claims Assistant API  
**Base URL**: `http://localhost:8007` (development), `https://edd-assistant.ca.gov` (production)  
**Version**: 1.0.0  
**Date**: 2026-04-02

---

## Endpoints

### Health Check

**`GET /health`**

Health check endpoint for load balancers and monitoring.

**Authentication**: None

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "edd-claims-assistant",
  "version": "1.0.0",
  "timestamp": "2026-04-02T10:30:00Z"
}
```

---

### Chat Interaction

**`POST /edd/chat`**

Submit a text message to the EDD Claims Assistant. Handles policy Q&A, eligibility screening, and general questions.

**Authentication**: None (public endpoint, rate-limited by IP)

**Request Body**:
```json
{
  "session_id": "session_abc123",
  "message": "How do I file for unemployment insurance?",
  "claim_type": "ui",
  "context": {
    "modality": "text"
  }
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | Yes | Unique session identifier (UUID) |
| `message` | string | Yes | User's message (1-2000 characters) |
| `claim_type` | string | No | Claim type filter: "ui", "di", or "pfl" |
| `context` | object | No | Additional context (modality, previous claim ID, etc.) |

**Response** (200 OK):
```json
{
  "session_id": "session_abc123",
  "response": "To file for Unemployment Insurance (UI) in California, you must:\n\n1. Have earned wages during your base period\n2. Be unemployed or working reduced hours through no fault of your own\n3. Be able and available to work\n4. Actively seek work each week\n\nYou can file online at edd.ca.gov/UI_Online or call 1-800-300-5616.",
  "citations": [
    {
      "title": "How to File for Unemployment Insurance Benefits",
      "url": "https://edd.ca.gov/en/Unemployment/Filing_a_Claim/",
      "effective_date": "2023-01-01"
    }
  ],
  "escalated": false,
  "timestamp": "2026-04-02T10:31:00Z"
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Session identifier (echoed from request) |
| `response` | string | Assistant's answer (markdown supported) |
| `citations` | array | List of policy sources (title, URL, effective date) |
| `escalated` | boolean | True if escalated to human agent |
| `escalation_ticket_id` | string | (Optional) Ticket ID if escalated |
| `timestamp` | string | ISO 8601 timestamp |

**Status Codes**:
- `200 OK`: Successful response
- `400 Bad Request`: Invalid request (missing fields, validation errors)
- `429 Too Many Requests`: Rate limit exceeded (30/minute)
- `500 Internal Server Error`: Server error

---

### Claim Status Lookup

**`POST /edd/claim-status`**

Look up claim status by claim ID. Requires identity verification (last 4 SSN + DOB).

**Authentication**: Identity verification required (last 4 SSN + DOB)

**Request Body**:
```json
{
  "session_id": "session_abc123",
  "claim_id": "UI-2024-123456",
  "verification": {
    "last4_ssn": "1234",
    "date_of_birth": "1990-05-15"
  }
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | Yes | Session identifier |
| `claim_id` | string | Yes | EDD claim ID (format: UI/DI/PFL-YYYY-NNNNNN) |
| `verification` | object | Yes | Identity verification data |
| `verification.last4_ssn` | string | Yes | Last 4 digits of SSN |
| `verification.date_of_birth` | string | Yes | Date of birth (ISO date: YYYY-MM-DD) |

**Response** (200 OK):
```json
{
  "claim_id": "UI-2024-123456",
  "type": "ui",
  "status": "approved",
  "filed_date": "2024-01-15",
  "weekly_benefit_amount": 450.00,
  "next_payment_date": "2024-04-10",
  "last_certification_date": "2024-04-01",
  "pending_issues": [],
  "required_actions": [
    "Complete bi-weekly certification by April 14"
  ],
  "total_paid": 5400.00,
  "claim_balance": 6300.00
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| `claim_id` | string | Claim identifier |
| `type` | string | Claim type ("ui", "di", "pfl") |
| `status` | string | Current status ("pending", "approved", "denied", "under_review") |
| `filed_date` | string | Date claim was filed (ISO date) |
| `weekly_benefit_amount` | number | Weekly benefit amount (USD) |
| `next_payment_date` | string | Next expected payment date (ISO date) |
| `last_certification_date` | string | Most recent certification submission (ISO date) |
| `pending_issues` | array | List of blocking issues (e.g., "ID Verification") |
| `required_actions` | array | Actions claimant must take |
| `total_paid` | number | Total amount paid to date (USD) |
| `claim_balance` | number | Remaining benefit balance (USD) |

**Status Codes**:
- `200 OK`: Claim found and verified
- `401 Unauthorized`: Identity verification failed
- `404 Not Found`: Claim ID not found
- `429 Too Many Requests`: Rate limit exceeded (5 failed attempts → 30-minute lockout)
- `500 Internal Server Error`: Server error

---

### Eligibility Pre-Screening

**`POST /edd/eligibility`**

Perform eligibility pre-screening by answering questions. Returns preliminary assessment.

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "session_id": "session_abc123",
  "claim_type": "ui",
  "answers": {
    "worked_in_ca_last_18_months": true,
    "separation_reason": "laid_off",
    "employment_type": "w2_employee",
    "weekly_work_hours": 0
  }
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | Yes | Session identifier |
| `claim_type` | string | Yes | Claim type ("ui", "di", "pfl") |
| `answers` | object | Yes | Key-value pairs of screening questions and answers |

**Response** (200 OK):
```json
{
  "assessment_id": "assess_xyz789",
  "claim_type": "ui",
  "result": "likely_eligible",
  "confidence_score": 0.85,
  "factors": [
    {
      "factor": "work_history",
      "meets_requirement": true,
      "explanation": "You worked in California within the last 18 months, meeting the base period requirement."
    },
    {
      "factor": "separation_reason",
      "meets_requirement": true,
      "explanation": "Being laid off qualifies as 'through no fault of your own' for UI eligibility."
    },
    {
      "factor": "employment_type",
      "meets_requirement": true,
      "explanation": "W-2 employees are covered by California UI."
    }
  ],
  "recommended_action": "Proceed with filing your UI claim online at edd.ca.gov/UI_Online",
  "disclaimer": "This is a preliminary assessment. Final eligibility is determined by EDD after you file."
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| `assessment_id` | string | Unique assessment identifier |
| `claim_type` | string | Claim type assessed |
| `result` | string | Result: "likely_eligible", "possibly_eligible", "likely_ineligible", "needs_review" |
| `confidence_score` | number | Confidence (0.0-1.0) |
| `factors` | array | List of factors with explanations |
| `recommended_action` | string | Next step for claimant |
| `disclaimer` | string | Legal disclaimer |

**Status Codes**:
- `200 OK`: Assessment complete
- `400 Bad Request`: Invalid answers (missing required fields)
- `500 Internal Server Error`: Server error

---

### Document Checklist Generation

**`POST /edd/document-checklist`**

Generate personalized document checklist based on claim type and employment situation.

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "session_id": "session_abc123",
  "claim_type": "ui",
  "employment_type": "w2_employee",
  "special_circumstances": ["multiple_employers"]
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | Yes | Session identifier |
| `claim_type` | string | Yes | Claim type ("ui", "di", "pfl") |
| `employment_type` | string | Yes | Employment classification ("w2_employee", "contractor_1099", "military", "federal_employee", "self_employed") |
| `special_circumstances` | array | No | Special flags (e.g., "multiple_employers", "union_member") |

**Response** (200 OK):
```json
{
  "checklist_id": "checklist_abc456",
  "claim_type": "ui",
  "employment_type": "w2_employee",
  "documents": [
    {
      "name": "Social Security Number",
      "description": "Required for claim filing and identity verification.",
      "required": true
    },
    {
      "name": "Most recent pay stub",
      "description": "Verifies your earnings during the base period. Provide stubs from all employers in the last 18 months.",
      "required": true
    },
    {
      "name": "Employer contact information",
      "description": "Company name, address, phone number for all employers in the last 18 months. Include supervisor name if available.",
      "required": true
    },
    {
      "name": "DD-214 (if applicable)",
      "description": "Military discharge papers if you served in the last 18 months. Request from National Archives if you don't have a copy.",
      "required": false
    }
  ],
  "generated_at": "2026-04-02T10:35:00Z"
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| `checklist_id` | string | Unique checklist identifier |
| `claim_type` | string | Claim type |
| `employment_type` | string | Employment classification |
| `documents` | array | List of documents |
| `documents[].name` | string | Document name |
| `documents[].description` | string | Why it's needed and where to get it |
| `documents[].required` | boolean | True if absolutely required |
| `generated_at` | string | ISO 8601 timestamp |

**Status Codes**:
- `200 OK`: Checklist generated
- `400 Bad Request`: Invalid claim type or employment type
- `500 Internal Server Error`: Server error

---

### Voice Session Initiation

**`POST /edd/voice/session`**

Initiate a voice session using Azure OpenAI Realtime API. Returns WebRTC connection details.

**Authentication**: None (public endpoint, rate-limited)

**Request Body**:
```json
{
  "session_id": "session_abc123"
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | Yes | Session identifier (same as text chat for context continuity) |

**Response** (200 OK):
```json
{
  "voice_session_id": "voice_xyz789",
  "rtc_session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "rtc_server_url": "wss://eastus.api.cognitive.microsoft.com/openai/realtime",
  "model": "gpt-4o-realtime-preview",
  "expires_at": "2026-04-02T11:35:00Z"
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| `voice_session_id` | string | Unique voice session identifier |
| `rtc_session_token` | string | JWT token for WebRTC authentication |
| `rtc_server_url` | string | WebSocket URL for Realtime API connection |
| `model` | string | Model used for voice processing |
| `expires_at` | string | Token expiration time (ISO 8601) |

**Status Codes**:
- `200 OK`: Session created
- `429 Too Many Requests`: Rate limit exceeded (10 sessions/hour)
- `503 Service Unavailable`: Realtime API unavailable (fallback to text)
- `500 Internal Server Error`: Server error

---

### Voice Tool Call Execution

**`POST /edd/voice/tool-call`**

Execute a tool during a voice session (claim lookup, policy Q&A, etc.). Called by Realtime API during voice conversation.

**Authentication**: Voice session token (in request body)

**Request Body**:
```json
{
  "voice_session_id": "voice_xyz789",
  "tool_name": "claim_status_lookup",
  "arguments": {
    "claim_id": "UI-2024-123456",
    "last4_ssn": "1234",
    "date_of_birth": "1990-05-15"
  }
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `voice_session_id` | string | Yes | Voice session identifier |
| `tool_name` | string | Yes | Tool to execute ("claim_status_lookup", "policy_search", "eligibility_assessment") |
| `arguments` | object | Yes | Tool-specific arguments |

**Response** (200 OK):
```json
{
  "tool_call_id": "toolcall_123",
  "result": {
    "claim_id": "UI-2024-123456",
    "status": "approved",
    "next_payment_date": "2024-04-10",
    "pending_issues": []
  }
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| `tool_call_id` | string | Unique tool call identifier |
| `result` | object | Tool execution result (schema varies by tool) |

**Status Codes**:
- `200 OK`: Tool executed successfully
- `401 Unauthorized`: Invalid voice session ID
- `400 Bad Request`: Invalid tool arguments
- `500 Internal Server Error`: Tool execution failed

---

### Create Escalation Ticket

**`POST /edd/escalate`**

Create an escalation ticket for human agent review. Includes full conversation context.

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "session_id": "session_abc123",
  "claim_id": "UI-2024-123456",
  "category": "appeal",
  "priority": "high",
  "reason": "Claimant wants to appeal denied claim",
  "conversation_transcript": [
    {
      "role": "user",
      "content": "My UI claim was denied. How do I appeal?",
      "timestamp": "2026-04-02T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "I can help you understand the appeal process. Let me connect you with a specialist.",
      "timestamp": "2026-04-02T10:30:05Z"
    }
  ]
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | Yes | Session identifier |
| `claim_id` | string | No | Associated claim ID (if applicable) |
| `category` | string | Yes | Ticket category ("status_inquiry", "eligibility_question", "appeal", "technical_issue", "escalation") |
| `priority` | string | Yes | Priority level ("low", "medium", "high", "urgent") |
| `reason` | string | Yes | Escalation reason (human-readable) |
| `conversation_transcript` | array | Yes | Full conversation history |

**Response** (201 Created):
```json
{
  "ticket_id": "TICKET-2024-789012",
  "status": "open",
  "priority": "high",
  "estimated_response_time": "2 business days",
  "contact_methods": [
    "Phone: 1-800-300-5616",
    "Email: edd.support@edd.ca.gov"
  ],
  "created_at": "2026-04-02T10:35:00Z"
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| `ticket_id` | string | Unique ticket identifier |
| `status` | string | Ticket status ("open", "assigned", "resolved", "closed") |
| `priority` | string | Priority level |
| `estimated_response_time` | string | Estimated time for human response |
| `contact_methods` | array | Alternative contact methods |
| `created_at` | string | ISO 8601 timestamp |

**Status Codes**:
- `201 Created`: Ticket created successfully
- `400 Bad Request`: Invalid request (missing fields)
- `500 Internal Server Error`: Server error

---

## Rate Limits

| Endpoint | Limit | Window | Lockout |
|----------|-------|--------|---------|
| `POST /edd/chat` | 30 requests | 1 minute | None |
| `POST /edd/claim-status` | 5 failed attempts | Per session | 30 minutes |
| `POST /edd/eligibility` | 10 requests | 1 minute | None |
| `POST /edd/voice/session` | 10 sessions | 1 hour | None |
| All endpoints combined | 100 requests | 1 minute | 5 minutes |

**Rate Limit Headers** (included in all responses):
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1646230800
```

---

## Error Responses

**Standard Error Format**:
```json
{
  "error": {
    "code": "CLAIM_NOT_FOUND",
    "message": "Claim ID UI-2024-999999 not found. Please verify the number.",
    "details": {
      "claim_id": "UI-2024-999999"
    }
  },
  "timestamp": "2026-04-02T10:40:00Z"
}
```

**Common Error Codes**:
- `INVALID_REQUEST`: Validation error (missing required fields)
- `CLAIM_NOT_FOUND`: Claim ID not found
- `VERIFICATION_FAILED`: Identity verification failed
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `SESSION_EXPIRED`: Session timeout (30 minutes inactivity)
- `SERVICE_UNAVAILABLE`: Azure OpenAI or Azure AI Search unavailable
- `VOICE_API_UNAVAILABLE`: Realtime API unavailable (fallback to text)

---

## Example Workflows

### Workflow 1: Policy Q&A
1. `POST /edd/chat` with question "How do I file for UI?"
2. Response includes policy answer with citations
3. (Optional) Follow-up questions in same session

### Workflow 2: Claim Status Lookup
1. `POST /edd/claim-status` with claim ID and verification
2. Response includes current status, pending issues, next payment date
3. If verification fails, retry (max 5 attempts)

### Workflow 3: Eligibility Pre-Screening
1. `POST /edd/eligibility` with answers to screening questions
2. Response includes preliminary assessment and recommended action
3. (Optional) Generate document checklist if eligible

### Workflow 4: Voice Interaction
1. `POST /edd/voice/session` to initiate voice session
2. Frontend establishes WebRTC connection to Realtime API
3. Claimant speaks question → Realtime API invokes `POST /edd/voice/tool-call`
4. Tool result returned to Realtime API → spoken response to claimant
5. Session expires after 30 minutes inactivity

### Workflow 5: Escalation
1. Claimant requests human assistance during chat
2. `POST /edd/escalate` with conversation transcript
3. Response includes ticket ID and estimated response time
4. EDD agent reviews ticket and contacts claimant via phone/email
