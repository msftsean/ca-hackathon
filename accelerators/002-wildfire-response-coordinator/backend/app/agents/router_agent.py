"""RouterAgent — Routes queries to appropriate wildfire response modules."""

from app.models.schemas import IncidentQuery, RoutingDecision


class RouterAgent:
    """Routes wildfire queries to appropriate response modules."""

    ROUTE_MAP: dict[str, str] = {
        "incident_report": "incident_command",
        "resource_request": "resource_management",
        "evacuation_query": "evacuation_ops",
        "weather_check": "weather_ops",
        "psps_info": "utility_coordination",
        "agency_coordination": "interagency",
        "status_update": "incident_command",
        "general_info": "incident_command",
    }

    PRIORITY_MAP: dict[str, str] = {
        "incident_report": "critical",
        "resource_request": "high",
        "evacuation_query": "critical",
        "weather_check": "medium",
        "psps_info": "medium",
        "agency_coordination": "medium",
        "status_update": "medium",
        "general_info": "low",
    }

    ESCALATION_KEYWORDS = [
        "catastrophic", "mass casualty", "fatality", "deaths",
        "out of control", "overrun", "entrapment",
    ]

    async def route(self, query: IncidentQuery) -> RoutingDecision:
        """Route query to the appropriate response module."""
        destination = self.ROUTE_MAP.get(query.intent, "incident_command")
        priority = self.PRIORITY_MAP.get(query.intent, "medium")

        escalate = False
        escalation_reason = None
        lower_input = query.raw_input.lower()

        # Check for escalation keywords
        for keyword in self.ESCALATION_KEYWORDS:
            if keyword in lower_input:
                escalate = True
                priority = "critical"
                escalation_reason = f"Escalation trigger: '{keyword}' detected"
                break

        # Escalate if containment < 10% mentioned
        containment = query.entities.get("containment_pct")
        if containment is not None and containment < 10:
            escalate = True
            priority = "critical"
            escalation_reason = f"Low containment: {containment}%"

        # Check for red flag warning + active fire
        if "red flag" in lower_input and any(w in lower_input for w in ["fire", "active", "burning"]):
            escalate = True
            priority = "critical"
            escalation_reason = "Red flag warning with active fire conditions"

        return RoutingDecision(
            destination=destination,
            priority=priority,
            escalate=escalate,
            escalation_reason=escalation_reason,
        )
