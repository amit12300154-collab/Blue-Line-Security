import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask
from database import db
from models.user import User
from models.emergency_contact import EmergencyContact
from models.police_station import PoliceStation
from models.emergency_number import EmergencyNumber


def seed_database(app: Flask):
    """Seed application database with initial admin, demo user, police stations, and helplines."""
    with app.app_context():
        # Ensure tables exist
        db.create_all()

        admin_email = app.config.get('ADMIN_DEFAULT_EMAIL', 'admin@blueline.local')
        admin_pass = app.config.get('ADMIN_DEFAULT_PASSWORD', 'Admin@12345')

        demo_email = app.config.get('DEMO_USER_EMAIL', 'demo@example.com')
        demo_pass = app.config.get('DEMO_USER_PASSWORD', 'Demo@12345')

        # 1. Admin User
        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            admin_user = User(
                full_name="System Administrator",
                email=admin_email,
                phone="+91 9999988888",
                address="Blue Line HQ, Central Control Center",
                blood_group="O+",
                role="ADMIN",
                is_active=True
            )
            admin_user.set_password(admin_pass)
            db.session.add(admin_user)
            print(f"[Seed] Created Administrator: {admin_email}")

        # 2. Demo User
        demo_user = User.query.filter_by(email=demo_email).first()
        if not demo_user:
            demo_user = User(
                full_name="Demo User",
                email=demo_email,
                phone="+91 9876543210",
                address="B-402, Green Avenue, Tech City",
                blood_group="B+",
                role="USER",
                is_active=True
            )
            demo_user.set_password(demo_pass)
            db.session.add(demo_user)
            db.session.flush()  # To obtain demo_user.id
            print(f"[Seed] Created Demo User: {demo_email}")

            # 3. Emergency Contacts for Demo User
            demo_contacts = [
                EmergencyContact(
                    user_id=demo_user.id,
                    name="Rajesh Kumar (Father)",
                    relationship="Father",
                    phone="+91 9876500001",
                    email="father.demo@example.com",
                    priority=1,
                    is_active=True
                ),
                EmergencyContact(
                    user_id=demo_user.id,
                    name="Sunita Devi (Mother)",
                    relationship="Mother",
                    phone="+91 9876500002",
                    email="mother.demo@example.com",
                    priority=2,
                    is_active=True
                ),
                EmergencyContact(
                    user_id=demo_user.id,
                    name="Amit Verma (Friend)",
                    relationship="Friend",
                    phone="+91 9876500003",
                    email="friend.demo@example.com",
                    priority=3,
                    is_active=True
                )
            ]
            db.session.add_all(demo_contacts)
            print(f"[Seed] Added {len(demo_contacts)} demo emergency contacts for {demo_email}")

        # 4. Verified Police Stations (Clearly marked as DEMO DATA)
        if PoliceStation.query.count() == 0:
            demo_stations = [
                PoliceStation(
                    station_name="Connaught Place Police Station (DEMO DATA)",
                    address="Connaught Circus, Sector 1, Central Delhi",
                    city="New Delhi",
                    state="Delhi",
                    latitude=28.6315,
                    longitude=77.2167,
                    phone_number="011-23747100 (DEMO)",
                    emergency_number="112",
                    is_verified=True
                ),
                PoliceStation(
                    station_name="IGI Airport Police Station (DEMO DATA)",
                    address="Terminal 3 Road, Near Aerocity Metro",
                    city="New Delhi",
                    state="Delhi",
                    latitude=28.5562,
                    longitude=77.1000,
                    phone_number="011-25652222 (DEMO)",
                    emergency_number="112",
                    is_verified=True
                ),
                PoliceStation(
                    station_name="Bandra Police Station (DEMO DATA)",
                    address="Hill Road, Bandra West",
                    city="Mumbai",
                    state="Maharashtra",
                    latitude=19.0596,
                    longitude=72.8295,
                    phone_number="022-26422222 (DEMO)",
                    emergency_number="112",
                    is_verified=True
                ),
                PoliceStation(
                    station_name="Koramangala Police Station (DEMO DATA)",
                    address="80 Feet Road, Koramangala 6th Block",
                    city="Bengaluru",
                    state="Karnataka",
                    latitude=12.9352,
                    longitude=77.6245,
                    phone_number="080-22942566 (DEMO)",
                    emergency_number="112",
                    is_verified=True
                ),
                PoliceStation(
                    station_name="Sector 29 Cyber & Traffic Station (DEMO DATA)",
                    address="Leisure Valley Road, Sector 29",
                    city="Gurugram",
                    state="Haryana",
                    latitude=28.4700,
                    longitude=77.0600,
                    phone_number="0124-2222222 (DEMO)",
                    emergency_number="112",
                    is_verified=True
                )
            ]
            db.session.add_all(demo_stations)
            print(f"[Seed] Added {len(demo_stations)} verified police station records (DEMO)")

        # 5. Emergency Helpline Numbers (Official National Indian Numbers)
        if EmergencyNumber.query.count() == 0:
            helpline_numbers = [
                EmergencyNumber(
                    name="National Emergency Response Support System",
                    number="112",
                    country="India",
                    state="National",
                    description="Unified pan-India emergency number for Police, Fire, and Ambulance dispatch.",
                    is_active=True
                ),
                EmergencyNumber(
                    name="Police Helpline",
                    number="100",
                    country="India",
                    state="National",
                    description="Immediate assistance for law enforcement and emergency intervention.",
                    is_active=True
                ),
                EmergencyNumber(
                    name="Women Safety & Domestic Distress Helpline",
                    number="1091",
                    country="India",
                    state="National",
                    description="24x7 dedicated emergency helpline for women in distress or danger.",
                    is_active=True
                ),
                EmergencyNumber(
                    name="Medical Emergency & Ambulance Dispatch",
                    number="108",
                    country="India",
                    state="National",
                    description="Emergency hospital transportation and trauma patient care.",
                    is_active=True
                ),
                EmergencyNumber(
                    name="Fire Brigade & Rescue Control",
                    number="101",
                    country="India",
                    state="National",
                    description="Fire fighting, hazardous situation control, and building evacuation.",
                    is_active=True
                ),
                EmergencyNumber(
                    name="National Highway Helpline",
                    number="1033",
                    country="India",
                    state="National",
                    description="24x7 highway assistance, road accidents, and ambulance dispatch on national expressways.",
                    is_active=True
                )
            ]
            db.session.add_all(helpline_numbers)
            print(f"[Seed] Added {len(helpline_numbers)} emergency helpline numbers")

        db.session.commit()
        print("[Seed] Database seeding completed successfully.")


if __name__ == '__main__':
    from app import create_app
    app = create_app()
    seed_database(app)
