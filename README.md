# 🏛️ California State AI Hackathon Accelerators

**Accelerating AI innovation for California state government — powered by the 3-agent pipeline pattern**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Azure](https://img.shields.io/badge/Azure-Ready-0078D4?style=flat&logo=microsoft-azure)](https://azure.microsoft.com)
[![CA Envision 2026](https://img.shields.io/badge/CA-Envision%202026-FDB515?style=flat)](https://innovation.ca.gov)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Overview

This repository contains **8 AI accelerators** built for California state agencies participating in the **California State Hackathon**. Each accelerator demonstrates practical AI solutions to improve public service delivery across diverse policy domains — from benefits navigation to emergency response.

**Key Features:**

- 🏗️ **3-Agent Pipeline Pattern**: QueryAgent → RouterAgent → ActionAgent architecture for reliable, governable AI
- 🎯 **Agency-Specific**: Each accelerator addresses real challenges for California state departments
- 📜 **Constitution-Driven**: All agent behavior governed by declarative policy in `constitution.md`
- 🔐 **Compliance-First**: Built to align with EO N-12-23, EO N-5-26, SB 53, and Envision 2026 strategy
- 🚀 **Standalone Projects**: Each accelerator can be developed and deployed independently
- 🛠️ **Shared Platform**: Common tech stack, governance framework, and deployment patterns

This work supports California's **Envision 2026** strategy, Executive Orders **N-12-23** (GenAI guidelines) and **N-5-26** (AI procurement), and the **Breakthrough Project** initiative for permitting modernization.

---

## 🎯 The 8 Accelerators

| # | Accelerator | Agency | Status | Description |
|---|-------------|--------|--------|-------------|
| 001 | BenefitsCal Navigator Agent | CDSS | 📋 Spec | Natural language Q&A for CalFresh, CalWORKs eligibility |
| 002 | Wildfire Response Coordinator | CAL FIRE / Cal OES | 📋 Spec | Multi-agent wildfire incident coordination |
| 003 | Medi-Cal Eligibility Agent | DHCS | 📋 Spec | Automated eligibility pre-determination |
| 004 | Permit Streamliner | OPR / HCD / DCA | 📋 Spec | Intelligent permit/license intake and routing |
| 005 | GenAI Procurement Compliance | CDT / DGS | 📋 Spec | AI vendor attestation review against EO N-5-26 |
| 006 | Cross-Agency Knowledge Hub | GovOps | 📋 Spec | Permission-aware federated search across 200+ agencies |
| 007 | EDD Claims Assistant | EDD | 📋 Spec | Natural language Q&A for UI/DI/PFL claims |
| 008 | Multilingual Emergency Chatbot | Cal OES | 📋 Spec | Emergency info in 70+ languages, SMS-capable |

Each accelerator lives in `specs/` with full specification, plan, and implementation artifacts.

---

## 🏗️ Architecture: The 3-Agent Pipeline Pattern


All accelerators follow a consistent three-agent architecture:

```
┌──────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│                (React + TypeScript + Tailwind)                   │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   QueryAgent     │  ← Analyzes user input
                    │   (GPT-4o)       │    Extracts intent & entities
                    └────────┬─────────┘    Validates against constitution
                             │
                             ▼
                    ┌──────────────────┐
                    │   RouterAgent    │  ← Determines action path
                    │   (Semantic      │    Routes to correct handler
                    │    Kernel)       │    Maintains session context
                    └────────┬─────────┘
                             │
                 ┌───────────┼──────────────┐
                 ▼           ▼              ▼
          ┌──────────┐ ┌──────────┐  ┌──────────┐
          │ RAG KB   │ │ API Call │  │ Escalate │  ← Action handlers
          │ Search   │ │ (SNOW,   │  │ to Human │    Execute intent
          │ (AI      │ │  CRM)    │  │          │    Log & audit
          │  Search) │ │          │  │          │
          └──────────┘ └──────────┘  └──────────┘
```

**Why Three Agents?**

1. **Separation of Concerns**: Each agent has a single, well-defined responsibility
2. **Governability**: Easier to audit, test, and control behavior at each stage
3. **Reusability**: Router logic and action handlers can be shared across accelerators
4. **Transparency**: Clear decision trails for compliance and debugging

**Shared Platform Code:**

All accelerators share common infrastructure in the `shared/` directory:
- `shared/platform/`: Core 3-agent orchestration engine
- `shared/ui-components/`: Reusable React components
- `shared/templates/`: Constitution and spec templates
- `shared/infra/`: Bicep modules for Azure deployment

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11+ / FastAPI / Pydantic v2 / Semantic Kernel |
| **Frontend** | React 18 / TypeScript 5 / Vite / Tailwind CSS |
| **AI/LLM** | Azure OpenAI (GPT-4o) + Azure AI Search (hybrid RAG) |
| **Voice** | Azure OpenAI Realtime API (WebRTC) |
| **Document AI** | Azure Document Intelligence |
| **Auth** | Azure Entra ID / MSAL |
| **Infrastructure** | Docker + docker-compose / Azure Developer CLI (azd) |
| **IaC** | Bicep |
| **Testing** | pytest + vitest + Playwright |
| **CI/CD** | GitHub Actions |
| **Governance** | Constitution-driven, EO N-12-23 / N-5-26 compliant |

---

## 🏁 Quick Start
# because the browser cannot reach localhost inside the container.
# VITE_API_BASE_URL=    <-- must be empty or unset

npm run dev
```

**⚠️ Important Codespaces Configuration:**

1. 🔓 **Make port 8000 public** for external access:

   ```bash
   gh codespace ports visibility 8000:public -c $CODESPACE_NAME
   ```

2. 🔗 **Get your Codespaces URLs** from the Ports tab in VS Code, or construct them:
   - 🎨 Frontend: `https://<codespace-name>-5173.app.github.dev`
   - 🔧 Backend: `https://<codespace-name>-8000.app.github.dev`
   - Your codespace name is in the environment variable `$CODESPACE_NAME`

3. ⚙️ **Update CORS configuration** in [backend/.env](backend/.env):

   ```bash
   CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","https://<your-codespace-name>-5173.app.github.dev"]
   ```

   Note: The backend config uses `validation_alias` to map `CORS_ORIGINS` from .env to the `allowed_origins` setting.

4. 🔄 **Restart the backend** after updating CORS settings to clear the settings cache.

5. ⚠️ **Frontend `.env` — Do NOT set `VITE_API_BASE_URL` to `http://localhost:8000`!**
   In Codespaces, the browser runs outside the container and cannot reach `localhost:8000`.
```bash
# 1. Open in GitHub Codespaces (recommended) or clone locally

# 2. Install dependencies
npm run setup

# 3. Start in mock mode (no Azure credentials needed)
npm start

# 4. Run smoke tests
npm run smoke-test
```

> **Mock mode** lets you develop and demo without Azure credentials. Perfect for prototyping and testing the 3-agent pipeline locally.

---

## 🏛️ California Governance & Compliance

This project is designed to align with California's emerging AI governance framework:

### 📜 Executive Orders & Legislation

- **EO N-12-23 (GenAI Guidelines for State Agencies)**: Establishes principles for responsible AI use in government, including transparency, accountability, and bias mitigation. Each accelerator's `constitution.md` codifies these principles into agent behavior.

- **EO N-5-26 (AI Procurement Requirements)**: Mandates AI vendor attestations for safety, security, and explainability. The **GenAI Procurement Compliance** accelerator (#005) automates review of vendor submissions against these requirements.

- **SB 53 (AI Safety)**: Requires state agencies to assess AI systems for risk and implement safeguards. All accelerators include risk assessments and guardrails in their specifications.

- **Breakthrough Project**: Governor's initiative to modernize permitting processes. The **Permit Streamliner** accelerator (#004) directly supports this goal with AI-powered intake and routing.

- **Envision 2026 Strategy**: CDT's vision for digital transformation across California government. These accelerators demonstrate practical AI implementations aligned with strategic goals.

### 🔐 Constitution-Driven Governance

Every accelerator includes a `constitution.md` file that defines:

- **Scope Boundaries**: What the agent can and cannot do
- **Safety Guardrails**: Red lines for sensitive topics (legal advice, medical diagnosis, etc.)
- **Equity Requirements**: Multilingual support, accessibility, plain language
- **Audit & Transparency**: All decisions logged with reasoning chains
- **Escalation Rules**: When to route to human staff

The constitution is **executable** — it's referenced in agent prompts and enforced at runtime, not just documentation.

**Example from BenefitsCal Navigator:**

```markdown
## Scope
- ✅ Provide eligibility criteria for CalFresh, CalWORKs, Medi-Cal
- ✅ Explain application processes and required documents
- ❌ Provide legal advice or represent applicants
- ❌ Make eligibility determinations (route to county staff)
```

---

## 📂 Project Structure

```
ca-hackathon/
├── specs/                          # Accelerator specifications
│   ├── 001-benefitscal-navigator/
│   │   ├── spec.md                 # Feature specification
│   │   ├── plan.md                 # Implementation plan
│   │   ├── tasks.md                # Task breakdown
│   │   └── constitution.md         # Governance rules
│   ├── 002-wildfire-coordinator/
│   └── ...
├── accelerators/                   # Implemented accelerators (TBD)
│   └── 001-benefitscal-navigator/
├── shared/                         # Shared platform code
│   ├── platform/                   # Core 3-agent engine
│   ├── ui-components/              # React component library
│   ├── templates/                  # Spec & constitution templates
│   └── infra/                      # Reusable Bicep modules
├── labs/                           # Hands-on learning labs
│   ├── 00-setup/
│   ├── 01-understanding-agents/
│   └── ...
├── backend/                        # FastAPI backend (reference impl)
│   ├── app/
│   │   ├── agents/                 # QueryAgent, RouterAgent, ActionAgent
│   │   ├── integrations/           # Azure OpenAI, AI Search, etc.
│   │   └── main.py
│   └── tests/
├── frontend/                       # React frontend (reference impl)
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.tsx
│   └── tests/
├── infra/                          # Bicep IaC for Azure deployment
└── docs/                           # Architecture diagrams, guides
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e

# Smoke test (validates 3-agent pipeline in mock mode)
npm run smoke-test
```

---

## 🚀 Deployment

Each accelerator can be deployed independently using Azure Developer CLI:

```bash
# Login to Azure
azd auth login

# Provision infrastructure + deploy code
azd up

# Update existing deployment
azd deploy
```

**What gets deployed:**
- Azure Container Apps (backend API)
- Azure Static Web Apps (frontend)
- Azure OpenAI (GPT-4o)
- Azure AI Search (knowledge base)
- Azure Cosmos DB (session storage)
- Azure Application Insights (monitoring)
- Azure Key Vault (secrets)

**Cost estimate**: ~$50-200/month per accelerator depending on usage (development tier)

---

## 🤝 Contributing

We welcome contributions from California state agency staff, vendors, and civic tech partners!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-accelerator`)
3. Follow the spec-driven workflow:
   - Write `spec.md` for your accelerator
   - Generate `plan.md` and `tasks.md` using the spec-kit
   - Implement following the plan
4. Run tests and linting
5. Submit a pull request

**Contribution Guidelines:**
- All code must align with EO N-12-23 principles
- Include a `constitution.md` for any new accelerator
- Add tests for new features
- Update documentation
- Use conventional commits

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

**Note**: This is open-source reference architecture. Agencies are responsible for compliance with state procurement, security, and privacy requirements when deploying to production.

---

## 📞 Contact & Support

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Architecture questions and best practices
- **CA CDT Innovation Team**: innovation@cdt.ca.gov

---

## 🙏 Acknowledgments

Built for the **California State Hackathon** by teams from:
- California Department of Technology (CDT)
- Government Operations Agency (GovOps)
- California Department of Social Services (CDSS)
- CAL FIRE / California Governor's Office of Emergency Services (Cal OES)
- Department of Health Care Services (DHCS)
- And many more California state agencies

**Powered by**: Azure OpenAI • Semantic Kernel • FastAPI • React • TypeScript

---

**🏛️ Built for California. By Californians. For all Californians.**
