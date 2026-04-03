"""QueryAgent — Parses procurement compliance queries and detects intent."""

from app.models.schemas import ComplianceQuery


class QueryAgent:
    """First stage: extracts intent and entities from user input."""

    INTENT_KEYWORDS: dict[str, list[str]] = {
        "compliance_check": [
            "compliance", "compliant", "check", "score", "assess", "review", "evaluate",
        ],
        "gap_analysis": [
            "gap", "gaps", "missing", "lacking", "deficiency", "shortfall", "remediation",
        ],
        "attestation_upload": [
            "upload", "submit", "document", "attestation", "file", "attach",
        ],
        "risk_assessment": [
            "risk", "tier", "classify", "classification", "danger", "threat",
        ],
        "regulation_lookup": [
            "regulation", "rule", "requirement", "eo", "executive order", "sb 53",
            "nist", "framework", "standard",
        ],
        "vendor_comparison": [
            "compare", "versus", "vs", "which vendor", "benchmark", "ranking",
        ],
        "general_info": [
            "help", "info", "information", "what", "how", "explain",
        ],
    }

    async def process(self, user_input: str, document_id: str | None = None) -> ComplianceQuery:
        lower = user_input.lower()
        intent = self._detect_intent(lower)
        entities: dict = {}
        if document_id:
            entities["document_id"] = document_id

        vendor = self._extract_vendor(lower)
        if vendor:
            entities["vendor_name"] = vendor

        return ComplianceQuery(
            raw_input=user_input,
            intent=intent,
            entities=entities,
        )

    def _detect_intent(self, text: str) -> str:
        scores: dict[str, int] = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            scores[intent] = sum(1 for k in keywords if k in text)
        best = max(scores, key=scores.get)  # type: ignore[arg-type]
        return best if scores[best] > 0 else "general_info"

    def _extract_vendor(self, text: str) -> str | None:
        known = ["ai solutions corp", "govtech analytics", "california data systems"]
        for v in known:
            if v in text:
                return v.title()
        return None
