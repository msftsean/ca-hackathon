# Feature Specification: EDD Claims Assistant

**Feature Branch**: `007-edd-claims-assistant`  
**Created**: 2026-04-02  
**Status**: Draft  
**Agency**: Employment Development Department (EDD)  
**Compliance**: EO N-12-23, Envision 2026 Goal 1, EDD security/privacy requirements  
**Input**: Natural language Q&A for UI, DI, and PFL claims processes with voice support, eligibility screening, and live agent escalation

## Problem Statement

The California Employment Development Department (EDD) is the state's most-criticized agency. Unemployment Insurance (UI), Disability Insurance (DI), and Paid Family Leave (PFL) claims face persistent processing delays, with phone wait times regularly exceeding 60 minutes. Claimants struggle to understand complex filing requirements, check claim status, and determine eligibility. The lack of accessible, 24/7 self-service support creates frustration and increases call center burden.

## Vision

Provide a natural language assistant that helps claimants navigate UI, DI, and PFL processes through conversational Q&A. The assistant answers questions backed by EDD policy citations, provides claim status lookups, performs eligibility pre-screening, generates personalized document checklists, and escalates to live agents when needed. Voice interaction via Azure OpenAI Realtime API reduces barriers for claimants with accessibility needs or those calling during wait times.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Claims Process Q&A (Priority: P1)

A claimant asks questions about the UI filing process, required documentation, or benefit amounts. The assistant retrieves answers from the EDD policy knowledge base, provides citation-backed responses, and offers next steps.

**Why this priority**: This is the core value proposition. If only this ships, claimants can get accurate, citation-backed answers to their questions 24/7 without waiting on hold.

**Independent Test**: Can be fully tested by asking "How do I file for unemployment?" and verifying the assistant returns step-by-step filing instructions with EDD policy citations within 5 seconds.

**Acceptance Scenarios**:

1. **Given** a claimant is on the assistant page, **When** they ask "How do I file for unemployment insurance?", **Then** the assistant retrieves EDD UI filing policy, responds with step-by-step instructions, and includes citations to official EDD documentation.
2. **Given** a claimant asks "What documents do I need for disability insurance?", **When** processed, **Then** the assistant returns a list of required documents for DI claims with links to forms and policy references.
3. **Given** a claimant asks "How much will I receive in unemployment benefits?", **When** the assistant processes the query, **Then** it explains the benefit calculation formula and suggests using the online benefit calculator.
4. **Given** a claimant asks about PFL, **When** they say "Can I take paid family leave to care for my mother?", **Then** the assistant explains PFL eligibility criteria for family care and provides next steps.
5. **Given** the knowledge base doesn't have a confident answer, **When** the assistant's confidence score is below 0.7, **Then** it responds "I don't have enough information to answer that confidently. Let me connect you with a live agent" and escalates.

---

### User Story 2 - Claim Status Lookup (Priority: P2)

A claimant provides their claim number and wants to check the current status, payment schedule, or pending issues. The assistant looks up the claim in the system and provides status information with next actions.

**Why this priority**: Status lookups reduce call center volume significantly. If implemented alone, claimants can self-service their most common inquiry without calling.

**Independent Test**: Can be tested by entering a claim number and verifying the assistant returns current claim status, next payment date, and pending actions within 3 seconds.

**Acceptance Scenarios**:

1. **Given** a claimant provides a UI claim number, **When** the assistant looks up the claim, **Then** it returns the current status (Pending, Approved, Denied, Under Review), last certification date, and next expected payment date.
2. **Given** a claim has pending issues (ID verification, employer response), **When** the claimant checks status, **Then** the assistant lists all pending issues and provides instructions to resolve each.
3. **Given** a claimant enters an invalid claim number, **When** the lookup fails, **Then** the assistant responds "I couldn't find a claim with that number. Please verify the number or contact EDD at [phone]" without exposing system errors.
4. **Given** a claim payment is delayed, **When** the claimant asks "When will I get paid?", **Then** the assistant explains typical payment timelines, checks for pending issues, and offers escalation if the delay exceeds normal processing time.
5. **Given** a claimant has multiple claims (UI and DI), **When** they ask about status, **Then** the assistant displays all active claims and asks which one they want to check.

---

### User Story 3 - Eligibility Pre-Screening (Priority: P3)

A claimant is unsure if they qualify for UI, DI, or PFL. The assistant asks clarifying questions about employment history, work hours, reason for claim, and provides a preliminary eligibility assessment with confidence level.

**Why this priority**: Pre-screening saves time for both claimants and EDD staff by helping people understand if they should apply before starting a lengthy application.

**Independent Test**: Can be tested by answering a series of eligibility questions and verifying the assistant provides a preliminary assessment with reasoning and next steps.

**Acceptance Scenarios**:

1. **Given** a claimant asks "Am I eligible for unemployment?", **When** the assistant starts screening, **Then** it asks 3-5 questions: "Did you work in California in the last 18 months?", "Why did you stop working?", "Were you an employee or contractor?", and similar.
2. **Given** the claimant answers all screening questions, **When** the assistant analyzes responses, **Then** it provides an assessment: "Based on your answers, you appear to be eligible for UI. However, final determination is made by EDD after you file."
3. **Given** a claimant is not eligible (e.g., quit without good cause), **When** the assessment is negative, **Then** the assistant explains why they may not qualify and suggests alternatives (e.g., PFL, SDI, or appeal process).
4. **Given** a claimant's situation is complex (partial unemployment, work-sharing), **When** the assistant detects complexity, **Then** it provides a preliminary assessment but strongly recommends speaking with a live agent for confirmation.
5. **Given** a claimant is eligible, **When** the assessment is complete, **Then** the assistant offers to start the filing process or provides a direct link to the online application.

---

### User Story 4 - Document Requirement Checklist (Priority: P4)

A claimant is preparing to file and wants to know exactly what documents they need. The assistant generates a personalized checklist based on claim type, employment situation, and special circumstances.

**Why this priority**: Missing documents cause processing delays. A personalized checklist reduces back-and-forth and speeds up claim processing.

**Independent Test**: Can be tested by providing claim type and employment details, then verifying the assistant generates a complete, personalized document checklist.

**Acceptance Scenarios**:

1. **Given** a claimant says "I'm filing for unemployment — what do I need?", **When** the assistant asks about their employment type (W-2 employee, contractor, military), **Then** it generates a checklist specific to that type (e.g., W-2 needs most recent pay stubs, employer contact, SSN).
2. **Given** a claimant worked multiple jobs, **When** the assistant detects this, **Then** the checklist includes instructions to provide documentation for all employers in the base period.
3. **Given** a claimant is filing DI, **When** they select DI claim type, **Then** the assistant provides a DI-specific checklist (medical certification, first day off work, treating physician info).
4. **Given** a claimant has special circumstances (union membership, federal employee, military discharge), **When** detected, **Then** the checklist includes additional required documents specific to that situation.
5. **Given** the checklist is generated, **When** the claimant reviews it, **Then** each item has a brief explanation of why it's needed and where to obtain it (e.g., "DD-214 (military discharge) — request from National Archives").

---

### User Story 5 - Voice Interaction (Priority: P5)

A claimant uses voice to interact with the assistant instead of typing. The voice interface uses the same claim Q&A, status lookup, and eligibility screening capabilities but through spoken conversation via Azure OpenAI Realtime API.

**Why this priority**: Voice interaction is critical for accessibility and for claimants calling during long wait times. It provides a parallel path to reduce phone burden.

**Independent Test**: Can be tested by clicking the microphone button, asking "What's the status of my claim?" via voice, and verifying the assistant responds verbally with status information.

**Acceptance Scenarios**:

1. **Given** a claimant clicks the microphone button, **When** the browser requests permission, **Then** the voice session activates with a pulsing waveform indicator.
2. **Given** the claimant speaks "How do I file for disability insurance?", **When** the voice agent processes the query, **Then** it invokes the claims Q&A tool, retrieves EDD DI policy, and speaks the answer back with citations.
3. **Given** a claimant provides a claim number via voice, **When** the assistant looks up the claim, **Then** it speaks the current status, next payment date, and any pending actions.
4. **Given** the voice session encounters a complex question, **When** the assistant needs to escalate, **Then** it verbally confirms "Let me connect you with a live EDD representative" and creates an escalation ticket.
5. **Given** a claimant switches from voice to text mid-conversation, **When** they type a follow-up question, **Then** the session context is preserved and the conversation continues seamlessly.
6. **Given** the Realtime API is unavailable, **When** the claimant clicks the microphone, **Then** the system displays "Voice mode is temporarily unavailable. Please use text chat or call EDD at [phone]."

---

### User Story 6 - Live Agent Escalation (Priority: P6)

A claimant's situation requires human judgment (complex case, emotional distress, policy ambiguity, or explicit request for a person). The assistant detects this, creates an escalation ticket with full conversation context, and provides estimated response time.

**Why this priority**: Escalation is safety-critical and constitutionally required. The assistant must know when to defer to humans.

**Independent Test**: Can be tested by saying "I need to speak to a person about my denied claim" and verifying the assistant creates an escalation ticket with high priority and provides callback information.

**Acceptance Scenarios**:

1. **Given** a claimant says "I want to talk to a real person", **When** the assistant detects the explicit human request, **Then** it immediately escalates, creates a ticket with the full conversation transcript, and provides an estimated callback time.
2. **Given** a claimant mentions a denied claim and asks to appeal, **When** the assistant detects "appeal" keyword, **Then** it escalates with high priority and provides information about the appeal process and timeline.
3. **Given** a claimant expresses frustration or distress ("I'm about to be evicted", "I haven't been paid in 8 weeks"), **When** sentiment analysis detects high urgency, **Then** the assistant escalates immediately and provides crisis resources (emergency assistance programs, legal aid numbers).
4. **Given** a claimant's question involves policy interpretation or discretion, **When** the assistant confidence score is low across multiple attempts, **Then** it escalates and explains "This requires EDD staff review. A specialist will contact you within [SLA]."
5. **Given** an escalation ticket is created, **When** the claimant asks for confirmation, **Then** the assistant provides the ticket number, priority level, estimated response time, and alternative contact methods if urgent.

---

### Edge Cases

- **Multiple active claims**: What happens when a claimant has both UI and DI claims active and asks "What's my status?" without specifying? → Assistant lists all active claims and asks which one to look up.
- **Expired session during voice**: How does the system handle voice session expiration or disconnection? → Graceful fallback to text with "Voice connection lost. Your conversation has been saved. Please continue via text or call [phone]."
- **PII in voice transcript**: What if a claimant speaks their SSN or sensitive data during a voice interaction? → Real-time PII detection flags and redacts sensitive data before logging, with audio cue "Please don't share your Social Security number over voice. I'll ask for verification through secure channels."
- **Claim status API outage**: How does the assistant handle claim lookup when the backend system is unavailable? → "I'm unable to access claim status right now. Please try again in a few minutes or call [phone]."
- **Conflicting eligibility factors**: What if a claimant's answers suggest both eligibility and disqualification? → Assistant flags the ambiguity: "Your situation has factors that could go either way. I recommend filing and letting EDD make the official determination."
- **Non-English interaction**: What if a claimant needs assistance in Spanish or another language? → If multilingual support is available, route to translated knowledge base; otherwise, provide language access line number: "Para asistencia en español, llame [phone]."
- **Fraudulent claim inquiry**: What if someone tries to check status on a claim that doesn't belong to them? → Assistant requires identity verification (last 4 of SSN, date of birth) and limits lookup attempts to prevent enumeration attacks.
- **Outdated policy in knowledge base**: How does the system handle questions about policies that may have changed? → All knowledge base articles include effective dates; assistant warns "This information is current as of [date]. For the most recent policy, visit [edd.ca.gov]."

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST retrieve EDD policy answers from Azure AI Search knowledge base with citation tracking for UI, DI, and PFL questions.
- **FR-002**: System MUST look up claim status by claim number, returning current status, pending issues, next payment date, and required actions.
- **FR-003**: System MUST perform eligibility pre-screening by asking 3-5 clarifying questions and providing preliminary assessment with confidence score.
- **FR-004**: System MUST generate personalized document checklists based on claim type (UI/DI/PFL), employment type (W-2, contractor, military, federal), and special circumstances.
- **FR-005**: System MUST support voice interaction via Azure OpenAI Realtime API with WebRTC transport, enabling all text capabilities through spoken conversation.
- **FR-006**: System MUST detect escalation triggers (explicit human request, policy keywords like "appeal" or "denied", low confidence, sentiment distress) and create escalation tickets with full context.
- **FR-007**: System MUST preserve conversation context across modality switches (text to voice, voice to text) within a single session.
- **FR-008**: System MUST redact PII (SSN, claim numbers, dates of birth) from logs and transcripts in accordance with EDD privacy requirements.
- **FR-009**: System MUST require identity verification (last 4 SSN + DOB) before returning claim status or personal information.
- **FR-010**: System MUST degrade gracefully when Azure OpenAI Realtime API is unavailable, falling back to text-only mode with clear user communication.
- **FR-011**: System MUST track all interactions (queries, claim lookups, escalations) for compliance auditing and quality assurance.
- **FR-012**: System MUST provide alternative contact methods (phone numbers, office locations) when unable to answer questions or during system outages.
- **FR-013**: System MUST include effective dates with all policy answers and warn users when information may be outdated.
- **FR-014**: System MUST rate-limit claim lookups to prevent enumeration attacks (max 5 failed attempts per session, require identity re-verification).
- **FR-015**: System MUST support multi-claim scenarios, allowing claimants with multiple active claims (UI + DI) to select which claim to inquire about.

### Key Entities

- **Claim**: Represents a UI, DI, or PFL claim with claim ID, claimant ID, type, status, filing date, benefit amount, next payment date, pending issues, and required actions.
- **ClaimType**: Defines claim categories (UI, DI, PFL) with associated eligibility rules, required documents, processing timelines, and benefit calculations.
- **EligibilityAssessment**: Records pre-screening results with claimant ID, claim type, eligibility determination, contributing factors, confidence score, and recommended next steps.
- **SupportTicket**: Tracks escalations with ticket ID, claim ID (if applicable), category (status inquiry, eligibility question, appeal, escalation), priority, status, assigned agent, and conversation transcript.
- **PolicyArticle**: Stores EDD knowledge base content with article ID, title, body text, claim type tags (UI/DI/PFL), effective date, expiration date, and policy citations.
- **ConversationSession**: Manages chat and voice sessions with session ID, claimant ID (if authenticated), modality (text/voice), message history, escalation flag, and timestamps.
- **DocumentChecklist**: Generates personalized document lists with checklist ID, claim type, employment type, special circumstances flags, and required document items with explanations.
- **IdentityVerification**: Securely validates claimant identity with verification ID, session ID, verification method (last 4 SSN + DOB), success status, attempt count, and lockout timestamp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Claimants can get answers to common UI/DI/PFL questions in under 10 seconds with 90%+ accuracy and policy citations.
- **SC-002**: Claim status lookups return current information in under 3 seconds for 95% of requests.
- **SC-003**: Eligibility pre-screening provides preliminary assessments with 85%+ accuracy compared to official EDD determinations.
- **SC-004**: Voice interactions complete successfully (full question-answer cycle) in under 15 seconds for 90% of queries.
- **SC-005**: System correctly escalates 95%+ of conversations containing escalation triggers (human request, policy keywords, low confidence).
- **SC-006**: System prevents unauthorized claim lookups with 99.9%+ success rate via identity verification and rate limiting.
- **SC-007**: Voice mode degrades gracefully to text-only within 2 seconds when Realtime API is unavailable, with zero data loss.
- **SC-008**: Reduce EDD call center volume for status inquiries and general questions by 30% within 3 months of deployment.
- **SC-009**: 80%+ of claimants report satisfaction with assistant accuracy and helpfulness in post-interaction surveys.
- **SC-010**: Zero PII leakage in logs or transcripts, verified through automated compliance scans and quarterly audits.
