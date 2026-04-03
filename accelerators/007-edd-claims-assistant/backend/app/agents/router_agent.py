"""RouterAgent — Routes queries to the appropriate EDD service."""

from app.models.schemas import ClaimQuery, RoutingDecision


INTENT_TO_DEPARTMENT: dict[str, str] = {
    "claim_status": "claims_services",
    "eligibility_check": "eligibility",
    "filing_help": "filing_assistance",
    "document_requirements": "document_processing",
    "payment_info": "payments",
    "appeal_info": "appeals",
    "general_info": "general_support",
}

INTENT_TO_PRIORITY: dict[str, str] = {
    "claim_status": "medium",
    "eligibility_check": "medium",
    "filing_help": "high",
    "document_requirements": "medium",
    "payment_info": "medium",
    "appeal_info": "high",
    "general_info": "low",
}

ESCALATION_KEYWORDS = [
    "appeal", "frustrated", "angry", "desperate", "unfair",
    "complaint", "sue", "lawyer", "attorney",
    "emergency", "homeless", "hungry",
]


class RouterAgent:
    """Routes EDD queries to the appropriate service department."""

    def _should_escalate(self, query: ClaimQuery) -> bool:
        lower = query.raw_input.lower()
        if query.entities.get("pii_detected"):
            return True
        return any(kw in lower for kw in ESCALATION_KEYWORDS)

    async def route(self, query: ClaimQuery) -> RoutingDecision:
        department = INTENT_TO_DEPARTMENT.get(query.intent, "general_support")
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
