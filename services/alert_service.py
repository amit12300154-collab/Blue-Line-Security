from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from database import db
from models.emergency_alert import EmergencyAlert
from models.emergency_contact import EmergencyContact
from models.user import User
from models.police_station import PoliceStation
from services.police_service import PoliceService
from services.notification_service import NotificationService
from utils.validators import validate_emergency_payload


class AlertService:
    """Core domain service for emergency alert lifecycle management."""

    @staticmethod
    def create_alert(
        user_id: int,
        trigger_type: str,
        emergency_type: str,
        description: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        accuracy: Optional[float] = None
    ) -> Tuple[bool, str, Optional[EmergencyAlert], Optional[list]]:
        """
        Create and persist a new emergency alert, calculate nearest police station,
        and dispatch notifications to active emergency contacts.
        """
        payload = {
            'trigger_type': trigger_type,
            'emergency_type': emergency_type,
            'latitude': latitude,
            'longitude': longitude
        }
        is_valid, err = validate_emergency_payload(payload)
        if not is_valid:
            return False, err, None, None

        user = db.session.get(User, user_id)
        if not user:
            return False, "User not found", None, None

        # Find nearest police station if coordinates are provided
        nearest_station = None
        if latitude is not None and longitude is not None:
            nearest_station, _ = PoliceService.find_nearest_station(float(latitude), float(longitude))

        alert = EmergencyAlert(
            user_id=user.id,
            trigger_type=trigger_type.upper(),
            emergency_type=emergency_type.upper(),
            description=description.strip() if description else None,
            status='ACTIVE',
            latitude=float(latitude) if latitude is not None else None,
            longitude=float(longitude) if longitude is not None else None,
            accuracy=float(accuracy) if accuracy is not None else None,
            nearest_police_station_id=nearest_station.id if nearest_station else None,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(alert)
        db.session.commit()

        # Notify active contacts
        contacts = EmergencyContact.query.filter_by(user_id=user.id, is_active=True).all()
        dispatch_results = NotificationService.notify_emergency_contacts(
            alert=alert,
            user=user,
            contacts=contacts,
            nearest_police=nearest_station
        )

        return True, "Emergency alert created successfully", alert, dispatch_results

    @staticmethod
    def resolve_alert(alert_id: int, user_id: int, is_admin: bool = False) -> Tuple[bool, str, Optional[EmergencyAlert]]:
        """Mark an emergency alert as RESOLVED."""
        alert = db.session.get(EmergencyAlert, alert_id)
        if not alert:
            return False, "Emergency alert not found", None

        if not is_admin and alert.user_id != user_id:
            return False, "Unauthorized to resolve this alert", None

        if alert.status in ('RESOLVED', 'FALSE_ALARM', 'CANCELLED'):
            return False, f"Alert is already in '{alert.status}' state", alert

        alert.status = 'RESOLVED'
        alert.resolved_at = datetime.now(timezone.utc)
        db.session.commit()

        return True, "Emergency alert marked as resolved", alert

    @staticmethod
    def mark_false_alarm(alert_id: int, user_id: int, is_admin: bool = False) -> Tuple[bool, str, Optional[EmergencyAlert]]:
        """Mark an emergency alert as FALSE_ALARM."""
        alert = db.session.get(EmergencyAlert, alert_id)
        if not alert:
            return False, "Emergency alert not found", None

        if not is_admin and alert.user_id != user_id:
            return False, "Unauthorized to update this alert", None

        if alert.status in ('RESOLVED', 'FALSE_ALARM', 'CANCELLED'):
            return False, f"Alert is already in '{alert.status}' state", alert

        alert.status = 'FALSE_ALARM'
        alert.resolved_at = datetime.now(timezone.utc)
        db.session.commit()

        return True, "Emergency alert marked as false alarm", alert

    @staticmethod
    def get_alert_summary(alert_id: int) -> Optional[Dict[str, Any]]:
        """Get enriched alert dictionary including nearest police station and contacts."""
        alert = db.session.get(EmergencyAlert, alert_id)
        if not alert:
            return None

        data = alert.to_dict()
        if alert.latitude is not None and alert.longitude is not None:
            police_details = PoliceService.get_nearest_station_details(alert.latitude, alert.longitude)
            data['nearest_police_station_details'] = police_details
        else:
            data['nearest_police_station_details'] = None

        return data
