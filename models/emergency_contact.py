from datetime import datetime, timezone
from database import db


class EmergencyContact(db.Model):
    """Emergency contact linked to a user account."""
    __tablename__ = 'emergency_contacts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(50), nullable=False)  # Father, Mother, Brother, Sister, Friend, etc.
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    priority = db.Column(db.Integer, default=1, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self) -> dict:
        """Serialize emergency contact to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'relationship': self.relationship,
            'phone': self.phone,
            'email': self.email,
            'priority': self.priority,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self) -> str:
        return f"<EmergencyContact {self.name} ({self.relationship}) - User {self.user_id}>"
