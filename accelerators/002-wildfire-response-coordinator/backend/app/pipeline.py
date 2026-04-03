"""Pipeline orchestrator for Wildfire Response Coordinator — 3-agent pipeline."""

from app.agents.query_agent import QueryAgent
from app.agents.router_agent import RouterAgent
from app.agents.action_agent import ActionAgent
from app.models.schemas import IncidentQuery, RoutingDecision, AgentResponse, ChatRequest, ChatResponse


class WildfirePipeline:
    """Orchestrates QueryAgent → RouterAgent → ActionAgent pipeline."""

    def __init__(self):
        self.query_agent = QueryAgent()
        self.router_agent = RouterAgent()
        self.action_agent = ActionAgent()

    async def process(self, request: ChatRequest) -> ChatResponse:
        """Run the full 3-agent pipeline."""
        # Step 1: Query Agent — intent detection & entity extraction
        query: IncidentQuery = await self.query_agent.process(request.message)

        # Inject incident_id from request if provided
        if request.incident_id:
            query.entities["incident_id"] = request.incident_id

        # Step 2: Router Agent — determine module and priority
        routing: RoutingDecision = await self.router_agent.route(query)

        # Step 3: Action Agent — generate response
        result: AgentResponse = await self.action_agent.execute(query, routing)

        return ChatResponse(
            response=result.response,
            confidence=result.confidence,
            citations=result.citations,
            incident=result.incident,
            resources=result.resources,
            evacuation=result.evacuation,
        )
