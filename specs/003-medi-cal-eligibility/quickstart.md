# Quickstart: Medi-Cal Eligibility Agent

**Accelerator**: 003-medi-cal-eligibility  
**Agency**: Department of Health Care Services (DHCS)  
**Port**: 8003 (backend), 5173 (frontend dev server)  
**Mode**: Mock services enabled by default (no Azure credentials needed)

---

## Prerequisites

### Required Software

- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher
- **PostgreSQL**: 15 or higher (or use Docker Compose)
- **Redis**: 7.x or higher (or use Docker Compose)
- **Git**: For cloning repository

### Verify Installations

```bash
python --version   # Should show 3.11+
node --version     # Should show v18.x
npm --version      # Should show 9.x
psql --version     # Should show 15.x
redis-cli --version # Should show 7.x
```

---

## Quick Start (Docker Compose - Recommended)

The fastest way to get started is using Docker Compose, which handles all dependencies:

### 1. Clone Repository

```bash
git clone https://github.com/your-org/ca-hackathon.git
cd ca-hackathon
```

### 2. Start All Services

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- Backend API (port 8003)
- Frontend dev server (port 5173)

### 3. Verify Health

```bash
curl http://localhost:8003/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

### 4. Open Frontend

Navigate to: `http://localhost:5173`

You should see the Medi-Cal Eligibility Agent interface.

### 5. Stop Services

```bash
docker-compose down
```

---

## Manual Setup (Without Docker)

If you prefer to run services manually or need to develop/debug:

### Backend Setup

#### 1. Navigate to Backend Directory

```bash
cd backend
```

#### 2. Create Python Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Set Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/medi_cal_dev
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=medi_cal_dev

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Mock Mode (no Azure credentials needed)
USE_MOCK_SERVICES=true

# Application Settings
PORT=8003
LOG_LEVEL=INFO
ENVIRONMENT=development

# Security (generate your own for production)
SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256

# Azure Services (not needed in mock mode, but required for production)
# AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com
# AZURE_OPENAI_API_KEY=your-api-key
# AZURE_OPENAI_DEPLOYMENT=gpt-4o
# AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-doc-intel.cognitiveservices.azure.com
# AZURE_DOCUMENT_INTELLIGENCE_API_KEY=your-api-key
# AZURE_STORAGE_ACCOUNT_NAME=your-storage-account
# AZURE_STORAGE_ACCOUNT_KEY=your-storage-key
```

#### 5. Set Up PostgreSQL Database

Start PostgreSQL server, then create database:

```bash
# Using psql
psql -U postgres -c "CREATE DATABASE medi_cal_dev;"

# Or using createdb
createdb -U postgres medi_cal_dev
```

#### 6. Run Database Migrations

```bash
# Install Alembic (if not already in requirements.txt)
pip install alembic

# Run migrations
alembic upgrade head
```

Or if migrations aren't set up yet, create tables manually:

```bash
python -m app.scripts.init_db
```

#### 7. Start Redis

```bash
# macOS (using Homebrew)
brew services start redis

# Linux (using systemd)
sudo systemctl start redis

# Or run in foreground
redis-server
```

#### 8. Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8003 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### 9. Verify Backend Health

```bash
curl http://localhost:8003/health
```

---

### Frontend Setup

#### 1. Navigate to Frontend Directory

Open a new terminal (keep backend running), then:

```bash
cd frontend
```

#### 2. Install Dependencies

```bash
npm install
```

This installs React, TypeScript, Vite, and all other dependencies.

#### 3. Set Environment Variables

Create `.env` file in `frontend/` directory:

```bash
VITE_API_BASE_URL=http://localhost:8003
VITE_USE_MOCK_AUTH=true
VITE_ENVIRONMENT=development
```

#### 4. Start Frontend Dev Server

```bash
npm run dev
```

You should see:
```
VITE v5.0.8  ready in 342 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
➜  press h + enter to show help
```

#### 5. Open Frontend

Navigate to: `http://localhost:5173`

---

## Mock Mode Verification

Mock mode is enabled by default (`USE_MOCK_SERVICES=true`). This allows full testing without Azure credentials.

### Test Document Upload (Mock)

```bash
# Create a sample W-2 file (or use any PDF)
echo "Sample W-2 for testing" > sample_w2.pdf

# Upload document
curl -X POST http://localhost:8003/api/v1/documents/upload \
  -H "Content-Type: multipart/form-data" \
  -F "application_id=00000000-0000-0000-0000-000000000001" \
  -F "document_type=w2" \
  -F "file=@sample_w2.pdf"
```

Expected response:
```json
{
  "document_id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
  "processing_status": "extracted",
  "message": "Document uploaded successfully (MOCK MODE).",
  "extracted_data": {
    "tax_year": 2025,
    "employer_name": "ACME Corporation",
    "box_1_wages": 42500.00,
    "box_2_federal_tax_withheld": 3825.50
  }
}
```

### Test Eligibility Screening (Mock)

```bash
curl -X POST http://localhost:8003/api/v1/eligibility/screen \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "00000000-0000-0000-0000-000000000001",
    "income_records": [
      {
        "source": "wages",
        "amount": 1500.00,
        "frequency": "monthly"
      }
    ],
    "household_size": 1,
    "program": "Medi-Cal MAGI Adult"
  }'
```

Expected response (eligible):
```json
{
  "eligible": true,
  "magi_income": 18000.00,
  "fpl_percentage": 109.0,
  "fpl_threshold": 138.0,
  "explanation": "Based on your annual income of $18,000 and household size of 1, your income is 109% of the Federal Poverty Level. This is below the 138% FPL threshold for Medi-Cal, so you are likely eligible for no-cost Medi-Cal coverage."
}
```

### Test Status Query (Mock)

```bash
curl -X POST http://localhost:8003/api/v1/status/query \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "00000000-0000-0000-0000-000000000001",
    "query": "What is the status of my application?"
  }'
```

Expected response:
```json
{
  "response": "Your application is currently in mock mode. In production, you would receive real-time status updates from the county eligibility system.",
  "application_status": "draft"
}
```

---

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_eligibility.py

# Run tests matching pattern
pytest -k "test_magi"
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode (re-runs on file changes)
npm run test:watch
```

---

## Common Troubleshooting

### Port 8003 Already in Use

```bash
# Find process using port
lsof -i :8003

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --reload --port 8004
# Update VITE_API_BASE_URL in frontend/.env to http://localhost:8004
```

### PostgreSQL Connection Failed

Check if PostgreSQL is running:

```bash
# macOS
brew services list | grep postgresql

# Linux
sudo systemctl status postgresql

# Check if database exists
psql -U postgres -l | grep medi_cal_dev
```

If database doesn't exist:

```bash
createdb -U postgres medi_cal_dev
```

### Redis Connection Failed

Start Redis:

```bash
# macOS
brew services start redis

# Linux
sudo systemctl start redis

# Check if running
redis-cli ping
# Should return: PONG
```

### Python Module Not Found

Make sure virtual environment is activated:

```bash
# Check if (venv) appears in prompt
which python  # Should point to venv/bin/python

# If not activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### Frontend API Calls Failing (CORS)

Check `VITE_API_BASE_URL` in `frontend/.env`:

```bash
# Should be:
VITE_API_BASE_URL=http://localhost:8003

# NOT:
VITE_API_BASE_URL=http://localhost:8003/  # Trailing slash causes issues
```

Backend CORS is configured for `http://localhost:5173`. If running frontend on different port:

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Add your port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Database Migration Errors

Reset database and re-run migrations:

```bash
# Drop and recreate database
dropdb -U postgres medi_cal_dev
createdb -U postgres medi_cal_dev

# Re-run migrations
alembic upgrade head
```

### Mock Mode Not Working

Verify `USE_MOCK_SERVICES=true` in `backend/.env`:

```bash
cd backend
cat .env | grep USE_MOCK_SERVICES
# Should show: USE_MOCK_SERVICES=true
```

Restart backend server after changing `.env`:

```bash
# Stop server (Ctrl+C)
# Restart
uvicorn app.main:app --reload --port 8003
```

---

## Next Steps

### Explore the Application

1. **Create Application**: Use frontend to create a new Medi-Cal application
2. **Upload Documents**: Test W-2 and pay stub upload with mock OCR extraction
3. **Check Eligibility**: Run eligibility screening with different income levels
4. **Query Status**: Use natural language status query interface

### Run Smoke Tests

```bash
cd backend
npm run smoke-test
```

This validates all core endpoints are working.

### Enable Azure Services (Optional)

To test with real Azure AI services:

1. Provision Azure resources (see `infra/README.md`)
2. Update `backend/.env` with Azure credentials
3. Set `USE_MOCK_SERVICES=false`
4. Restart backend server

### Read Documentation

- **API Contract**: `specs/003-medi-cal-eligibility/contracts/api.md`
- **Data Model**: `specs/003-medi-cal-eligibility/data-model.md`
- **Tech Research**: `specs/003-medi-cal-eligibility/research.md`
- **Full Spec**: `specs/003-medi-cal-eligibility/spec.md`
- **Implementation Plan**: `specs/003-medi-cal-eligibility/plan.md`

---

## Support

For issues or questions:

- **Project Lead**: Sean Gayle
- **GitHub Issues**: https://github.com/your-org/ca-hackathon/issues
- **Slack**: #003-medi-cal-eligibility channel

---

**Happy coding! 🚀**
