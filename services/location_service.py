from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from database import db
from models.emergency_alert import EmergencyAlert
from models.location_update import LocationUpdate
from services.police_service import PoliceService
from utils.validators import validate_coordinates


class LocationService:
    """Service to handle GPS coordinate ingestion, validation, and history tracking."""

    @staticmethod
    def record_update(alert_id: int, lat: float, lon: float, accuracy: Optional[float] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Record a GPS coordinate ping for an active emergency alert.
        Updates latest coordinates on the alert and attaches a location breadcrumb.
        """
        is_valid, error_msg = validate_coordinates(lat, lon)
        if not is_valid:
            return False, error_msg, None

        alert = db.session.get(EmergencyAlert, alert_id)
        if not alert:
            return False, "Emergency alert not found", None

        if alert.status in ('RESOLVED', 'FALSE_ALARM', 'CANCELLED'):
            return False, f"Cannot update location for alert with status '{alert.status}'", None

        # Create breadcrumb record
        update_entry = LocationUpdate(
            alert_id=alert.id,
            latitude=float(lat),
            longitude=float(lon),
            accuracy=float(accuracy) if accuracy is not None else None,
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(update_entry)

        # Update latest coordinates on alert
        alert.latitude = float(lat)
        alert.longitude = float(lon)
        if accuracy is not None:
            alert.accuracy = float(accuracy)

        # If nearest police station not yet associated, calculate and assign
        if not alert.nearest_police_station_id:
            nearest_station, _ = PoliceService.find_nearest_station(alert.latitude, alert.longitude)
            if nearest_station:
                alert.nearest_police_station_id = nearest_station.id

        db.session.commit()

        return True, "Location recorded successfully", update_entry.to_dict()

    @staticmethod
    def get_alert_breadcrumbs(alert_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve historical coordinate points for mapping alert movement trajectory."""
        updates = (
            LocationUpdate.query
            .filter_by(alert_id=alert_id)
            .order_by(LocationUpdate.timestamp.asc())
            .limit(limit)
            .all()
        )
        return [u.to_dict() for u in updates]

