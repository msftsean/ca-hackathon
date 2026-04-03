"""RouterAgent — Routes queries to departments with priority and escalation."""

from app.models.schemas import EmergencyQuery, RoutingDecision


class RouterAgent:
    """Second stage: determines department, priority, and escalation."""

    DEPARTMENT_MAP: dict[str, str] = {
        "active_alerts": "cal_oes_alerts",
        "evacuation_status": "cal_oes_evacuation",
        "shelter_search": "cal_oes_shelters",
        "air_quality": "carb_air_quality",
        "safety_tips": "cal_oes_preparedness",
        "general_info": "cal_oes_general",
    }

    PRIORITY_MAP: dict[str, str] = {
        "active_alerts": "critical",
        "evacuation_status": "critical",
        "shelter_search": "high",
        "air_quality": "medium",
        "safety_tips": "low",
        "general_info": "low",
    }

    async def route(self, query: EmergencyQuery) -> RoutingDecision:
        department = self.DEPARTMENT_MAP.get(query.intent, "cal_oes_general")
        priority = self.PRIORITY_MAP.get(query.intent, "low")

        escalate = False
        reason = f"Routed based on intent: {query.intent}"

        if query.emergency_type and query.intent == "evacuation_status":
            escalate = True
            reason = f"Escalation: {query.emergency_type} evacuation detected"

        if query.intent in ("active_alerts", "evacuation_status") and query.emergency_type:
            priority = "critical"
            reason = f"Critical: {query.emergency_type} {query.intent}"

        return RoutingDecision(
            department=department,
            priority=priority,
            reason=reason,
            escalate=escalate,
        )
