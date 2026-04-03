"""QueryAgent — Intent detection, entity extraction, and PII filtering."""

import re
from app.models.schemas import ClaimQuery


INTENT_KEYWORDS: dict[str, list[str]] = {
    "claim_status": [
        "status", "check", "where", "my claim", "payment",
        "certified", "certification", "update", "pending",
    ],
    "eligibility_check": [
        "eligible", "qualify", "can i file", "am i eligible",
        "eligibility", "qualified", "can i get",
    ],
    "filing_help": [
        "file", "apply", "start", "new claim", "how to",
        "submit", "begin", "open",
    ],
    "document_requirements": [
        "documents", "upload", "submit", "proof", "verification",
        "paperwork", "documentation", "need to provide",
    ],
    "payment_info": [
        "payment", "deposit", "amount", "when", "how much",
        "paid", "direct deposit", "debit card",
    ],
    "appeal_info": [
        "appeal", "denied", "disagree", "reconsider",
        "hearing", "overturn", "unfair",
    ],
    "general_info": [
        "help", "info", "information", "question", "about",
        "what", "how", "tell me",
    ],
}

CLAIM_TYPE_MAP: dict[str, str] = {
    "unemployment": "UI",
    "unemployed": "UI",
    "laid off": "UI",
    "lost job": "UI",
    "fired": "UI",
    "disability insurance": "DI",
    "disability": "DI",
    "disabled": "DI",
    "injured": "DI",
    "illness": "DI",
    "family leave": "PFL",
    "pfl": "PFL",
    "parental": "PFL",
    "bonding": "PFL",
    "maternity": "PFL",
    "paternity": "PFL",
    "care for": "PFL",
}

SSN_PATTERN = re.compile(r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b")
SSN_LAST4_PATTERN = re.compile(r"\b\d{4}\b")
DATE_PATTERN = re.compile(r"\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b")

ESCALATION_KEYWORDS = [
    "frustrated", "angry", "desperate", "unfair",
    "complaint", "sue", "lawyer", "attorney",
    "emergency", "homeless", "hungry", "dying",
]


class QueryAgent:
    """Detects user intent, extracts entities, and filters PII from EDD queries."""

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

    def _extract_claim_type(self, text: str) -> str | None:
        lower = text.lower()
        # Check longer phrases first to avoid substring matches
        phrase_map = [
            ("family leave", "PFL"),
            ("paid family", "PFL"),
            ("bonding", "PFL"),
            ("parental", "PFL"),
            ("maternity", "PFL"),
            ("paternity", "PFL"),
            ("care for", "PFL"),
            ("unemployment", "UI"),
            ("unemployed", "UI"),
            ("laid off", "UI"),
            ("lost job", "UI"),
            ("fired", "UI"),
            ("disability insurance", "DI"),
            ("disability", "DI"),
            ("disabled", "DI"),
            ("injured", "DI"),
            ("illness", "DI"),
        ]
        for keyword, claim_type in phrase_map:
            if keyword in lower:
                return claim_type
        return None

    def _detect_pii(self, text: str) -> bool:
        return bool(SSN_PATTERN.search(text))

    def _extract_entities(self, text: str) -> dict:
        entities: dict = {}
        claim_type = self._extract_claim_type(text)
        if claim_type:
            entities["claim_type"] = claim_type
        if self._detect_pii(text):
            entities["pii_detected"] = True
        date_match = DATE_PATTERN.search(text)
        if date_match:
            entities["date_mentioned"] = date_match.group()
        return entities

    async def process(self, user_input: str, language: str = "en") -> ClaimQuery:
        intent = self._detect_intent(user_input)
        entities = self._extract_entities(user_input)
        claim_type = self._extract_claim_type(user_input)

        return ClaimQuery(
            raw_input=user_input,
            intent=intent,
            claim_type=claim_type,
            entities=entities,
        )
