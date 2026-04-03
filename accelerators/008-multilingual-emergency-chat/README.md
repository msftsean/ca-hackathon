# 008 — Multilingual Emergency Chatbot

**Agency:** California Governor's Office of Emergency Services (Cal OES)

## Problem Statement

During emergencies, non-English-speaking Californians face critical information gaps. Emergency alerts and safety instructions are often available only in English, leaving millions of residents unable to understand evacuation orders, shelter locations, or safety procedures. Low-bandwidth conditions during disasters further limit access to information.

## Solution Overview

A lightweight, multilingual emergency chatbot supporting 70+ languages via Azure Translator. Designed for low-bandwidth conditions with SMS gateway integration, it delivers emergency alerts, shelter information, and safety instructions in the user's preferred language. The 3-agent pipeline (QueryAgent → RouterAgent → ActionAgent) detects language, routes to emergency knowledge, and delivers translated responses optimized for SMS and limited connectivity.

## Quick Start

```bash
cd accelerators/008-multilingual-emergency-chat

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8008

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **Frontend:** React 18 / TypeScript / Vite / Tailwind CSS
- **AI:** Azure OpenAI (GPT-4o) / Azure Translator (70+ languages)
- **Channels:** SMS gateway, low-bandwidth web
- **Compliance:** EO N-12-23, FEMA IPAWS, ADA Section 508

## Specification

See [../../specs/008-multilingual-emergency-chat/spec.md](../../specs/008-multilingual-emergency-chat/spec.md)
