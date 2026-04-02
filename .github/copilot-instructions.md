- @azure Rule - Use Azure Best Practices: When generating code for Azure, running terminal commands for Azure, or performing operations related to Azure, invoke your `azure_development-get_best_practices` tool if available.

## California State AI Hackathon Accelerators Context

This repository contains **8 AI accelerators** for California state government agencies, based on the 3-agent pipeline pattern (QueryAgent → RouterAgent → ActionAgent). Each accelerator is spec-driven and constitution-governed.

### Key Conventions
- Use **spec-driven development**: write specs before code (see `.specify/templates/`)
- Follow the **constitution** in `shared/constitution.md` for agent boundaries and CA compliance
- All accelerators must comply with **EO N-12-23**, **EO N-5-26**, **SB 53**, **CCPA/CPRA**
- Labs 00–03 work in **mock mode** (no Azure needed); Labs 04+ require Azure credentials
- The squad agents (`.squad/agents/`) define role boundaries — respect them
- Use `npm run smoke-test` to validate changes quickly
- Each accelerator in `accelerators/` is independently deployable
- Shared governance files live in `shared/` (constitution, routing, schemas)

### Accelerator IDs
- 001: BenefitsCal Navigator (CDSS)
- 002: Wildfire Response Coordinator (CAL FIRE / Cal OES)
- 003: Medi-Cal Eligibility Agent (DHCS)
- 004: Permit Streamliner (OPR / HCD / DCA)
- 005: GenAI Procurement Compliance (CDT / DGS)
- 006: Cross-Agency Knowledge Hub (GovOps)
- 007: EDD Claims Assistant (EDD)
- 008: Multilingual Emergency Chatbot (Cal OES)