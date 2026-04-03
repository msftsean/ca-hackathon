"""RouterAgent — Routes compliance queries to appropriate review teams."""

from app.models.schemas import ComplianceQuery, RoutingDecision


class RouterAgent:
    """Second stage: determines department, priority, and escalation."""

    DEPARTMENT_MAP: dict[str, str] = {
        "compliance_check": "compliance_review",
        "gap_analysis": "gap_analysis",
        "attestation_upload": "document_intake",
        "risk_assessment": "risk_assessment",
        "regulation_lookup": "policy_guidance",
        "vendor_comparison": "compliance_review",
        "general_info": "general_support",
    }

    PRIORITY_MAP: dict[str, str] = {
        "compliance_check": "high",
        "gap_analysis": "high",
        "attestation_upload": "medium",
        "risk_assessment": "critical",
        "regulation_lookup": "low",
        "vendor_comparison": "medium",
        "general_info": "low",
    }

    async def route(self, query: ComplianceQuery) -> RoutingDecision:
        department = self.DEPARTMENT_MAP.get(query.intent, "general_support")
        priority = self.PRIORITY_MAP.get(query.intent, "low")

        escalate = query.intent == "risk_assessment"
        reason = f"Routed based on intent: {query.intent}"

        if escalate:
            reason = f"Escalation: risk assessment requires senior review"

        return RoutingDecision(
            department=department,
            priority=priority,
            reason=reason,
            escalate=escalate,
        )
