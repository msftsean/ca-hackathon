"""Mock service returning sample emergency alert data."""

from datetime import datetime, timedelta
from app.models.schemas import EmergencyQuery, EmergencyAlert


class MockEmergencyService:
    """Returns mock emergency alert data for development."""

    def get_alerts(self, query: EmergencyQuery) -> list[EmergencyAlert]:
        now = datetime.now()
        return [
            EmergencyAlert(
                alert_id="ALERT-2025-001",
                title="Wildfire Evacuation Warning",
                description="A wildfire evacuation WARNING is in effect for communities in eastern Butte County.",
                severity="severe",
                emergency_type="wildfire",
                affected_areas=["Paradise", "Magalia", "Stirling City"],
                issued_at=now - timedelta(hours=2),
                expires_at=now + timedelta(hours=22),
                instructions="Prepare to evacuate. Gather essential items. Monitor local news for updates.",
                source="Cal OES / CAL FIRE",
            ),
            EmergencyAlert(
                alert_id="ALERT-2025-002",
                title="Flood Watch",
                description="A flood watch is in effect for low-lying areas along the Sacramento River.",
                severity="moderate",
                emergency_type="flood",
                affected_areas=["Sacramento", "West Sacramento", "Yolo County"],
                issued_at=now - timedelta(hours=6),
                expires_at=now + timedelta(hours=18),
                instructions="Avoid flood-prone areas. Do not drive through standing water.",
                source="Cal OES / NWS",
            ),
        ]
