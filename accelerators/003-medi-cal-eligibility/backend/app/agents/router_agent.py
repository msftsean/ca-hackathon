"""RouterAgent — Routes queries to the appropriate Medi-Cal service pathway."""

from app.models.schemas import MediCalQuery, RoutingDecision


class RouterAgent:
    """Routes Medi-Cal queries to appropriate processing pathways."""

    ROUTE_MAP: dict[str, str] = {
        "eligibility_check": "eligibility_screening",
        "application_status": "application_processing",
        "income_verification": "income_review",
        "document_help": "document_verification",
        "program_info": "eligibility_screening",
        "county_info": "county_services",
        "general_info": "eligibility_screening",
    }

    PRIORITY_MAP: dict[str, str] = {
        "eligibility_check": "medium",
        "application_status": "high",
        "income_verification": "high",
        "document_help": "medium",
        "program_info": "low",
        "county_info": "low",
        "general_info": "low",
    }

    ESCALATION_KEYWORDS = [
        "pregnancy", "pregnant", "disability", "disabled",
        "emergency", "urgent", "emergency medical", "er visit",
    ]

    async def route(self, query: MediCalQuery) -> RoutingDecision:
        """Route query to the appropriate service pathway."""
        destination = self.ROUTE_MAP.get(query.intent, "eligibility_screening")
        priority = self.PRIORITY_MAP.get(query.intent, "medium")

        escalate = False
        escalation_reason = None
        lower_input = query.raw_input.lower()

        for keyword in self.ESCALATION_KEYWORDS:
            if keyword in lower_input:
                escalate = True
                priority = "critical"
                escalation_reason = f"Escalation trigger: '{keyword}' detected"
                break

        return RoutingDecision(
            destination=destination,
            priority=priority,
            escalate=escalate,
            escalation_reason=escalation_reason,
        )
