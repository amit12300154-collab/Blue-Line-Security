def test_login_rejects_external_redirect(client):
    """The ?next= parameter must never send users to another website."""
    response = client.post(
        '/login?next=//evil.example.com',
        data={'email': 'testuser@example.com', 'password': 'Secret123'}
    )
    assert response.status_code == 302
    assert 'evil.example.com' not in response.headers['Location']


def test_trigger_with_bad_coordinates_does_not_crash(user_client):
    """Garbage GPS values must be ignored instead of causing a 500 error."""
    response = user_client.post('/emergency/trigger', data={
        'trigger_type': 'PANIC_BUTTON',
        'emergency_type': 'FIRE',
        'latitude': 'abc',
        'longitude': 'xyz'
    })
    assert response.status_code == 302


def test_live_location_update_flow(user_client):
    """Creating an alert then streaming a GPS breadcrumb must work end to end."""
    created = user_client.post('/api/emergency/create', json={
        'trigger_type': 'PANIC_BUTTON',
        'emergency_type': 'FIRE',
        'latitude': 28.6139,
        'longitude': 77.2090
    })
    assert created.status_code == 201
    alert_id = created.get_json()['data']['alert']['id']

    update = user_client.post(f'/api/emergency/{alert_id}/location', json={
        'latitude': 28.6150,
        'longitude': 77.2100,
        'accuracy': 12
    })
    assert update.status_code == 200
