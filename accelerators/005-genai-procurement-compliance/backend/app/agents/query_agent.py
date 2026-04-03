"""QueryAgent — Parses vendor attestation documents and compliance queries."""

from app.models.schemas import ComplianceQuery


class QueryAgent:
    """Extracts structured data from vendor attestation submissions."""

    async def process(self, user_input: str, attestation_id: str | None = None) -> ComplianceQuery:
        return ComplianceQuery(
            raw_input=user_input,
            intent="compliance_review",
            attestation_id=attestation_id,
            vendor_name=None,
            frameworks=["eo-n-5-26", "sb-53"],
        )
