- @azure Rule - Use Azure Best Practices: When generating code for Azure, running terminal commands for Azure, or performing operations related to Azure, invoke your `azure_development-get_best_practices` tool if available.

## California Hackathon Accelerator Context

This repository is a **hackathon accelerator** based on the 47 Doors three-agent AI system. Teams use the spec kit (`.specify/`) and labs (`labs/`) to rapidly build, extend, and demo agentic AI solutions for university student support.

### Key Conventions
- Use **spec-driven development**: write specs before code (see `.specify/templates/`)
- Follow the **constitution** in `.specify/memory/constitution.md` for agent boundaries
- Labs 00–03 work in **mock mode** (no Azure needed); Labs 04+ require Azure credentials
- The squad agents (`.squad/agents/`) define role boundaries — respect them
- Use `npm run smoke-test` to validate changes quickly