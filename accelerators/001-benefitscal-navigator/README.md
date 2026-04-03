# 001 — BenefitsCal Navigator

**Agency:** California Department of Social Services (CDSS)

## Problem Statement

Millions of Californians struggle to understand their eligibility for public benefit programs like CalFresh, CalWORKs, and Medi-Cal. Call centers face long wait times and inconsistent responses, leaving vulnerable populations without timely assistance. Language barriers further compound access issues for non-English speakers.

## Solution Overview

An AI-powered conversational navigator that answers benefits eligibility questions across CalFresh, CalWORKs, Medi-Cal, and other CDSS programs. The system supports 8 languages and voice-enabled interaction, using the 3-agent pipeline (QueryAgent → RouterAgent → ActionAgent) to detect intent, route to the correct program knowledge base, and deliver accurate, citation-backed responses.

## Quick Start

```bash
# Clone and navigate
cd accelerators/001-benefitscal-navigator

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8001

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **Frontend:** React 18 / TypeScript / Vite / Tailwind CSS
- **AI:** Azure OpenAI (GPT-4o) / Azure AI Search
- **Compliance:** EO N-12-23, CCPA/CPRA, Section 508

## Specification

See [../../specs/001-benefitscal-navigator/spec.md](../../specs/001-benefitscal-navigator/spec.md)
