"""Pipeline — Wire QueryAgent → RouterAgent → ActionAgent."""

from app.agents.query_agent import QueryAgent
from app.agents.router_agent import RouterAgent
from app.agents.action_agent import ActionAgent
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ClaimStatus,
    DocumentItem,
    EligibilityAssessment,
)


class EDDClaimsPipeline:
    """Orchestrates the 3-agent pipeline for EDD claims queries."""

    def __init__(self) -> None:
        self.query_agent = QueryAgent()
        self.router_agent = RouterAgent()
        self.action_agent = ActionAgent()

    async def process(self, request: ChatRequest) -> ChatResponse:
        query = await self.query_agent.process(
            user_input=request.message,
            language=request.language,
        )

        routing = await self.router_agent.route(query)

        agent_response = await self.action_agent.execute(query, routing)

        claim_status: ClaimStatus | None = None
        eligibility: EligibilityAssessment | None = None
        document_checklist: list[DocumentItem] | None = None

        if agent_response.data:
            if "claim_status" in agent_response.data and agent_response.data["claim_status"]:
                cs = agent_response.data["claim_status"]
                claim_status = ClaimStatus(**cs) if isinstance(cs, dict) else cs

            if "eligibility" in agent_response.data:
                ea = agent_response.data["eligibility"]
                eligibility = EligibilityAssessment(**ea) if isinstance(ea, dict) else ea

            if "document_checklist" in agent_response.data:
                dc = agent_response.data["document_checklist"]
                document_checklist = [
                    DocumentItem(**d) if isinstance(d, dict) else d
                    for d in dc
                ]

        return ChatResponse(
            response=agent_response.response_text,
            confidence=agent_response.confidence,
            citations=agent_response.citations,
            claim_status=claim_status,
            eligibility=eligibility,
            document_checklist=document_checklist,
        )
