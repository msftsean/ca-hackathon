# 007 — EDD Claims Assistant

**Agency:** Employment Development Department (EDD)

## Problem Statement

EDD processes millions of Unemployment Insurance (UI), Disability Insurance (DI), and Paid Family Leave (PFL) claims annually. Claimants face long hold times, confusing eligibility criteria, and difficulty tracking claim status. The volume overwhelms call center staff, leading to delays and frustration for California workers who need timely assistance.

## Solution Overview

An AI-powered claims assistant that helps claimants check status, screen eligibility, and create support tickets. Uses the 3-agent pipeline (QueryAgent → RouterAgent → ActionAgent) to understand claim inquiries, route to the appropriate program (UI/DI/PFL), and deliver status updates or escalate to human agents. Supports voice-enabled interaction for phone channel integration.

## Quick Start

```bash
cd accelerators/007-edd-claims-assistant

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8007

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **Frontend:** React 18 / TypeScript / Vite / Tailwind CSS
- **AI:** Azure OpenAI (GPT-4o) / Azure AI Search
- **Voice:** Azure Speech Services
- **Compliance:** EO N-12-23, CCPA/CPRA, EDD data security standards

## Specification

See [../../specs/007-edd-claims-assistant/spec.md](../../specs/007-edd-claims-assistant/spec.md)
