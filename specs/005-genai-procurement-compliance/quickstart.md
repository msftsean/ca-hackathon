# Quickstart Guide: GenAI Procurement Compliance Checker

**Feature**: `005-genai-procurement-compliance`  
**Port**: 8005  
**Mode**: Backend API only (no frontend)

## Prerequisites

### Required Software

- **Python**: 3.11 or higher
- **pip**: 23.0 or higher (usually included with Python)
- **Git**: 2.40 or higher

### Optional (for Azure deployment)

- **Azure CLI**: 2.50 or higher
- **Docker**: 24.0 or higher (for containerization)

### Verify Installation

```bash
python3 --version  # Should show 3.11.x or higher
pip3 --version     # Should show 23.x or higher
git --version      # Should show 2.x or higher
```

## Quick Start (5 minutes)

### 1. Clone Repository

```bash
# Clone the repository (if not already done)
git clone https://github.com/california/ca-hackathon.git
cd ca-hackathon
```

### 2. Set Up Backend

```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Create .env file in backend directory
cat > .env << 'EOF'
# Mock mode (no Azure credentials needed)
USE_MOCK_SERVICES=true

# Application settings
APP_NAME=GenAI Procurement Compliance Checker
APP_VERSION=1.0.0
PORT=8005
LOG_LEVEL=INFO

# Mock data paths (automatically created)
MOCK_DATA_DIR=./mock-data
MOCK_ATTESTATIONS_DIR=./mock-data/attestations
MOCK_PARSED_DIR=./mock-data/parsed

# Database (async SQLite for mock mode)
DATABASE_URL=sqlite+aiosqlite:///./compliance.db

# Azure settings (not needed in mock mode, but kept for future)
# AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
# AZURE_OPENAI_API_KEY=your-api-key
# AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-turbo
# AZURE_BLOB_STORAGE_CONNECTION_STRING=your-connection-string
# AZURE_ENTRA_TENANT_ID=your-tenant-id
EOF
```

### 4. Initialize Mock Data

```bash
# Create mock data directories
mkdir -p mock-data/attestations mock-data/parsed mock-data/reports

# Download sample attestation documents (mock data)
# These files are pre-created for workshop/development
python -m src.scripts.init_mock_data
```

This script creates:
- `mock-data/compliance-rules.json` (EO N-5-26, SB 53, NIST AI RMF rules)
- `mock-data/compliance-results.json` (pre-computed compliance analysis)
- `mock-data/gap-analysis.json` (pre-computed gap analysis)
- `mock-data/attestations/vendor-a-complete.pdf` (compliant, score 95)
- `mock-data/attestations/vendor-b-gaps.pdf` (non-compliant, score 62)
- `mock-data/attestations/vendor-c-partial.docx` (partial, score 78)

### 5. Start Backend Server

```bash
# Start FastAPI server with auto-reload
uvicorn src.main:app --host 0.0.0.0 --port 8005 --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8005 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Mock mode enabled - using local mock data
```

Server is now running at: **http://localhost:8005**

## Verify Installation (Mock Mode)

### Test 1: Health Check

```bash
curl http://localhost:8005/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-12-19T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "azure_openai": "mock",
    "blob_storage": "mock"
  }
}
```

### Test 2: Upload Mock Attestation

```bash
# Upload vendor A attestation (compliant)
curl -X POST http://localhost:8005/attestations/upload \
  -F "file=@mock-data/attestations/vendor-a-complete.pdf" \
  -F "vendor_name=Acme AI Corporation" \
  -F "vendor_contact=compliance@acme-ai.com" \
  -F "procurement_id=RFP-2024-CDT-MOCK-001" \
  -F "assigned_to=john.doe@state.ca.gov"
```

Expected response (201 Created):
```json
{
  "attestation_id": "550e8400-e29b-41d4-a716-446655440000",
  "vendor_name": "Acme AI Corporation",
  "procurement_id": "RFP-2024-CDT-MOCK-001",
  "file_format": "PDF",
  "status": "uploaded",
  "analysis_url": "/attestations/550e8400-e29b-41d4-a716-446655440000/analyze"
}
```

### Test 3: Analyze Attestation (Mock)

```bash
# Trigger analysis (instant in mock mode)
curl -X POST http://localhost:8005/attestations/550e8400-e29b-41d4-a716-446655440000/analyze
```

Expected response (202 Accepted):
```json
{
  "attestation_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "analyzing",
  "analysis_started_at": "2024-12-19T10:35:00Z",
  "progress_url": "/attestations/550e8400-e29b-41d4-a716-446655440000/analysis-status"
}
```

In mock mode, analysis completes instantly. Check results:

```bash
curl http://localhost:8005/attestations/550e8400-e29b-41d4-a716-446655440000/results
```

Expected response (200 OK):
```json
{
  "attestation_id": "550e8400-e29b-41d4-a716-446655440000",
  "vendor_name": "Acme AI Corporation",
  "overall_score": 95,
  "compliance_summary": {
    "total_rules": 18,
    "compliant": 17,
    "partial": 1,
    "non_compliant": 0
  },
  "severity_breakdown": {
    "critical_gaps": 0,
    "high_gaps": 0,
    "medium_gaps": 1,
    "low_gaps": 0
  }
}
```

### Test 4: Gap Analysis

```bash
curl http://localhost:8005/attestations/550e8400-e29b-41d4-a716-446655440000/gaps
```

Expected response: Detailed gap analysis with remediation guidance.

### Test 5: Compare Vendors (Mock)

First, upload two more attestations (vendor B and C), then compare:

```bash
# Upload vendor B (non-compliant)
curl -X POST http://localhost:8005/attestations/upload \
  -F "file=@mock-data/attestations/vendor-b-gaps.pdf" \
  -F "vendor_name=BetaTech Solutions" \
  -F "procurement_id=RFP-2024-CDT-MOCK-001"

# Upload vendor C (partial)
curl -X POST http://localhost:8005/attestations/upload \
  -F "file=@mock-data/attestations/vendor-c-partial.docx" \
  -F "vendor_name=GammaAI Inc" \
  -F "procurement_id=RFP-2024-CDT-MOCK-001"

# Analyze both
curl -X POST http://localhost:8005/attestations/{vendor_b_id}/analyze
curl -X POST http://localhost:8005/attestations/{vendor_c_id}/analyze

# Compare all three
curl -X POST http://localhost:8005/compare \
  -H "Content-Type: application/json" \
  -d '{
    "procurement_id": "RFP-2024-CDT-MOCK-001",
    "attestation_ids": [
      "550e8400-e29b-41d4-a716-446655440000",
      "{vendor_b_id}",
      "{vendor_c_id}"
    ]
  }'
```

Expected response: Side-by-side comparison matrix with scores and recommendations.

## Switching to Azure Mode

When you're ready to test with real Azure services:

### 1. Update Environment Variables

Edit `backend/.env`:

```bash
# Disable mock mode
USE_MOCK_SERVICES=false

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-turbo
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure Blob Storage
AZURE_BLOB_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...

# Azure Document Intelligence (for OCR)
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-di-resource.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_API_KEY=your-di-key-here

# Azure Entra ID (authentication)
AZURE_ENTRA_TENANT_ID=your-tenant-id
AZURE_ENTRA_CLIENT_ID=your-client-id
```

### 2. Restart Server

```bash
# Stop server (Ctrl+C)
# Restart with new settings
uvicorn src.main:app --host 0.0.0.0 --port 8005 --reload
```

### 3. Test Azure Connection

```bash
curl http://localhost:8005/health
```

Should show `"azure_openai": "healthy"` instead of `"azure_openai": "mock"`.

## Running Tests

### Unit Tests

```bash
# From backend directory
pytest tests/unit -v
```

### Integration Tests

```bash
# Mock mode integration tests (no Azure needed)
pytest tests/integration -v --mock

# Azure integration tests (requires Azure credentials)
pytest tests/integration -v
```

### Contract Tests

```bash
# Verify API contracts match OpenAPI spec
pytest tests/contract -v
```

## Common Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'src'`

**Solution**: Ensure virtual environment is activated and dependencies installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: `Port 8005 already in use`

**Solution**: Either stop the existing process or use a different port:
```bash
# Find and kill process on port 8005
lsof -ti:8005 | xargs kill -9  # macOS/Linux
# Or use different port
uvicorn src.main:app --port 8006
```

### Issue: `Database is locked` (SQLite)

**Solution**: Async SQLite has file lock issues if multiple processes access DB:
```bash
# Stop all uvicorn processes
pkill -f uvicorn
# Restart single instance
uvicorn src.main:app --port 8005
```

### Issue: Mock data files not found

**Solution**: Re-run mock data initialization:
```bash
python -m src.scripts.init_mock_data
```

### Issue: Azure OpenAI quota exceeded

**Solution**: Check Azure portal quota settings or switch back to mock mode:
```bash
# In .env file
USE_MOCK_SERVICES=true
```

### Issue: File upload fails with 413 error

**Solution**: Check file size (max 50MB). If using Nginx/reverse proxy, update `client_max_body_size`:
```nginx
client_max_body_size 50M;
```

## API Documentation

Once server is running, access interactive API docs:

- **Swagger UI**: http://localhost:8005/docs
- **ReDoc**: http://localhost:8005/redoc
- **OpenAPI JSON**: http://localhost:8005/openapi.json

## Project Structure

```
backend/
├── src/
│   ├── main.py                      # FastAPI application entry point
│   ├── models/                      # Pydantic entity models
│   │   ├── vendor_attestation.py
│   │   ├── compliance_rule.py
│   │   └── compliance_result.py
│   ├── services/                    # Business logic services
│   │   ├── document_parser.py
│   │   ├── compliance_analyzer.py
│   │   ├── scoring_engine.py
│   │   └── gap_analyzer.py
│   ├── api/                         # API route handlers
│   │   ├── attestation_routes.py
│   │   ├── compliance_routes.py
│   │   └── audit_routes.py
│   ├── storage/                     # Data persistence
│   │   ├── blob_storage.py
│   │   └── db_client.py
│   └── scripts/                     # Utility scripts
│       └── init_mock_data.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── mock-data/                       # Mock mode data files
│   ├── compliance-rules.json
│   ├── compliance-results.json
│   └── attestations/
├── requirements.txt                 # Python dependencies
├── .env                             # Environment configuration
└── compliance.db                    # SQLite database (auto-created)
```

## Next Steps

1. **Explore API Documentation**: Visit http://localhost:8005/docs to see all endpoints
2. **Test Compliance Rules**: Review `mock-data/compliance-rules.json` to understand EO N-5-26, SB 53, NIST AI RMF requirements
3. **Customize Severity Weights**: Edit scoring logic in `src/services/scoring_engine.py`
4. **Add New Compliance Rules**: Update `shared/compliance-rules/*.json` and restart server
5. **Integrate with External Systems**: Use API endpoints to integrate with CaleProcure, FI$Cal
6. **Deploy to Azure**: Follow deployment guide in `docs/deployment.md`

## Development Workflow

```bash
# 1. Make code changes in src/
# 2. Server auto-reloads (if using --reload flag)
# 3. Test changes with curl or Swagger UI
# 4. Run unit tests
pytest tests/unit -v
# 5. Commit changes
git add .
git commit -m "Add feature X"
git push origin feature-branch
```

## Support

- **Documentation**: `/docs` folder in repository
- **API Issues**: Check `/attestations/{id}/analysis-status` for error details
- **Azure Setup**: See `docs/azure-setup.md`
- **Regulatory Questions**: Consult `shared/compliance-rules/*.json` comments

## Mock Mode vs Azure Mode Summary

| Feature | Mock Mode | Azure Mode |
|---------|-----------|------------|
| Credentials | None required | Azure keys/tokens |
| Analysis Speed | Instant (<100ms) | 2-5 minutes |
| Document Parsing | Pre-extracted text | pypdf + Document Intelligence |
| Compliance Scoring | Fixed scores | Real GPT-4 analysis |
| Audit Logging | In-memory | Persistent SQLite |
| Cost | Free | ~$0.10-0.50 per attestation |
| Use Case | Development, workshops, demos | Production, real procurements |

**Recommended**: Start with mock mode for development, switch to Azure for testing, deploy Azure mode for production.
