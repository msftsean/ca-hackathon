# Project Context

- **Owner:** msftsean
- **Project:** California State AI Hackathon Accelerators — 8 AI accelerators for California state government agencies
- **Stack:** Python 3.11+ / FastAPI 0.109+, TypeScript 5 / React 18, Azure OpenAI, Azure AI Search, Semantic Kernel, Azure Document Intelligence, Pydantic v2.5+
- **Architecture:** Three-agent pipeline (QueryAgent → RouterAgent → ActionAgent) deployed across 8 accelerators for CDSS, CAL FIRE, DHCS, OPR, CDT, GovOps, EDD, Cal OES
- **Governance:** EO N-12-23, EO N-5-26, SB 53, CCPA/CPRA compliance
- **Created:** 2026-03-13

## Learnings

- **2026-04-03 (Morpheus):** Phase B task generation for all 8 accelerators (commit d44b89c) provided actionable, dependency-ordered tasks that enabled Tank's 4-wave concurrent implementation to reach 100% test pass rate (503 tests). Task structure enforced by speckit-tasks.agent aligned teams on acceptance criteria, enabling parallelization. Constitution governance across all 8 accelerators proved effective — zero agency boundary conflicts, consistent CCPA/CPRA consent flows, EO N-12-23 compliance checks, emergency escalation rules. Key learning: spec-driven development from specs/ → tasks.md → concurrent implementation reduced rework and eliminated regressions.

- **2026-04-02 (Morpheus):** Rebranded CLAUDE.md and .github/copilot-instructions.md from 47 Doors university context to California State AI Hackathon Accelerators. Updated all project references, added 8 accelerator IDs with agency mappings, added CA governance context (EO N-12-23, N-5-26, SB 53, CCPA/CPRA), clarified architecture pattern and project structure for CA state deployments.

## Work Log

### 2026-03-13T18:46:00Z — Azure-First Spec Update (Morpheus)
Updated `specs/002-voice-interaction/spec.md` to prioritize Azure Container Apps as primary deployment target.

**Changes:**
- MVP scope: Added "Azure Container Apps deployment"
- VFR-026–029: Deployment requirements (Azure primary, local dev secondary, parity)
- Updated assumptions and dependencies to reflect Azure-first strategy
- Mock mode clarified as dev/test tool, not demo default

**Commit:** `71a91d6`

**Cross-agent impact:** Tank's Phase 1 deployment config must align with these requirements.
