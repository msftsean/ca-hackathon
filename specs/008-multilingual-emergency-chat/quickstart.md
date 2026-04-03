# Quickstart: Multilingual Emergency Chatbot (008)

**Local Development Setup** — Get the Multilingual Emergency Chatbot running in mock mode (no Azure credentials required).

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.11+** (check: `python3 --version`)
- **Node.js 18+** (check: `node --version`)
- **npm 9+** (check: `npm --version`)
- **Git** (check: `git --version`)
- **6 GB RAM** minimum (backend + frontend + mock services)
- **Port 8008** available (backend API)
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
API_PORT=8008
API_HOST=0.0.0.0
CORS_ORIGINS=["http://localhost:5173"]

# Rate limiting (mock mode)
RATE_LIMIT_WEB_PER_MINUTE=30
RATE_LIMIT_SMS_PER_HOUR=10
RATE_LIMIT_TRANSLATION_PER_MINUTE=50

# Mock data paths
MOCK_ALERTS_PATH=mocks/emergency_alerts.json
MOCK_SHELTERS_PATH=mocks/shelters.json
MOCK_EVACUATION_PATH=mocks/evacuation_orders.json
MOCK_AQI_PATH=mocks/air_quality.json
MOCK_TRANSLATIONS_PATH=mocks/translations.json

# Translation caching
TRANSLATION_CACHE_TTL_HOURS=24
TRANSLATION_CACHE_ENABLED=true

# Logging
LOG_LEVEL=INFO

# Azure OpenAI (not used in mock mode, but required by config schema)
AZURE_OPENAI_ENDPOINT=https://mock.openai.azure.com
AZURE_OPENAI_KEY=mock-key-not-used
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure Translator (not used in mock mode)
AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com
AZURE_TRANSLATOR_KEY=mock-key-not-used
AZURE_TRANSLATOR_REGION=westus2

# Azure AI Search (not used in mock mode)
AZURE_SEARCH_ENDPOINT=https://mock.search.windows.net
AZURE_SEARCH_KEY=mock-key-not-used
AZURE_SEARCH_INDEX_NAME=emergency-alerts

# Azure Communication Services SMS (not used in mock mode)
AZURE_COMM_SERVICES_CONNECTION_STRING=mock-connection-string
AZURE_COMM_SERVICES_PHONE_NUMBER=+18005551234
EOF
```

### Verify Mock Data Files

Mock data should be pre-populated in `backend/mocks/`:

```bash
ls -lh backend/mocks/
# Expected files:
# emergency_alerts.json      (20+ alerts)
# shelters.json              (100+ shelters)
# evacuation_orders.json     (10+ zones)
# air_quality.json           (50+ AQI stations)
# translations.json          (common phrases in 3 languages)
```

If files are missing, create them or copy from the accelerator template.

### Start Backend Server

```bash
# From backend/ directory with venv activated
uvicorn app.main:app --host 0.0.0.0 --port 8008 --reload
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8008 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     [Mock Mode] Using mock alert service
INFO:     [Mock Mode] Using mock shelter service
INFO:     [Mock Mode] Using mock AQI service
INFO:     [Mock Mode] Using mock translation service (3 languages)
```

**Verify backend is running**:
```bash
curl http://localhost:8008/health
# Expected response:
# {"status":"healthy","service":"multilingual-emergency-chat","version":"1.0.0","timestamp":"..."}
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
VITE_API_BASE_URL=http://localhost:8008
VITE_USE_MOCK_MODE=true
VITE_DEFAULT_LANGUAGE=en
VITE_ENABLE_LOW_BANDWIDTH_MODE=true
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

**Open in browser**: http://localhost:5173/emergency

---

## Step 4: Verify Mock Mode

### Test 1: Alert Lookup

**In browser** (http://localhost:5173/emergency):
1. Enter ZIP code: `94102`
2. Select language: **English**
3. Click **Get Alerts**
4. **Expected**: Air quality alert displayed with details

**Or via curl**:
```bash
curl -X POST http://localhost:8008/emergency/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "location": "94102",
    "language": "en"
  }'
```

**Expected response**:
```json
{
  "location": "94102",
  "alerts": [
    {
      "alert_id": "aqi_sf_20260402_002",
      "type": "air_quality",
      "severity": "warning",
      "area": "San Francisco Bay Area",
      "title": "Unhealthy Air Quality - Wildfire Smoke",
      "message": "Air quality is unhealthy due to smoke from regional wildfires. Limit outdoor activity. Use N95 masks if you must go outside.",
      "issued_at": "2026-04-02T08:00:00Z",
      "expires_at": "2026-04-03T20:00:00Z",
      "source": "Bay Area AQMD",
      "last_updated": "2026-04-02T16:00:00Z"
    }
  ],
  "language": "en",
  "timestamp": "..."
}
```

---

### Test 2: Shelter Search

**Via curl**:
```bash
curl -X POST http://localhost:8008/emergency/shelters \
  -H "Content-Type: application/json" \
  -d '{
    "location": "90405",
    "max_distance_miles": 10,
    "filters": {
      "ada_accessible": true,
      "pets_allowed": true
    },
    "language": "en"
  }'
```

**Expected response**:
```json
{
  "location": "90405",
  "shelters": [
    {
      "shelter_id": "shelter_la_redcross_001",
      "name": "Red Cross Emergency Shelter - Santa Monica HS",
      "address": "601 Pico Blvd, Santa Monica, CA",
      "city": "Santa Monica",
      "zip_code": "90405",
      "distance_miles": 0.8,
      "capacity_current": 85,
      "capacity_max": 150,
      "is_at_capacity": false,
      "services": ["ada_accessible", "pets_allowed", "food_service", "charging_stations"],
      "hours": "24/7",
      "contact_phone": "310-555-0199",
      "notes": "Pets must be in crates. Bring vaccination records. Limited medical supplies available.",
      "capacity_last_updated": "2026-04-02T16:30:00Z",
      "is_open": true
    }
  ],
  "language": "en",
  "timestamp": "..."
}
```

---

### Test 3: AQI Lookup

**Via curl**:
```bash
curl -X POST http://localhost:8008/emergency/aqi \
  -H "Content-Type: application/json" \
  -d '{
    "location": "San Francisco",
    "language": "en"
  }'
```

**Expected response**:
```json
{
  "location": "San Francisco - Downtown",
  "aqi": 165,
  "category": "unhealthy",
  "pm25": 85.0,
  "pm10": 110.0,
  "ozone": 45.0,
  "health_guidance": "Everyone should reduce prolonged or heavy outdoor exertion. People with respiratory conditions, children, and older adults should avoid outdoor activity.",
  "forecast": "AQI expected to remain Unhealthy (150-200) through tonight. Improvement expected tomorrow morning.",
  "monitoring_station": "San Francisco - 4th Street Station",
  "updated_at": "2026-04-02T16:00:00Z",
  "source": "PurpleAir",
  "language": "en"
}
```

---

### Test 4: Evacuation Status

**Via curl**:
```bash
curl -X POST http://localhost:8008/emergency/evacuation-status \
  -H "Content-Type: application/json" \
  -d '{
    "location": "90290",
    "language": "en"
  }'
```

**Expected response**:
```json
{
  "location": "90290",
  "status": "voluntary",
  "zone": "Topanga Canyon - Zone B",
  "issued_at": "2026-04-02T14:30:00Z",
  "expires_at": null,
  "recommended_routes": ["Highway 1 South"],
  "road_closures": ["Topanga Canyon Blvd (north of PCH)"],
  "shelter_ids": ["shelter_la_redcross_001"],
  "instructions": "Voluntary evacuation recommended. Prepare to leave if conditions worsen. Monitor local news.",
  "source": "LA County Fire Department",
  "language": "en",
  "last_updated": "2026-04-02T15:45:00Z"
}
```

---

### Test 5: Translation (Spanish)

**Via curl**:
```bash
curl -X POST http://localhost:8008/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Where is the nearest shelter?",
    "target_language": "es"
  }'
```

**Expected response** (mock mode returns canned translations):
```json
{
  "original_text": "Where is the nearest shelter?",
  "translated_text": "¿Dónde está el refugio más cercano?",
  "source_language": "en",
  "target_language": "es",
  "cached": false
}
```

**Note**: Mock mode supports 3 languages (English, Spanish, Chinese). Real mode supports 70+ languages via Azure Translator.

---

### Test 6: Chat Interface

**In browser**:
1. Click on **Chat** tab
2. Type: "What's the air quality in San Francisco?"
3. Click **Send**
4. **Expected**: Assistant responds with AQI data and health guidance

**Or via curl**:
```bash
curl -X POST http://localhost:8008/emergency/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_001",
    "message": "What is the air quality in San Francisco?",
    "language": "en"
  }'
```

**Expected response**:
```json
{
  "session_id": "test_session_001",
  "response": "The air quality in San Francisco is Unhealthy (AQI: 165). Everyone should reduce prolonged outdoor activity. People with respiratory conditions, children, and older adults should avoid outdoor activity.",
  "data": {
    "aqi": 165,
    "category": "unhealthy",
    "location": "San Francisco - Downtown"
  },
  "language": "en",
  "timestamp": "..."
}
```

---

### Test 7: Low-Bandwidth Mode

**In browser**:
1. Visit: http://localhost:8008/emergency-low?location=94102
2. **Expected**: Server-rendered HTML page with alerts (no JavaScript, inline CSS only)
3. Page size: <50 KB
4. Works on slow connections (2G)

---

## Step 5: Run Tests

### Backend Tests

```bash
cd backend

# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Full test suite
pytest -v
```

**Expected output**:
```
tests/unit/test_alert_service.py::test_get_alerts_mock PASSED
tests/unit/test_shelter_service.py::test_search_shelters_mock PASSED
tests/unit/test_translation_service.py::test_translate_mock PASSED
tests/integration/test_emergency_agent.py::test_alert_lookup_tool PASSED
...
==================== 35 passed in 10.12s ====================
```

---

### Frontend Tests

```bash
cd frontend

# Unit tests
npm run test

# E2E tests (requires backend running on port 8008)
npm run test:e2e
```

**Expected output**:
```
 ✓ src/components/emergency/EmergencyAlertCard.test.tsx (4)
 ✓ src/components/emergency/ShelterList.test.tsx (5)
 ✓ src/services/emergencyApiClient.test.ts (7)

 Test Files  3 passed (3)
      Tests  16 passed (16)
```

---

## Port Assignments

| Service | Port | URL |
|---------|------|-----|
| **Backend API** | 8008 | http://localhost:8008 |
| **Frontend** | 5173 | http://localhost:5173 |
| **Health Check** | 8008 | http://localhost:8008/health |
| **Low-Bandwidth Mode** | 8008 | http://localhost:8008/emergency-low |

**Convention**: Accelerator 008 uses port **8008** (8000 + accelerator number).

---

## Common Troubleshooting

### Issue 1: Port 8008 Already in Use

**Error**:
```
OSError: [Errno 48] Address already in use
```

**Solution**:
```bash
# Find process using port 8008
lsof -i :8008
# Or on Linux:
netstat -tulnp | grep 8008

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --port 8009
# Update frontend .env: VITE_API_BASE_URL=http://localhost:8009
```

---

### Issue 2: Mock Data Files Missing

**Error**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'backend/mocks/emergency_alerts.json'
```

**Solution**:
```bash
# Create mock data files
mkdir -p backend/mocks

# Create minimal mock file
cat > backend/mocks/emergency_alerts.json << 'EOF'
[
  {
    "alert_id": "fire_la_20260402_001",
    "type": "fire",
    "severity": "urgent",
    "area": "Los Angeles County - Topanga Canyon area",
    "title": "Wildfire Warning - Topanga Canyon Fire",
    "message": "A fast-moving wildfire has been reported in Topanga Canyon. Residents in the area should prepare for possible evacuation.",
    "issued_at": "2026-04-02T14:30:00Z",
    "expires_at": null,
    "source": "LA County Fire Department",
    "affected_zip_codes": ["90290", "90265", "90272"],
    "last_updated": "2026-04-02T15:45:00Z"
  }
]
EOF
```

---

### Issue 3: Translation Not Working

**Error**:
```
Translation unavailable
```

**Solution** (Mock Mode):
```bash
# 1. Verify mock translations file exists
cat backend/mocks/translations.json

# 2. Mock mode only supports 3 languages (en, es, zh-Hans)
# For other languages, use real Azure Translator (not available in mock)

# 3. Check backend logs for translation errors
tail -f backend/logs/app.log
```

---

### Issue 4: CORS Errors in Browser

**Error** (in browser console):
```
Access to fetch at 'http://localhost:8008/emergency/alerts' from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Solution**:
```bash
# Update backend/.env
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

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
curl http://localhost:8008/health

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

### Issue 6: Low-Bandwidth Mode Not Loading

**Error**:
```
404 Not Found
```

**Solution**:
```bash
# 1. Verify backend route exists
curl http://localhost:8008/emergency-low?location=94102

# 2. Check backend logs for template errors
tail -f backend/logs/app.log

# 3. Ensure Jinja2 templates exist
ls backend/app/templates/emergency_low.html
```

---

### Issue 7: SMS Not Working (Mock Mode)

**Note**: SMS features are limited in mock mode (no real SMS gateway).

**Solution**:
```bash
# 1. Mock mode simulates SMS via HTTP endpoint
curl -X POST http://localhost:8008/sms/inbound \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+14155551234",
    "to": "+18005551234",
    "message": "What shelters are near 90405?",
    "messageId": "msg_test123",
    "timestamp": "2026-04-02T16:20:00Z"
  }'

# 2. For real SMS, set up Azure Communication Services (not available in mock)
```

---

## Next Steps

1. **Explore the UI**: http://localhost:5173/emergency
   - Try different locations (ZIP codes, cities)
   - Test language switching (English, Spanish, Chinese in mock mode)
   - Search for shelters with filters (ADA, pets)
   - Check evacuation status

2. **Review Mock Data**: `backend/mocks/` — add more alerts, shelters, or AQI stations for testing

3. **Read the Spec**: `specs/008-multilingual-emergency-chat/spec.md` — understand user stories P1-P7

4. **Check API Docs**: `specs/008-multilingual-emergency-chat/contracts/api.md` — full endpoint reference

5. **Run Full Test Suite**: `pytest && npm run test:e2e` — ensure all tests pass

6. **Enable Real Azure Services**: Update `.env` with actual Azure credentials (requires Azure subscription)

---

## Production Setup (Real Mode)

To run with real Azure services (not mock mode):

1. **Azure OpenAI**: Create Azure OpenAI resource, deploy GPT-4o-mini model
2. **Azure Translator**: Create Azure Translator resource (supports 70+ languages)
3. **Azure AI Search**: Create search service, upload emergency alert index
4. **Azure Communication Services**: Create SMS resource, provision phone number
5. **Update `.env`**: Replace mock values with real Azure credentials
6. **Set `USE_MOCK_SERVICES=false`**
7. **Restart backend**

See `docs/azure-setup.md` for detailed Azure configuration instructions.

---

## Support

- **Issues**: https://github.com/ca-hackathon/accelerators/issues
- **Docs**: `/workspaces/ca-hackathon/docs/`
- **Spec**: `/workspaces/ca-hackathon/specs/008-multilingual-emergency-chat/`
