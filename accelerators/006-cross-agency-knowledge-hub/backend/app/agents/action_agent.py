"""ActionAgent — Retrieves knowledge and generates citation-backed responses."""

from app.models.schemas import (
    AgentResponse,
    Citation,
    CrossReference,
    DocumentResult,
    ExpertInfo,
    RoutingDecision,
    SearchQuery,
)
from app.services.mock_service import MockKnowledgeService


class ActionAgent:
    """Generates responses using mock agency knowledge bases."""

    def __init__(self) -> None:
        self.service = MockKnowledgeService()

    async def execute(
        self, query: SearchQuery, routing: RoutingDecision
    ) -> AgentResponse:
        intent = query.intent

        if intent == "policy_search":
            return self._handle_policy_search(query)
        elif intent == "document_lookup":
            return self._handle_document_lookup(query)
        elif intent == "expert_search":
            return self._handle_expert_search(query)
        elif intent == "cross_reference":
            return self._handle_cross_reference(query)
        elif intent == "agency_info":
            return self._handle_agency_info(query)
        else:
            return self._handle_general(query)

    def _handle_policy_search(self, query: SearchQuery) -> AgentResponse:
        docs = self.service.search_documents(
            keywords=query.keywords,
            agencies=query.agencies,
            document_types=query.document_types or ["policy", "regulation"],
        )
        if not docs:
            return self._handle_general(query)

        doc_summaries = []
        citations = []
        for doc in docs[:5]:
            doc_summaries.append(f"• {doc.title} ({doc.agency}): {doc.summary}")
            citations.append(Citation(
                source=doc.title,
                text=doc.summary,
                agency=doc.agency,
                document_id=doc.doc_id,
            ))

        return AgentResponse(
            intent="policy_search",
            response_text=(
                f"Found {len(docs)} policy document(s) matching your query:\n\n"
                + "\n".join(doc_summaries)
            ),
            confidence=0.92,
            citations=citations,
            data={
                "documents": [d.model_dump() for d in docs[:5]],
                "total_results": len(docs),
            },
        )

    def _handle_document_lookup(self, query: SearchQuery) -> AgentResponse:
        docs = self.service.search_documents(
            keywords=query.keywords,
            agencies=query.agencies,
            document_types=query.document_types,
        )
        if not docs:
            return self._handle_general(query)

        citations = [
            Citation(
                source=doc.title,
                text=doc.summary,
                agency=doc.agency,
                document_id=doc.doc_id,
            )
            for doc in docs[:5]
        ]

        return AgentResponse(
            intent="document_lookup",
            response_text=(
                f"Found {len(docs)} document(s):\n\n"
                + "\n".join(
                    f"• [{doc.doc_id}] {doc.title} — {doc.agency} ({doc.document_type})"
                    for doc in docs[:5]
                )
            ),
            confidence=0.88,
            citations=citations,
            data={"documents": [d.model_dump() for d in docs[:5]]},
        )

    def _handle_expert_search(self, query: SearchQuery) -> AgentResponse:
        experts = self.service.find_experts(
            keywords=query.keywords,
            agencies=query.agencies,
        )
        if not experts:
            return AgentResponse(
                intent="expert_search",
                response_text="No experts found matching your criteria. Try broadening your search.",
                confidence=0.5,
                citations=[],
            )

        expert_lines = []
        for exp in experts[:5]:
            areas = ", ".join(exp.expertise_areas[:3])
            expert_lines.append(
                f"• {exp.name} ({exp.agency}, {exp.department}) — {areas}"
            )

        return AgentResponse(
            intent="expert_search",
            response_text=(
                f"Found {len(experts)} expert(s):\n\n" + "\n".join(expert_lines)
            ),
            confidence=0.85,
            citations=[
                Citation(source="Agency Directory", text=f"Expert: {e.name}", agency=e.agency)
                for e in experts[:3]
            ],
            data={"experts": [e.model_dump() for e in experts[:5]]},
        )

    def _handle_cross_reference(self, query: SearchQuery) -> AgentResponse:
        refs = self.service.get_cross_references(
            keywords=query.keywords,
            agencies=query.agencies,
        )
        if not refs:
            return AgentResponse(
                intent="cross_reference",
                response_text="No cross-references found for the specified documents.",
                confidence=0.5,
                citations=[],
            )

        ref_lines = []
        for ref in refs[:5]:
            ref_lines.append(
                f"• {ref.source_doc_id} → {ref.target_doc_id}: "
                f"{ref.relationship} — {ref.description}"
            )

        return AgentResponse(
            intent="cross_reference",
            response_text=(
                f"Found {len(refs)} cross-reference(s):\n\n" + "\n".join(ref_lines)
            ),
            confidence=0.87,
            citations=[
                Citation(
                    source="Cross-Reference Index",
                    text=ref.description,
                    document_id=ref.source_doc_id,
                )
                for ref in refs[:3]
            ],
            data={"cross_references": [r.model_dump() for r in refs[:5]]},
        )

    def _handle_agency_info(self, query: SearchQuery) -> AgentResponse:
        permissions = self.service.get_agency_permissions()
        agency_lines = [
            f"• {p.agency_code}: {p.agency_name} — Departments: {', '.join(p.departments[:3])}"
            for p in permissions[:5]
        ]
        return AgentResponse(
            intent="agency_info",
            response_text=(
                "California state agencies in the Knowledge Hub:\n\n"
                + "\n".join(agency_lines)
            ),
            confidence=0.90,
            citations=[
                Citation(
                    source="Agency Directory",
                    text="California state agency listing",
                    agency="GovOps",
                )
            ],
            data={"agencies": [p.model_dump() for p in permissions]},
        )

    def _handle_general(self, query: SearchQuery) -> AgentResponse:
        docs = self.service.search_documents(
            keywords=query.keywords,
            agencies=query.agencies,
            document_types=query.document_types,
        )
        if docs:
            citations = [
                Citation(
                    source=doc.title,
                    text=doc.summary,
                    agency=doc.agency,
                    document_id=doc.doc_id,
                )
                for doc in docs[:3]
            ]
            return AgentResponse(
                intent="general_info",
                response_text=(
                    "Here are some relevant documents from the Knowledge Hub:\n\n"
                    + "\n".join(f"• {d.title} ({d.agency})" for d in docs[:3])
                    + "\n\nWould you like more details on any of these?"
                ),
                confidence=0.70,
                citations=citations,
                data={"documents": [d.model_dump() for d in docs[:3]]},
            )

        return AgentResponse(
            intent="general_info",
            response_text=(
                "Welcome to the Cross-Agency Knowledge Hub. I can help you:\n"
                "• Search policies and regulations across agencies\n"
                "• Find subject matter experts\n"
                "• Discover cross-references between documents\n"
                "• Look up agency information\n\n"
                "What would you like to search for?"
            ),
            confidence=0.50,
            citations=[
                Citation(
                    source="Knowledge Hub",
                    text="Cross-agency knowledge search system",
                    agency="GovOps",
                )
            ],
        )
