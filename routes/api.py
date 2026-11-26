from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, current_user, login_required
from database import db
from models.user import User
from models.emergency_contact import EmergencyContact
from models.emergency_alert import EmergencyAlert
from models.police_station import PoliceStation
from models.emergency_number import EmergencyNumber
from services.alert_service import AlertService
from services.location_service import LocationService
from services.police_service import PoliceService
from services.emergency_service import EmergencyService
from utils.helpers import api_response, to_float
from utils.validators import validate_email, validate_phone, validate_coordinates

api_bp = Blueprint('api', __name__, url_prefix='/api')


# ---------------------------------------------------------
# AUTHENTICATION APIS
# ---------------------------------------------------------
@api_bp.route('/login', methods=['POST'])
def api_login():
    """API endpoint to authenticate user."""
    data = request.get_json(silent=True) or request.form
    email = str(data.get('email') or '').strip().lower()
    password = str(data.get('password') or '')

    if not email or not password:
        return api_response(False, "Email and password are required", status_code=400)

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return api_response(False, "Invalid email or password", status_code=401)

    if not user.is_active:
        return api_response(False, "User account is deactivated", status_code=403)

    login_user(user)
    return api_response(True, "Login successful", user.to_dict())


@api_bp.route('/logout', methods=['POST'])
@login_required
def api_logout():
    """API endpoint to logout user."""
    logout_user()
    return api_response(True, "Successfully logged out")


# ---------------------------------------------------------
# EMERGENCY APIS
# ---------------------------------------------------------
@api_bp.route('/emergency/create', methods=['POST'])
@login_required
def api_create_emergency():
    """API endpoint to trigger and create a new emergency alert."""
    data = request.get_json(silent=True) or request.form

    trigger_type = data.get('trigger_type', 'PANIC_BUTTON')
    emergency_type = data.get('emergency_type', 'OTHER')
    description = data.get('description')
    lat = data.get('latitude')
    lon = data.get('longitude')
    acc = data.get('accuracy')

    # Convert coordinates if provided
    lat_val, lon_val, acc_val = to_float(lat), to_float(lon), to_float(acc)

    # Check for active alert
    existing = EmergencyService.get_active_alert_for_user(current_user.id)
    if existing:
        return api_response(
            False,
            "An active emergency is already ongoing. Resolve existing alert first.",
            {'alert': existing.to_dict()},
            status_code=409
        )

    success, message, alert, dispatch_results = AlertService.create_alert(
        user_id=current_user.id,
        trigger_type=trigger_type,
        emergency_type=emergency_type,
        description=description,
        latitude=lat_val,
        longitude=lon_val,
        accuracy=acc_val
    )

    if not success:
        return api_response(False, message, status_code=400)

    alert_summary = AlertService.get_alert_summary(alert.id)
    return api_response(
        True,
        message,
        {
            'alert': alert_summary,
            'notifications_dispatched': dispatch_results
        },
        status_code=201
    )


@api_bp.route('/emergency/<int:alert_id>', methods=['GET'])
@login_required
def api_get_emergency(alert_id: int):
    """API endpoint to get single emergency alert summary and breadcrumbs."""
    alert = db.session.get(EmergencyAlert, alert_id)
    if not alert:
        return api_response(False, "Emergency alert not found", status_code=404)

    if alert.user_id != current_user.id and not current_user.is_admin:
        return api_response(False, "Unauthorized access to alert details", status_code=403)

    summary = AlertService.get_alert_summary(alert.id)
    breadcrumbs = LocationService.get_alert_breadcrumbs(alert.id)
    summary['breadcrumbs'] = breadcrumbs

    return api_response(True, "Alert retrieved successfully", summary)


@api_bp.route('/emergency/<int:alert_id>/location', methods=['POST'])
@login_required
def api_update_location(alert_id: int):
    """API endpoint to record live GPS breadcrumb during emergency."""
    alert = db.session.get(EmergencyAlert, alert_id)
    if not alert:
        return api_response(False, "Emergency alert not found", status_code=404)

    if alert.user_id != current_user.id and not current_user.is_admin:
        return api_response(False, "Unauthorized", status_code=403)

    data = request.get_json(silent=True) or request.form
    lat = data.get('latitude')
    lon = data.get('longitude')
    acc = data.get('accuracy')

    if lat is None or lon is None:
        return api_response(False, "Latitude and Longitude are required", status_code=400)

    success, msg, breadcrumb = LocationService.record_update(alert_id, lat, lon, acc)
    if not success:
        return api_response(False, msg, status_code=400)

    return api_response(True, msg, breadcrumb)


@api_bp.route('/emergency/<int:alert_id>/resolve', methods=['POST'])
@login_required
def api_resolve_emergency(alert_id: int):
    """API endpoint to resolve emergency."""
    success, msg, alert = AlertService.resolve_alert(alert_id, current_user.id, current_user.is_admin)
    if not success:
        return api_response(False, msg, status_code=400)
    return api_response(True, msg, alert.to_dict())


@api_bp.route('/emergency/<int:alert_id>/false-alarm', methods=['POST'])
@login_required
def api_false_alarm(alert_id: int):
    """API endpoint to mark alert as false alarm."""
    success, msg, alert = AlertService.mark_false_alarm(alert_id, current_user.id, current_user.is_admin)
    if not success:
        return api_response(False, msg, status_code=400)
    return api_response(True, msg, alert.to_dict())


# ---------------------------------------------------------
# CONTACTS APIS
# ---------------------------------------------------------
@api_bp.route('/contacts', methods=['GET'])
@login_required
def api_get_contacts():
    """Retrieve all contacts for current user."""
    contacts = EmergencyContact.query.filter_by(user_id=current_user.id).order_by(EmergencyContact.priority.asc()).all()
    return api_response(True, "Contacts retrieved", [c.to_dict() for c in contacts])


@api_bp.route('/contacts', methods=['POST'])
@login_required
def api_create_contact():
    """Create a new contact."""
    data = request.get_json(silent=True) or request.form
    name = data.get('name', '').strip()
    rel = data.get('relationship', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()
    priority = data.get('priority', 1)

    if not name or not rel or not validate_phone(phone):
        return api_response(False, "Valid name, relationship, and phone are required", status_code=400)

    if email and not validate_email(email):
        return api_response(False, "Invalid email address format", status_code=400)

    try:
        priority = int(priority)
    except (ValueError, TypeError):
        priority = 1

    contact = EmergencyContact(
        user_id=current_user.id,
        name=name,
        relationship=rel,
        phone=phone,
        email=email if email else None,
        priority=priority,
        is_active=True
    )
    db.session.add(contact)
    db.session.commit()

    return api_response(True, "Emergency contact added", contact.to_dict(), status_code=201)


@api_bp.route('/contacts/<int:contact_id>', methods=['PUT'])
@login_required
def api_update_contact(contact_id: int):
    """Update contact."""
    contact = EmergencyContact.query.filter_by(id=contact_id, user_id=current_user.id).first()
    if not contact:
        return api_response(False, "Contact not found", status_code=404)

    data = request.get_json(silent=True) or request.form
    name = data.get('name', contact.name).strip()
    rel = data.get('relationship', contact.relationship).strip()
    phone = data.get('phone', contact.phone).strip()
    email = data.get('email', contact.email or '').strip()

    if not validate_phone(phone):
        return api_response(False, "Invalid phone number", status_code=400)

    if email and not validate_email(email):
        return api_response(False, "Invalid email address", status_code=400)

    contact.name = name
    contact.relationship = rel
    contact.phone = phone
    contact.email = email if email else None

    if 'priority' in data:
        try:
            contact.priority = int(data['priority'])
        except (ValueError, TypeError):
            pass

    if 'is_active' in data:
        contact.is_active = bool(data['is_active'])

    db.session.commit()
    return api_response(True, "Contact updated", contact.to_dict())


@api_bp.route('/contacts/<int:contact_id>', methods=['DELETE'])
@login_required
def api_delete_contact(contact_id: int):
    """Delete contact."""
    contact = EmergencyContact.query.filter_by(id=contact_id, user_id=current_user.id).first()
    if not contact:
        return api_response(False, "Contact not found", status_code=404)

    db.session.delete(contact)
    db.session.commit()
    return api_response(True, "Contact deleted")


# ---------------------------------------------------------
# POLICE STATIONS & HELPLINES APIS
# ---------------------------------------------------------
@api_bp.route('/police-stations', methods=['GET'])
def api_get_police_stations():
    """Retrieve verified police stations."""
    stations = PoliceStation.query.all()
    return api_response(True, "Police stations retrieved", [s.to_dict() for s in stations])


@api_bp.route('/police-stations/nearest', methods=['GET'])
def api_get_nearest_police():
    """Query nearest police station using latitude and longitude query parameters."""
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if not lat or not lon:
        return api_response(False, "Query parameters 'lat' and 'lon' are required", status_code=400)

    valid, msg = validate_coordinates(lat, lon)
    if not valid:
        return api_response(False, msg, status_code=400)

    details = PoliceService.get_nearest_station_details(float(lat), float(lon))
    if not details:
        return api_response(False, "No police stations registered in database", status_code=404)

    return api_response(True, "Nearest police station calculated", details)


@api_bp.route('/emergency-numbers', methods=['GET'])
def api_get_emergency_numbers():
    """Retrieve active emergency helpline numbers."""
    numbers = EmergencyNumber.query.filter_by(is_active=True).all()
    return api_response(True, "Emergency numbers retrieved", [n.to_dict() for n in numbers])


@api_bp.route('/dashboard/stats', methods=['GET'])
@login_required
def api_dashboard_stats():
    """Retrieve dashboard status metrics."""
    if current_user.is_admin:
        stats = EmergencyService.get_admin_metrics()
    else:
        stats = EmergencyService.get_dashboard_summary(current_user)
    return api_response(True, "Dashboard statistics retrieved", stats)
