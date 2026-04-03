"""RouterAgent — Routes to the correct departments and permit pathway."""

from app.models.schemas import PermitQuery, RoutingDecision


INTENT_TO_DEPARTMENTS: dict[str, list[str]] = {
    "project_intake": ["building", "zoning"],
    "requirement_check": ["building"],
    "zoning_check": ["zoning"],
    "status_check": ["building"],
    "fee_estimate": ["building"],
    "general_info": ["building"],
}

PROJECT_DEPARTMENTS: dict[str, list[str]] = {
    "addition": ["building", "zoning"],
    "new_construction": ["building", "zoning", "fire", "environmental_review"],
    "renovation": ["building"],
    "adu": ["building", "zoning"],
    "commercial": ["building", "zoning", "fire", "health"],
    "demolition": ["building", "environmental_review"],
    "solar": ["building", "electrical"],
    "sign": ["building", "zoning"],
}

INTENT_TO_PRIORITY: dict[str, str] = {
    "project_intake": "high",
    "requirement_check": "medium",
    "zoning_check": "medium",
    "status_check": "high",
    "fee_estimate": "low",
    "general_info": "low",
}

DEPARTMENT_SLA: dict[str, int] = {
    "building": 30,
    "zoning": 21,
    "fire": 14,
    "electrical": 14,
    "plumbing": 14,
    "environmental_review": 45,
    "health": 21,
}


class RouterAgent:
    """Routes permit queries to the appropriate departments."""

    async def route(self, query: PermitQuery) -> RoutingDecision:
        # Determine departments
        departments = list(INTENT_TO_DEPARTMENTS.get(query.intent, ["building"]))
        if query.project_type and query.project_type in PROJECT_DEPARTMENTS:
            departments = list(PROJECT_DEPARTMENTS[query.project_type])

        priority = INTENT_TO_PRIORITY.get(query.intent, "medium")
        sla_days = max(DEPARTMENT_SLA.get(d, 30) for d in departments) if departments else 30

        escalate = query.intent == "status_check" and "urgent" in query.raw_input.lower()

        return RoutingDecision(
            departments=departments,
            priority=priority,
            reason=f"Intent '{query.intent}' routed to {', '.join(departments)}",
            escalate=escalate,
            sla_days=sla_days,
        )
