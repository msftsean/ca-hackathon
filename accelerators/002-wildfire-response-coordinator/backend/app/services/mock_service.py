"""Mock service returning sample wildfire incident data."""

from datetime import datetime
from app.models.schemas import WildfireIncident


class MockWildfireService:
    """Returns mock wildfire incident data for development."""

    def get_incidents(self) -> list[WildfireIncident]:
        return [
            WildfireIncident(
                incident_id="CA-BDF-002847",
                name="Summit Fire",
                location="San Bernardino National Forest",
                county="San Bernardino",
                acres_burned=3450.0,
                containment_pct=25.0,
                status="active",
                latitude=34.15,
                longitude=-117.25,
                started_at=datetime(2025, 7, 15, 14, 30),
            ),
            WildfireIncident(
                incident_id="CA-LNU-001234",
                name="Valley Fire",
                location="Lake County",
                county="Lake",
                acres_burned=780.0,
                containment_pct=60.0,
                status="active",
                latitude=38.85,
                longitude=-122.75,
                started_at=datetime(2025, 7, 12, 9, 15),
            ),
        ]
