"""ActionAgent — Retrieves knowledge and generates citation-backed responses."""

from app.models.schemas import (
    AgentResponse,
    BenefitQuery,
    Citation,
    RoutingDecision,
)
from app.services.mock_service import MockBenefitsService


class ActionAgent:
    """Generates responses using mock CDSS program knowledge bases."""

    def __init__(self) -> None:
        self.service = MockBenefitsService()

    async def execute(
        self, query: BenefitQuery, routing: RoutingDecision
    ) -> AgentResponse:
        intent = query.intent
        program = query.program

        if intent == "eligibility_check":
            return self._handle_eligibility(query, program)
        elif intent == "program_info":
            return self._handle_program_info(query, program)
        elif intent == "application_help":
            return self._handle_application_help(query, program)
        elif intent == "document_requirements":
            return self._handle_document_requirements(query, program)
        elif intent == "office_locations":
            return self._handle_office_locations(query)
        elif intent == "status_check":
            return self._handle_status_check(query)
        else:
            return self._handle_general(query)

    def _handle_eligibility(self, query: BenefitQuery, program: str | None) -> AgentResponse:
        prog = program or "calfresh"
        info = self.service.get_program(prog)
        if not info:
            return self._handle_general(query)

        return AgentResponse(
            intent="eligibility_check",
            response_text=(
                f"To be eligible for {info['name']}, you generally need to meet "
                f"these requirements: {', '.join(info['requirements'][:3])}. "
                f"Income limit for a household of 1: {info['income_limits']['household_1']}. "
                f"Apply online at BenefitsCal.com or visit your county office."
            ),
            confidence=0.92,
            citations=[
                Citation(
                    source="CDSS Policy Manual",
                    text=info["policy_citation"],
                    policy_ref=info["policy_ref"],
                ),
                Citation(
                    source="CalFresh Handbook",
                    text="Income and resource eligibility standards",
                    policy_ref="7 CFR 273.9",
                ),
            ],
            data={
                "program": info["name"],
                "requirements": info["requirements"],
                "income_limits": info["income_limits"],
            },
        )

    def _handle_program_info(self, query: BenefitQuery, program: str | None) -> AgentResponse:
        prog = program or "calfresh"
        info = self.service.get_program(prog)
        if not info:
            programs = self.service.list_programs()
            return AgentResponse(
                intent="program_info",
                response_text=(
                    "California offers several public assistance programs: "
                    + ", ".join(p["name"] for p in programs)
                    + ". How can I help you learn more about a specific program?"
                ),
                confidence=0.85,
                citations=[
                    Citation(source="CDSS", text="Program overview", url="https://benefitscal.com")
                ],
            )

        return AgentResponse(
            intent="program_info",
            response_text=f"{info['name']}: {info['description']}",
            confidence=0.90,
            citations=[
                Citation(
                    source="CDSS Policy Manual",
                    text=info["policy_citation"],
                    policy_ref=info["policy_ref"],
                ),
            ],
            data={"program": info},
        )

    def _handle_application_help(self, query: BenefitQuery, program: str | None) -> AgentResponse:
        prog = program or "calfresh"
        info = self.service.get_program(prog)
        name = info["name"] if info else "benefits"
        steps = [
            f"1. Visit BenefitsCal.com to start your {name} application",
            "2. Create an account or log in",
            "3. Complete the application form with your household information",
            "4. Upload required documents (ID, proof of income, residency)",
            "5. Submit your application",
            "6. Attend your eligibility interview (phone or in-person)",
        ]
        return AgentResponse(
            intent="application_help",
            response_text="Here's how to apply:\n" + "\n".join(steps),
            confidence=0.90,
            citations=[
                Citation(
                    source="CalFresh Handbook",
                    text="Application procedures",
                    url="https://benefitscal.com",
                ),
                Citation(
                    source="CDSS Policy Manual",
                    text="Application processing timelines",
                    policy_ref="MPP 63-301",
                ),
            ],
            data={"steps": steps},
        )

    def _handle_document_requirements(self, query: BenefitQuery, program: str | None) -> AgentResponse:
        prog = program or "calfresh"
        info = self.service.get_program(prog)
        if not info:
            docs = [
                "Government-issued photo ID",
                "Proof of income (pay stubs, tax returns)",
                "Proof of residency (utility bill, lease)",
                "Social Security cards for household members",
            ]
        else:
            docs = info["documents_needed"]

        return AgentResponse(
            intent="document_requirements",
            response_text=(
                "You'll need the following documents: " + "; ".join(docs) + "."
            ),
            confidence=0.88,
            citations=[
                Citation(
                    source="CalWORKs Guidelines",
                    text="Required verification documents",
                    policy_ref="MPP 40-105",
                ),
            ],
            data={"documents": docs},
        )

    def _handle_office_locations(self, query: BenefitQuery) -> AgentResponse:
        county = query.county or "Los Angeles"
        office = self.service.get_county_office(county)
        return AgentResponse(
            intent="office_locations",
            response_text=(
                f"The {county} County DPSS office is located at {office['address']}. "
                f"Hours: {office['hours']}. Phone: {office['phone']}."
            ),
            confidence=0.85,
            citations=[
                Citation(source="CDSS", text=f"{county} County office information"),
            ],
            data={"office": office},
        )

    def _handle_status_check(self, query: BenefitQuery) -> AgentResponse:
        return AgentResponse(
            intent="status_check",
            response_text=(
                "To check your application status, you can: "
                "1) Log in to BenefitsCal.com, "
                "2) Call your county office, or "
                "3) Visit your local DPSS office with your case number."
            ),
            confidence=0.87,
            citations=[
                Citation(
                    source="CDSS Policy Manual",
                    text="Application status inquiry procedures",
                    policy_ref="MPP 10-500",
                ),
            ],
        )

    def _handle_general(self, query: BenefitQuery) -> AgentResponse:
        programs = self.service.list_programs()
        return AgentResponse(
            intent="general_info",
            response_text=(
                "I can help you with California public assistance programs including: "
                + ", ".join(p["name"] for p in programs)
                + ". What would you like to know?"
            ),
            confidence=0.50,
            citations=[
                Citation(
                    source="CDSS",
                    text="California public assistance programs overview",
                    url="https://benefitscal.com",
                ),
            ],
        )
