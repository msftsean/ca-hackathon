# Feature Specification: BenefitsCal Navigator Agent

**Feature Branch**: `001-benefitscal-navigator`  
**Created**: 2026-02-02  
**Status**: Draft  
**Agency**: California Department of Social Services (CDSS)  
**Programs**: CalFresh, CalWORKs, General Relief, CAPI  
**NYC Analog**: Constituent Services Agent

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Eligibility Q&A (Priority: P1)

A California resident visits the BenefitsCal portal to understand if they qualify for CalFresh benefits. They ask natural language questions like "Do I qualify for CalFresh if I work part-time?" or "What are the income limits for a family of 4?" The agent provides citation-backed answers from CDSS policy manuals, helping residents understand eligibility before starting an application.

**Why this priority**: Core value proposition. Reduces county office burden by helping residents self-assess eligibility. Directly addresses the backlogs from shifting federal eligibility rules (H.R. 1 work requirements). Must work independently to deliver value.

**Independent Test**: Can be fully tested by asking benefit eligibility questions and verifying citation-backed responses are provided without requiring any other features. Delivers immediate value by reducing confusion and unnecessary applications.

**Acceptance Scenarios**:

1. **Given** a resident visits the BenefitsCal Navigator, **When** they ask "What are the income limits for CalFresh for a family of 3?", **Then** the agent provides the current income limits with citations to CDSS policy manuals
2. **Given** a resident asks about work requirements, **When** they specify "Do I need to work to get CalFresh?", **Then** the agent explains the current work requirements with references to updated federal and state guidelines
3. **Given** a question about multiple programs, **When** the resident asks "What benefits am I eligible for?", **Then** the agent explains CalFresh, CalWORKs, General Relief, and CAPI at a high level and asks clarifying questions
4. **Given** an ambiguous question, **When** the resident asks "Can I get help?", **Then** the agent asks clarifying questions about household situation, income, and specific needs
5. **Given** a policy question outside the knowledge base, **When** the resident asks about a hypothetical scenario, **Then** the agent acknowledges uncertainty and provides county contact information

---

### User Story 2 - Multi-Language Support (Priority: P2)

A California resident whose primary language is Spanish navigates to the BenefitsCal portal and asks "¿Califico para CalFresh?" The agent detects the language, responds in Spanish, and provides all subsequent interactions in the selected language. The system supports Spanish, Chinese (Mandarin/Cantonese), Vietnamese, Tagalog, Korean, Armenian, Farsi, and Arabic to serve California's diverse population (40%+ speak a primary language other than English).

**Why this priority**: Critical for equity and accessibility per California Government Code §7290-7299.8 and Envision 2026 Goal 1. However, P1 (core Q&A) must work first to validate the knowledge base and agent logic. Language support can be added as a layer on top.

**Independent Test**: Can be tested by submitting queries in each supported language and verifying responses are provided in the same language with accurate translations. Can be demonstrated separately from eligibility screening or voice features.

**Acceptance Scenarios**:

1. **Given** a resident types a question in Spanish, **When** they ask "¿Cuáles son los límites de ingresos para CalFresh?", **Then** the agent responds in Spanish with accurate policy information
2. **Given** a resident starts in English, **When** they request to switch to Vietnamese mid-conversation, **Then** the agent switches language and continues the conversation context
3. **Given** a resident types in Chinese characters, **When** they ask about CalWORKs eligibility, **Then** the agent detects Chinese and responds in Chinese (Mandarin/Cantonese based on detection)
4. **Given** a language preference is set, **When** the resident navigates to different sections, **Then** the language preference persists throughout the session
5. **Given** a resident uses a language not supported, **When** they type in a language like Russian, **Then** the agent responds in English and offers contact information for in-language support

---

### User Story 3 - Eligibility Pre-Screening (Priority: P3)

A California resident wants to know their preliminary eligibility before investing time in a full application. They enter household information (household size, county, income, citizenship status, age, disability status) and the agent provides a preliminary eligibility determination for CalFresh, CalWORKs, General Relief, and CAPI based on documented eligibility rules. This helps residents understand which programs to pursue.

**Why this priority**: High value but requires P1 foundation. Pre-screening reduces wasted effort for both residents and county workers. However, the Q&A foundation must be solid first, as pre-screening depends on accurate knowledge base and policy interpretation.

**Independent Test**: Can be tested by entering various household scenarios and verifying preliminary eligibility determinations match documented policy rules. Delivers standalone value by helping residents identify relevant programs before applying.

**Acceptance Scenarios**:

1. **Given** a resident selects the pre-screening tool, **When** they enter household size 3, income $2,500/month, Los Angeles County, **Then** the agent shows preliminary CalFresh eligibility with income limit comparison
2. **Given** household information indicates senior age 65+, **When** income is below CAPI thresholds, **Then** the agent highlights CAPI eligibility and provides program information
3. **Given** household information includes a disability status, **When** income exceeds standard limits, **Then** the agent explains higher income limits for disabled individuals and shows updated eligibility
4. **Given** a resident enters information that suggests ineligibility for all programs, **When** pre-screening completes, **Then** the agent provides county contact information for case-by-case review and appeals process
5. **Given** a resident enters partial information, **When** they skip required fields, **Then** the agent explains which fields are needed and why, offering to provide general guidance without full pre-screening

---

### User Story 4 - Voice Interaction (Priority: P4)

A California resident accesses the BenefitsCal Navigator via voice interface using Azure OpenAI Realtime API. They speak their questions instead of typing, enabling access for residents with visual impairments, low literacy, or who prefer voice interaction. The voice agent follows Constitutional voice-specific obligations (identification as AI, consent, crisis detection).

**Why this priority**: Important for accessibility (ADA/WCAG 2.1 AA) and digital equity, but depends on P1-P3 working correctly. Voice is a delivery mechanism for the core capabilities. Can be added after validating text-based interactions.

**Independent Test**: Can be tested by initiating voice sessions, asking questions verbally, and verifying accurate voice responses with proper disclosures. Demonstrates accessibility compliance independently.

**Acceptance Scenarios**:

1. **Given** a resident initiates a voice session, **When** the session starts, **Then** the agent identifies itself as an AI agent and confirms recording consent per California two-party consent law
2. **Given** a resident speaks "What are the CalFresh income limits?", **When** the voice query is processed, **Then** the agent responds with accurate information at a measured pace for comprehension
3. **Given** a resident uses a speech disability or accent, **When** they speak slowly or with pauses, **Then** the agent allows extended input time and confirms understanding before responding
4. **Given** a resident says "I can't afford food for my kids this week", **When** distress is detected, **Then** the agent offers immediate county emergency services contact and crisis resources
5. **Given** background noise interferes with voice input, **When** the agent cannot understand the query, **Then** the agent asks the resident to repeat or offers to switch to text-based interaction

---

### User Story 5 - Human Escalation with Confidence Scoring (Priority: P5)

When the BenefitsCal Navigator encounters a query outside its capabilities, detects low confidence in its response, or identifies escalation triggers (crisis language, fraud allegations, policy exceptions), it gracefully escalates to county welfare staff. The agent preserves conversation context, creates a ticket, provides expected response time, and ensures no resident is left without a next step.

**Why this priority**: Critical for Constitutional compliance (Graceful Escalation principle) but should be the last feature built. Requires P1-P4 to determine what "low confidence" means and when escalation is needed. Acts as a safety net for the other features.

**Independent Test**: Can be tested by triggering various escalation conditions (ambiguous queries, crisis keywords, requests outside scope) and verifying appropriate escalation with ticket creation and human routing.

**Acceptance Scenarios**:

1. **Given** a resident asks a question the agent cannot answer with >70% confidence, **When** the query is processed, **Then** the agent explains uncertainty and offers to escalate to a county worker with expected 2-business-day response time
2. **Given** a resident mentions "I want to report fraud", **When** the query is classified, **Then** the agent immediately escalates to the fraud investigation unit and provides a case reference number
3. **Given** a resident asks about a policy exception or special circumstance, **When** the query requires human judgment, **Then** the agent creates a ticket, preserves conversation context, and routes to appropriate county staff
4. **Given** a resident uses crisis language like "I'm going to hurt myself", **When** the query is processed, **Then** the agent immediately provides 988 Suicide & Crisis Lifeline and offers to connect to emergency services
5. **Given** a ticket has been created, **When** a county worker reviews the escalation, **Then** the full conversation context, language preference, and resident contact information are available in the ticket

---

### Edge Cases

- What happens when a resident asks about a benefit program not administered by CDSS (e.g., unemployment insurance, Social Security)?
- How does the system handle questions about benefits in counties with different local rules or implementation?
- What happens when federal policy changes (H.R. 1 implementation) and knowledge base is not yet updated?
- How does the system handle residents who provide conflicting information between Q&A and pre-screening?
- What happens when a resident's income is exactly at the eligibility threshold?
- How does the system handle questions that mix multiple languages in a single query?
- What happens when voice input contains extremely loud background noise or multiple speakers?
- How does the system handle California Public Records Act (CPRA) requests related to agent interactions?
- What happens when a resident explicitly refuses consent for recording in voice mode?
- How does the system route county-specific questions when the resident's county is not specified?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST process natural language queries about CalFresh, CalWORKs, General Relief, and CAPI eligibility and benefits
- **FR-002**: System MUST provide responses with citations to CDSS policy manuals, regulations, or official guidance documents
- **FR-003**: System MUST detect and respond in Spanish, Chinese (Mandarin/Cantonese), Vietnamese, Tagalog, Korean, Armenian, Farsi, and Arabic
- **FR-004**: System MUST support language switching mid-conversation while preserving context
- **FR-005**: System MUST provide preliminary eligibility determination based on household size, income, county, citizenship status, age, and disability status
- **FR-006**: System MUST compare household information against documented income limits and eligibility criteria for each program
- **FR-007**: System MUST support voice input and output via Azure OpenAI Realtime API
- **FR-008**: System MUST identify itself as an AI agent at the start of voice sessions per Constitutional requirements
- **FR-009**: System MUST confirm recording consent in voice mode per California two-party consent law
- **FR-010**: System MUST detect crisis language (suicide, self-harm, immediate danger) and provide crisis resources (988 Lifeline)
- **FR-011**: System MUST calculate confidence scores for all responses and flag low-confidence responses (<70%)
- **FR-012**: System MUST escalate to county welfare staff when confidence is low, policy exceptions are requested, or Constitutional triggers are detected
- **FR-013**: System MUST create escalation tickets with preserved conversation context, language preference, and case reference number
- **FR-014**: System MUST provide expected response times for escalations per state service standards (2 business days default)
- **FR-015**: System MUST log all queries, responses, confidence scores, and escalations per Auditability & Transparency requirements
- **FR-016**: System MUST mask and protect PII (SSN, driver's license, financial accounts) in logs and responses
- **FR-017**: System MUST route county-administered programs to appropriate county contact information
- **FR-018**: System MUST support mock mode for development without Azure dependencies
- **FR-019**: System MUST comply with WCAG 2.1 Level AA accessibility standards
- **FR-020**: System MUST use plain language at 8th-grade reading level or below per Constitution Principle II
- **FR-021**: System MUST provide text alternatives for any visual content references
- **FR-022**: System MUST allow extended input time for residents with speech disabilities in voice mode
- **FR-023**: System MUST never promise outcomes that require human approval or eligibility determination per Constitution Prohibited Actions
- **FR-024**: System MUST never store or log SSNs, driver's license numbers, or financial account information per Constitution Prohibited Actions

### Key Entities

- **Query**: A resident's question or request, including session ID, query text, detected language, classified intent, confidence score, and generated response
- **EligibilityProfile**: Household information for pre-screening, including household size, total monthly income, county, citizenship status, age of household members, and disability status
- **BenefitProgram**: A CDSS-administered program (CalFresh, CalWORKs, General Relief, CAPI) with program ID, name, description, eligibility requirements, and county-specific income limits
- **PolicyDocument**: A source document in the knowledge base (CDSS manual, regulation, guidance) with document ID, title, section, content chunks, and citation format
- **EscalationTicket**: A record of escalation to county staff, including ticket ID, session ID, escalation reason, priority level, assigned county, ticket status, expected resolution time, and preserved conversation context
- **ConversationSession**: A single interaction with a resident, including session ID, start time, language preference, channel (web/voice), query history, and escalation status

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Residents can get accurate answers to common eligibility questions in under 30 seconds
- **SC-002**: System provides citation-backed responses with references to CDSS policy manuals in 95%+ of eligibility queries
- **SC-003**: Language detection accurately identifies Spanish, Chinese, Vietnamese, Tagalog, Korean, Armenian, Farsi, and Arabic with 95%+ accuracy
- **SC-004**: Preliminary eligibility determinations match documented CDSS policy rules in 98%+ of test cases
- **SC-005**: Voice sessions successfully complete with accurate voice-to-text and text-to-voice conversion in 90%+ of interactions
- **SC-006**: Escalation triggers (crisis language, fraud, low confidence) are detected and routed appropriately in 100% of test cases
- **SC-007**: 90% of residents successfully complete their primary task (Q&A, pre-screening, or escalation) on first attempt
- **SC-008**: County welfare office support tickets related to eligibility questions decrease by 30% in pilot counties
- **SC-009**: System maintains WCAG 2.1 Level AA compliance across all interfaces (web, voice, multilingual)
- **SC-010**: Audit logs capture all required information (query, intent, confidence, routing, escalation) for 100% of interactions per Constitution requirements
- **SC-011**: System response time remains under 2 seconds for 95% of text queries and under 5 seconds for voice queries
- **SC-012**: No PII (SSN, driver's license, financial accounts) appears in logs or non-authenticated responses per CCPA/CPRA compliance requirements
