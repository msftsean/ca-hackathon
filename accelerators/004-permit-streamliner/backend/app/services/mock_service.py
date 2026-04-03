"""Mock service returning sample permit data."""

from datetime import datetime, timedelta
from typing import Any


PERMIT_REQUIREMENTS: dict[str, list[dict[str, Any]]] = {
    "residential": [
        {"name": "Site plan (to scale)", "required": True, "category": "building"},
        {"name": "Floor plan with dimensions", "required": True, "category": "building"},
        {"name": "Title 24 energy compliance", "required": True, "category": "building"},
        {"name": "Structural calculations", "required": True, "category": "building"},
        {"name": "Proof of ownership", "required": True, "category": "zoning"},
        {"name": "CEQA exemption form", "required": False, "category": "environmental"},
    ],
    "addition": [
        {"name": "Site plan showing existing and new", "required": True, "category": "building"},
        {"name": "Floor plan with dimensions", "required": True, "category": "building"},
        {"name": "Title 24 energy compliance", "required": True, "category": "building"},
        {"name": "Structural calculations", "required": True, "category": "building"},
        {"name": "Proof of ownership", "required": True, "category": "zoning"},
        {"name": "Setback verification", "required": True, "category": "zoning"},
    ],
    "new_construction": [
        {"name": "Architectural plans", "required": True, "category": "building"},
        {"name": "Structural engineering plans", "required": True, "category": "building"},
        {"name": "Title 24 energy compliance", "required": True, "category": "building"},
        {"name": "Grading plan", "required": True, "category": "building"},
        {"name": "Soils report", "required": True, "category": "building"},
        {"name": "Fire access plan", "required": True, "category": "fire"},
        {"name": "CEQA clearance", "required": True, "category": "environmental"},
        {"name": "Utility connection letters", "required": True, "category": "building"},
    ],
    "renovation": [
        {"name": "Existing floor plan", "required": True, "category": "building"},
        {"name": "Proposed floor plan", "required": True, "category": "building"},
        {"name": "Scope of work description", "required": True, "category": "building"},
        {"name": "Title 24 energy compliance", "required": False, "category": "building"},
    ],
    "adu": [
        {"name": "Site plan showing ADU location", "required": True, "category": "building"},
        {"name": "Floor plan with dimensions", "required": True, "category": "building"},
        {"name": "Title 24 energy compliance", "required": True, "category": "building"},
        {"name": "Proof of owner occupancy", "required": True, "category": "zoning"},
        {"name": "Setback verification", "required": True, "category": "zoning"},
    ],
    "commercial": [
        {"name": "Architectural plans", "required": True, "category": "building"},
        {"name": "Structural engineering plans", "required": True, "category": "building"},
        {"name": "Fire suppression plan", "required": True, "category": "fire"},
        {"name": "ADA compliance documentation", "required": True, "category": "building"},
        {"name": "Health department approval", "required": True, "category": "health"},
        {"name": "Parking analysis", "required": True, "category": "zoning"},
        {"name": "CEQA clearance", "required": True, "category": "environmental"},
    ],
    "demolition": [
        {"name": "Demolition plan", "required": True, "category": "building"},
        {"name": "Asbestos survey", "required": True, "category": "environmental"},
        {"name": "Lead paint assessment", "required": True, "category": "environmental"},
        {"name": "Utility disconnect confirmation", "required": True, "category": "building"},
    ],
}

ZONING_DATA: dict[str, dict[str, Any]] = {
    "R-1": {
        "zone_code": "R-1",
        "zone_name": "Single-Family Residential",
        "permitted_uses": [
            "Single-family dwelling", "ADU", "Home occupation",
            "Residential care (6 or fewer)", "Parks",
        ],
        "conditional_uses": [
            "Religious assembly", "Schools", "Day care centers",
        ],
        "setbacks": {"front": 20, "side": 5, "rear": 15},
        "max_height_ft": 35.0,
        "lot_coverage_pct": 50.0,
    },
    "C-2": {
        "zone_code": "C-2",
        "zone_name": "General Commercial",
        "permitted_uses": [
            "Retail", "Office", "Restaurant", "Personal services",
            "Medical office", "Financial institution",
        ],
        "conditional_uses": [
            "Drive-through", "Gas station", "Auto repair",
        ],
        "setbacks": {"front": 0, "side": 0, "rear": 10},
        "max_height_ft": 55.0,
        "lot_coverage_pct": 75.0,
    },
    "MU": {
        "zone_code": "MU",
        "zone_name": "Mixed Use",
        "permitted_uses": [
            "Residential above ground floor", "Retail", "Office",
            "Restaurant", "Live/work units",
        ],
        "conditional_uses": [
            "Entertainment venue", "Micro-brewery", "Art gallery",
        ],
        "setbacks": {"front": 0, "side": 0, "rear": 5},
        "max_height_ft": 65.0,
        "lot_coverage_pct": 80.0,
    },
}

ADDRESS_TO_ZONE: dict[str, str] = {
    "123 main st": "R-1",
    "456 oak ave": "R-1",
    "789 broadway": "C-2",
    "100 market st": "C-2",
    "200 mixed blvd": "MU",
}

FEE_SCHEDULES: dict[str, dict[str, str]] = {
    "residential": {
        "building_permit": "$1,200",
        "plan_check": "$780",
        "school_fee": "$4.50/sqft",
        "technology_fee": "$45",
        "total": "$2,025 + school fees",
    },
    "addition": {
        "building_permit": "$800",
        "plan_check": "$520",
        "school_fee": "$4.50/sqft (new area)",
        "technology_fee": "$45",
        "total": "$1,365 + school fees",
    },
    "new_construction": {
        "building_permit": "$3,500",
        "plan_check": "$2,275",
        "grading_permit": "$500",
        "school_fee": "$4.50/sqft",
        "fire_review": "$350",
        "total": "$6,625 + school fees",
    },
    "renovation": {
        "building_permit": "$600",
        "plan_check": "$390",
        "technology_fee": "$45",
        "total": "$1,035",
    },
    "adu": {
        "building_permit": "$0 (waived per SB 13)",
        "plan_check": "$0 (waived)",
        "school_fee": "$0 (waived)",
        "total": "$0 (fees waived for ADU under 750 sqft)",
    },
    "commercial": {
        "building_permit": "$5,000",
        "plan_check": "$3,250",
        "fire_review": "$750",
        "health_review": "$500",
        "parking_review": "$250",
        "total": "$9,750",
    },
    "demolition": {
        "demolition_permit": "$400",
        "asbestos_survey_fee": "$200",
        "total": "$600",
    },
}

SAMPLE_APPLICATIONS = [
    {
        "app_id": "PRM-2025-00042",
        "applicant_name": "Jane Smith",
        "project_type": "addition",
        "project_description": "500 sqft kitchen and bedroom addition",
        "address": "123 Main St",
        "status": "under_review",
        "submitted_at": (datetime.now() - timedelta(days=12)).isoformat(),
        "estimated_completion": (datetime.now() + timedelta(days=18)).isoformat(),
    },
    {
        "app_id": "PRM-2025-00038",
        "applicant_name": "John Doe",
        "project_type": "adu",
        "project_description": "600 sqft detached ADU",
        "address": "456 Oak Ave",
        "status": "approved",
        "submitted_at": (datetime.now() - timedelta(days=25)).isoformat(),
        "estimated_completion": None,
    },
    {
        "app_id": "PRM-2025-00051",
        "applicant_name": "Acme Corp",
        "project_type": "commercial",
        "project_description": "5,000 sqft restaurant build-out",
        "address": "789 Broadway",
        "status": "revision_needed",
        "submitted_at": (datetime.now() - timedelta(days=8)).isoformat(),
        "estimated_completion": (datetime.now() + timedelta(days=35)).isoformat(),
    },
    {
        "app_id": "PRM-2025-00055",
        "applicant_name": "Bob Builder",
        "project_type": "new_construction",
        "project_description": "2,400 sqft single-family residence",
        "address": "100 Market St",
        "status": "submitted",
        "submitted_at": (datetime.now() - timedelta(days=2)).isoformat(),
        "estimated_completion": (datetime.now() + timedelta(days=43)).isoformat(),
    },
]

SLA_DATA = [
    {
        "application_id": "PRM-2025-00042",
        "department": "building",
        "assigned_date": (datetime.now() - timedelta(days=12)).isoformat(),
        "due_date": (datetime.now() + timedelta(days=18)).isoformat(),
        "status": "on_track",
        "days_remaining": 18,
    },
    {
        "application_id": "PRM-2025-00051",
        "department": "fire",
        "assigned_date": (datetime.now() - timedelta(days=8)).isoformat(),
        "due_date": (datetime.now() + timedelta(days=6)).isoformat(),
        "status": "at_risk",
        "days_remaining": 6,
    },
]


class MockPermitService:
    """Returns mock permit data for development and testing."""

    def get_requirements(self, project_type: str) -> list[dict]:
        return PERMIT_REQUIREMENTS.get(
            project_type, PERMIT_REQUIREMENTS["residential"]
        )

    def get_zoning_info(self, address: str) -> dict:
        lower = address.lower()
        zone_code = ADDRESS_TO_ZONE.get(lower, "R-1")
        zone_data = dict(ZONING_DATA[zone_code])
        zone_data["address"] = address
        zone_data["compliant"] = True
        zone_data["issues"] = []
        return zone_data

    def get_fee_schedule(self, project_type: str) -> dict[str, str]:
        return FEE_SCHEDULES.get(project_type, FEE_SCHEDULES["residential"])

    def get_sample_applications(self) -> list[dict]:
        return SAMPLE_APPLICATIONS

    def get_sla_data(self) -> list[dict]:
        return SLA_DATA

    def list_permit_types(self) -> list[str]:
        return list(PERMIT_REQUIREMENTS.keys())
