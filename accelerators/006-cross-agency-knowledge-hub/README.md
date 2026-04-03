# 006 — Cross-Agency Knowledge Hub

**Agency:** Government Operations Agency (GovOps)

## Problem Statement

California state employees across 200+ departments waste significant time searching for policies, procedures, and institutional knowledge spread across siloed systems. Inconsistent naming, duplicated documents, and lack of cross-agency search make it difficult to find authoritative information, leading to inconsistent policy application.

## Solution Overview

A federated search platform that provides agency-scoped access to policies, procedures, and knowledge across California state government. Uses hybrid search (BM25 + semantic) with role-based access controls to deliver relevant results while respecting agency boundaries. The 3-agent pipeline (QueryAgent → RouterAgent → ActionAgent) handles query understanding, agency routing, and result synthesis.

## Quick Start

```bash
cd accelerators/006-cross-agency-knowledge-hub

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8006

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **Frontend:** React 18 / TypeScript / Vite / Tailwind CSS
- **AI:** Azure OpenAI (GPT-4o) / Azure AI Search (hybrid BM25 + semantic)
- **Compliance:** EO N-12-23, CCPA/CPRA, agency RBAC

## Specification

See [../../specs/006-cross-agency-knowledge-hub/spec.md](../../specs/006-cross-agency-knowledge-hub/spec.md)
