from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from database import db
from models.user import User
from models.emergency_alert import EmergencyAlert
from models.police_station import PoliceStation
from models.emergency_number import EmergencyNumber
from services.emergency_service import EmergencyService
from services.location_service import LocationService
from services.police_service import PoliceService
from services.alert_service import AlertService
from utils.helpers import admin_required
from utils.validators import validate_coordinates

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Main administrative control panel with live metric counters and active alerts."""
    metrics = EmergencyService.get_admin_metrics()
    active_alerts = (
        EmergencyAlert.query
        .filter_by(status='ACTIVE')
        .order_by(EmergencyAlert.created_at.desc())
        .all()
    )
    return render_template(
        'admin/dashboard.html',
        metrics=metrics,
        active_alerts=active_alerts
    )


# ---------------------------------------------------------
# ALERT MANAGEMENT
# ---------------------------------------------------------
@admin_bp.route('/alerts')
@login_required
@admin_required
def list_alerts():
    """List all emergency alerts with optional status filter."""
    status_filter = request.args.get('status')
    query = EmergencyAlert.query.order_by(EmergencyAlert.created_at.desc())
    if status_filter:
        query = query.filter_by(status=status_filter.upper())
    alerts = query.all()
    return render_template('admin/alerts.html', alerts=alerts, current_filter=status_filter)


@admin_bp.route('/alerts/<int:alert_id>')
@login_required
@admin_required
def alert_details(alert_id: int):
    """View complete incident breakdown, breadcrumbs trail, and nearest station."""
    alert = EmergencyAlert.query.get_or_404(alert_id)
    breadcrumbs = LocationService.get_alert_breadcrumbs(alert.id)
    police_details = None
    if alert.latitude is not None and alert.longitude is not None:
        police_details = PoliceService.get_nearest_station_details(alert.latitude, alert.longitude)

    return render_template(
        'admin/alert_details.html',
        alert=alert,
        breadcrumbs=breadcrumbs,
        police_details=police_details
    )


@admin_bp.route('/alerts/<int:alert_id>/resolve', methods=['POST'])
@login_required
@admin_required
def resolve_alert_admin(alert_id: int):
    """Resolve an emergency directly from admin dashboard."""
    success, msg, alert = AlertService.resolve_alert(alert_id, user_id=0, is_admin=True)
    if success:
        flash(f"Incident #{alert_id} was marked as resolved.", "success")
    else:
        flash(f"Error: {msg}", "danger")
    return redirect(url_for('admin.dashboard'))


# ---------------------------------------------------------
# USER MANAGEMENT
# ---------------------------------------------------------
@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    """List all registered system users."""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_details(user_id: int):
    """Detailed view of a specific user with contacts and incidents."""
    user = User.query.get_or_404(user_id)
    return render_template('admin/user_details.html', user=user)


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id: int):
    """Activate or deactivate user access."""
    user = User.query.get_or_404(user_id)
    if user.is_admin and user.email == 'admin@blueline.local':
        flash("The primary system administrator cannot be deactivated.", "warning")
        return redirect(url_for('admin.list_users'))

    user.is_active = not user.is_active
    db.session.commit()
    flash(f"User '{user.full_name}' status updated to {'Active' if user.is_active else 'Deactivated'}.", "info")
    return redirect(url_for('admin.list_users'))


# ---------------------------------------------------------
# POLICE STATIONS MANAGEMENT
# ---------------------------------------------------------
@admin_bp.route('/police-stations')
@login_required
@admin_required
def list_police_stations():
    """Manage database records of police stations."""
    stations = PoliceStation.query.order_by(PoliceStation.state, PoliceStation.city).all()
    return render_template('admin/police_stations.html', stations=stations)


@admin_bp.route('/police-stations/add', methods=['POST'])
@login_required
@admin_required
def add_police_station():
    """Register a new police station."""
    name = request.form.get('station_name', '').strip()
    address = request.form.get('address', '').strip()
    city = request.form.get('city', '').strip()
    state = request.form.get('state', '').strip()
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')
    phone = request.form.get('phone_number', '').strip()
    emergency_num = request.form.get('emergency_number', '112').strip()
    is_verified = bool(request.form.get('is_verified'))

    if not name or not address or not city or not state:
        flash("Name, Address, City, and State are required.", "danger")
        return redirect(url_for('admin.list_police_stations'))

    valid_coords, msg = validate_coordinates(lat, lon)
    if not valid_coords:
        flash(msg, "danger")
        return redirect(url_for('admin.list_police_stations'))

    station = PoliceStation(
        station_name=name,
        address=address,
        city=city,
        state=state,
        latitude=float(lat),
        longitude=float(lon),
        phone_number=phone if phone else None,
        emergency_number=emergency_num,
        is_verified=is_verified
    )
    db.session.add(station)
    db.session.commit()
    flash(f"Police Station '{name}' registered successfully.", "success")
    return redirect(url_for('admin.list_police_stations'))


@admin_bp.route('/police-stations/edit/<int:station_id>', methods=['POST'])
@login_required
@admin_required
def edit_police_station(station_id: int):
    """Edit police station."""
    station = PoliceStation.query.get_or_404(station_id)
    station.station_name = request.form.get('station_name', station.station_name).strip()
    station.address = request.form.get('address', station.address).strip()
    station.city = request.form.get('city', station.city).strip()
    station.state = request.form.get('state', station.state).strip()

    lat = request.form.get('latitude', station.latitude)
    lon = request.form.get('longitude', station.longitude)
    valid_coords, msg = validate_coordinates(lat, lon)
    if not valid_coords:
        flash(msg, "danger")
        return redirect(url_for('admin.list_police_stations'))

    station.latitude = float(lat)
    station.longitude = float(lon)
    station.phone_number = request.form.get('phone_number', station.phone_number)
    station.emergency_number = request.form.get('emergency_number', station.emergency_number)
    station.is_verified = bool(request.form.get('is_verified'))

    db.session.commit()
    flash(f"Police station '{station.station_name}' updated.", "success")
    return redirect(url_for('admin.list_police_stations'))


@admin_bp.route('/police-stations/delete/<int:station_id>', methods=['POST'])
@login_required
@admin_required
def delete_police_station(station_id: int):
    """Delete a police station."""
    station = PoliceStation.query.get_or_404(station_id)
    name = station.station_name
    db.session.delete(station)
    db.session.commit()
    flash(f"Police station '{name}' removed.", "info")
    return redirect(url_for('admin.list_police_stations'))


@admin_bp.route('/police-stations/toggle-verify/<int:station_id>', methods=['POST'])
@login_required
@admin_required
def toggle_verify_police_station(station_id: int):
    """Toggle verified status of a police station."""
    station = PoliceStation.query.get_or_404(station_id)
    station.is_verified = not station.is_verified
    db.session.commit()
    status = "verified" if station.is_verified else "unverified"
    flash(f"Police station '{station.station_name}' marked as {status}.", "info")
    return redirect(url_for('admin.list_police_stations'))


# ---------------------------------------------------------
# EMERGENCY NUMBERS MANAGEMENT
# ---------------------------------------------------------
@admin_bp.route('/emergency-numbers')
@login_required
@admin_required
def list_emergency_numbers():
    """Manage database emergency helpline numbers."""
    numbers = EmergencyNumber.query.order_by(EmergencyNumber.id.asc()).all()
    return render_template('admin/emergency_numbers.html', numbers=numbers)


@admin_bp.route('/emergency-numbers/add', methods=['POST'])
@login_required
@admin_required
def add_emergency_number():
    """Add a new helpline number."""
    name = request.form.get('name', '').strip()
    number = request.form.get('number', '').strip()
    country = request.form.get('country', 'India').strip()
    state = request.form.get('state', '').strip()
    desc = request.form.get('description', '').strip()

    if not name or not number:
        flash("Helpline Name and Number are required.", "danger")
        return redirect(url_for('admin.list_emergency_numbers'))

    entry = EmergencyNumber(
        name=name,
        number=number,
        country=country,
        state=state if state else None,
        description=desc if desc else None,
        is_active=True
    )
    db.session.add(entry)
    db.session.commit()
    flash(f"Helpline '{name} ({number})' added.", "success")
    return redirect(url_for('admin.list_emergency_numbers'))


@admin_bp.route('/emergency-numbers/edit/<int:num_id>', methods=['POST'])
@login_required
@admin_required
def edit_emergency_number(num_id: int):
    """Edit an existing helpline."""
    entry = EmergencyNumber.query.get_or_404(num_id)
    entry.name = request.form.get('name', entry.name).strip()
    entry.number = request.form.get('number', entry.number).strip()
    entry.country = request.form.get('country', entry.country).strip()
    entry.state = request.form.get('state', entry.state)
    entry.description = request.form.get('description', entry.description)
    entry.is_active = bool(request.form.get('is_active'))

    db.session.commit()
    flash(f"Helpline '{entry.name}' updated.", "success")
    return redirect(url_for('admin.list_emergency_numbers'))


@admin_bp.route('/emergency-numbers/delete/<int:num_id>', methods=['POST'])
@login_required
@admin_required
def delete_emergency_number(num_id: int):
    """Delete a helpline."""
    entry = EmergencyNumber.query.get_or_404(num_id)
    name = entry.name
    db.session.delete(entry)
    db.session.commit()
    flash(f"Helpline '{name}' deleted.", "info")
    return redirect(url_for('admin.list_emergency_numbers'))


@admin_bp.route('/emergency-numbers/toggle/<int:num_id>', methods=['POST'])
@login_required
@admin_required
def toggle_emergency_number(num_id: int):
    """Toggle active/inactive helpline status."""
    entry = EmergencyNumber.query.get_or_404(num_id)
    entry.is_active = not entry.is_active
    db.session.commit()
    status = "activated" if entry.is_active else "deactivated"
    flash(f"Helpline '{entry.name}' {status}.", "info")
    return redirect(url_for('admin.list_emergency_numbers'))
