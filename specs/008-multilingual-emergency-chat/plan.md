# Implementation Plan: Multilingual Emergency Chatbot

**Branch**: `008-multilingual-emergency-chat` | **Date**: 2026-04-02 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/008-multilingual-emergency-chat/spec.md`

## Summary

The Multilingual Emergency Chatbot delivers real-time emergency information (alerts, evacuation orders, shelter locations, air quality) in 70+ languages via Azure Translator. Architecture is deliberately lightweight — single-agent design with Azure AI Search for emergency knowledge base, Azure Translator for real-time translation, and SMS gateway for low-bandwidth access. The system prioritizes resilience during infrastructure strain: server-side rendering fallback, aggressive translation caching, and graceful degradation when APIs are unavailable. Targets WCAG AA accessibility and <5s page load on 2G connections.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5 (frontend)  
**Primary Dependencies**: FastAPI, Pydantic v2, Azure Translator, Azure AI Search (backend); React 18, Vite, Tailwind CSS (frontend); Twilio/Azure Communication Services (SMS gateway)  
**Storage**: JSON mock data (development), Azure AI Search index (emergency knowledge base), Redis (translation cache, production)  
**Testing**: pytest (backend unit/integration), vitest (frontend unit), Playwright (E2E multi-language flows + SMS simulation)  
**Target Platform**: Linux server (Docker), Azure Container Apps (production)  
**Project Type**: Lightweight web application with SMS channel  
**Performance Goals**: <3s alert lookup, <2s shelter/AQI queries, <10s SMS response, <5s page load on 2G, 10k+ concurrent users  
**Constraints**: WCAG AA required, <50 KB page size for low-bandwidth mode, translation cache hit rate >60%, graceful degradation for all APIs  
**Scale/Scope**: 10k+ concurrent residents during major incidents, 70+ languages via Azure Translator, 500+ shelters statewide, real-time AQI for 200+ monitoring stations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Analysis

**Principle I (Simplicity)**: ✅ **PASS** — Deliberately simpler than other accelerators. Single-agent design (no multi-agent pipeline). Azure AI Search for emergency knowledge lookup, Azure Translator for language support. No voice integration (pure text/SMS).

**Principle II (One LLM Call)**: ✅ **PASS** — Each user query = 1 LLM call to Azure OpenAI (GPT-4o-mini for lightweight processing). Deterministic tools (alert lookup, shelter search, AQI retrieval) execute within that call. No orchestration layers.

**Principle III (Voice Parity)**: ✅ **PASS** (N/A for this accelerator) — This accelerator is text/SMS only. No voice channel. If voice is added later, it must follow Principle III, but not required for initial scope.

**Principle IV (Tool Implementation)**: ✅ **PASS** — Tools are Python functions decorated with `@kernel_function`. Alert lookup, shelter search, AQI retrieval, and evacuation order checks are deterministic queries to mock/Azure data sources.

**Principle V (Mock Development)**: ✅ **PASS** — Mock mode uses JSON fixtures for emergency alerts, shelters, evacuation orders, and AQI data. Azure Translator mock returns canned translations (English ↔ Spanish/Chinese/Vietnamese for testing). Full UX testable without Azure credentials.

**Principle VI (Accessibility)**: ✅ **PASS** — WCAG AA compliance required for Cal OES. Semantic HTML, keyboard navigation, skip links, screen reader support in both full and low-bandwidth modes. SMS channel inherently accessible (text-only, no visual UI).

**Principle VII (Graceful Degradation)**: ✅ **PASS** — Critical for emergency scenarios. Azure Translator failure → English-only fallback with notification. Azure AI Search failure → basic keyword search in mock data. SMS gateway failure → display web-only mode message with alternative contact numbers.

**Principle VIII (Transparency)**: ✅ **PASS** — All emergency data includes last-updated timestamps. Translation language is always visible to user. Shelter capacity shows "as of [time]" to avoid misleading outdated info.

### Violations: None

No complexity tracking required.

## Project Structure

### Documentation (this feature)

```text
specs/008-multilingual-emergency-chat/
├── spec.md              # Feature specification (P1-P7 user stories)
├── plan.md              # This file — implementation plan
├── data-model.md        # Entity definitions (backend/frontend schemas)
└── tasks.md             # Task breakdown (generated via /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── emergency_schemas.py     # Pydantic models: EmergencyAlert, Shelter, AirQualityReport
│   │   ├── emergency_enums.py       # AlertType, Severity, EvacuationStatus
│   │   └── sms_schemas.py           # SMSMessage, SMSSession
│   ├── services/
│   │   ├── alert_service.py         # Emergency alert retrieval by location
│   │   ├── evacuation_service.py    # Evacuation order lookup
│   │   ├── shelter_service.py       # Shelter search with filtering (ADA, pets, capacity)
│   │   ├── air_quality_service.py   # AQI data retrieval
│   │   ├── translation_service.py   # Azure Translator integration with caching
│   │   └── sms_service.py           # SMS gateway (Twilio/Azure Comm Services)
│   ├── agents/
│   │   └── emergency_agent.py       # Single agent with @kernel_function tools
│   ├── api/
│   │   ├── emergency_routes.py      # FastAPI endpoints: /emergency/alerts, /emergency/shelters, /emergency/aqi
│   │   └── sms_routes.py            # SMS webhook endpoint: POST /sms/inbound
│   ├── cache/
│   │   └── translation_cache.py     # Redis-backed translation cache (mock: in-memory dict)
│   └── mocks/
│       ├── emergency_alerts.json    # Mock alerts (fire, flood, earthquake, AQI)
│       ├── shelters.json            # Mock shelter data (100+ statewide)
│       ├── evacuation_orders.json   # Mock evacuation zones
│       └── air_quality.json         # Mock AQI data for 50+ monitoring stations
│
├── tests/
│   ├── unit/
│   │   ├── test_alert_service.py
│   │   ├── test_shelter_service.py
│   │   ├── test_translation_service.py
│   │   └── test_sms_service.py
│   ├── integration/
│   │   ├── test_emergency_agent.py       # Tool invocation, multi-turn flows
│   │   └── test_sms_integration.py       # SMS webhook simulation
│   └── contract/
│       └── test_emergency_api_contracts.py  # Schema validation
│
frontend/
├── src/
│   ├── components/
│   │   ├── emergency/
│   │   │   ├── EmergencyAlertCard.tsx    # Alert display widget
│   │   │   ├── ShelterList.tsx           # Shelter search results
│   │   │   ├── AirQualityWidget.tsx      # AQI display with health guidance
│   │   │   ├── EvacuationStatusCard.tsx  # Evacuation order display
│   │   │   └── LanguageSelector.tsx      # 70+ language dropdown
│   │   └── low-bandwidth/
│   │       └── LowBandwidthFallback.tsx  # Server-side rendered fallback component
│   ├── pages/
│   │   ├── EmergencyPage.tsx             # Main page (full version)
│   │   └── EmergencyPageSSR.tsx          # Low-bandwidth server-rendered version
│   ├── services/
│   │   ├── emergencyApiClient.ts         # API client for /emergency/* endpoints
│   │   └── translationService.ts         # Frontend translation logic (browser lang detection)
│   ├── types/
│   │   └── emergency.ts                  # TypeScript interfaces
│   └── utils/
│       └── bandwidthDetection.ts         # Network speed detection for low-bandwidth mode
│
├── tests/
│   ├── unit/
│   │   └── emergency/
│   │       ├── EmergencyAlertCard.test.tsx
│   │       ├── ShelterList.test.tsx
│   │       └── LanguageSelector.test.tsx
│   └── e2e/
│       ├── emergency-alert-lookup.spec.ts      # P1: Alert lookup flow
│       ├── multilingual-translation.spec.ts    # P2: Language switching
│       ├── evacuation-order-check.spec.ts      # P3: Evacuation status
│       ├── shelter-search.spec.ts              # P4: Shelter locator
│       ├── air-quality-lookup.spec.ts          # P5: AQI check
│       ├── sms-access.spec.ts                  # P6: SMS interaction (simulated)
│       └── low-bandwidth-mode.spec.ts          # P7: Low-bandwidth fallback
```

**Structure Decision**: Lightweight full-stack application with dedicated emergency module. Backend follows existing `backend/app/` structure with new `emergency_*` and `sms_*` service modules. Frontend adds `src/components/emergency/` for emergency-specific UI and `src/components/low-bandwidth/` for fallback components. Translation caching in `backend/app/cache/` reduces Azure Translator API calls. Mock data in `backend/mocks/emergency_*` enables full development without Azure credentials.

**Key Architectural Notes**:
- **Single Agent Design**: Unlike other accelerators (which use 3-agent pipelines), this uses a single `emergency_agent.py` with deterministic tools. Simpler = more resilient during infrastructure strain.
- **Translation Caching**: Redis cache (dev: in-memory dict) stores translated content keyed by `{content_hash}_{target_lang}`. Cache hit avoids Azure Translator API call.
- **Low-Bandwidth Mode**: FastAPI serves server-side-rendered HTML when `?lowbandwidth=true` query param detected or via automatic bandwidth detection. No React hydration, no JS required.
- **SMS Gateway**: Twilio or Azure Communication Services webhook receives SMS, processes via `emergency_agent`, and responds via SMS API. Rate limiting prevents abuse during high-volume events.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations — this section is empty.*
