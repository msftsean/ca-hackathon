# Implementation Plan: Wildfire Response Coordinator

**Branch**: `002-wildfire-response-coordinator` | **Date**: 2026-02-02 | **Spec**: [spec.md](./spec.md)

## Summary

The Wildfire Response Coordinator provides AI-assisted multi-agency coordination for California's #1 emergency threat. It automates lead agency mapping (Wildfire→CAL FIRE, Earthquake→Cal OES, Flood→DWR, HazMat→CHP), resource allocation across 6 Cal OES mutual aid regions, evacuation planning, weather/Red Flag Warning integration, and utility PSPS coordination. The system uses 47doors multi-agent pipeline with weather/traffic service plugins, Azure Maps for geospatial visualization, and MCP tools for CAL FIRE data feeds. It must comply with EO N-12-23 high-risk use case reporting (life-safety decisions) and Envision 2026 Goal 2 (security).

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, Pydantic v2, Semantic Kernel, Azure OpenAI SDK, Azure Maps SDK, Azure Communication Services  
**Storage**: PostgreSQL (incidents, resources, evacuations, PSPS events), Redis (real-time resource status, weather cache), Azure Maps (geospatial data)  
**Testing**: pytest (unit, integration), Playwright (E2E), Constitutional compliance test suite  
**Target Platform**: Linux containers (Docker), Azure Container Apps deployment  
**Project Type**: Web service (FastAPI backend + React frontend with map visualization)  
**Performance Goals**: <3s response time for 95% of coordinator actions, <10s for resource allocation recommendations, support 500 concurrent coordinators  
**Constraints**: <200ms p95 latency for resource queries, <5s for evacuation zone calculations, offline mode with cached data, Constitutional compliance logging  
**Scale/Scope**: 100+ concurrent incidents during peak fire season, 10,000+ resources tracked, 58 counties, 6 mutual aid regions, 3 major utilities

## Constitution Check

*Passing requirements based on `/workspaces/ca-hackathon/shared/constitution.md`:*

✅ **Principle I - Data Privacy & Security**: 
- No constituent PII in wildfire coordination system
- Incident data considered public information per California Emergency Services Act
- Secure communications for inter-agency coordination
- Access controls for incident command staff only

✅ **Principle II - Accessibility & Multilingual Access**: 
- Evacuation notifications in Spanish, Chinese, Vietnamese, Tagalog, Korean per Language Access requirements
- Web interface WCAG 2.1 AA compliant
- Plain language alerts for public-facing communications
- Text alternatives for map visualizations

✅ **Principle III - Equity & Bias Mitigation**: 
- Equal priority for all communities regardless of size or location
- Rural and urban areas receive equivalent evacuation planning support
- No assumptions about evacuation capability based on demographics
- Resource allocation based on objective criteria (fire behavior, threat to life, strategic value)

✅ **Principle IV - Graceful Escalation**: 
- High-risk decisions (evacuations, resource allocation during shortages) escalated to incident commanders
- System recommends but does not autonomously execute life-safety actions
- Conflicting priorities flagged for human decision-making
- Integration with emergency alert systems requires human approval

✅ **Principle V - Auditability & Transparency**: 
- All incident decisions logged with reasoning and data sources
- Resource deployments tracked for after-action reviews
- Weather data and fire behavior predictions preserved for analysis
- Support California Public Records Act requests for incident documentation

✅ **Executive Order N-12-23 High-Risk Use Case**: 
- Life-safety decisions (evacuations, resource allocation) flagged as high-risk
- Human-in-the-loop required for all evacuation orders and critical resource deployments
- Bias audits for resource allocation across counties and communities
- Regular reporting to California Department of Technology on high-risk AI decisions

**No violations requiring justification.**

## Project Structure

### Documentation (this feature)

```text
specs/002-wildfire-response-coordinator/
├── spec.md              # Feature specification (user stories, requirements, success criteria)
├── plan.md              # This implementation plan
└── data-model.md        # Entity definitions and data model
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── agents/
│   │   ├── incident_agent.py       # Incident classification and lead agency mapping
│   │   ├── resource_agent.py       # Resource allocation and deployment recommendations
│   │   ├── evacuation_agent.py     # Evacuation zone and route optimization
│   │   └── coordination_agent.py   # Multi-agency coordination and escalation
│   ├── models/
│   │   ├── incident.py             # Incident, IncidentTimeline models
│   │   ├── resource.py             # Resource, ResourceStatus models
│   │   ├── evacuation.py           # EvacuationZone, EvacuationRoute models
│   │   ├── weather.py              # WeatherCondition, RedFlagWarning models
│   │   ├── agency.py               # AgencyAssignment, MutualAidRegion models
│   │   └── psps.py                 # PSPSEvent, AffectedCircuit models
│   ├── services/
│   │   ├── lead_agency_mapper.py   # Lead agency determination logic
│   │   ├── mutual_aid_router.py    # Mutual aid region and resource routing
│   │   ├── resource_allocator.py   # Resource allocation engine
│   │   ├── evacuation_planner.py   # Evacuation zone and route optimization
│   │   ├── weather_service.py      # Weather API integration, Red Flag Warning ingestion
│   │   ├── fire_behavior_model.py  # Fire spread prediction based on weather
│   │   ├── azure_maps_service.py   # Azure Maps integration for geospatial operations
│   │   ├── psps_coordinator.py     # PSPS coordination with utilities
│   │   ├── alert_service.py        # Emergency alert system integration
│   │   └── compliance_logger.py    # Constitutional compliance and EO N-12-23 logging
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── incidents.py        # Incident CRUD and assessment endpoints
│   │   │   ├── resources.py        # Resource management and allocation endpoints
│   │   │   ├── evacuations.py      # Evacuation planning and notification endpoints
│   │   │   ├── weather.py          # Weather data and alert endpoints
│   │   │   ├── psps.py             # PSPS coordination endpoints
│   │   │   └── coordination.py     # Multi-agency coordination endpoints
│   │   ├── middleware/
│   │   │   ├── auth.py             # Azure Entra ID authentication
│   │   │   └── incident_access.py  # Incident-based access control
│   │   └── main.py                 # FastAPI application entry point
│   ├── plugins/
│   │   ├── calfire_mcp.py          # MCP tool for CAL FIRE data feeds
│   │   ├── weather_mcp.py          # MCP tool for weather APIs
│   │   └── traffic_mcp.py          # MCP tool for traffic data
│   └── config/
│       ├── settings.py             # Configuration (Azure, DB, mock mode, utilities)
│       ├── constitution.py         # Constitutional compliance rules
│       └── lead_agency_rules.py    # Lead agency mapping rules
└── tests/
    ├── unit/
    │   ├── test_incident_agent.py  # Incident classification tests
    │   ├── test_resource_allocator.py # Resource allocation logic tests
    │   ├── test_evacuation_planner.py # Evacuation planning tests
    │   └── test_fire_behavior.py   # Fire behavior model tests
    ├── integration/
    │   ├── test_incident_workflow.py # End-to-end incident management
    │   ├── test_weather_integration.py # Weather API integration tests
    │   ├── test_maps_integration.py # Azure Maps integration tests
    │   └── test_psps_coordination.py # PSPS workflow tests
    ├── constitutional/
    │   ├── test_high_risk_decisions.py # EO N-12-23 compliance tests
    │   ├── test_equity.py          # Resource allocation equity tests
    │   ├── test_accessibility.py   # Evacuation notification accessibility tests
    │   └── test_audit_logs.py      # Logging completeness tests
    └── e2e/
        ├── test_wildfire_scenario.py # End-to-end wildfire coordination
        ├── test_multi_incident.py  # Multiple concurrent incidents
        └── test_offline_mode.py    # Offline mode functionality

frontend/
├── src/
│   ├── components/
│   │   ├── IncidentMap.tsx         # Azure Maps incident visualization
│   │   ├── IncidentDashboard.tsx   # Incident overview and status
│   │   ├── ResourcePanel.tsx       # Resource management UI
│   │   ├── EvacuationPlanner.tsx   # Evacuation zone and route UI
│   │   ├── WeatherPanel.tsx        # Weather data and Red Flag Warnings
│   │   ├── PSPSCoordination.tsx    # PSPS event tracking
│   │   └── IncidentTimeline.tsx    # Incident timeline visualization
│   ├── pages/
│   │   ├── IncidentCommand.tsx     # Incident command center
│   │   ├── ResourceManagement.tsx  # Resource tracking and allocation
│   │   └── AfterAction.tsx         # After-action review and reporting
│   ├── services/
│   │   ├── apiClient.ts            # Backend API client
│   │   ├── mapsClient.ts           # Azure Maps client
│   │   └── realtimeClient.ts       # WebSocket for real-time updates
│   ├── hooks/
│   │   ├── useIncident.ts          # Incident state management
│   │   ├── useResources.ts         # Resource state management
│   │   ├── useWeather.ts           # Weather data management
│   │   └── useMap.ts               # Map interaction management
│   └── styles/
│       └── tailwind.config.ts      # Tailwind CSS (WCAG 2.1 AA compliant)
└── tests/
    └── accessibility/
        └── test_wcag.spec.ts       # Playwright WCAG 2.1 AA tests

shared/
├── constitution.md                 # California State AI Agent Constitution
└── data/
    ├── mutual-aid-regions/         # 6 Cal OES mutual aid region boundaries
    ├── fire-stations/              # CAL FIRE and county fire station locations
    ├── utility-service-areas/      # PG&E, SCE, SDG&E service territory maps
    └── evacuation-assembly-points/ # Pre-identified evacuation centers
```

**Structure Decision**: Web application structure (backend + frontend) selected because the Wildfire Response Coordinator requires both a FastAPI backend for agent orchestration, geospatial operations, and multi-agency coordination, and a React frontend with Azure Maps for incident command visualization. The `shared/` directory contains mutual aid region boundaries, fire station locations, and utility service areas used by evacuation planning and PSPS coordination.

## Complexity Tracking

> No Constitutional violations requiring justification.

| Tech Stack Layer | Technology | Rationale |
|------------------|------------|-----------|
| Backend Runtime | Python 3.11+ | Required for Semantic Kernel agent orchestration and geospatial calculations |
| Backend Framework | FastAPI | Async performance for real-time updates, WebSocket support for live resource tracking |
| AI/LLM | Azure OpenAI (GPT-4o) | Required for natural language coordination assistance and multi-agent orchestration |
| Geospatial | Azure Maps | Required for incident mapping, evacuation route optimization, and proximity calculations |
| Weather Integration | National Weather Service API | Required for Red Flag Warnings and real-time weather data |
| Traffic Data | California Highway Patrol / Caltrans APIs | Required for evacuation route traffic modeling |
| Communication | Azure Communication Services | Required for emergency alert integration and coordinator notifications |
| Frontend | React 18 + TypeScript 5 + Vite | Modern, accessible UI framework with WCAG 2.1 AA compliance |
| Styling | Tailwind CSS | Utility-first CSS for rapid accessible design |
| Testing | pytest + Playwright + vitest | Comprehensive unit, integration, E2E, and accessibility testing |
| IaC | Bicep | Azure-native infrastructure as code |
| Deployment | Docker + Azure Developer CLI | Containerized deployment to Azure Container Apps |
| CI/CD | GitHub Actions | Automated testing and deployment pipeline |
