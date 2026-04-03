"""Pipeline — Wire QueryAgent → RouterAgent → ActionAgent."""

from app.agents.query_agent import QueryAgent
from app.agents.router_agent import RouterAgent
from app.agents.action_agent import ActionAgent
from app.models.schemas import ChatRequest, ChatResponse, Citation, ProgramInfo, EligibilityResult


class BenefitsCalPipeline:
    """Orchestrates the 3-agent pipeline for benefits queries."""

    def __init__(self) -> None:
        self.query_agent = QueryAgent()
        self.router_agent = RouterAgent()
        self.action_agent = ActionAgent()

    async def process(self, request: ChatRequest) -> ChatResponse:
        # Step 1: Query Agent — intent detection, entity extraction
        query = await self.query_agent.process(
            user_input=request.message,
            language=request.language,
            county=request.county,
        )

        # Step 2: Router Agent — department routing
        routing = await self.router_agent.route(query)

        # Step 3: Action Agent — response generation
        agent_response = await self.action_agent.execute(query, routing)

        # Build citations
        citations = agent_response.citations

        # Build program info if available
        programs: list[ProgramInfo] | None = None
        if agent_response.data and "program" in agent_response.data:
            prog_data = agent_response.data["program"]
            if isinstance(prog_data, dict) and "program_id" in prog_data:
                programs = [
                    ProgramInfo(
                        program_id=prog_data["program_id"],
                        name=prog_data["name"],
                        description=prog_data["description"],
                        agency=prog_data.get("agency", "CDSS"),
                        requirements=prog_data.get("requirements", []),
                        documents_needed=prog_data.get("documents_needed", []),
                    )
                ]

        # Build eligibility result if available
        eligibility: EligibilityResult | None = None
        if agent_response.data and "requirements" in agent_response.data:
            eligibility = EligibilityResult(
                program=agent_response.data.get("program", "Unknown"),
                likely_eligible=True,
                confidence=agent_response.confidence,
                factors=agent_response.data.get("requirements", [])[:3],
                next_steps=["Apply online at BenefitsCal.com", "Visit your county office"],
            )

        return ChatResponse(
            response=agent_response.response_text,
            confidence=agent_response.confidence,
            citations=citations,
            programs=programs,
            eligibility=eligibility,
        )
