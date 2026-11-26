import pytest
from app import create_app
from database import db
from models.user import User
from models.police_station import PoliceStation
from models.emergency_number import EmergencyNumber


@pytest.fixture
def app():
    """Create test application configured with in-memory database."""
    application = create_app('testing')
    with application.app_context():
        db.create_all()

        # Create test user
        user = User(
            full_name="Regular Tester",
            email="testuser@example.com",
            phone="+91 9876543210",
            address="Test Street, Delhi",
            blood_group="O+",
            role="USER",
            is_active=True
        )
        user.set_password("Secret123")
        db.session.add(user)

        # Create admin user
        admin = User(
            full_name="Admin Tester",
            email="admin@blueline.local",
            phone="+91 9999900000",
            address="HQ Command",
            blood_group="A+",
            role="ADMIN",
            is_active=True
        )
        admin.set_password("AdminPass123")
        db.session.add(admin)

        # Seed sample police station
        station = PoliceStation(
            station_name="Central Police Station (DEMO)",
            address="Connaught Circus",
            city="New Delhi",
            state="Delhi",
            latitude=28.6315,
            longitude=77.2167,
            phone_number="011-23747100",
            emergency_number="112",
            is_verified=True
        )
        db.session.add(station)

        # Seed emergency number
        num = EmergencyNumber(
            name="National Emergency",
            number="112",
            country="India",
            is_active=True
        )
        db.session.add(num)

        db.session.commit()

    yield application

    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client fixture."""
    return app.test_client()


@pytest.fixture
def user_client(app):
    """Authenticated client logged in as regular user."""
    c = app.test_client()
    c.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'Secret123'
    }, follow_redirects=True)
    return c


@pytest.fixture
def admin_client(app):
    """Authenticated client logged in as admin."""
    c = app.test_client()
    c.post('/login', data={
        'email': 'admin@blueline.local',
        'password': 'AdminPass123'
    }, follow_redirects=True)
    return c

