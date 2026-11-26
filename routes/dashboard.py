from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from models.emergency_number import EmergencyNumber
from services.emergency_service import EmergencyService

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    """Landing page introducing Blue Line emergency response system."""
    helplines = EmergencyNumber.query.filter_by(is_active=True).limit(4).all()
    return render_template('index.html', helplines=helplines)


@dashboard_bp.route('/dashboard')
@login_required
def user_dashboard():
    """Main user control center with SOS trigger, status cards, and recent history."""
    summary = EmergencyService.get_dashboard_summary(current_user)
    return render_template(
        'dashboard.html',
        summary=summary,
        demo_mode=current_app.config.get('DEMO_MODE', True),
        impact_threshold=current_app.config.get('IMPACT_THRESHOLD', 25.0),
        emergency_countdown=current_app.config.get('EMERGENCY_COUNTDOWN', 10)
    )


@dashboard_bp.route('/how-it-works')
def how_it_works():
    """Explains workflow: registration, protection, sensor trigger, GPS, police lookup, resolution."""
    return render_template('how_it_works.html')


@dashboard_bp.route('/privacy')
def privacy():
    """Transparency policy regarding location data, sensor triggers, and demo status."""
    return render_template('privacy.html')


@dashboard_bp.route('/settings')
@login_required
def settings():
    """User sensor preferences, countdown durations, and sensitivity threshold."""
    return render_template(
        'settings.html',
        impact_threshold=current_app.config.get('IMPACT_THRESHOLD', 25.0),
        emergency_countdown=current_app.config.get('EMERGENCY_COUNTDOWN', 10),
        demo_mode=current_app.config.get('DEMO_MODE', True)
    )


@dashboard_bp.route('/map')
@login_required
def live_map():
    """Full-screen interactive map showing current location and nearest police stations."""
    active_alert = EmergencyService.get_active_alert_for_user(current_user.id)
    return render_template('map.html', active_alert=active_alert)
