from datetime import datetime, timedelta, timezone
from typing import Literal
from dotenv import load_dotenv
import os

load_dotenv()

def parse_ttl_bands() -> dict[str, int]:
    """Parse TTL_BANDS environment variable into a dictionary."""
    ttl_bands_str = os.getenv("TTL_BANDS", "CBD_PEAK:180|URBAN:360|RESIDENTIAL:600")
    ttl_bands = {}

    for band in ttl_bands_str.split("|"):
        zone, ttl = band.split(":")
        ttl_bands[zone] = int(ttl)

    return ttl_bands

def parse_confidence_thresholds() -> dict[str, int]:
    """Parse CONFIDENCE_THRESHOLDS environment variable into a dictionary."""
    thresholds_str = os.getenv("CONFIDENCE_THRESHOLDS", "FRESH:90|FADING:240|LOW:999999")
    thresholds = {}

    for threshold in thresholds_str.split("|"):
        level, seconds = threshold.split(":")
        thresholds[level] = int(seconds)

    return thresholds

def determine_zone_type(lat: float, lon: float) -> str:
    """
    Determine zone type based on coordinates.
    For PoC, we'll use a simple heuristic. In production, this would use
    actual geographic data or time-of-day patterns.
    """
    # Simple heuristic for PoC - this would be replaced with real zone data
    # For now, we'll assume URBAN as default
    return "URBAN"

def calculate_ttl_seconds(lat: float, lon: float, spot_type: str, timestamp: datetime) -> int:
    """
    Calculate TTL in seconds based on location, spot type, and time.
    """
    zone_type = determine_zone_type(lat, lon)
    ttl_bands = parse_ttl_bands()

    base_ttl = ttl_bands.get(zone_type, ttl_bands["URBAN"])

    # Adjust TTL based on spot type
    if spot_type == "leaving":
        # "Leaving" spots might be more reliable
        multiplier = 1.0
    else:  # "found"
        # "Found" spots might be less reliable
        multiplier = 0.8

    # Adjust based on time of day (simple heuristic for PoC)
    hour = timestamp.hour
    if 7 <= hour <= 9 or 17 <= hour <= 19:  # Peak hours
        multiplier *= 0.6  # Shorter TTL during peak hours
    elif 22 <= hour or hour <= 6:  # Night hours
        multiplier *= 1.5  # Longer TTL at night

    return int(base_ttl * multiplier)

def calculate_expires_at(lat: float, lon: float, spot_type: str, timestamp: datetime) -> datetime:
    """
    Calculate expiration timestamp for a parking spot.
    """
    publish_delay = int(os.getenv("PUBLISH_DELAY_SECONDS", 75))
    ttl_seconds = calculate_ttl_seconds(lat, lon, spot_type, timestamp)

    # Add publish delay to timestamp, then add TTL
    publish_time = timestamp + timedelta(seconds=publish_delay)
    expires_at = publish_time + timedelta(seconds=ttl_seconds)

    return expires_at

def calculate_confidence(expires_at: datetime, current_time: datetime = None) -> Literal["high", "medium", "low"]:
    """
    Calculate confidence level based on time remaining until expiration.
    """
    if current_time is None:
        current_time = datetime.now(timezone.utc)

    if expires_at <= current_time:
        return "low"

    seconds_remaining = (expires_at - current_time).total_seconds()
    thresholds = parse_confidence_thresholds()

    if seconds_remaining >= thresholds["FADING"]:
        return "high"
    elif seconds_remaining >= thresholds["FRESH"]:
        return "medium"
    else:
        return "low"

def get_seconds_remaining(expires_at: datetime, current_time: datetime = None) -> int:
    """
    Get seconds remaining until expiration.
    """
    if current_time is None:
        current_time = datetime.now(timezone.utc)

    if expires_at <= current_time:
        return 0

    return int((expires_at - current_time).total_seconds())