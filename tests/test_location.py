from database import db
from models.emergency_alert import EmergencyAlert
from models.location_update import LocationUpdate
from utils.validators import validate_coordinates


def test_coordinate_validation():
    """Test boundary checks on latitude (-90..90) and longitude (-180..180)."""
    valid, _ = validate_coordinates(28.6139, 77.2090)
    assert valid is True

    valid_lat_oob, msg = validate_coordinates(95.0, 77.0)
    assert valid_lat_oob is False
    assert "Latitude must be between" in msg

    valid_lon_oob, msg2 = validate_coordinates(28.0, 190.0)
    assert valid_lon_oob is False
    assert "Longitude must be between" in msg2


def test_live_location_updates(user_client, app):
    """Test recording periodic GPS coordinate breadcrumbs during an active incident."""
    create_resp = user_client.post('/api/emergency/create', json={
        'trigger_type': 'PANIC_BUTTON',
        'emergency_type': 'MEDICAL',
        'latitude': 28.6000,
        'longitude': 77.2000
    })
    alert_id = create_resp.get_json()['data']['alert']['id']

    # Send GPS update 1
    update1 = user_client.post(f'/api/emergency/{alert_id}/location', json={
        'latitude': 28.6010,
        'longitude': 77.2015,
        'accuracy': 8.0
    })
    assert update1.status_code == 200
    assert update1.get_json()['success'] is True

    # Send GPS update 2
    update2 = user_client.post(f'/api/emergency/{alert_id}/location', json={
        'latitude': 28.6025,
        'longitude': 77.2030,
        'accuracy': 5.0
    })
    assert update2.status_code == 200

    with app.app_context():
        breadcrumbs = LocationUpdate.query.filter_by(alert_id=alert_id).all()
        assert len(breadcrumbs) == 2
        alert = db.session.get(EmergencyAlert, alert_id)
        assert alert.latitude == 28.6025  # Latest coordinates updated on alert

    # Resolve alert
    user_client.post(f'/api/emergency/{alert_id}/resolve')

    # Now location updates must be rejected
    update_after = user_client.post(f'/api/emergency/{alert_id}/location', json={
        'latitude': 28.6050,
        'longitude': 77.2050
    })
    assert update_after.status_code == 400
    assert b"Cannot update location for alert with status 'RESOLVED'" in update_after.data
