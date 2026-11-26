from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.contacts import contacts_bp
from routes.emergency import emergency_bp
from routes.api import api_bp
from routes.admin import admin_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'contacts_bp',
    'emergency_bp',
    'api_bp',
    'admin_bp'
]
