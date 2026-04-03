"""ActionAgent — Generates permit guidance from mock data."""

from app.models.schemas import (
    AgentResponse,
    Citation,
    PermitQuery,
    RoutingDecision,
)
from app.services.mock_service import MockPermitService


class ActionAgent:
    """Generates permit-related responses using mock knowledge base."""

    def __init__(self) -> None:
        self.service = MockPermitService()

    async def execute(
        self, query: PermitQuery, routing: RoutingDecision
    ) -> AgentResponse:
        intent = query.intent

        if intent == "project_intake":
            return self._handle_project_intake(query, routing)
        elif intent == "requirement_check":
            return self._handle_requirement_check(query)
        elif intent == "zoning_check":
            return self._handle_zoning_check(query)
        elif intent == "status_check":
            return self._handle_status_check(query)
        elif intent == "fee_estimate":
            return self._handle_fee_estimate(query)
        else:
            return self._handle_general(query)

    def _handle_project_intake(self, query: PermitQuery, routing: RoutingDecision) -> AgentResponse:
        ptype = query.project_type or "residential"
        checklist = self.service.get_requirements(ptype)
        fees = self.service.get_fee_schedule(ptype)

        return AgentResponse(
            intent="project_intake",
            response_text=(
                f"For your {ptype.replace('_', ' ')} project, you'll need permits from: "
                f"{', '.join(routing.departments)}. "
                f"Required documents: {', '.join(item['name'] for item in checklist[:4])}. "
                f"Estimated fees: {fees['total']}. "
                f"Expected review time: {routing.sla_days} days."
            ),
            confidence=0.90,
            citations=[
                Citation(
                    source="Municipal Building Code",
                    text=f"Permit requirements for {ptype}",
                    policy_ref="CBC Title 24",
                ),
                Citation(
                    source="Local Zoning Ordinance",
                    text="Zoning compliance requirements",
                    policy_ref="ZO-2024",
                ),
            ],
            data={
                "project_type": ptype,
                "departments": routing.departments,
                "checklist": checklist,
                "fees": fees,
                "sla_days": routing.sla_days,
            },
        )

    def _handle_requirement_check(self, query: PermitQuery) -> AgentResponse:
        ptype = query.project_type or "residential"
        checklist = self.service.get_requirements(ptype)

        items_text = "; ".join(f"{item['name']} ({'required' if item['required'] else 'optional'})" for item in checklist)

        return AgentResponse(
            intent="requirement_check",
            response_text=f"For a {ptype.replace('_', ' ')} permit, you need: {items_text}.",
            confidence=0.88,
            citations=[
                Citation(
                    source="Municipal Building Code",
                    text="Document submission requirements",
                    policy_ref="CBC 107.2",
                ),
            ],
            data={"checklist": checklist},
        )

    def _handle_zoning_check(self, query: PermitQuery) -> AgentResponse:
        address = query.address or "123 Main St"
        zoning = self.service.get_zoning_info(address)

        return AgentResponse(
            intent="zoning_check",
            response_text=(
                f"Zoning for {zoning['address']}: Zone {zoning['zone_code']} ({zoning['zone_name']}). "
                f"Permitted uses: {', '.join(zoning['permitted_uses'][:3])}. "
                f"Max height: {zoning['max_height_ft']} ft. "
                f"Lot coverage: {zoning['lot_coverage_pct']}%. "
                + ("Compliant." if zoning["compliant"] else f"Issues: {', '.join(zoning['issues'])}")
            ),
            confidence=0.85,
            citations=[
                Citation(
                    source="Local Zoning Ordinance",
                    text=f"Zone {zoning['zone_code']} regulations",
                    policy_ref=f"ZO-{zoning['zone_code']}",
                ),
            ],
            data={"zoning": zoning},
        )

    def _handle_status_check(self, query: PermitQuery) -> AgentResponse:
        applications = self.service.get_sample_applications()
        app_list = "; ".join(
            f"{a['app_id']} ({a['project_type']}): {a['status']}" for a in applications[:3]
        )

        return AgentResponse(
            intent="status_check",
            response_text=(
                f"Here are recent applications: {app_list}. "
                "To check a specific application, provide your permit number."
            ),
            confidence=0.87,
            citations=[
                Citation(
                    source="Permit Tracking System",
                    text="Application status records",
                ),
            ],
            data={"applications": applications},
        )

    def _handle_fee_estimate(self, query: PermitQuery) -> AgentResponse:
        ptype = query.project_type or "residential"
        fees = self.service.get_fee_schedule(ptype)

        fee_text = "; ".join(f"{k}: {v}" for k, v in fees.items() if k != "total")

        return AgentResponse(
            intent="fee_estimate",
            response_text=(
                f"Estimated fees for {ptype.replace('_', ' ')} permit: "
                f"{fee_text}. Total: {fees['total']}."
            ),
            confidence=0.85,
            citations=[
                Citation(
                    source="Fee Schedule",
                    text=f"Current fee schedule for {ptype}",
                    policy_ref="FS-2024",
                ),
            ],
            data={"fees": fees},
        )

    def _handle_general(self, query: PermitQuery) -> AgentResponse:
        return AgentResponse(
            intent="general_info",
            response_text=(
                "I can help with building permits, zoning checks, fee estimates, "
                "and application status. What would you like to know about?"
            ),
            confidence=0.50,
            citations=[
                Citation(
                    source="Permit Office",
                    text="General permit information",
                    url="https://permits.ca.gov",
                ),
            ],
        )
