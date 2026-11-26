from database import db
from models.emergency_contact import EmergencyContact
from models.user import User


def test_add_emergency_contact(user_client, app):
    """Test registering a new emergency contact."""
    response = user_client.post('/contacts/add', data={
        'name': 'Ramesh Verma',
        'relationship': 'Father',
        'phone': '+91 9876500005',
        'email': 'father@example.com',
        'priority': 1
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"added successfully" in response.data

    with app.app_context():
        contact = EmergencyContact.query.filter_by(name='Ramesh Verma').first()
        assert contact is not None
        assert contact.relationship == 'Father'
        assert contact.is_active is True


def test_edit_emergency_contact(user_client, app):
    """Test modifying existing emergency contact details."""
    with app.app_context():
        user = User.query.filter_by(email='testuser@example.com').first()
        c = EmergencyContact(
            user_id=user.id,
            name='Old Name',
            relationship='Friend',
            phone='+91 9876543211',
            is_active=True
        )
        db.session.add(c)
        db.session.commit()
        c_id = c.id

    response = user_client.post(f'/contacts/edit/{c_id}', data={
        'name': 'Updated Name',
        'relationship': 'Brother',
        'phone': '+91 9876543299',
        'email': 'bro@example.com',
        'priority': 2
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"updated successfully" in response.data

    with app.app_context():
        updated = db.session.get(EmergencyContact, c_id)
        assert updated.name == 'Updated Name'
        assert updated.relationship == 'Brother'


def test_delete_emergency_contact(user_client, app):
    """Test removing an emergency contact."""
    with app.app_context():
        user = User.query.filter_by(email='testuser@example.com').first()
        c = EmergencyContact(
            user_id=user.id,
            name='To Delete',
            relationship='Other',
            phone='+91 9000000000',
            is_active=True
        )
        db.session.add(c)
        db.session.commit()
        c_id = c.id

    response = user_client.post(f'/contacts/delete/{c_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b"was removed from your emergency list" in response.data

    with app.app_context():
        assert db.session.get(EmergencyContact, c_id) is None
