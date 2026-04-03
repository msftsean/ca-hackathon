"""QueryAgent — Intent detection, entity extraction, and PII filtering."""

import re
from app.models.schemas import SearchQuery


INTENT_KEYWORDS: dict[str, list[str]] = {
    "policy_search": [
        "policy", "regulation", "rule", "guideline", "procedure",
        "compliance", "standard", "requirement",
    ],
    "document_lookup": [
        "document", "find", "search", "locate", "retrieve",
        "look up", "get", "show me",
    ],
    "expert_search": [
        "expert", "who", "contact", "specialist", "sme",
        "person", "staff", "responsible",
    ],
    "cross_reference": [
        "related", "similar", "supersedes", "conflicts", "cross-reference",
        "reference", "linked", "complementary",
    ],
    "agency_info": [
        "agency", "department", "organization", "division",
        "office", "unit", "bureau",
    ],
    "general_info": [
        "help", "info", "information", "overview", "about",
        "what", "how", "tell me",
    ],
}

AGENCY_NAMES: dict[str, str] = {
    "cdss": "CDSS",
    "social services": "CDSS",
    "calhr": "CalHR",
    "human resources": "CalHR",
    "caltrans": "Caltrans",
    "transportation": "Caltrans",
    "dhcs": "DHCS",
    "health care": "DHCS",
    "dmv": "DMV",
    "motor vehicles": "DMV",
    "edd": "EDD",
    "employment": "EDD",
    "dgs": "DGS",
    "general services": "DGS",
    "procurement": "DGS",
    "caloes": "CalOES",
    "cal oes": "CalOES",
    "emergency": "CalOES",
    "doj": "DOJ",
    "justice": "DOJ",
    "attorney general": "DOJ",
    "cdph": "CDPH",
    "public health": "CDPH",
}

DOCUMENT_TYPE_KEYWORDS: dict[str, str] = {
    "policy": "policy",
    "policies": "policy",
    "procedure": "procedure",
    "procedures": "procedure",
    "regulation": "regulation",
    "regulations": "regulation",
    "guidance": "guidance",
    "guide": "guidance",
    "memo": "memo",
    "memorandum": "memo",
    "faq": "faq",
    "frequently asked": "faq",
}

SSN_PATTERN = re.compile(r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b")


class QueryAgent:
    """Detects user intent, extracts entities, and filters PII."""

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

    def _extract_agencies(self, text: str) -> list[str]:
        lower = text.lower()
        found: list[str] = []
        for keyword, agency in AGENCY_NAMES.items():
            if keyword in lower and agency not in found:
                found.append(agency)
        return found

    def _extract_document_types(self, text: str) -> list[str]:
        lower = text.lower()
        found: list[str] = []
        for keyword, doc_type in DOCUMENT_TYPE_KEYWORDS.items():
            if keyword in lower and doc_type not in found:
                found.append(doc_type)
        return found

    def _extract_keywords(self, text: str) -> list[str]:
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "shall", "can",
            "for", "and", "nor", "but", "or", "yet", "so", "at", "by",
            "from", "in", "into", "of", "on", "to", "with", "about",
            "what", "which", "who", "whom", "this", "that", "these",
            "those", "i", "me", "my", "we", "our", "you", "your",
            "he", "she", "it", "they", "them", "their", "find", "search",
            "show", "tell", "get", "look", "up",
        }
        words = re.findall(r"\b[a-z]{3,}\b", text.lower())
        return [w for w in words if w not in stop_words][:10]

    def _detect_pii(self, text: str) -> bool:
        return bool(SSN_PATTERN.search(text))

    async def process(
        self,
        user_input: str,
        agency_filter: list[str] | None = None,
        document_types: list[str] | None = None,
    ) -> SearchQuery:
        intent = self._detect_intent(user_input)
        agencies = agency_filter or self._extract_agencies(user_input)
        doc_types = document_types or self._extract_document_types(user_input)
        keywords = self._extract_keywords(user_input)

        return SearchQuery(
            raw_input=user_input,
            intent=intent,
            agencies=agencies,
            keywords=keywords,
            document_types=doc_types,
        )
