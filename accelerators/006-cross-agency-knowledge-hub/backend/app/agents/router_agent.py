"""RouterAgent — Routes queries to the appropriate service."""

from app.models.schemas import SearchQuery, RoutingDecision


INTENT_TO_DEPARTMENT: dict[str, str] = {
    "policy_search": "search_index",
    "document_lookup": "search_index",
    "expert_search": "expert_directory",
    "cross_reference": "cross_reference_engine",
    "agency_info": "agency_directory",
    "general_info": "search_index",
}

INTENT_TO_PRIORITY: dict[str, str] = {
    "policy_search": "high",
    "document_lookup": "medium",
    "expert_search": "medium",
    "cross_reference": "high",
    "agency_info": "low",
    "general_info": "low",
}

ESCALATION_KEYWORDS = [
    "confidential", "restricted", "classified", "sensitive",
    "urgent", "emergency", "critical", "security",
]


class RouterAgent:
    """Routes knowledge queries to the appropriate service."""

    def _should_escalate(self, query: SearchQuery) -> bool:
        lower = query.raw_input.lower()
        return any(kw in lower for kw in ESCALATION_KEYWORDS)

    async def route(self, query: SearchQuery) -> RoutingDecision:
        department = INTENT_TO_DEPARTMENT.get(query.intent, "search_index")
        priority = INTENT_TO_PRIORITY.get(query.intent, "low")
        escalate = self._should_escalate(query)

        if escalate:
            priority = "critical"

        return RoutingDecision(
            department=department,
            priority=priority,
            reason=f"Intent '{query.intent}' routed to {department}",
            escalate=escalate,
        )
