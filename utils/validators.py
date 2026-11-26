import re
from typing import Tuple

ALLOWED_TRIGGER_TYPES = {
    'PANIC_BUTTON',
    'IMPACT_DETECTED',
    'VOICE_TRIGGER',
    'MANUAL_REPORT'
}

ALLOWED_EMERGENCY_TYPES = {
    'ROBBERY',
    'THEFT',
    'ACCIDENT',
    'MEDICAL',
    'ASSAULT',
    'HARASSMENT',
    'FIRE',
    'OTHER'
}

ALLOWED_STATUSES = {
    'ACTIVE',
    'NOTIFIED',
    'RESOLVED',
    'FALSE_ALARM',
    'CANCELLED'
}

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
PHONE_REGEX = re.compile(r'^\+?[0-9\s\-()]{7,20}$')


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def validate_phone(phone: str) -> bool:
    """Validate phone format."""
    if not phone or not isinstance(phone, str):
        return False
    digits = re.sub(r'\D', '', phone)
    return len(digits) >= 7 and bool(PHONE_REGEX.match(phone.strip()))


def validate_coordinates(lat: float, lon: float) -> Tuple[bool, str]:
    """Validate latitude and longitude ranges."""
    try:
        lat = float(lat)
        lon = float(lon)
    except (ValueError, TypeError):
        return False, "Coordinates must be valid decimal numbers."

    if not (-90.0 <= lat <= 90.0):
        return False, f"Latitude must be between -90 and +90 degrees. Received {lat}."
    if not (-180.0 <= lon <= 180.0):
        return False, f"Longitude must be between -180 and +180 degrees. Received {lon}."

    return True, ""


def validate_emergency_payload(payload: dict) -> Tuple[bool, str]:
    """Validate emergency creation request payload."""
    trigger_type = payload.get('trigger_type', '').upper()
    emergency_type = payload.get('emergency_type', '').upper()

    if trigger_type not in ALLOWED_TRIGGER_TYPES:
        return False, f"Invalid trigger_type. Allowed: {', '.join(sorted(ALLOWED_TRIGGER_TYPES))}"

    if emergency_type not in ALLOWED_EMERGENCY_TYPES:
        return False, f"Invalid emergency_type. Allowed: {', '.join(sorted(ALLOWED_EMERGENCY_TYPES))}"

    if 'latitude' in payload and 'longitude' in payload:
        if payload['latitude'] is not None and payload['longitude'] is not None:
            valid_coord, msg = validate_coordinates(payload['latitude'], payload['longitude'])
            if not valid_coord:
                return False, msg

    return True, ""
