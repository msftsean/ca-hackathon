"""QueryAgent — Intent detection, entity extraction, and PII filtering."""

import re
from app.models.schemas import BenefitQuery


INTENT_KEYWORDS: dict[str, list[str]] = {
    "eligibility_check": [
        "eligible", "qualify", "can i get", "do i qualify", "am i eligible",
        "eligibility", "qualified",
    ],
    "program_info": [
        "what is", "tell me about", "explain", "how does", "information about",
        "learn about", "details",
    ],
    "application_help": [
        "apply", "application", "sign up", "enroll", "how to apply",
        "submit", "register",
    ],
    "document_requirements": [
        "documents", "paperwork", "need to bring", "proof", "documentation",
        "what do i need", "checklist",
    ],
    "office_locations": [
        "office", "where", "location", "nearest", "hours", "address",
        "visit", "in person",
    ],
    "status_check": [
        "status", "pending", "approved", "denied", "check my",
        "my application", "update on",
    ],
    "general_info": [
        "help", "info", "benefits", "programs", "services", "assistance",
    ],
}

PROGRAM_NAMES: dict[str, str] = {
    "calfresh": "calfresh",
    "cal-fresh": "calfresh",
    "food stamps": "calfresh",
    "snap": "calfresh",
    "calworks": "calworks",
    "cal-works": "calworks",
    "cash aid": "calworks",
    "tanf": "calworks",
    "general relief": "general_relief",
    "general assistance": "general_relief",
    "gr": "general_relief",
    "ga": "general_relief",
    "capi": "capi",
    "cash assistance": "capi",
    "medi-cal": "medi_cal",
    "medical": "medi_cal",
    "medicaid": "medi_cal",
}

CALIFORNIA_COUNTIES = [
    "los angeles", "san diego", "orange", "riverside", "san bernardino",
    "santa clara", "alameda", "sacramento", "san francisco", "contra costa",
    "fresno", "ventura", "san mateo", "kern", "san joaquin",
    "stanislaus", "sonoma", "tulare", "santa barbara", "solano",
    "monterey", "placer", "san luis obispo", "santa cruz", "merced",
    "marin", "butte", "yolo", "el dorado", "shasta",
]

SSN_PATTERN = re.compile(r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b")
DOB_PATTERN = re.compile(
    r"\b(?:\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\b"
)


class QueryAgent:
    """Detects user intent, extracts entities, and filters PII from benefit queries."""

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

    def _extract_program(self, text: str) -> str | None:
        lower = text.lower()
        for keyword, program in PROGRAM_NAMES.items():
            if keyword in lower:
                return program
        return None

    def _extract_county(self, text: str) -> str | None:
        lower = text.lower()
        for county in CALIFORNIA_COUNTIES:
            if county in lower:
                return county.title()
        return None

    def _detect_pii(self, text: str) -> bool:
        return bool(SSN_PATTERN.search(text) or DOB_PATTERN.search(text))

    def _extract_entities(self, text: str) -> dict:
        entities: dict = {}
        program = self._extract_program(text)
        if program:
            entities["program"] = program
        county = self._extract_county(text)
        if county:
            entities["county"] = county
        if self._detect_pii(text):
            entities["pii_detected"] = True
        income_match = re.search(r"\$[\d,]+(?:\.\d{2})?", text)
        if income_match:
            entities["income_mentioned"] = income_match.group()
        return entities

    async def process(self, user_input: str, language: str = "en", county: str | None = None) -> BenefitQuery:
        intent = self._detect_intent(user_input)
        entities = self._extract_entities(user_input)
        program = self._extract_program(user_input)
        detected_county = self._extract_county(user_input)

        return BenefitQuery(
            raw_input=user_input,
            intent=intent,
            language=language,
            entities=entities,
            county=county or detected_county,
            program=program,
        )
