"""Mock service returning sample benefits data."""

from typing import Any


PROGRAMS_DB: dict[str, dict[str, Any]] = {
    "calfresh": {
        "program_id": "calfresh",
        "name": "CalFresh",
        "description": (
            "CalFresh (formerly Food Stamps/SNAP) provides monthly food benefits "
            "to low-income individuals and families to help buy nutritious food."
        ),
        "agency": "CDSS",
        "requirements": [
            "Be a California resident",
            "Be a U.S. citizen or qualified non-citizen",
            "Meet gross and net income limits",
            "Have limited resources (varies by household)",
            "Register for work if able-bodied adult without dependents",
        ],
        "documents_needed": [
            "Government-issued photo ID",
            "Proof of income (pay stubs, employer statement)",
            "Proof of California residency (utility bill, lease agreement)",
            "Social Security numbers for all household members",
            "Proof of immigration status if non-citizen",
            "Bank statements for the last 30 days",
        ],
        "income_limits": {
            "household_1": "$2,510/month gross",
            "household_2": "$3,408/month gross",
            "household_3": "$4,304/month gross",
            "household_4": "$5,200/month gross",
        },
        "policy_citation": "CalFresh eligibility per MPP 63-503",
        "policy_ref": "MPP 63-503",
    },
    "calworks": {
        "program_id": "calworks",
        "name": "CalWORKs",
        "description": (
            "CalWORKs provides temporary cash aid and services to families with "
            "children who have little or no income."
        ),
        "agency": "CDSS",
        "requirements": [
            "Have a child under 18 (or 19 if full-time student)",
            "Be a California resident",
            "Be a U.S. citizen or qualified non-citizen",
            "Meet income and resource limits",
            "Participate in welfare-to-work activities",
            "Cooperate with child support enforcement",
        ],
        "documents_needed": [
            "Birth certificates for children",
            "Government-issued photo ID",
            "Proof of income",
            "Proof of residency",
            "Social Security cards",
            "School enrollment verification (for children 16-18)",
        ],
        "income_limits": {
            "household_1": "$1,160/month gross",
            "household_2": "$1,598/month gross",
            "household_3": "$1,920/month gross",
            "household_4": "$2,280/month gross",
        },
        "policy_citation": "CalWORKs eligibility per MPP 44-211",
        "policy_ref": "MPP 44-211",
    },
    "general_relief": {
        "program_id": "general_relief",
        "name": "General Relief",
        "description": (
            "General Relief provides cash assistance to indigent adults who are "
            "not eligible for federal or state assistance programs."
        ),
        "agency": "County DPSS",
        "requirements": [
            "Be a county resident",
            "Be at least 18 years old",
            "Not eligible for other aid programs",
            "Meet county income and resource limits",
            "Cooperate with employability plan",
        ],
        "documents_needed": [
            "Government-issued photo ID",
            "Proof of county residency",
            "Proof of income (if any)",
            "Medical documentation (if claiming disability)",
        ],
        "income_limits": {
            "household_1": "$625/month gross",
        },
        "policy_citation": "General Relief per WIC §17000",
        "policy_ref": "WIC §17000",
    },
    "capi": {
        "program_id": "capi",
        "name": "CAPI (Cash Assistance Program for Immigrants)",
        "description": (
            "CAPI provides cash benefits to aged, blind, and disabled non-citizens "
            "who are ineligible for SSI/SSP due to their immigration status."
        ),
        "agency": "CDSS",
        "requirements": [
            "Be aged (65+), blind, or disabled",
            "Be a legal non-citizen ineligible for SSI/SSP",
            "Be a California resident",
            "Meet income and resource limits",
            "Not be receiving SSI/SSP",
        ],
        "documents_needed": [
            "Immigration documents",
            "Government-issued photo ID",
            "Proof of age, blindness, or disability",
            "Proof of California residency",
            "Proof of income and resources",
        ],
        "income_limits": {
            "individual": "$1,971/month gross",
            "couple": "$2,915/month gross",
        },
        "policy_citation": "CAPI eligibility per MPP 49-020",
        "policy_ref": "MPP 49-020",
    },
}

COUNTY_OFFICES: dict[str, dict[str, str]] = {
    "Los Angeles": {
        "name": "Los Angeles County DPSS",
        "address": "12860 Crossroads Pkwy S, City of Industry, CA 91746",
        "phone": "(866) 613-3777",
        "hours": "Mon-Fri 8:00 AM - 5:00 PM",
    },
    "San Diego": {
        "name": "San Diego County HHSA",
        "address": "1255 Imperial Ave, Suite 100, San Diego, CA 92101",
        "phone": "(866) 262-9881",
        "hours": "Mon-Fri 7:30 AM - 5:00 PM",
    },
    "San Francisco": {
        "name": "San Francisco HSA",
        "address": "1235 Mission St, San Francisco, CA 94103",
        "phone": "(415) 557-5000",
        "hours": "Mon-Fri 8:00 AM - 5:00 PM",
    },
    "Sacramento": {
        "name": "Sacramento County DHA",
        "address": "2700 Fulton Ave, Sacramento, CA 95821",
        "phone": "(916) 874-3100",
        "hours": "Mon-Fri 8:00 AM - 5:00 PM",
    },
}

ELIGIBILITY_SCENARIOS: dict[str, dict] = {
    "single_low_income": {
        "program": "CalFresh",
        "likely_eligible": True,
        "confidence": 0.90,
        "factors": [
            "Income below gross limit for household of 1",
            "California resident",
            "U.S. citizen or qualified non-citizen",
        ],
        "next_steps": [
            "Apply online at BenefitsCal.com",
            "Gather proof of income and residency",
            "Schedule eligibility interview",
        ],
    },
    "family_with_children": {
        "program": "CalWORKs",
        "likely_eligible": True,
        "confidence": 0.85,
        "factors": [
            "Has dependent children",
            "Income below CalWORKs limits",
            "Meets residency requirements",
        ],
        "next_steps": [
            "Apply at BenefitsCal.com",
            "Bring birth certificates and ID to interview",
            "Prepare for welfare-to-work orientation",
        ],
    },
}


class MockBenefitsService:
    """Returns mock benefits data for development and testing."""

    def get_program(self, program_id: str) -> dict | None:
        return PROGRAMS_DB.get(program_id)

    def list_programs(self) -> list[dict]:
        return [
            {
                "program_id": pid,
                "name": p["name"],
                "description": p["description"],
                "agency": p["agency"],
                "requirements": p["requirements"],
                "documents_needed": p["documents_needed"],
            }
            for pid, p in PROGRAMS_DB.items()
        ]

    def get_county_office(self, county: str) -> dict[str, str]:
        return COUNTY_OFFICES.get(
            county,
            {
                "name": f"{county} County Office",
                "address": "Contact your local county DPSS",
                "phone": "1-877-847-3663",
                "hours": "Mon-Fri 8:00 AM - 5:00 PM",
            },
        )

    def get_eligibility_scenario(self, scenario: str) -> dict | None:
        return ELIGIBILITY_SCENARIOS.get(scenario)
