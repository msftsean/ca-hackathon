"""QueryAgent — Parses claim inquiries and detects intent."""

from app.models.schemas import ClaimQuery


class QueryAgent:
    """Detects intent from EDD claim-related queries."""

    async def process(self, user_input: str) -> ClaimQuery:
        intent = "status_check"
        if any(w in user_input.lower() for w in ["eligible", "qualify", "can i"]):
            intent = "eligibility_screening"
        elif any(w in user_input.lower() for w in ["file", "submit", "apply"]):
            intent = "file_claim"
        elif any(w in user_input.lower() for w in ["help", "speak", "agent", "problem"]):
            intent = "escalation"

        return ClaimQuery(
            raw_input=user_input,
            intent=intent,
            claim_id=None,
            program=None,
            pii_detected=False,
        )
