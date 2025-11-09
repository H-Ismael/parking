import math
import random
from typing import Tuple
from dotenv import load_dotenv
import os

load_dotenv()

CELL_SIZE_METERS = float(os.getenv("CELL_SIZE_METERS", 100))
OBFUSCATION_JITTER_METERS = float(os.getenv("OBFUSCATION_JITTER_METERS", 15))

def snap_to_cell(lat: float, lon: float) -> Tuple[str, float, float]:
    """
    Snap GPS coordinates to a grid cell and return cell_id and centroid.
    Cell size is approximately CELL_SIZE_METERS.
    """
    # Convert meters to degrees (rough approximation)
    # 1 degree lat ≈ 111,000 meters
    # 1 degree lon ≈ 111,000 * cos(lat) meters
    lat_deg_per_meter = 1.0 / 111000.0
    lon_deg_per_meter = 1.0 / (111000.0 * math.cos(math.radians(lat)))

    cell_size_lat = CELL_SIZE_METERS * lat_deg_per_meter
    cell_size_lon = CELL_SIZE_METERS * lon_deg_per_meter

    # Snap to grid
    cell_lat_idx = math.floor(lat / cell_size_lat)
    cell_lon_idx = math.floor(lon / cell_size_lon)

    # Calculate cell centroid
    cell_lat = (cell_lat_idx + 0.5) * cell_size_lat
    cell_lon = (cell_lon_idx + 0.5) * cell_size_lon

    # Generate cell ID
    cell_id = f"cell_{cell_lat:.3f}_{cell_lon:.3f}"

    return cell_id, cell_lat, cell_lon

def add_obfuscation_jitter(lat: float, lon: float) -> Tuple[float, float]:
    """
    Add small random jitter to coordinates for additional privacy.
    """
    # Convert jitter from meters to degrees
    lat_deg_per_meter = 1.0 / 111000.0
    lon_deg_per_meter = 1.0 / (111000.0 * math.cos(math.radians(lat)))

    jitter_lat_deg = OBFUSCATION_JITTER_METERS * lat_deg_per_meter
    jitter_lon_deg = OBFUSCATION_JITTER_METERS * lon_deg_per_meter

    # Add random jitter within the range 
    # Todo : minimize jitter
    jitter_lat = random.uniform(-jitter_lat_deg, jitter_lat_deg)
    jitter_lon = random.uniform(-jitter_lon_deg, jitter_lon_deg)

    return lat + jitter_lat, lon + jitter_lon

def calculate_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula.
    Returns distance in meters.
    """
    R = 6371000  # Earth's radius in meters

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (math.sin(delta_lat / 2) * math.sin(delta_lat / 2) +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) * math.sin(delta_lon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c