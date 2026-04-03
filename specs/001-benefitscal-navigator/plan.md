# Implementation Plan: BenefitsCal Navigator Agent

**Branch**: `001-benefitscal-navigator` | **Date**: 2026-02-02 | **Spec**: [spec.md](./spec.md)

## Summary

The BenefitsCal Navigator Agent provides natural language Q&A about California benefit programs (CalFresh, CalWORKs, General Relief, CAPI) for millions of BenefitsCal portal users. It addresses county welfare office backlogs from shifting federal eligibility rules by enabling residents to self-assess eligibility before applying. The agent uses a 47doors 3-agent pipeline (QueryAgent → RouterAgent → ActionAgent) with Azure AI Search for CDSS knowledge base retrieval, Azure OpenAI for response generation, multi-language support for 8 languages, voice interaction via Realtime API, and human escalation with confidence scoring. The system must comply with EO N-12-23, CCPA/CPRA, and California's Envision 2026 digital equity goals.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, Pydantic v2, Semantic Kernel, Azure OpenAI SDK, Azure AI Search SDK, Azure Speech SDK  
**Storage**: Azure AI Search (vector + hybrid search for CDSS knowledge base), PostgreSQL (conversation sessions, escalation tickets), Redis (session state)  
**Testing**: pytest (unit, integration), Playwright (E2E), Constitutional compliance test suite  
**Target Platform**: Linux containers (Docker), Azure Container Apps deployment  
**Project Type**: Web service (FastAPI backend + React frontend)  
**Performance Goals**: <2s response time for 95% of text queries, <5s for voice queries, support 10,000 concurrent sessions  
**Constraints**: <200ms p95 latency for knowledge base retrieval, <100MB memory per session, WCAG 2.1 AA compliant, CCPA/CPRA compliant logging  
**Scale/Scope**: 1M+ monthly users, 8 languages, 4 benefit programs, 58 counties, 100k+ policy document chunks in knowledge base

## Constitution Check

*Passing requirements based on `/workspaces/ca-hackathon/shared/constitution.md`:*

✅ **Principle I - Data Privacy & Security**: 
- Never reveal benefit amounts, case numbers, or PII without verification
- All queries routed to county staff for constituent-specific records
- PII masking in logs (SSN, driver's license, financial accounts)
- CCPA/CPRA compliant data minimization and retention

✅ **Principle II - Accessibility & Multilingual Access**: 
- 8th-grade reading level responses
- WCAG 2.1 AA compliance (screen reader support, extended input time)
- 8 language support per California Government Code §7290-7299.8
- Voice interface for accessibility

✅ **Principle III - Equity & Bias Mitigation**: 
- Consistent response quality across all 4 benefit programs
- No assumptions based on name, language, location
- Equal support for all counties (rural and urban)
- Dignity-focused language for benefit inquiries

✅ **Principle IV - Graceful Escalation**: 
- Crisis language detection with 988 Lifeline provision
- Low confidence (<70%) escalation to county staff
- Fraud allegations routed to investigation units
- CPRA requests routed to Public Records Coordinators
- 2-business-day expected response time for escalations

✅ **Principle V - Auditability & Transparency**: 
- Log all queries, intents, confidence scores, routing decisions
- Full conversation context preserved for escalations
- Enable SB 53 algorithmic accountability reviews
- CPRA-compliant log retention

✅ **Voice-Specific Obligations**: 
- AI identification at session start
- Recording consent per California two-party consent law
- Distress detection and crisis resource provision
- TTY/TDD relay support
- Speech disability accommodation (extended input time)

**No violations requiring justification.**

## Project Structure

### Documentation (this feature)

```text
specs/001-benefitscal-navigator/
├── spec.md              # Feature specification (user stories, requirements, success criteria)
├── plan.md              # This implementation plan
└── data-model.md        # Entity definitions and data model
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── agents/
│   │   ├── query_agent.py       # Intent classification, entity extraction, language detection
│   │   ├── router_agent.py      # Agency routing, priority setting, escalation triggers
│   │   └── action_agent.py      # Knowledge base search, response generation, ticket creation
│   ├── models/
│   │   ├── query.py             # Query, ConversationSession models
│   │   ├── eligibility.py       # EligibilityProfile, BenefitProgram models
│   │   ├── escalation.py        # EscalationTicket model
│   │   └── policy.py            # PolicyDocument, Citation models
│   ├── services/
│   │   ├── knowledge_base.py    # Azure AI Search integration (hybrid retrieval)
│   │   ├── language_detection.py # Language detection and translation
│   │   ├── eligibility_engine.py # Pre-screening logic and income comparison
│   │   ├── voice_service.py     # Azure OpenAI Realtime API integration
│   │   ├── escalation_service.py # Ticket creation and routing
│   │   └── compliance_logger.py # Constitutional compliance logging
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── chat.py          # Text-based Q&A endpoints
│   │   │   ├── voice.py         # Voice session endpoints (WebRTC)
│   │   │   ├── prescreening.py  # Eligibility pre-screening endpoints
│   │   │   └── escalation.py    # Escalation ticket endpoints
│   │   ├── middleware/
│   │   │   ├── pii_masking.py   # PII detection and masking
│   │   │   └── session_tracking.py # Session management
│   │   └── main.py              # FastAPI application entry point
│   └── config/
│       ├── settings.py          # Configuration (Azure, DB, mock mode)
│       └── constitution.py      # Constitutional compliance rules
└── tests/
    ├── unit/
    │   ├── test_agents.py       # Agent logic tests
    │   ├── test_eligibility.py  # Pre-screening rule tests
    │   └── test_language.py     # Language detection tests
    ├── integration/
    │   ├── test_pipeline.py     # 3-agent pipeline integration
    │   ├── test_knowledge_base.py # Azure AI Search integration
    │   └── test_escalation.py   # Escalation workflow tests
    ├── constitutional/
    │   ├── test_privacy.py      # CCPA/CPRA compliance tests
    │   ├── test_accessibility.py # WCAG 2.1 AA compliance tests
    │   ├── test_escalation_triggers.py # Crisis detection tests
    │   └── test_audit_logs.py   # Logging completeness tests
    └── e2e/
        ├── test_chat_flow.py    # End-to-end text chat scenarios
        ├── test_voice_flow.py   # End-to-end voice scenarios
        └── test_multilingual.py # Multi-language scenarios

frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx    # Text-based chat UI
│   │   ├── VoiceInterface.tsx   # Voice interaction UI (WebRTC)
│   │   ├── LanguageSelector.tsx # Language switcher (8 languages)
│   │   ├── PreScreeningForm.tsx # Eligibility pre-screening form
│   │   └── EscalationStatus.tsx # Ticket status display
│   ├── pages/
│   │   ├── Navigator.tsx        # Main navigator page
│   │   └── EscalationHistory.tsx # Escalation ticket history
│   ├── services/
│   │   ├── apiClient.ts         # Backend API client
│   │   └── voiceClient.ts       # WebRTC voice client
│   ├── hooks/
│   │   ├── useChat.ts           # Chat state management
│   │   ├── useVoice.ts          # Voice session management
│   │   └── useLanguage.ts       # Language preference management
│   └── styles/
│       └── tailwind.config.ts   # Tailwind CSS (WCAG 2.1 AA compliant)
└── tests/
    └── accessibility/
        └── test_wcag.spec.ts    # Playwright WCAG 2.1 AA tests

shared/
├── constitution.md              # California State AI Agent Constitution
└── data/
    └── cdss-policy-manuals/     # CDSS knowledge base source documents
        ├── calfresh/
        ├── calworks/
        ├── general-relief/
        └── capi/
```

**Structure Decision**: Web application structure (backend + frontend) selected because the BenefitsCal Navigator requires both a FastAPI backend for agent orchestration and Azure service integration, and a React frontend for accessible web UI. The `shared/` directory contains the California State Constitution and CDSS policy manual source documents used by all accelerators.

## Complexity Tracking

> No Constitutional violations requiring justification.

| Tech Stack Layer | Technology | Rationale |
|------------------|------------|-----------|
| Backend Runtime | Python 3.11+ | Required for Semantic Kernel agent orchestration |
| Backend Framework | FastAPI | Async performance for concurrent sessions, automatic OpenAPI docs |
| AI/LLM | Azure OpenAI (GPT-4o) | Required for natural language understanding and response generation |
| Knowledge Base | Azure AI Search | Hybrid search (vector + keyword) for CDSS policy retrieval |
| Voice | Azure OpenAI Realtime API | Real-time voice interaction via WebRTC for accessibility |
| Translation | Azure AI Translator | Support for 8 languages per California Government Code §7290 |
| Frontend | React 18 + TypeScript 5 + Vite | Modern, accessible UI framework with WCAG 2.1 AA compliance |
| Styling | Tailwind CSS | Utility-first CSS for rapid accessible design |
| Testing | pytest + Playwright + vitest | Comprehensive unit, integration, E2E, and accessibility testing |
| IaC | Bicep | Azure-native infrastructure as code |
| Deployment | Docker + Azure Developer CLI | Containerized deployment to Azure Container Apps |
| CI/CD | GitHub Actions | Automated testing and deployment pipeline |
