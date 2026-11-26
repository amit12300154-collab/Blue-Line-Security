from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models.emergency_alert import EmergencyAlert
from models.emergency_number import EmergencyNumber
from services.alert_service import AlertService
from services.emergency_service import EmergencyService
from services.location_service import LocationService
from services.police_service import PoliceService
from utils.helpers import to_float

emergency_bp = Blueprint('emergency', __name__, url_prefix='/emergency')


@emergency_bp.route('/', methods=['GET'])
@login_required
def active_emergency_screen():
    """Emergency response screen showing active alert, live location, and police station."""
    active_alert = EmergencyService.get_active_alert_for_user(current_user.id)
    if not active_alert:
        flash("No active emergency in progress. You are safe.", "info")
        return redirect(url_for('dashboard.user_dashboard'))

    nearest_police = None
    if active_alert.latitude is not None and active_alert.longitude is not None:
        nearest_police = PoliceService.get_nearest_station_details(active_alert.latitude, active_alert.longitude)

    helpline = EmergencyNumber.query.filter_by(number='112').first()
    if not helpline:
        helpline = EmergencyNumber.query.first()

    return render_template(
        'emergency.html',
        alert=active_alert,
        nearest_police=nearest_police,
        helpline=helpline,
        demo_mode=current_app.config.get('DEMO_MODE', True)
    )


@emergency_bp.route('/trigger', methods=['POST'])
@login_required
def trigger_emergency():
    """Trigger an emergency alert from form input or SOS button."""
    trigger_type = request.form.get('trigger_type', 'PANIC_BUTTON').upper()
    emergency_type = request.form.get('emergency_type', 'OTHER').upper()
    description = request.form.get('description', '').strip()
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')
    acc = request.form.get('accuracy')

    lat_val, lon_val, acc_val = to_float(lat), to_float(lon), to_float(acc)

    # Check if there's already an active alert
    active = EmergencyService.get_active_alert_for_user(current_user.id)
    if active:
        flash("An emergency alert is already active!", "warning")
        return redirect(url_for('emergency.active_emergency_screen'))

    success, msg, alert, dispatch_results = AlertService.create_alert(
        user_id=current_user.id,
        trigger_type=trigger_type,
        emergency_type=emergency_type,
        description=description,
        latitude=lat_val,
        longitude=lon_val,
        accuracy=acc_val
    )

    if not success:
        flash(f"Could not activate alert: {msg}", "danger")
        return redirect(url_for('dashboard.user_dashboard'))

    notified_count = len([r for r in dispatch_results if r['status'] == 'SENT']) if dispatch_results else 0
    flash(f"Emergency Alert Activated! {notified_count} emergency contact(s) notified.", "danger")
    return redirect(url_for('emergency.active_emergency_screen'))


@emergency_bp.route('/resolve/<int:alert_id>', methods=['POST'])
@login_required
def resolve_emergency(alert_id: int):
    """Mark emergency alert as resolved / user is safe."""
    success, msg, alert = AlertService.resolve_alert(alert_id, current_user.id, current_user.is_admin)
    if success:
        flash("Emergency marked as RESOLVED. Glad to know you are safe!", "success")
    else:
        flash(f"Error: {msg}", "danger")
    return redirect(url_for('dashboard.user_dashboard'))


@emergency_bp.route('/false-alarm/<int:alert_id>', methods=['POST'])
@login_required
def false_alarm(alert_id: int):
    """Mark alert as false alarm."""
    success, msg, alert = AlertService.mark_false_alarm(alert_id, current_user.id, current_user.is_admin)
    if success:
        flash("Alert marked as FALSE ALARM. Live tracking stopped.", "info")
    else:
        flash(f"Error: {msg}", "danger")
    return redirect(url_for('dashboard.user_dashboard'))


@emergency_bp.route('/history')
@login_required
def history():
    """View past emergency incident records for the current user."""
    alerts = (
        EmergencyAlert.query
        .filter_by(user_id=current_user.id)
        .order_by(EmergencyAlert.created_at.desc())
        .all()
    )
    return render_template('history.html', alerts=alerts)


@emergency_bp.route('/view/<int:alert_id>')
@login_required
def view_alert(alert_id: int):
    """View details and trajectory of an alert."""
    alert = EmergencyAlert.query.get_or_404(alert_id)
    # Check ownership or admin
    if alert.user_id != current_user.id and not current_user.is_admin:
        flash("You do not have permission to view this incident.", "danger")
        return redirect(url_for('emergency.history'))

    breadcrumbs = LocationService.get_alert_breadcrumbs(alert.id)
    police_details = None
    if alert.latitude is not None and alert.longitude is not None:
        police_details = PoliceService.get_nearest_station_details(alert.latitude, alert.longitude)

    return render_template(
        'admin/alert_details.html' if current_user.is_admin else 'history.html',
        alert=alert,
        breadcrumbs=breadcrumbs,
        police_details=police_details,
        single_view=True
    )
