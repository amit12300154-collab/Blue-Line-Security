from utils.distance import haversine_distance, format_distance
from services.police_service import PoliceService
from models.police_station import PoliceStation
from database import db


def test_haversine_distance_calculation():
    """
    Test mathematical validity of Haversine formula.
    Distance between New Delhi (28.6139, 77.2090) and Mumbai (19.0760, 72.8777)
    is approximately 1148 - 1155 km.
    """
    delhi_lat, delhi_lon = 28.6139, 77.2090
    mumbai_lat, mumbai_lon = 19.0760, 72.8777

    dist = haversine_distance(delhi_lat, delhi_lon, mumbai_lat, mumbai_lon)
    assert 1140.0 < dist < 1160.0

    # Test short distance formatting
    assert format_distance(0.450) == "450 meters"
    assert format_distance(12.345) == "12.35 km"


def test_nearest_police_station_lookup(app):
    """Test retrieving closest police station from database."""
    with app.app_context():
        # Add a second station further away
        far_station = PoliceStation(
            station_name="Far Away Station (DEMO)",
            address="Highway 1",
            city="Jaipur",
            state="Rajasthan",
            latitude=26.9124,
            longitude=75.7873,
            phone_number="0141-111111",
            emergency_number="112",
            is_verified=True
        )
        db.session.add(far_station)
        db.session.commit()

        # Query near Connaught Place, New Delhi (28.6300, 77.2150)
        station, dist = PoliceService.find_nearest_station(28.6300, 77.2150)
        assert station is not None
        assert station.station_name == "Central Police Station (DEMO)"
        assert dist < 1.0  # Less than 1 km away


def test_police_station_api(client):
    """Test REST API endpoint for nearest police station."""
    response = client.get('/api/police-stations/nearest?lat=28.6300&lon=77.2150')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['station_name'] == "Central Police Station (DEMO)"
    assert "formatted_distance" in data['data']
    assert "notification_status" in data['data']
