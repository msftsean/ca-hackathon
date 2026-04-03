# Data Model: BenefitsCal Navigator Agent

**Feature**: BenefitsCal Navigator Agent  
**Version**: 1.0  
**Date**: 2026-02-02

## Overview

This document defines the core entities and relationships for the BenefitsCal Navigator Agent. The data model supports natural language Q&A, eligibility pre-screening, multi-language interaction, voice sessions, and human escalation workflows while maintaining CCPA/CPRA compliance and Constitutional audit requirements.

---

## Core Entities

### 1. ConversationSession

Represents a single interaction between a resident and the BenefitsCal Navigator.

**Attributes**:
- `session_id` (UUID, primary key): Unique identifier for the conversation session
- `started_at` (datetime): Timestamp when the session was initiated
- `ended_at` (datetime, nullable): Timestamp when the session concluded
- `channel` (enum: "web", "voice"): Interaction channel
- `language` (string): ISO 639-1 language code (en, es, zh, vi, tl, ko, hy, fa, ar)
- `county` (string, nullable): California county if specified by resident
- `escalated` (boolean): Whether this session resulted in an escalation to county staff
- `escalation_ticket_id` (UUID, nullable, foreign key): Reference to EscalationTicket if escalated
- `user_agent` (string, nullable): Browser user agent for accessibility tracking
- `ip_address_hash` (string, nullable): Hashed IP address for abuse prevention (not stored in plaintext per CCPA)

**Relationships**:
- One-to-many with `Query` (a session contains multiple queries)
- One-to-one with `EscalationTicket` (if escalated)
- One-to-one with `EligibilityProfile` (if pre-screening performed)

**Indexes**:
- Primary key on `session_id`
- Index on `started_at` for temporal queries
- Index on `county` for county-level reporting
- Index on `escalated` for escalation tracking

---

### 2. Query

Represents a single resident question or request within a conversation session.

**Attributes**:
- `query_id` (UUID, primary key): Unique identifier for the query
- `session_id` (UUID, foreign key): Reference to parent ConversationSession
- `timestamp` (datetime): When the query was submitted
- `query_text` (text): The resident's question (PII-masked in storage)
- `query_text_original_language` (string): ISO 639-1 language code of original query
- `intent` (enum): Classified intent - "eligibility_question", "program_info", "prescreening", "application_status", "escalation_request", "crisis", "unknown"
- `confidence_score` (float, 0.0-1.0): Agent's confidence in intent classification
- `entities_extracted` (JSON): Extracted entities (program names, counties, income amounts, household size)
- `response_text` (text): The agent's response
- `response_language` (string): ISO 639-1 language code of response
- `citations` (JSON array): References to PolicyDocument chunks used in response
- `processing_time_ms` (integer): Time taken to generate response in milliseconds
- `routed_to` (string, nullable): Agency or county office if routed
- `escalated` (boolean): Whether this specific query triggered escalation

**Relationships**:
- Many-to-one with `ConversationSession`
- Many-to-many with `PolicyDocument` (via citations)

**Indexes**:
- Primary key on `query_id`
- Foreign key index on `session_id`
- Index on `intent` for analytics
- Index on `confidence_score` for low-confidence tracking
- Index on `escalated` for escalation analysis

**Constitutional Compliance**:
- `query_text` MUST be PII-masked before storage (no SSN, driver's license, financial accounts)
- All queries logged for Auditability & Transparency (Principle V)
- Crisis intent triggers immediate escalation per Graceful Escalation (Principle IV)

---

### 3. EligibilityProfile

Represents household information for preliminary eligibility determination.

**Attributes**:
- `profile_id` (UUID, primary key): Unique identifier for the eligibility profile
- `session_id` (UUID, foreign key): Reference to parent ConversationSession
- `created_at` (datetime): When the profile was created
- `household_size` (integer): Number of people in the household (1-20)
- `monthly_income_total` (decimal): Total household monthly income in USD
- `county` (string): California county (one of 58 counties)
- `has_senior_65plus` (boolean): Household includes someone age 65+
- `has_disability` (boolean): Household includes someone with a disability
- `has_child_under_18` (boolean): Household includes a child under 18
- `citizenship_status` (enum): "citizen", "qualified_immigrant", "mixed_status", "prefer_not_to_say"
- `currently_working` (boolean, nullable): Any household member currently employed
- `receiving_other_benefits` (JSON array, nullable): List of other benefits currently received (SSI, SSDI, unemployment)
- `preliminary_eligibility_results` (JSON): Structured results for CalFresh, CalWORKs, General Relief, CAPI

**Relationships**:
- Many-to-one with `ConversationSession`
- Many-to-many with `BenefitProgram` (via eligibility results)

**Indexes**:
- Primary key on `profile_id`
- Foreign key index on `session_id`
- Index on `county` for county-level analytics

**Constitutional Compliance**:
- PII-masked data (no names, SSN, addresses) per Data Privacy & Security (Principle I)
- No assumptions based on citizenship status per Equity & Bias Mitigation (Principle III)
- Temporary data (deleted after session ends unless resident opts to save) per CCPA/CPRA

---

### 4. BenefitProgram

Represents a CDSS-administered benefit program with eligibility criteria.

**Attributes**:
- `program_id` (string, primary key): Program identifier ("calfresh", "calworks", "general_relief", "capi")
- `program_name` (string): Display name ("CalFresh", "CalWORKs", "General Relief", "Cash Assistance Program for Immigrants")
- `description` (text): Program overview in plain language (8th-grade reading level)
- `administering_agency` (string): "California Department of Social Services (CDSS)"
- `county_administered` (boolean): Whether counties administer the program locally
- `income_limits` (JSON): Structured income limits by household size and county (if county-specific)
- `eligibility_requirements` (JSON): Structured eligibility criteria (age, citizenship, work requirements, etc.)
- `policy_document_ids` (JSON array): References to PolicyDocument chunks with detailed rules
- `application_url` (string): URL to BenefitsCal application page
- `contact_phone` (string): Statewide contact phone number
- `multilingual_support` (JSON): Contact numbers for each supported language

**Relationships**:
- Many-to-many with `EligibilityProfile` (via preliminary eligibility results)
- Many-to-many with `PolicyDocument` (via policy references)

**Indexes**:
- Primary key on `program_id`

**Constitutional Compliance**:
- All descriptions at 8th-grade reading level per Accessibility (Principle II)
- Multilingual support contact info per Language Access requirements

---

### 5. PolicyDocument

Represents a CDSS policy manual, regulation, or guidance document in the knowledge base.

**Attributes**:
- `document_id` (UUID, primary key): Unique identifier for the document
- `document_type` (enum): "manual", "regulation", "guidance", "FAQ", "legislation"
- `title` (string): Document title
- `program` (string): Related program ("calfresh", "calworks", "general_relief", "capi", "general")
- `section` (string, nullable): Section or chapter within document
- `content` (text): Full text content of the document or chunk
- `content_vector` (vector, nullable): Embedding vector for semantic search (Azure AI Search)
- `effective_date` (date): When this policy became effective
- `updated_date` (date): Last update date
- `source_url` (string): URL to official CDSS source document
- `citation_format` (string): How to cite this document (e.g., "CDSS CalFresh Manual Section 63-300.1")
- `language` (string): ISO 639-1 language code (policy documents primarily in English)

**Relationships**:
- Many-to-many with `Query` (via citations in responses)
- Many-to-many with `BenefitProgram` (via policy references)

**Indexes**:
- Primary key on `document_id`
- Full-text search index on `content` (Azure AI Search)
- Vector index on `content_vector` (Azure AI Search)
- Index on `program` for program-specific retrieval
- Index on `effective_date` for temporal policy queries

**Constitutional Compliance**:
- Source URLs provide transparency per Auditability (Principle V)
- Effective dates support accurate policy interpretation per Constitutional accuracy requirements

---

### 6. EscalationTicket

Represents an escalation from the agent to county welfare staff.

**Attributes**:
- `ticket_id` (UUID, primary key): Unique identifier for the escalation ticket
- `session_id` (UUID, foreign key): Reference to parent ConversationSession
- `created_at` (datetime): When the escalation was created
- `escalation_reason` (enum): "low_confidence", "crisis", "fraud_allegation", "policy_exception", "cpra_request", "constituent_request", "unknown_intent"
- `priority` (enum): "emergency", "urgent", "high", "medium", "low"
- `assigned_county` (string, nullable): California county office assigned to handle escalation
- `assigned_agency` (string, nullable): State agency if not county-specific (e.g., "CDSS Fraud Division")
- `status` (enum): "pending", "assigned", "in_progress", "resolved", "closed"
- `expected_resolution_time` (string): Human-readable expected response time (e.g., "2 business days")
- `conversation_context` (JSON): Full query and response history from session
- `resident_contact_info` (text, nullable): Contact information if resident provided (PII-encrypted)
- `language_preference` (string): ISO 639-1 language code for follow-up communication
- `resolved_at` (datetime, nullable): When the ticket was resolved
- `resolution_notes` (text, nullable): County staff notes on resolution (not shown to agent)

**Relationships**:
- Many-to-one with `ConversationSession`

**Indexes**:
- Primary key on `ticket_id`
- Foreign key index on `session_id`
- Index on `status` for workflow tracking
- Index on `assigned_county` for county-level workload distribution
- Index on `priority` for triage
- Index on `created_at` for SLA tracking

**Constitutional Compliance**:
- Preserves full conversation context per Graceful Escalation (Principle IV)
- `resident_contact_info` encrypted at rest per Data Privacy & Security (Principle I)
- Expected resolution time provided per Graceful Escalation requirements
- CPRA requests routed to Public Records Coordinators per California Public Records Act

---

### 7. AuditLog

Represents Constitutional compliance logging for all agent decisions and actions.

**Attributes**:
- `log_id` (UUID, primary key): Unique identifier for the audit log entry
- `timestamp` (datetime): When the event occurred (ISO 8601 format)
- `session_id` (UUID, foreign key, nullable): Reference to ConversationSession if applicable
- `query_id` (UUID, foreign key, nullable): Reference to Query if applicable
- `agent` (enum): "QueryAgent", "RouterAgent", "ActionAgent"
- `action` (enum): "classify_intent", "extract_entities", "route_to_agency", "search_knowledge_base", "generate_response", "create_ticket", "detect_escalation", "detect_crisis"
- `input` (JSON): Input data to the agent (query text, prior agent output, etc.)
- `decision` (string): Selected category, action, or routing decision
- `confidence` (float, 0.0-1.0, nullable): Confidence score if applicable
- `reasoning` (text): Why this decision was made (LLM reasoning trace)
- `compliance_flags` (JSON array): Constitutional compliance checks ["privacy_check", "escalation_trigger", "language_detected", "pii_masked", "crisis_detected"]
- `processing_time_ms` (integer): Time taken for this action in milliseconds

**Relationships**:
- Many-to-one with `ConversationSession` (nullable)
- Many-to-one with `Query` (nullable)

**Indexes**:
- Primary key on `log_id`
- Foreign key indexes on `session_id` and `query_id`
- Index on `timestamp` for temporal analysis
- Index on `agent` for agent-specific analytics
- Index on `action` for action-specific analytics
- Index on `compliance_flags` (GIN index for JSON array) for compliance audits

**Constitutional Compliance**:
- Supports SB 53 algorithmic accountability reviews per Auditability (Principle V)
- Enables CPRA requests and compliance audits
- Provides trace-back from ticket to original query per Constitutional requirements
- Reasoning field supports explainability and bias detection

---

## Entity Relationships Diagram

```
ConversationSession
    ├── session_id (PK)
    ├── language
    ├── county
    └── escalation_ticket_id (FK) ────┐
                                       │
Query                                  │
    ├── query_id (PK)                  │
    ├── session_id (FK) ───────────┐  │
    ├── intent                      │  │
    ├── confidence_score            │  │
    └── citations (FK array) ───┐   │  │
                                 │   │  │
EligibilityProfile               │   │  │
    ├── profile_id (PK)          │   │  │
    ├── session_id (FK) ─────────┤   │  │
    └── preliminary_results      │   │  │
                                 │   │  │
BenefitProgram                   │   │  │
    ├── program_id (PK)          │   │  │
    ├── income_limits            │   │  │
    └── policy_document_ids ──┐  │   │  │
                               │  │   │  │
PolicyDocument                 │  │   │  │
    ├── document_id (PK) ◄─────┴──┴───┘  │
    ├── content                           │
    ├── content_vector                    │
    └── citation_format                   │
                                          │
EscalationTicket                          │
    ├── ticket_id (PK) ◄──────────────────┘
    ├── session_id (FK)
    ├── escalation_reason
    ├── priority
    └── conversation_context

AuditLog
    ├── log_id (PK)
    ├── session_id (FK)
    ├── query_id (FK)
    ├── agent
    ├── action
    └── compliance_flags
```

---

## Data Retention and Privacy

Per CCPA/CPRA and California State data retention policies:

- **ConversationSession**: Retained for 7 years for audit and compliance purposes
- **Query**: PII-masked queries retained for 7 years; original unmasked queries deleted after session ends
- **EligibilityProfile**: Deleted immediately after session ends unless resident opts to save (encrypted, 30-day retention)
- **BenefitProgram**: Retained indefinitely; updated when policies change
- **PolicyDocument**: Retained indefinitely; versioned when policies change
- **EscalationTicket**: Retained for 10 years per state records retention schedule; resident contact info encrypted at rest
- **AuditLog**: Retained for 7 years per SB 53 algorithmic accountability requirements

**PII Handling**:
- SSN, driver's license numbers, financial account numbers NEVER stored per Constitution Prohibited Actions
- IP addresses hashed (not stored in plaintext)
- Resident contact info in escalation tickets encrypted at rest (AES-256)
- Query text PII-masked before storage using regex and NER (Named Entity Recognition)

---

## Sample Data

### Sample ConversationSession

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "started_at": "2026-02-02T14:30:00Z",
  "ended_at": "2026-02-02T14:45:00Z",
  "channel": "web",
  "language": "es",
  "county": "Los Angeles",
  "escalated": false,
  "escalation_ticket_id": null,
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
  "ip_address_hash": "5d41402abc4b2a76b9719d911017c592"
}
```

### Sample Query

```json
{
  "query_id": "660e8400-e29b-41d4-a716-446655440111",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-02-02T14:30:15Z",
  "query_text": "¿Cuáles son los límites de ingresos para CalFresh para una familia de 3?",
  "query_text_original_language": "es",
  "intent": "eligibility_question",
  "confidence_score": 0.95,
  "entities_extracted": {
    "program": "CalFresh",
    "household_size": 3,
    "county": null
  },
  "response_text": "Para una familia de 3 personas en California, el límite de ingresos brutos mensuales para CalFresh es de $2,495 (130% del nivel federal de pobreza). El límite de ingresos netos es de $1,920 (100% FPL). Estos límites se actualizan anualmente. Fuente: CDSS CalFresh Manual Sección 63-300.1.",
  "response_language": "es",
  "citations": [
    {
      "document_id": "770e8400-e29b-41d4-a716-446655440222",
      "citation": "CDSS CalFresh Manual Sección 63-300.1",
      "relevance_score": 0.92
    }
  ],
  "processing_time_ms": 1850,
  "routed_to": null,
  "escalated": false
}
```

### Sample EligibilityProfile

```json
{
  "profile_id": "880e8400-e29b-41d4-a716-446655440333",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-02-02T14:35:00Z",
  "household_size": 3,
  "monthly_income_total": 2200.00,
  "county": "Los Angeles",
  "has_senior_65plus": false,
  "has_disability": false,
  "has_child_under_18": true,
  "citizenship_status": "citizen",
  "currently_working": true,
  "receiving_other_benefits": [],
  "preliminary_eligibility_results": {
    "calfresh": {
      "likely_eligible": true,
      "reason": "Gross income $2,200 is below limit $2,495 for household of 3",
      "next_steps": "Apply at BenefitsCal portal"
    },
    "calworks": {
      "likely_eligible": false,
      "reason": "Income exceeds CalWORKs limits for household of 3 with one child",
      "next_steps": "Contact Los Angeles County DPSS for case-by-case review"
    },
    "general_relief": {
      "likely_eligible": false,
      "reason": "General Relief is for individuals without children",
      "next_steps": null
    },
    "capi": {
      "likely_eligible": false,
      "reason": "No household member 65+ or disabled",
      "next_steps": null
    }
  }
}
```

### Sample EscalationTicket

```json
{
  "ticket_id": "990e8400-e29b-41d4-a716-446655440444",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-02-02T14:40:00Z",
  "escalation_reason": "policy_exception",
  "priority": "medium",
  "assigned_county": "Los Angeles",
  "assigned_agency": null,
  "status": "pending",
  "expected_resolution_time": "2 business days",
  "conversation_context": {
    "queries": [
      {
        "query_text": "I have a special situation with my income calculation...",
        "response_text": "Income exceptions require case-by-case review. I'll escalate to a county worker.",
        "timestamp": "2026-02-02T14:39:00Z"
      }
    ]
  },
  "resident_contact_info": "[ENCRYPTED]",
  "language_preference": "en",
  "resolved_at": null,
  "resolution_notes": null
}
```
