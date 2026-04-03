"""RouterAgent — Routes queries to the appropriate department."""

from app.models.schemas import BenefitQuery, RoutingDecision


INTENT_TO_DEPARTMENT: dict[str, str] = {
    "eligibility_check": "eligibility_services",
    "program_info": "general_support",
    "application_help": "enrollment_services",
    "document_requirements": "document_processing",
    "office_locations": "county_offices",
    "status_check": "enrollment_services",
    "general_info": "general_support",
}

INTENT_TO_PRIORITY: dict[str, str] = {
    "eligibility_check": "medium",
    "program_info": "low",
    "application_help": "high",
    "document_requirements": "medium",
    "office_locations": "low",
    "status_check": "high",
    "general_info": "low",
}

ESCALATION_KEYWORDS = [
    "appeal", "complaint", "urgent", "emergency", "grievance",
    "discrimination", "denied unfairly", "hearing",
]


class RouterAgent:
    """Routes benefit queries to the appropriate CDSS department."""

    def _should_escalate(self, query: BenefitQuery) -> bool:
        lower = query.raw_input.lower()
        if query.entities.get("pii_detected"):
            return True
        for keyword in ESCALATION_KEYWORDS:
            if keyword in lower:
                return True
        return False

    async def route(self, query: BenefitQuery) -> RoutingDecision:
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
