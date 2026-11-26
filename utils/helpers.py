from functools import wraps
from flask import jsonify, redirect, url_for, flash, request
from flask_login import current_user


def admin_required(f):
    """Decorator to restrict access to users with ADMIN role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Authentication required'}), 401
            flash('Please log in as an administrator to view this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))

        if not getattr(current_user, 'is_admin', False):
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Administrator access required'}), 403
            flash('Access denied: Administrator privileges required.', 'danger')
            return redirect(url_for('dashboard.user_dashboard'))

        return f(*args, **kwargs)
    return decorated_function


def to_float(value):
    """Convert form/JSON value to float; return None when empty or invalid."""
    if value is None or value == '':
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def api_response(success: bool, message: str, data=None, status_code: int = 200):
    """Standardized JSON API response structure."""
    payload = {
        'success': success,
        'message': message,
        'data': data if data is not None else {}
    }
    return jsonify(payload), status_code
