# Quickstart: EDD Claims Assistant (007)

**Local Development Setup** — Get the EDD Claims Assistant running in mock mode (no Azure credentials required).

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.11+** (check: `python3 --version`)
- **Node.js 18+** (check: `node --version`)
- **npm 9+** (check: `npm --version`)
- **Git** (check: `git --version`)
- **8 GB RAM** minimum (backend + frontend + mock services)
- **Port 8007** available (backend API)
- **Port 5173** available (frontend dev server)

---

## Step 1: Clone Repository

```bash
cd /workspaces/ca-hackathon
# Repository should already be cloned if you're reading this file
```

---

## Step 2: Backend Setup

### Install Python Dependencies

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
cat > .env << 'EOF'
# Mock mode (no Azure credentials needed)
USE_MOCK_SERVICES=true

# API configuration
API_PORT=8007
API_HOST=0.0.0.0
CORS_ORIGINS=["http://localhost:5173"]

# Session configuration
SESSION_TIMEOUT_MINUTES=30
MAX_CONVERSATION_HISTORY=50

# Rate limiting (mock mode)
RATE_LIMIT_CHAT_PER_MINUTE=30
RATE_LIMIT_CLAIM_LOOKUP_PER_MINUTE=5
RATE_LIMIT_VOICE_PER_HOUR=10

# Mock data paths
MOCK_CLAIMS_PATH=mocks/edd_claims.json
MOCK_POLICIES_PATH=mocks/edd_policies.json
MOCK_ELIGIBILITY_RULES_PATH=mocks/edd_eligibility_rules.json

# Logging
LOG_LEVEL=INFO
LOG_PII_REDACTION=true

# Azure OpenAI (not used in mock mode, but required by config schema)
AZURE_OPENAI_ENDPOINT=https://mock.openai.azure.com
AZURE_OPENAI_KEY=mock-key-not-used
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure AI Search (not used in mock mode)
AZURE_SEARCH_ENDPOINT=https://mock.search.windows.net
AZURE_SEARCH_KEY=mock-key-not-used
AZURE_SEARCH_INDEX_NAME=edd-policies
EOF
```

### Verify Mock Data Files

Mock data should be pre-populated in `backend/mocks/`:

```bash
ls -lh backend/mocks/
# Expected files:
# edd_claims.json           (20+ sample claims)
# edd_policies.json         (50+ policy articles)
# edd_eligibility_rules.json (decision trees)
```

If files are missing, create them or copy from the accelerator template.

### Start Backend Server

```bash
# From backend/ directory with venv activated
uvicorn app.main:app --host 0.0.0.0 --port 8007 --reload
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8007 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     [Mock Mode] Using mock EDD claim service
INFO:     [Mock Mode] Using mock policy search service
INFO:     [Mock Mode] Using mock eligibility service
```

**Verify backend is running**:
```bash
curl http://localhost:8007/health
# Expected response:
# {"status":"healthy","service":"edd-claims-assistant","version":"1.0.0","timestamp":"..."}
```

---

## Step 3: Frontend Setup

Open a **new terminal** (keep backend running in the first terminal).

### Install Node Dependencies

```bash
cd frontend

# Install dependencies
npm install
```

### Configure Frontend Environment

Create `.env` file in `frontend/` directory:

```bash
cat > .env << 'EOF'
VITE_API_BASE_URL=http://localhost:8007
VITE_USE_MOCK_MODE=true
VITE_ENABLE_VOICE=true
VITE_VOICE_MOCK=true
EOF
```

### Start Frontend Dev Server

```bash
# From frontend/ directory
npm run dev
```

**Expected output**:
```
  VITE v5.0.0  ready in 1234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Open in browser**: http://localhost:5173/edd

---

## Step 4: Verify Mock Mode

### Test 1: Policy Q&A

**In browser** (http://localhost:5173/edd):
1. Type: "How do I file for unemployment insurance?"
2. Click **Send** or press Enter
3. **Expected**: Response with step-by-step UI filing instructions and policy citations

**Or via curl**:
```bash
curl -X POST http://localhost:8007/edd/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_001",
    "message": "How do I file for unemployment insurance?",
    "claim_type": "ui"
  }'
```

**Expected response**:
```json
{
  "session_id": "test_session_001",
  "response": "To file for Unemployment Insurance (UI) in California, you must:\n\n1. Have earned wages during your base period\n2. Be unemployed or working reduced hours through no fault of your own\n3. Be able and available to work\n4. Actively seek work each week\n\nYou can file online at edd.ca.gov/UI_Online or call 1-800-300-5616.",
  "citations": [
    {
      "title": "How to File for Unemployment Insurance Benefits",
      "url": "https://edd.ca.gov/en/Unemployment/Filing_a_Claim/",
      "effective_date": "2023-01-01"
    }
  ],
  "escalated": false,
  "timestamp": "..."
}
```

---

### Test 2: Claim Status Lookup

**Via curl**:
```bash
curl -X POST http://localhost:8007/edd/claim-status \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_002",
    "claim_id": "UI-2024-123456",
    "verification": {
      "last4_ssn": "1234",
      "date_of_birth": "1990-01-01"
    }
  }'
```

**Expected response**:
```json
{
  "claim_id": "UI-2024-123456",
  "type": "ui",
  "status": "approved",
  "filed_date": "2024-01-15",
  "weekly_benefit_amount": 450.00,
  "next_payment_date": "2024-04-10",
  "pending_issues": [],
  "required_actions": [
    "Complete bi-weekly certification by April 14"
  ],
  "total_paid": 5400.00,
  "claim_balance": 6300.00
}
```

**Note**: Mock mode has pre-seeded claims. Try these claim IDs:
- `UI-2024-123456` (approved)
- `DI-2024-789012` (pending with issues)
- `PFL-2024-555001` (denied)

---

### Test 3: Eligibility Pre-Screening

**Via curl**:
```bash
curl -X POST http://localhost:8007/edd/eligibility \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_003",
    "claim_type": "ui",
    "answers": {
      "worked_in_ca_last_18_months": true,
      "separation_reason": "laid_off",
      "employment_type": "w2_employee",
      "weekly_work_hours": 0
    }
  }'
```

**Expected response**:
```json
{
  "assessment_id": "assess_...",
  "claim_type": "ui",
  "result": "likely_eligible",
  "confidence_score": 0.85,
  "factors": [
    {
      "factor": "work_history",
      "meets_requirement": true,
      "explanation": "You worked in California within the last 18 months, meeting the base period requirement."
    }
  ],
  "recommended_action": "Proceed with filing your UI claim online at edd.ca.gov/UI_Online",
  "disclaimer": "This is a preliminary assessment. Final eligibility is determined by EDD after you file."
}
```

---

### Test 4: Voice Mode (Mock)

**In browser**:
1. Click the **microphone button** in the EDD Assistant UI
2. Browser will show "Voice mode is in mock mode" notification
3. Type a message in the voice input box (simulates spoken input)
4. Click **Send**
5. **Expected**: Assistant responds with text (no actual audio in mock mode)

**Note**: Real voice mode requires Azure OpenAI Realtime API credentials (not available in mock mode).

---

## Step 5: Run Tests

### Backend Tests

```bash
cd backend

# Unit tests
pytest tests/unit/ -v

# Integration tests (includes mock service tests)
pytest tests/integration/ -v

# Contract tests (API schema validation)
pytest tests/contract/ -v

# Full test suite
pytest -v
```

**Expected output**:
```
tests/unit/test_edd_claim_service.py::test_get_claim_status_mock PASSED
tests/unit/test_edd_policy_service.py::test_search_policies_mock PASSED
tests/integration/test_edd_claims_agent.py::test_claim_lookup_tool PASSED
...
==================== 42 passed in 12.34s ====================
```

---

### Frontend Tests

```bash
cd frontend

# Unit tests
npm run test

# E2E tests (requires backend running on port 8007)
npm run test:e2e
```

**Expected output**:
```
 ✓ src/components/edd/EDDChatInterface.test.tsx (5)
 ✓ src/components/edd/EDDClaimStatusCard.test.tsx (3)
 ✓ src/services/eddApiClient.test.ts (8)

 Test Files  3 passed (3)
      Tests  16 passed (16)
```

---

## Port Assignments

| Service | Port | URL |
|---------|------|-----|
| **Backend API** | 8007 | http://localhost:8007 |
| **Frontend** | 5173 | http://localhost:5173 |
| **Health Check** | 8007 | http://localhost:8007/health |

**Convention**: Accelerator 007 uses port **8007** (8000 + accelerator number).

---

## Common Troubleshooting

### Issue 1: Port 8007 Already in Use

**Error**:
```
OSError: [Errno 48] Address already in use
```

**Solution**:
```bash
# Find process using port 8007
lsof -i :8007
# Or on Linux:
netstat -tulnp | grep 8007

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --port 8008
# Update frontend .env: VITE_API_BASE_URL=http://localhost:8008
```

---

### Issue 2: Python Dependencies Not Installing

**Error**:
```
ERROR: Could not find a version that satisfies the requirement fastapi
```

**Solution**:
```bash
# Upgrade pip
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# If specific package fails, install individually
pip install fastapi pydantic semantic-kernel
```

---

### Issue 3: Mock Data Files Missing

**Error**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'backend/mocks/edd_claims.json'
```

**Solution**:
```bash
# Create mock data files
mkdir -p backend/mocks

# Copy from template (if available)
cp -r accelerators/007-edd-claims-assistant/mocks/* backend/mocks/

# Or create minimal mock files
cat > backend/mocks/edd_claims.json << 'EOF'
[
  {
    "claim_id": "UI-2024-123456",
    "claimant_id": "claimant_test",
    "type": "ui",
    "status": "approved",
    "filed_date": "2024-01-15",
    "weekly_benefit_amount": 450.00,
    "next_payment_date": "2024-04-10",
    "pending_issues": [],
    "required_actions": ["Complete bi-weekly certification by April 14"],
    "total_paid": 5400.00,
    "claim_balance": 6300.00
  }
]
EOF
```

---

### Issue 4: CORS Errors in Browser

**Error** (in browser console):
```
Access to fetch at 'http://localhost:8007/edd/chat' from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Solution**:
```bash
# Update backend/.env
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# Or in app/main.py, add:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Restart backend
```

---

### Issue 5: Frontend Not Connecting to Backend

**Error**:
```
Failed to fetch
```

**Solution**:
```bash
# 1. Verify backend is running
curl http://localhost:8007/health

# 2. Check frontend .env
cat frontend/.env
# VITE_API_BASE_URL should match backend URL

# 3. Check browser console for errors
# Open DevTools (F12) → Console tab

# 4. Restart frontend dev server
cd frontend
npm run dev
```

---

### Issue 6: Voice Mode Not Working

**Error**:
```
Voice API is unavailable
```

**Solution** (Mock Mode):
```bash
# 1. Verify frontend .env has voice mock enabled
cat frontend/.env
# VITE_VOICE_MOCK=true

# 2. Voice features are limited in mock mode (no real audio)
# For real voice, set up Azure OpenAI Realtime API credentials

# 3. If voice button is disabled, check browser console for errors
```

---

### Issue 7: Tests Failing

**Error**:
```
FAILED tests/integration/test_edd_claims_agent.py::test_claim_lookup - AssertionError
```

**Solution**:
```bash
# 1. Ensure backend is NOT running during tests (tests start their own server)
pkill -f uvicorn

# 2. Clear pytest cache
pytest --cache-clear

# 3. Run specific test with verbose output
pytest tests/integration/test_edd_claims_agent.py::test_claim_lookup -vv

# 4. Check mock data paths in test files match actual file locations
```

---

## Next Steps

1. **Explore the UI**: http://localhost:5173/edd
   - Try different claim types (UI, DI, PFL)
   - Test eligibility screening flow
   - Generate document checklists
   - Trigger escalation ("I need to speak to a person")

2. **Review Mock Data**: `backend/mocks/` — add more claims, policies, or eligibility rules for testing

3. **Read the Spec**: `specs/007-edd-claims-assistant/spec.md` — understand user stories P1-P6

4. **Check API Docs**: `specs/007-edd-claims-assistant/contracts/api.md` — full endpoint reference

5. **Run Full Test Suite**: `pytest && npm run test:e2e` — ensure all tests pass

6. **Enable Real Azure Services**: Update `.env` with actual Azure credentials (requires Azure subscription)

---

## Production Setup (Real Mode)

To run with real Azure services (not mock mode):

1. **Azure OpenAI**: Create Azure OpenAI resource, deploy GPT-4o model
2. **Azure AI Search**: Create search service, upload EDD policy index
3. **Azure Realtime API**: Enable Realtime API in Azure OpenAI
4. **Update `.env`**: Replace mock values with real Azure credentials
5. **Set `USE_MOCK_SERVICES=false`**
6. **Restart backend**

See `docs/azure-setup.md` for detailed Azure configuration instructions.

---

## Support

- **Issues**: https://github.com/ca-hackathon/accelerators/issues
- **Docs**: `/workspaces/ca-hackathon/docs/`
- **Spec**: `/workspaces/ca-hackathon/specs/007-edd-claims-assistant/`
