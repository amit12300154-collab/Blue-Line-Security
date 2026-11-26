from database import db


class EmergencyNumber(db.Model):
    """Configurable emergency helpline numbers."""
    __tablename__ = 'emergency_numbers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., National Emergency, Women Helpline, Ambulance
    number = db.Column(db.String(30), nullable=False)  # e.g., 112, 1091, 108
    country = db.Column(db.String(50), default="India", nullable=False)
    state = db.Column(db.String(50), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self) -> dict:
        """Serialize emergency helpline to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'number': self.number,
            'country': self.country,
            'state': self.state,
            'description': self.description,
            'is_active': self.is_active
        }

    def __repr__(self) -> str:
        return f"<EmergencyNumber {self.name}: {self.number}>"
