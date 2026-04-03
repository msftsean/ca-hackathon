"""ActionAgent — Generates EDD-specific responses with policy citations."""

from app.models.schemas import (
    AgentResponse,
    Citation,
    ClaimQuery,
    RoutingDecision,
)
from app.services.mock_service import MockEDDService


class ActionAgent:
    """Generates responses for EDD claims queries using mock data."""

    def __init__(self) -> None:
        self.service = MockEDDService()

    async def execute(
        self, query: ClaimQuery, routing: RoutingDecision
    ) -> AgentResponse:
        intent = query.intent

        if intent == "claim_status":
            return self._handle_claim_status(query)
        elif intent == "eligibility_check":
            return self._handle_eligibility(query)
        elif intent == "filing_help":
            return self._handle_filing_help(query)
        elif intent == "document_requirements":
            return self._handle_document_requirements(query)
        elif intent == "payment_info":
            return self._handle_payment_info(query)
        elif intent == "appeal_info":
            return self._handle_appeal_info(query)
        else:
            return self._handle_general(query)

    def _handle_claim_status(self, query: ClaimQuery) -> AgentResponse:
        claim_type = query.claim_type or "UI"
        claim = self.service.get_claim(claim_type)
        if not claim:
            return self._handle_general(query)

        status_text = (
            f"Your {claim.claim_type} claim ({claim.claim_id}) status: **{claim.status}**\n\n"
            f"• Weekly benefit amount: ${claim.weekly_benefit_amount:.2f}\n"
            f"• Remaining balance: ${claim.remaining_balance:.2f}\n"
            f"• Filed: {claim.filed_date.strftime('%m/%d/%Y')}\n"
        )
        if claim.next_payment_date:
            status_text += f"• Next payment: {claim.next_payment_date.strftime('%m/%d/%Y')}\n"
        if claim.pending_issues:
            status_text += f"• Pending issues: {', '.join(claim.pending_issues)}\n"

        return AgentResponse(
            intent="claim_status",
            response_text=status_text,
            confidence=0.92,
            citations=[
                Citation(
                    source="EDD Policy Manual",
                    text="Claim status and benefit information",
                    policy_ref="CUIC §1326",
                ),
            ],
            data={"claim_status": claim.model_dump()},
        )

    def _handle_eligibility(self, query: ClaimQuery) -> AgentResponse:
        claim_type = query.claim_type or "UI"
        assessment = self.service.get_eligibility(claim_type)

        status = "likely eligible" if assessment.likely_eligible else "may not be eligible"
        text = (
            f"Based on general {claim_type} eligibility criteria, you are **{status}**.\n\n"
            f"**Requirements:**\n"
            + "\n".join(f"• {r}" for r in assessment.requirements)
            + "\n\n**Next steps:**\n"
            + "\n".join(f"• {s}" for s in assessment.next_steps)
        )

        return AgentResponse(
            intent="eligibility_check",
            response_text=text,
            confidence=assessment.confidence,
            citations=[
                Citation(
                    source="EDD Policy Manual",
                    text=f"{claim_type} eligibility requirements",
                    policy_ref="CUIC §1253",
                ),
                Citation(
                    source="CCR Title 22",
                    text="Eligibility determination standards",
                    policy_ref="CCR §1253-1",
                ),
            ],
            data={"eligibility": assessment.model_dump()},
        )

    def _handle_filing_help(self, query: ClaimQuery) -> AgentResponse:
        claim_type = query.claim_type or "UI"
        steps = self.service.get_filing_steps(claim_type)

        return AgentResponse(
            intent="filing_help",
            response_text=(
                f"Here's how to file a {claim_type} claim:\n\n"
                + "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))
                + "\n\nProcessing time: 2-3 weeks for most claims."
            ),
            confidence=0.90,
            citations=[
                Citation(
                    source="EDD Policy Manual",
                    text=f"Filing procedures for {claim_type} claims",
                    policy_ref="CUIC §1326",
                ),
                Citation(
                    source="EDD Website",
                    text="Online claim filing instructions",
                    policy_ref="edd.ca.gov",
                ),
            ],
            data={"steps": steps, "claim_type": claim_type},
        )

    def _handle_document_requirements(self, query: ClaimQuery) -> AgentResponse:
        claim_type = query.claim_type or "UI"
        checklist = self.service.get_document_checklist(claim_type)

        doc_lines = []
        for doc in checklist:
            status = "✓" if doc.submitted else "☐"
            req = " (required)" if doc.required else " (optional)"
            doc_lines.append(f"{status} {doc.name}{req}: {doc.description}")

        return AgentResponse(
            intent="document_requirements",
            response_text=(
                f"Document checklist for {claim_type} claims:\n\n"
                + "\n".join(doc_lines)
            ),
            confidence=0.88,
            citations=[
                Citation(
                    source="EDD Policy Manual",
                    text="Required documentation for claims",
                    policy_ref="CCR Title 22 §1253-3",
                ),
            ],
            data={"document_checklist": [d.model_dump() for d in checklist]},
        )

    def _handle_payment_info(self, query: ClaimQuery) -> AgentResponse:
        claim_type = query.claim_type or "UI"
        claim = self.service.get_claim(claim_type)

        if claim:
            text = (
                f"Payment information for your {claim_type} claim:\n\n"
                f"• Weekly benefit amount: ${claim.weekly_benefit_amount:.2f}\n"
                f"• Remaining balance: ${claim.remaining_balance:.2f}\n"
            )
            if claim.next_payment_date:
                text += f"• Next scheduled payment: {claim.next_payment_date.strftime('%m/%d/%Y')}\n"
            text += (
                "\nPayments are issued via EDD Debit Card or direct deposit. "
                "Certify for benefits every two weeks to continue receiving payments."
            )
        else:
            text = (
                "To receive payment information, please provide your claim details. "
                "Payments are typically issued within 48 hours after certification."
            )

        return AgentResponse(
            intent="payment_info",
            response_text=text,
            confidence=0.87,
            citations=[
                Citation(
                    source="EDD Policy Manual",
                    text="Benefit payment schedules",
                    policy_ref="CUIC §1329",
                ),
            ],
            data={"claim_status": claim.model_dump() if claim else None},
        )

    def _handle_appeal_info(self, query: ClaimQuery) -> AgentResponse:
        return AgentResponse(
            intent="appeal_info",
            response_text=(
                "If your claim was denied, you have the right to appeal.\n\n"
                "**Appeal process:**\n"
                "1. File an appeal within 20 days of the denial notice\n"
                "2. Complete the appeal form (DE 1000M)\n"
                "3. Include any supporting documentation\n"
                "4. Attend the Administrative Law Judge hearing\n"
                "5. Receive a decision within 45-60 days\n\n"
                "You may represent yourself or have an attorney. "
                "Free legal assistance is available through Legal Aid societies."
            ),
            confidence=0.90,
            citations=[
                Citation(
                    source="CUIC Code",
                    text="Appeal rights and procedures",
                    policy_ref="CUIC §1328",
                ),
                Citation(
                    source="CCR Title 22",
                    text="Administrative hearing procedures",
                    policy_ref="CCR §5100",
                ),
            ],
            data={"appeal_deadline_days": 20},
        )

    def _handle_general(self, query: ClaimQuery) -> AgentResponse:
        return AgentResponse(
            intent="general_info",
            response_text=(
                "Welcome to the EDD Claims Assistant. I can help you with:\n\n"
                "• **Unemployment Insurance (UI)** — Check status, file claims, certify\n"
                "• **Disability Insurance (DI)** — Short-term disability benefits\n"
                "• **Paid Family Leave (PFL)** — Family care and bonding\n\n"
                "What would you like help with?"
            ),
            confidence=0.50,
            citations=[
                Citation(
                    source="EDD",
                    text="Employment Development Department services overview",
                    policy_ref="edd.ca.gov",
                ),
            ],
        )
