import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on the Earth's surface
    using the Haversine formula.

    :param lat1: Latitude of point 1 in decimal degrees
    :param lon1: Longitude of point 1 in decimal degrees
    :param lat2: Latitude of point 2 in decimal degrees
    :param lon2: Longitude of point 2 in decimal degrees
    :return: Distance in kilometers
    """
    # Earth radius in kilometers
    R = 6371.0

    # Convert coordinates from degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    distance = R * c
    return round(distance, 3)


def format_distance(distance_km: float) -> str:
    """Format distance into user-friendly units (meters or kilometers)."""
    if distance_km < 1.0:
        meters = int(round(distance_km * 1000))
        return f"{meters} meters"
    return f"{distance_km:.2f} km"
