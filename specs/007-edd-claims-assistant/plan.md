# Implementation Plan: EDD Claims Assistant

**Branch**: `007-edd-claims-assistant` | **Date**: 2026-04-02 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/007-edd-claims-assistant/spec.md`

## Summary

The EDD Claims Assistant provides natural language Q&A for Unemployment Insurance (UI), Disability Insurance (DI), and Paid Family Leave (PFL) processes. Claimants can ask questions (backed by EDD policy citations via Azure AI Search), check claim status, complete eligibility pre-screening, generate document checklists, and interact via voice (Azure OpenAI Realtime API with WebRTC). The system escalates complex cases to live agents. Architecture follows the 47doors full-stack pattern with 3-agent pipeline (intent detection, routing, ticket creation), voice integration, and mock mode for development without Azure credentials.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5 (frontend)  
**Primary Dependencies**: FastAPI, Pydantic v2, Semantic Kernel (backend); React 18, Vite, Tailwind CSS (frontend); Azure OpenAI GPT-4o, Azure AI Search, Azure OpenAI Realtime API  
**Storage**: JSON mock data (development), Azure AI Search vector index (EDD policy knowledge base), in-memory session state (production)  
**Testing**: pytest (backend unit/integration), vitest (frontend unit), Playwright (E2E voice + text flows)  
**Target Platform**: Linux server (Docker), Azure Container Apps (production)  
**Project Type**: Full-stack web application with voice interface  
**Performance Goals**: <10s policy Q&A response, <3s claim status lookup, <15s voice round-trip, 1000+ concurrent sessions  
**Constraints**: PII redaction required (EDD compliance), identity verification for claim lookups, <200ms p95 latency for text, graceful voice degradation  
**Scale/Scope**: 10k+ daily claimants (target), 500+ EDD policy articles in knowledge base, 3-5 question eligibility screening flows, 70%+ automation rate for common inquiries

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Analysis

**Principle I (Simplicity)**: ✅ **PASS** — Reuses existing 47doors architecture (3-agent pipeline, voice integration pattern from 002-voice-interaction). No new abstractions beyond domain-specific tools (claim lookup, eligibility assessment).

**Principle II (One LLM Call)**: ✅ **PASS** — Each user turn = 1 LLM call to GPT-4o via Semantic Kernel. Tools (claim lookup, policy search, eligibility screening) execute within that call. Voice uses Realtime API's tool-calling model (no additional orchestration LLM calls).

**Principle III (Voice Parity)**: ✅ **PASS** — Voice and text share identical 3-agent pipeline. Voice transcript entries convert to `VoiceMessage` objects, processed same as text `ChatRequest`. All tools (claim lookup, policy Q&A, escalation) work identically across modalities.

**Principle IV (Tool Implementation)**: ✅ **PASS** — Tools are Python functions decorated with `@kernel_function`. Claim lookup, eligibility assessment, and document checklist generation are deterministic business logic. Azure AI Search for policy retrieval is stateless.

**Principle V (Mock Development)**: ✅ **PASS** — Mock mode uses JSON fixtures for claim data, policy articles, and eligibility rules. Voice mock generates canned responses without Realtime API. Full UX testable without Azure credentials.

**Principle VI (Accessibility)**: ✅ **PASS** — Voice interaction inherently accessible for motor/visual impairments. Keyboard shortcuts for voice activation. Screen reader announcements for state changes. WCAG AA compliance required (EDD mandate).

**Principle VII (Graceful Degradation)**: ✅ **PASS** — Voice-to-text fallback on Realtime API failure. Claim lookup returns cached status if backend unavailable. Policy search falls back to basic keyword matching if Azure AI Search down.

**Principle VIII (Transparency)**: ✅ **PASS** — All policy answers include citations with effective dates. Eligibility assessments show confidence scores and reasoning. Escalation tickets preserve full conversation context for audit.

### Violations: None

No complexity tracking required.

## Project Structure

### Documentation (this feature)

```text
specs/007-edd-claims-assistant/
├── spec.md              # Feature specification (P1-P6 user stories)
├── plan.md              # This file — implementation plan
├── data-model.md        # Entity definitions (backend/frontend schemas)
└── tasks.md             # Task breakdown (generated via /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── edd_schemas.py          # Pydantic models: Claim, EligibilityAssessment, PolicyArticle
│   │   ├── edd_enums.py            # ClaimType, ClaimStatus, EligibilityResult
│   │   └── voice_schemas.py        # Existing VoiceMessage, VoiceSession (from 002)
│   ├── services/
│   │   ├── edd_claim_service.py    # Claim lookup, status retrieval
│   │   ├── edd_eligibility_service.py  # Pre-screening logic, rules engine
│   │   ├── edd_policy_service.py   # Azure AI Search integration for policy Q&A
│   │   └── edd_ticket_service.py   # Escalation ticket creation
│   ├── agents/
│   │   ├── edd_claims_agent.py     # Main agent with @kernel_function tools
│   │   └── edd_escalation_agent.py # Escalation detection and routing
│   ├── api/
│   │   └── edd_routes.py           # FastAPI endpoints: /edd/chat, /edd/claim-status, /edd/voice
│   └── mocks/
│       ├── edd_claims.json         # Mock claim data (20+ sample claims)
│       ├── edd_policies.json       # Mock EDD policy articles (50+ KB entries)
│       └── edd_eligibility_rules.json  # Mock eligibility decision trees
│
├── tests/
│   ├── unit/
│   │   ├── test_edd_claim_service.py
│   │   ├── test_edd_eligibility_service.py
│   │   └── test_edd_policy_service.py
│   ├── integration/
│   │   ├── test_edd_claims_agent.py     # Tool invocation, multi-turn flows
│   │   └── test_edd_voice_integration.py
│   └── contract/
│       └── test_edd_api_contracts.py    # Schema validation for API responses
│
frontend/
├── src/
│   ├── components/
│   │   ├── edd/
│   │   │   ├── EDDChatInterface.tsx    # Main chat UI for EDD assistant
│   │   │   ├── EDDClaimStatusCard.tsx  # Claim status display widget
│   │   │   ├── EDDDocumentChecklist.tsx # Document checklist generator UI
│   │   │   └── EDDVoiceToggle.tsx      # Voice activation button (reuses VoiceProvider from 002)
│   │   └── voice/
│   │       └── VoiceProvider.tsx       # Existing voice context provider (from 002)
│   ├── pages/
│   │   └── EDDAssistantPage.tsx        # Main page component
│   ├── services/
│   │   └── eddApiClient.ts             # API client for /edd/* endpoints
│   └── types/
│       └── edd.ts                      # TypeScript interfaces for EDD entities
│
├── tests/
│   ├── unit/
│   │   └── edd/
│   │       ├── EDDChatInterface.test.tsx
│   │       └── EDDClaimStatusCard.test.tsx
│   └── e2e/
│       ├── edd-claims-qa.spec.ts       # P1: Policy Q&A flow
│       ├── edd-claim-status.spec.ts    # P2: Status lookup flow
│       ├── edd-eligibility.spec.ts     # P3: Pre-screening flow
│       └── edd-voice-interaction.spec.ts # P5: Voice end-to-end
```

**Structure Decision**: Full-stack web application with dedicated EDD module. Backend follows existing `backend/app/` structure with new `edd_*` service modules. Frontend adds `src/components/edd/` for EDD-specific UI while reusing existing voice infrastructure from 002-voice-interaction. Mock data in `backend/mocks/edd_*` enables development without Azure credentials.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations — this section is empty.*
