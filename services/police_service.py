from typing import Optional, Tuple, Dict, Any
from models.police_station import PoliceStation
from utils.distance import haversine_distance, format_distance


class PoliceService:
    """Service to query police stations and calculate distances using Haversine formula."""

    @staticmethod
    def find_nearest_station(lat: float, lon: float, verified_only: bool = False) -> Tuple[Optional[PoliceStation], Optional[float]]:
        """
        Find the closest registered police station to the given GPS coordinates.

        :param lat: User latitude
        :param lon: User longitude
        :param verified_only: Filter by verified stations only if True
        :return: Tuple of (PoliceStation object or None, distance_km or None)
        """
        query = PoliceStation.query
        if verified_only:
            query = query.filter_by(is_verified=True)

        stations = query.all()
        if not stations:
            return None, None

        nearest_station = None
        min_distance = float('inf')

        for station in stations:
            dist = haversine_distance(lat, lon, station.latitude, station.longitude)
            if dist < min_distance:
                min_distance = dist
                nearest_station = station

        return nearest_station, min_distance

    @staticmethod
    def get_nearest_station_details(lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Get structured dictionary with nearest station info and calculated distance."""
        station, distance_km = PoliceService.find_nearest_station(lat, lon)
        if not station:
            return None

        station_dict = station.to_dict()
        station_dict['distance_km'] = distance_km
        station_dict['formatted_distance'] = format_distance(distance_km)
        station_dict['notification_status'] = "SIMULATED (Demo Mode - No real emergency transmission)"
        return station_dict
