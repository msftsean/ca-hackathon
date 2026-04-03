"""Pipeline — Wire QueryAgent -> RouterAgent -> ActionAgent."""

from app.agents.query_agent import QueryAgent
from app.agents.router_agent import RouterAgent
from app.agents.action_agent import ActionAgent
from app.models.schemas import ChatRequest, ChatResponse


class PermitPipeline:
    """Orchestrates the 3-agent pipeline for permit queries."""

    def __init__(self) -> None:
        self.query_agent = QueryAgent()
        self.router_agent = RouterAgent()
        self.action_agent = ActionAgent()

    async def process(self, request: ChatRequest) -> ChatResponse:
        # Step 1: Query Agent
        query = await self.query_agent.process(request.message)

        # Step 2: Router Agent
        routing = await self.router_agent.route(query)

        # Step 3: Action Agent
        agent_response = await self.action_agent.execute(query, routing)

        return ChatResponse(
            response=agent_response.response_text,
            confidence=agent_response.confidence,
            citations=agent_response.citations,
            data=agent_response.data,
        )
