"""QueryAgent — Parses permit applications and status queries."""

import re
from app.models.schemas import PermitQuery


INTENT_KEYWORDS: dict[str, list[str]] = {
    "project_intake": [
        "build", "construct", "add on", "renovate", "remodel", "new construction",
        "addition", "adu", "accessory dwelling", "demolish", "tear down",
    ],
    "requirement_check": [
        "need", "require", "checklist", "documents", "what do i need",
        "paperwork", "submit", "documentation",
    ],
    "zoning_check": [
        "zoning", "zone", "allowed", "permitted", "setback", "land use",
        "height limit", "lot coverage", "conditional use",
    ],
    "status_check": [
        "status", "where", "progress", "my application", "tracking",
        "update", "when will", "how long",
    ],
    "fee_estimate": [
        "cost", "fee", "price", "how much", "estimate", "charges", "payment",
    ],
    "general_info": [
        "help", "info", "permit", "information", "question", "process",
    ],
}

PROJECT_TYPES: dict[str, str] = {
    "new construction": "new_construction",
    "new build": "new_construction",
    "commercial": "commercial",
    "retail": "commercial",
    "office": "commercial",
    "addition": "addition",
    "renovation": "renovation",
    "remodel": "renovation",
    "adu": "adu",
    "accessory dwelling": "adu",
    "granny flat": "adu",
    "demolition": "demolition",
    "tear down": "demolition",
    "demolish": "demolition",
    "solar": "solar",
    "solar panel": "solar",
    "sign": "sign",
    "signage": "sign",
}

SQFT_PATTERN = re.compile(r"(\d{1,6})\s*(?:sq\.?\s*ft\.?|square\s*feet|sqft)", re.IGNORECASE)
ADDRESS_PATTERN = re.compile(r"\d+\s+[\w\s]+(?:St|Ave|Blvd|Dr|Rd|Way|Ln|Ct|Pl)\.?", re.IGNORECASE)


class QueryAgent:
    """Detects intent from permit-related queries and extracts application details."""

    def _detect_intent(self, text: str) -> str:
        lower = text.lower()
        best_intent = "general_info"
        best_score = 0
        for intent, keywords in INTENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in lower)
            if score > best_score:
                best_score = score
                best_intent = intent
        return best_intent

    def _extract_project_type(self, text: str) -> str | None:
        lower = text.lower()
        for keyword, ptype in PROJECT_TYPES.items():
            if keyword in lower:
                return ptype
        return None

    def _extract_sqft(self, text: str) -> int | None:
        match = SQFT_PATTERN.search(text)
        return int(match.group(1)) if match else None

    def _extract_address(self, text: str) -> str | None:
        match = ADDRESS_PATTERN.search(text)
        return match.group(0).strip() if match else None

    def _extract_entities(self, text: str) -> dict:
        entities: dict = {}
        ptype = self._extract_project_type(text)
        if ptype:
            entities["project_type"] = ptype
        sqft = self._extract_sqft(text)
        if sqft:
            entities["square_footage"] = sqft
        addr = self._extract_address(text)
        if addr:
            entities["address"] = addr
        return entities

    async def process(self, user_input: str) -> PermitQuery:
        intent = self._detect_intent(user_input)
        entities = self._extract_entities(user_input)
        project_type = self._extract_project_type(user_input)
        address = self._extract_address(user_input)

        return PermitQuery(
            raw_input=user_input,
            intent=intent,
            entities=entities,
            project_type=project_type,
            address=address,
        )
