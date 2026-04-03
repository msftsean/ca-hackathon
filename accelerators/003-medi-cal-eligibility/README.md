# 003 — Medi-Cal Eligibility Agent

**Agency:** Department of Health Care Services (DHCS)

## Problem Statement

Medi-Cal eligibility determination requires manual review of income documents like W-2s, pay stubs, and tax returns—a slow, error-prone process that delays coverage for millions of Californians. HIPAA compliance requirements add complexity to document handling and data processing.

## Solution Overview

An AI-powered eligibility agent that uses Azure Document Intelligence to extract income data from uploaded documents, applies Pydantic-validated eligibility rules based on MAGI methodology, and generates determination recommendations. The 3-agent pipeline (QueryAgent → RouterAgent → ActionAgent) handles document intake, eligibility routing, and determination output with full HIPAA compliance.

## Quick Start

```bash
cd accelerators/003-medi-cal-eligibility

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8003

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **Frontend:** React 18 / TypeScript / Vite / Tailwind CSS
- **AI:** Azure OpenAI (GPT-4o) / Azure Document Intelligence
- **Compliance:** HIPAA, EO N-12-23, CCPA/CPRA, 42 CFR Part 2

## Specification

See [../../specs/003-medi-cal-eligibility/spec.md](../../specs/003-medi-cal-eligibility/spec.md)
