"""Pipeline — Wire QueryAgent → RouterAgent → ActionAgent."""

from app.agents.query_agent import QueryAgent
from app.agents.router_agent import RouterAgent
from app.agents.action_agent import ActionAgent
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    CrossReference,
    DocumentResult,
    ExpertInfo,
)


class KnowledgeHubPipeline:
    """Orchestrates the 3-agent pipeline for knowledge queries."""

    def __init__(self) -> None:
        self.query_agent = QueryAgent()
        self.router_agent = RouterAgent()
        self.action_agent = ActionAgent()

    async def process(self, request: ChatRequest) -> ChatResponse:
        query = await self.query_agent.process(
            user_input=request.message,
            agency_filter=request.agency_filter,
            document_types=request.document_types,
        )

        routing = await self.router_agent.route(query)

        agent_response = await self.action_agent.execute(query, routing)

        documents: list[DocumentResult] | None = None
        experts: list[ExpertInfo] | None = None
        cross_references: list[CrossReference] | None = None

        if agent_response.data:
            if "documents" in agent_response.data:
                doc_list = agent_response.data["documents"]
                documents = [
                    DocumentResult(**d) if isinstance(d, dict) else d
                    for d in doc_list
                ]
            if "experts" in agent_response.data:
                exp_list = agent_response.data["experts"]
                experts = [
                    ExpertInfo(**e) if isinstance(e, dict) else e
                    for e in exp_list
                ]
            if "cross_references" in agent_response.data:
                ref_list = agent_response.data["cross_references"]
                cross_references = [
                    CrossReference(**r) if isinstance(r, dict) else r
                    for r in ref_list
                ]

        return ChatResponse(
            response=agent_response.response_text,
            confidence=agent_response.confidence,
            citations=agent_response.citations,
            documents=documents,
            experts=experts,
            cross_references=cross_references,
        )
