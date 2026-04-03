"""QueryAgent — Intent detection, entity extraction, and PII filtering for Medi-Cal."""

import re
from app.models.schemas import MediCalQuery


class QueryAgent:
    """Detects user intent, extracts entities, and filters PII from Medi-Cal queries."""

    INTENT_KEYWORDS: dict[str, list[str]] = {
        "eligibility_check": [
            "eligible", "qualify", "can i get", "do i qualify", "am i eligible",
            "do we qualify", "need medical", "cannot afford", "need coverage", "disability",
        ],
        "application_status": ["status", "my application", "where is my", "progress", "approved", "denied", "pending"],
        "document_help": ["document", "upload", "submit", "proof", "w2", "paystub", "tax return", "verification"],
        "income_verification": ["income", "earn", "make", "salary", "wages", "pay", "w-2", "paycheck"],
        "county_info": ["county", "local office", "where to go", "office location", "nearest", "office in"],
        "program_info": ["what is", "types", "coverage", "benefits", "difference", "programs", "explain"],
    }

    PROGRAM_KEYWORDS: dict[str, str] = {
        "magi": "MAGI_Adult",
        "abd": "ABD",
        "aged": "ABD",
        "blind": "ABD",
        "disabled": "ABD",
        "disability": "ABD",
        "qmb": "QMB",
        "qualified medicare": "QMB",
        "slmb": "SLMB",
        "pregnancy": "Pregnancy",
        "pregnant": "Pregnancy",
        "child": "MAGI_Child",
        "children": "MAGI_Child",
        "kids": "MAGI_Child",
    }

    COUNTY_NAMES = [
        "los angeles", "san diego", "san francisco", "sacramento", "fresno",
        "alameda", "orange", "riverside", "san bernardino", "santa clara",
    ]

    async def process(self, user_input: str) -> MediCalQuery:
        """Parse user input to detect intent, extract entities, and identify program type."""
        lower_input = user_input.lower()
        intent = self._detect_intent(lower_input)
        entities = self._extract_entities(lower_input)
        program_type = self._detect_program(lower_input)

        return MediCalQuery(
            raw_input=user_input,
            intent=intent,
            entities=entities,
            program_type=program_type,
        )

    def _detect_intent(self, text: str) -> str:
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    return intent
        return "general_info"

    def _extract_entities(self, text: str) -> dict:
        entities: dict = {}

        # Extract income amounts ($X,XXX or $XX,XXX or $XXXX)
        income_matches = re.findall(r"\$[\d,]+(?:\.\d{2})?", text)
        if income_matches:
            amounts = [float(m.replace("$", "").replace(",", "")) for m in income_matches]
            entities["income_amounts"] = amounts

        # Extract household size mentions
        hh_match = re.search(r"(?:household|family)\s*(?:of|size)?\s*(\d+)", text)
        if hh_match:
            entities["household_size"] = int(hh_match.group(1))

        # Single person indicators
        if any(phrase in text for phrase in ["live alone", "just me", "single", "by myself"]):
            entities.setdefault("household_size", 1)

        # County names
        for county in self.COUNTY_NAMES:
            if county in text:
                entities["county"] = county.title()
                break

        return entities

    def _detect_program(self, text: str) -> str | None:
        for keyword, program in self.PROGRAM_KEYWORDS.items():
            if keyword in text:
                return program
        return None
