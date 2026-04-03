# California State AI Hackathon Accelerators — Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-02

## Active Technologies

- Python 3.11+ (backend), TypeScript 5 (frontend), Node.js 18+ + FastAPI 0.109+, Pydantic v2.5+, React 18, Azure OpenAI, Azure AI Search, Semantic Kernel, Azure Document Intelligence

## Project Structure

```text
specs/          # Feature specifications (speckit-driven)
accelerators/   # Individual accelerator projects
shared/         # Shared constitution, routing, schemas
backend/        # Core platform backend
frontend/       # Core platform frontend
labs/           # Workshop labs
infra/          # Bicep IaC templates
```

## Commands

- `npm run setup` — Install all dependencies
- `npm start` — Start in mock mode
- `npm run smoke-test` — Run smoke tests
- `cd backend && python -m pytest -x` — Run backend tests
- `cd frontend && npm run test` — Run frontend tests
- `ruff check .` — Lint Python code

## Code Style

- Python: Follow PEP 8, use type hints, Pydantic v2 models
- TypeScript: Strict mode, React functional components with hooks
- All agents must comply with shared/constitution.md

## California Governance Context

This project implements AI accelerators for California state agencies under:
- **EO N-12-23**: GenAI guidelines for state agencies
- **EO N-5-26**: AI procurement and vendor attestation requirements
- **SB 53**: AI safety legislation
- **CCPA/CPRA**: California consumer privacy
- **Envision 2026**: California's digital government strategy
- **Breakthrough Project**: Permitting modernization initiative

## Architecture Pattern

All accelerators follow the 3-agent pipeline:
1. **QueryAgent**: Intent detection, entity extraction, PII filtering
2. **RouterAgent**: Agency routing, priority setting, escalation triggers
3. **ActionAgent**: Knowledge retrieval, ticket creation, response formatting

## Recent Changes

- Rebranded from 47doors university context to California state government
- Added specs for 8 CA state accelerators
- Updated constitution for CA compliance (EO N-12-23, N-5-26, SB 53, CCPA/CPRA)

## Azure Deployment

### Full Deployment
```bash
azd up                              # Provision infrastructure + deploy all services
azd provision                       # Provision infrastructure only
azd deploy                          # Deploy all services to existing infrastructure
```

### Selective Deployment
```bash
./scripts/azd-deploy.sh all         # Deploy everything
./scripts/azd-deploy.sh platform    # Deploy core platform only
./scripts/azd-deploy.sh 001         # Deploy specific accelerator
azd deploy accel-001                # Deploy accelerator backend directly
azd deploy accel-001-fe             # Deploy accelerator frontend directly
```

### Local Accelerator Development
```bash
docker-compose -f docker-compose.accelerators.yml up              # Run all accelerators
docker-compose -f docker-compose.accelerators.yml up accel-001-backend  # Run single accelerator
docker-compose -f docker-compose.accelerators.yml up --build      # Rebuild and run
```

### Port Mapping (Local)
| Service | Backend Port | Frontend Port |
|---------|-------------|---------------|
| Core Platform | 8000 | 3000 |
| Accelerator 001 | 8001 | 3001 |
| Accelerator 002 | 8002 | 3002 |
| Accelerator 003 | 8003 | 3003 |
| Accelerator 004 | 8004 | 3004 |
| Accelerator 005 | 8005 | — |
| Accelerator 006 | 8006 | 3006 |
| Accelerator 007 | 8007 | 3007 |
| Accelerator 008 | 8008 | 3008 |
