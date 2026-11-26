from typing import Optional, Dict, Any
from models.emergency_alert import EmergencyAlert
from models.user import User
from models.emergency_contact import EmergencyContact
from models.police_station import PoliceStation
from models.emergency_number import EmergencyNumber
from services.alert_service import AlertService


class EmergencyService:
    """Orchestration service for emergency state management and system metrics."""

    @staticmethod
    def get_active_alert_for_user(user_id: int) -> Optional[EmergencyAlert]:
        """Find the currently active emergency alert for a given user, if any."""
        return (
            EmergencyAlert.query
            .filter_by(user_id=user_id, status='ACTIVE')
            .order_by(EmergencyAlert.created_at.desc())
            .first()
        )

    @staticmethod
    def get_dashboard_summary(user: User) -> Dict[str, Any]:
        """Compile complete status metrics for a user's dashboard."""
        active_alert = EmergencyService.get_active_alert_for_user(user.id)
        contacts_count = EmergencyContact.query.filter_by(user_id=user.id, is_active=True).count()
        recent_alerts = (
            EmergencyAlert.query
            .filter_by(user_id=user.id)
            .order_by(EmergencyAlert.created_at.desc())
            .limit(5)
            .all()
        )
        emergency_numbers = EmergencyNumber.query.filter_by(is_active=True).all()

        return {
            'user': user.to_dict(),
            'has_active_alert': active_alert is not None,
            'active_alert': active_alert.to_dict() if active_alert else None,
            'contacts_count': contacts_count,
            'recent_alerts': [a.to_dict() for a in recent_alerts],
            'emergency_numbers': [n.to_dict() for n in emergency_numbers]
        }

    @staticmethod
    def get_admin_metrics() -> Dict[str, Any]:
        """Compile system-wide metrics for administrator dashboard."""
        total_users = User.query.filter_by(role='USER').count()
        total_admins = User.query.filter_by(role='ADMIN').count()
        active_emergencies = EmergencyAlert.query.filter_by(status='ACTIVE').count()
        resolved_emergencies = EmergencyAlert.query.filter_by(status='RESOLVED').count()
        false_alarms = EmergencyAlert.query.filter_by(status='FALSE_ALARM').count()
        total_contacts = EmergencyContact.query.count()
        total_police_stations = PoliceStation.query.count()
        verified_police_stations = PoliceStation.query.filter_by(is_verified=True).count()
        emergency_numbers_count = EmergencyNumber.query.count()

        return {
            'total_users': total_users,
            'total_admins': total_admins,
            'active_emergencies': active_emergencies,
            'resolved_emergencies': resolved_emergencies,
            'false_alarms': false_alarms,
            'total_contacts': total_contacts,
            'total_police_stations': total_police_stations,
            'verified_police_stations': verified_police_stations,
            'emergency_numbers_count': emergency_numbers_count
        }
