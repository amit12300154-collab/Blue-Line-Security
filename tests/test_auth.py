from database import db
from models.user import User


def test_user_registration(client, app):
    """Test successful user registration and password hashing."""
    response = client.post('/register', data={
        'full_name': 'Aarav Patel',
        'email': 'aarav@example.com',
        'phone': '+91 9123456780',
        'password': 'Password@123',
        'confirm_password': 'Password@123',
        'address': 'Ahmedabad, Gujarat',
        'blood_group': 'B+',
        'terms': 'on'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Registration successful" in response.data

    with app.app_context():
        user = User.query.filter_by(email='aarav@example.com').first()
        assert user is not None
        assert user.check_password('Password@123') is True
        assert user.password_hash != 'Password@123'  # Must be hashed


def test_duplicate_email_registration(client):
    """Reject duplicate user registration with existing email."""
    response = client.post('/register', data={
        'full_name': 'Duplicate Person',
        'email': 'testuser@example.com',  # Pre-seeded in conftest
        'phone': '+91 9999999999',
        'password': 'Password@123',
        'confirm_password': 'Password@123',
        'terms': 'on'
    }, follow_redirects=True)

    assert b"already exists" in response.data


def test_login_successful(client):
    """Test successful login with correct credentials."""
    response = client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'Secret123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Welcome back, Regular Tester" in response.data


def test_login_invalid_password(client):
    """Reject login with incorrect password."""
    response = client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'WrongPassword999'
    }, follow_redirects=True)

    assert b"Invalid email or password" in response.data


def test_admin_access_control(user_client, admin_client):
    """Ensure non-admin users cannot access admin dashboard."""
    # Regular user attempting admin route
    resp = user_client.get('/admin/', follow_redirects=True)
    assert b"Access denied: Administrator privileges required" in resp.data

    # Admin accessing admin route
    admin_resp = admin_client.get('/admin/')
    assert admin_resp.status_code == 200, f"Got {admin_resp.status_code} redirecting to {admin_resp.location}"
    assert b"Administrator Command Hub" in admin_resp.data


def test_logout(user_client):
    """Test sign out and session clearance."""
    response = user_client.get('/logout', follow_redirects=True)
    assert b"signed out successfully" in response.data
