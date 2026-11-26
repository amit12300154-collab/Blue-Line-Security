from database import db
from models.emergency_alert import EmergencyAlert
from models.user import User


def test_emergency_alert_creation_and_resolve(user_client, app):
    """Test full cycle of emergency creation via API, nearest station association, and resolution."""
    # 1. Trigger Alert
    response = user_client.post('/api/emergency/create', json={
        'trigger_type': 'PANIC_BUTTON',
        'emergency_type': 'ROBBERY',
        'description': 'Someone attempted to take my wallet.',
        'latitude': 28.6310,
        'longitude': 77.2160,
        'accuracy': 15.0
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    alert_id = data['data']['alert']['id']

    with app.app_context():
        alert = db.session.get(EmergencyAlert, alert_id)
        assert alert is not None
        assert alert.status == 'ACTIVE'
        assert alert.emergency_type == 'ROBBERY'
        assert alert.trigger_type == 'PANIC_BUTTON'
        assert alert.nearest_police_station_id is not None  # Matched Central Police Station

    # 2. Cannot create duplicate active alert while one is ongoing
    dup_resp = user_client.post('/api/emergency/create', json={
        'trigger_type': 'PANIC_BUTTON',
        'emergency_type': 'THEFT'
    })
    assert dup_resp.status_code == 409
    assert b"active emergency is already ongoing" in dup_resp.data

    # 3. Resolve Alert
    resolve_resp = user_client.post(f'/api/emergency/{alert_id}/resolve')
    assert resolve_resp.status_code == 200
    res_data = resolve_resp.get_json()
    assert res_data['success'] is True
    assert res_data['data']['status'] == 'RESOLVED'

    with app.app_context():
        resolved_alert = db.session.get(EmergencyAlert, alert_id)
        assert resolved_alert.status == 'RESOLVED'
        assert resolved_alert.resolved_at is not None


def test_false_alarm_marking(user_client, app):
    """Test marking an active alert as FALSE_ALARM."""
    # Create alert
    create_resp = user_client.post('/api/emergency/create', json={
        'trigger_type': 'IMPACT_DETECTED',
        'emergency_type': 'ACCIDENT',
        'latitude': 28.6000,
        'longitude': 77.2000
    })
    alert_id = create_resp.get_json()['data']['alert']['id']

    # Mark False Alarm
    fa_resp = user_client.post(f'/api/emergency/{alert_id}/false-alarm')
    assert fa_resp.status_code == 200
    assert fa_resp.get_json()['data']['status'] == 'FALSE_ALARM'

    with app.app_context():
        alert = db.session.get(EmergencyAlert, alert_id)
        assert alert.status == 'FALSE_ALARM'
