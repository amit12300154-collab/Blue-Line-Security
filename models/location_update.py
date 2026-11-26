from datetime import datetime, timezone
from database import db


class LocationUpdate(db.Model):
    """Stores periodic GPS breadcrumb coordinates for active emergency tracking."""
    __tablename__ = 'location_updates'

    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey('emergency_alerts.id'), nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    def to_dict(self) -> dict:
        """Serialize location update point to dictionary."""
        return {
            'id': self.id,
            'alert_id': self.alert_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'accuracy': self.accuracy,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

    def __repr__(self) -> str:
        return f"<LocationUpdate Alert #{self.alert_id} ({self.latitude}, {self.longitude})>"
