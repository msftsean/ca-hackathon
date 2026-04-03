# Quickstart Guide: BenefitsCal Navigator Agent

**Feature**: BenefitsCal Navigator Agent  
**Port**: 8001  
**Local Development URL**: `http://localhost:8001`

## Overview

This guide walks you through setting up the BenefitsCal Navigator Agent for local development. You'll run the backend API server, frontend UI, and test the system in mock mode (no Azure credentials required).

---

## Prerequisites

### Required Software

- **Python 3.11+** — Backend runtime
  ```bash
  python3 --version  # Should show 3.11 or higher
  ```

- **Node.js 18+** — Frontend runtime
  ```bash
  node --version  # Should show v18 or higher
  npm --version   # Should show 9 or higher
  ```

- **Git** — Version control
  ```bash
  git --version
  ```

### Optional (for Azure Integration)

- **Azure CLI** — For Azure deployment (not needed for mock mode)
- **Azure Developer CLI (azd)** — For infrastructure deployment

---

## Project Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/ca-hackathon.git
cd ca-hackathon
```

### 2. Install All Dependencies

From the repository root, run the convenience script:

```bash
npm run setup
```

This installs:
- Backend Python dependencies (`backend/requirements.txt`)
- Frontend Node dependencies (`frontend/package.json`)
- Shared dependencies

**Manual Installation (if npm run setup fails)**:

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..

# Frontend
cd frontend
npm install
cd ..
```

---

## Backend Setup (Port 8001)

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Activate Python Virtual Environment

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### 3. Set Environment Variables for Mock Mode

Create a `.env` file in the `backend/` directory:

```bash
# backend/.env
USE_MOCK_SERVICES=true
PORT=8001
LOG_LEVEL=info
DATABASE_URL=postgresql://localhost:5432/benefitscal_dev
REDIS_URL=redis://localhost:6379/0
```

**Important**: In mock mode, Azure credentials are not required. The system uses mock responses.

**Optional: Full Azure Integration (skip for mock mode)**

```bash
# Add these only if you have Azure credentials
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-api-key
AZURE_TRANSLATOR_KEY=your-translator-key
AZURE_TRANSLATOR_REGION=westus
```

### 4. Initialize Database (Optional for Mock Mode)

Mock mode works without PostgreSQL, but if you want to test database features:

```bash
# Start PostgreSQL (if installed locally)
# macOS:
brew services start postgresql

# Linux:
sudo systemctl start postgresql

# Create database
createdb benefitscal_dev

# Run migrations (if migrations exist)
alembic upgrade head
```

### 5. Start Backend Server

```bash
uvicorn src.api.main:app --reload --port 8001
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify Backend Health**:

Open a new terminal and test the health endpoint:

```bash
curl http://localhost:8001/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "benefitscal-navigator",
  "version": "1.0.0",
  "timestamp": "2026-02-02T14:30:00Z",
  "dependencies": {
    "azure_openai": "mock",
    "azure_search": "mock",
    "postgres": "healthy",
    "redis": "mock"
  },
  "mock_mode": true
}
```

---

## Frontend Setup (Port 3000)

### 1. Navigate to Frontend Directory

Open a **new terminal** (keep backend running):

```bash
cd frontend
```

### 2. Set Environment Variables

Create a `.env` file in the `frontend/` directory:

```bash
# frontend/.env
VITE_API_BASE_URL=http://localhost:8001
VITE_MOCK_MODE=true
```

### 3. Start Frontend Development Server

```bash
npm run dev
```

You should see:
```
  VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

### 4. Open in Browser

Navigate to `http://localhost:3000` in your browser. You should see the BenefitsCal Navigator interface.

---

## Testing Mock Mode

### Test 1: Health Check

```bash
curl http://localhost:8001/health
```

Expected: `"status": "healthy"`, `"mock_mode": true`

### Test 2: Create a Session

```bash
curl -X POST http://localhost:8001/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "web",
    "language": "en",
    "county": "Los Angeles"
  }'
```

Expected response:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "started_at": "2026-02-02T14:30:00Z",
  "channel": "web",
  "language": "en",
  "county": "Los Angeles"
}
```

Copy the `session_id` for the next test.

### Test 3: Ask a Question (Chat Endpoint)

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "query": "What are the income limits for CalFresh for a family of 3?",
    "language": "en"
  }'
```

Expected response (mock):
```json
{
  "query_id": "660e8400-e29b-41d4-a716-446655440111",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "For a family of 3 people in California, the gross monthly income limit for CalFresh is $2,495 (130% of the Federal Poverty Level). The net monthly income limit is $1,920 (100% FPL).",
  "intent": "eligibility_question",
  "confidence": 0.95,
  "language": "en",
  "citations": [...],
  "escalated": false
}
```

### Test 4: Eligibility Pre-Screening

```bash
curl -X POST http://localhost:8001/prescreening \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "household_size": 3,
    "monthly_income_total": 2200.00,
    "county": "Los Angeles",
    "has_child_under_18": true,
    "citizenship_status": "citizen",
    "currently_working": true
  }'
```

Expected response:
```json
{
  "profile_id": "880e8400-e29b-41d4-a716-446655440333",
  "results": {
    "calfresh": {
      "likely_eligible": true,
      "reason": "Gross income $2,200 is below limit $2,495 for household of 3"
    },
    "calworks": {
      "likely_eligible": false,
      "reason": "Income exceeds CalWORKs limits"
    },
    "general_relief": {
      "likely_eligible": false
    },
    "capi": {
      "likely_eligible": false
    }
  }
}
```

### Test 5: List Benefit Programs

```bash
curl http://localhost:8001/programs
```

Expected: JSON array of 4 programs (CalFresh, CalWORKs, General Relief, CAPI)

---

## Common Issues and Troubleshooting

### Issue: "Address already in use" on port 8001

**Cause**: Another process is using port 8001.

**Solution**:

```bash
# Find process using port 8001
lsof -i :8001  # macOS/Linux
netstat -ano | findstr :8001  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use a different port
uvicorn src.api.main:app --reload --port 8002
# Update frontend/.env: VITE_API_BASE_URL=http://localhost:8002
```

### Issue: "Module not found" errors in Python

**Cause**: Virtual environment not activated or dependencies not installed.

**Solution**:

```bash
cd backend
source venv/bin/activate  # Activate venv
pip install -r requirements.txt  # Reinstall dependencies
```

### Issue: Frontend shows "Network Error" or "Cannot connect to backend"

**Cause**: Backend not running or incorrect `VITE_API_BASE_URL`.

**Solution**:

1. Verify backend is running: `curl http://localhost:8001/health`
2. Check `frontend/.env`: `VITE_API_BASE_URL=http://localhost:8001` (no trailing slash)
3. Restart frontend dev server: `npm run dev`

### Issue: Database connection errors

**Cause**: PostgreSQL not running or incorrect `DATABASE_URL`.

**Solution** (for mock mode, database is optional):

```bash
# In backend/.env, comment out DATABASE_URL or set to in-memory SQLite
DATABASE_URL=sqlite:///./test.db
```

For full database support:
```bash
# Start PostgreSQL
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Linux

# Verify connection
psql -h localhost -U postgres -c "SELECT 1"
```

### Issue: Mock responses are too generic

**Cause**: Mock mode uses pre-scripted responses, not actual LLM.

**Solution**: For real LLM responses, configure Azure OpenAI credentials in `backend/.env` and set `USE_MOCK_SERVICES=false`.

### Issue: Voice endpoints return errors

**Cause**: Voice integration requires Azure OpenAI Realtime API (not available in mock mode).

**Solution**: Mock mode voice endpoints return mock WebRTC config but do not establish actual voice connections. For full voice testing, deploy to Azure with Realtime API credentials.

---

## Running Tests

### Backend Unit Tests

```bash
cd backend
source venv/bin/activate
pytest tests/unit -v
```

### Backend Integration Tests (requires running backend)

```bash
cd backend
source venv/bin/activate
pytest tests/integration -v
```

### Frontend Tests

```bash
cd frontend
npm run test
```

### Linting

```bash
# Backend (Python)
cd backend
ruff check .

# Frontend (TypeScript)
cd frontend
npm run lint
```

---

## Next Steps

### 1. Explore the UI

- Navigate to `http://localhost:3000`
- Try asking questions in the chat interface
- Test language switching (Spanish mock available)
- Submit eligibility pre-screening forms

### 2. Review API Documentation

See `specs/001-benefitscal-navigator/contracts/api.md` for full API reference.

### 3. Customize Mock Data

Edit mock responses:
- `backend/src/mocks/openai_responses.json` — Chat Q&A responses
- `backend/src/mocks/translations.json` — Spanish translations
- `shared/data/cdss-policy-manuals/` — Policy document excerpts

### 4. Deploy to Azure (Optional)

```bash
# Install Azure Developer CLI
curl -fsSL https://aka.ms/install-azd.sh | bash

# Login to Azure
azd auth login

# Deploy infrastructure and app
azd up
```

---

## Development Workflow

1. **Start backend**: `cd backend && uvicorn src.api.main:app --reload --port 8001`
2. **Start frontend**: `cd frontend && npm run dev`
3. **Make changes**: Edit code in `backend/src/` or `frontend/src/`
4. **Test changes**: Both servers auto-reload on file changes
5. **Run tests**: `pytest` (backend), `npm run test` (frontend)
6. **Commit**: `git add . && git commit -m "Your message"`

---

## Port Summary

| Service | Port | URL |
|---------|------|-----|
| **Backend API** | 8001 | `http://localhost:8001` |
| **Frontend UI** | 3000 | `http://localhost:3000` |
| **PostgreSQL** (optional) | 5432 | N/A |
| **Redis** (optional) | 6379 | N/A |

---

## Getting Help

- **API Documentation**: `specs/001-benefitscal-navigator/contracts/api.md`
- **Implementation Plan**: `specs/001-benefitscal-navigator/plan.md`
- **Data Model**: `specs/001-benefitscal-navigator/data-model.md`
- **Constitution**: `shared/constitution.md`
- **Workshop Labs**: `labs/00-setup.md` through `labs/07-deploy.md`

---

**Last Updated**: 2026-02-02  
**Questions?** Contact the backend team or open an issue in the repository.
