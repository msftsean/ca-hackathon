"""Pipeline — wires the 3-agent chain together."""

from app.agents.action_agent import ActionAgent
from app.agents.query_agent import QueryAgent
from app.agents.router_agent import RouterAgent
from app.models.schemas import ChatRequest, ChatResponse

query_agent = QueryAgent()
router_agent = RouterAgent()
action_agent = ActionAgent()


async def process_message(request: ChatRequest) -> ChatResponse:
    """Run the full QueryAgent -> RouterAgent -> ActionAgent pipeline."""
    query_result = await query_agent.process(request.message, request.document_id)
    routing = await router_agent.route(query_result)
    response = await action_agent.act(query_result, routing)

    return ChatResponse(
        response=response.response_text,
        confidence=response.confidence,
        citations=response.citations,
        compliance_data=response.data,
    )
