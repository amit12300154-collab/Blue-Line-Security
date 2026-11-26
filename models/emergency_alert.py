from __future__ import annotations
from datetime import datetime, timezone
from database import db


class EmergencyAlert(db.Model):
    """Emergency incident alert record."""
    __tablename__ = 'emergency_alerts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    trigger_type = db.Column(db.String(50), nullable=False)  # PANIC_BUTTON, IMPACT_DETECTED, VOICE_TRIGGER, MANUAL_REPORT
    emergency_type = db.Column(db.String(50), nullable=False)  # ROBBERY, THEFT, ACCIDENT, MEDICAL, ASSAULT, HARASSMENT, FIRE, OTHER
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default="ACTIVE", nullable=False, index=True)  # ACTIVE, NOTIFIED, RESOLVED, FALSE_ALARM, CANCELLED
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    accuracy = db.Column(db.Float, nullable=True)
    nearest_police_station_id = db.Column(db.Integer, db.ForeignKey('police_stations.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    location_updates = db.relationship(
        'LocationUpdate',
        backref='alert',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    @property
    def google_maps_url(self) -> str | None:
        """Generate direct Google Maps link if coordinates exist."""
        if self.latitude is not None and self.longitude is not None:
            return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
        return None

    def to_dict(self) -> dict:
        """Serialize emergency alert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else None,
            'user_phone': self.user.phone if self.user else None,
            'trigger_type': self.trigger_type,
            'emergency_type': self.emergency_type,
            'description': self.description,
            'status': self.status,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'accuracy': self.accuracy,
            'nearest_police_station_id': self.nearest_police_station_id,
            'nearest_police_station': self.nearest_police_station.to_dict() if self.nearest_police_station else None,
            'google_maps_url': self.google_maps_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }

    def __repr__(self) -> str:
        return f"<EmergencyAlert #{self.id} {self.emergency_type} ({self.status}) - User {self.user_id}>"
