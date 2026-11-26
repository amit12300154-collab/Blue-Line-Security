from datetime import datetime, timezone
from database import db


class PoliceStation(db.Model):
    """Police station records for location-based distance matching."""
    __tablename__ = 'police_stations'

    id = db.Column(db.Integer, primary_key=True)
    station_name = db.Column(db.String(150), nullable=False, index=True)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False, index=True)
    state = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    phone_number = db.Column(db.String(50), nullable=True)
    emergency_number = db.Column(db.String(50), default="112", nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    alerts = db.relationship('EmergencyAlert', backref='nearest_police_station', lazy='dynamic')

    def to_dict(self) -> dict:
        """Serialize police station to dictionary."""
        return {
            'id': self.id,
            'station_name': self.station_name,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'phone_number': self.phone_number,
            'emergency_number': self.emergency_number,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self) -> str:
        return f"<PoliceStation {self.station_name}, {self.city}>"
