# 002 — Wildfire Response Coordinator

**Agency:** CAL FIRE / California Governor's Office of Emergency Services (Cal OES)

## Problem Statement

California faces increasingly severe wildfire seasons, with multiple simultaneous incidents requiring rapid coordination across agencies. Incident commanders need real-time intelligence on resource allocation, weather conditions, and evacuation routing, but current systems are fragmented and manual. Delayed information sharing costs lives and property.

## Solution Overview

An AI-powered emergency coordination assistant that aggregates wildfire incident data, optimizes resource allocation, and generates evacuation routing recommendations. Uses the 3-agent pipeline (QueryAgent → RouterAgent → ActionAgent) to process situation reports, route to specialized response modules, and deliver actionable intelligence to incident commanders.

## Quick Start

```bash
cd accelerators/002-wildfire-response-coordinator

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8002

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **Frontend:** React 18 / TypeScript / Vite / Tailwind CSS
- **AI:** Azure OpenAI (GPT-4o) / Azure AI Search
- **Data:** CAL FIRE incident feeds, NWS weather data
- **Compliance:** EO N-12-23, FEMA ICS standards

## Specification

See [../../specs/002-wildfire-response-coordinator/spec.md](../../specs/002-wildfire-response-coordinator/spec.md)
