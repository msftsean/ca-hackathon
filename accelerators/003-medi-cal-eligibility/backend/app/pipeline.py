"""Pipeline orchestrator for Medi-Cal Eligibility Agent — 3-agent pipeline."""

from app.agents.query_agent import QueryAgent
from app.agents.router_agent import RouterAgent
from app.agents.action_agent import ActionAgent
from app.models.schemas import MediCalQuery, RoutingDecision, AgentResponse, ChatRequest, ChatResponse


class MediCalPipeline:
    """Orchestrates QueryAgent → RouterAgent → ActionAgent pipeline."""

    def __init__(self):
        self.query_agent = QueryAgent()
        self.router_agent = RouterAgent()
        self.action_agent = ActionAgent()

    async def process(self, request: ChatRequest) -> ChatResponse:
        """Run the full 3-agent pipeline."""
        # Step 1: Query Agent — intent detection & entity extraction
        query: MediCalQuery = await self.query_agent.process(request.message)

        # Inject application_id from request if provided
        if request.application_id:
            query.entities["application_id"] = request.application_id

        # Step 2: Router Agent — determine pathway and priority
        routing: RoutingDecision = await self.router_agent.route(query)

        # Step 3: Action Agent — generate response
        result: AgentResponse = await self.action_agent.execute(query, routing)

        return ChatResponse(
            response=result.response,
            confidence=result.confidence,
            citations=result.citations,
            eligibility=result.eligibility,
            application=result.application,
        )
