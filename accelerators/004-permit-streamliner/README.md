# 004 — Permit Streamliner

**Agency:** Office of Planning and Research (OPR) / Housing and Community Development (HCD) / Department of Consumer Affairs (DCA)

## Problem Statement

California's permitting process spans multiple agencies with inconsistent requirements, lengthy timelines, and opaque status tracking. Builders, developers, and homeowners face weeks of delays navigating overlapping jurisdictions. The state's housing crisis demands faster, more transparent permitting aligned with the Breakthrough Project initiative.

## Solution Overview

An AI-powered permit intake and routing system that validates applications, generates requirement checklists, routes to the correct jurisdiction, and tracks SLA compliance. The 3-agent pipeline (QueryAgent → RouterAgent → ActionAgent) handles intake parsing, jurisdiction routing, and checklist/status generation to accelerate the permitting process.

## Quick Start

```bash
cd accelerators/004-permit-streamliner

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8004

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **Frontend:** React 18 / TypeScript / Vite / Tailwind CSS
- **AI:** Azure OpenAI (GPT-4o) / Azure AI Search
- **Compliance:** EO N-12-23, Breakthrough Project, CEQA

## Specification

See [../../specs/004-permit-streamliner/spec.md](../../specs/004-permit-streamliner/spec.md)
