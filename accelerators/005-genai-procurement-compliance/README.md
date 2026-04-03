# 005 — GenAI Procurement Compliance

**Agency:** California Department of Technology (CDT) / Department of General Services (DGS)

## Problem Statement

Executive Order N-5-26 requires vendor attestation and compliance scoring for all state GenAI procurements, but reviews are manual, inconsistent, and slow. Procurement officers lack tooling to systematically evaluate vendor compliance against state requirements, leading to delays and risk exposure.

## Solution Overview

A backend-only API and CLI tool that automates vendor attestation review and compliance scoring against EO N-5-26, SB 53, and CDT procurement standards. The 3-agent pipeline (QueryAgent → RouterAgent → ActionAgent) parses attestation documents, routes to relevant compliance frameworks, and generates structured compliance scores with remediation guidance. No frontend — designed for integration into existing procurement workflows.

## Quick Start

```bash
cd accelerators/005-genai-procurement-compliance

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8005

# Test the API
curl http://localhost:8005/health
```

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **AI:** Azure OpenAI (GPT-4o) / Azure AI Search
- **Compliance:** EO N-5-26, SB 53, CDT procurement standards, SIMM 5300

## Specification

See [../../specs/005-genai-procurement-compliance/spec.md](../../specs/005-genai-procurement-compliance/spec.md)
