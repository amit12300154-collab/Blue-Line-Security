from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import db


class User(UserMixin, db.Model):
    """User model representing application users and administrators."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    blood_group = db.Column(db.String(10), nullable=True)
    role = db.Column(db.String(20), default="USER", nullable=False)  # 'USER' or 'ADMIN'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    emergency_contacts = db.relationship(
        'EmergencyContact',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    emergency_alerts = db.relationship(
        'EmergencyAlert',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def set_password(self, password: str) -> None:
        """Hash and store user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify user password against hashed password."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        """Check if user has administrator role."""
        return self.role == "ADMIN"

    def to_dict(self) -> dict:
        """Serialize user object to dictionary."""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'blood_group': self.blood_group,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"
