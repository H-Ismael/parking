from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, select
from datetime import datetime, timezone
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
import logging
from app.database.database import get_db
from app.models.parking_spot import ParkingSpot
from app.models.schemas import SpotCreate, SpotResponse, SpotsResponse, SpotInfo
from app.core.geo_utils import snap_to_cell, add_obfuscation_jitter, calculate_distance_meters
from app.core.ttl_utils import calculate_expires_at, calculate_confidence, get_seconds_remaining

router = APIRouter()

@router.post("/spot", response_model=SpotResponse)
def create_spot(spot_data: SpotCreate, db: Session = Depends(get_db)):
    """
    Report a leaving or found parking spot.
    """
    try:
        # Snap to cell for obfuscation
        cell_id, cell_lat, cell_lon = snap_to_cell(spot_data.lat, spot_data.lon)

        # Calculate expiration time
        expires_at = calculate_expires_at(
            spot_data.lat, spot_data.lon, spot_data.type, spot_data.timestamp
        )
        print("expires at in spots.py --- ", expires_at)

        # Calculate initial confidence
        confidence = calculate_confidence(expires_at, spot_data.timestamp)

        # Create geometry point for database storage (raw GPS for internal use)
        location_point = Point(spot_data.lon, spot_data.lat)

        # Create parking spot record
        parking_spot = ParkingSpot(
            user_id=spot_data.user_id,
            type=spot_data.type,
            location=from_shape(location_point, srid=4326),
            cell_id=cell_id,
            expires_at=expires_at,
            confidence=confidence
        )

        db.add(parking_spot)
        db.commit()
        db.refresh(parking_spot)

        return SpotResponse(
            status="ok",
            spot_id=parking_spot.id,
            cell_id=cell_id,
            expires_at=expires_at
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create spot: {str(e)}")

@router.get("/spots", response_model=SpotsResponse)
def get_spots(lat: float, lon: float, radius_meters: int = 1000, db: Session = Depends(get_db)):
    """
    Fetch available parking spots within radius (meters).
    Uses geography so ST_DWithin works in meters.
    Returns obfuscated cell centroids with jitter.
    """
    try:
        current_time = datetime.now(timezone.utc)

        # Important notes:
        # - Use ST_SetSRID(ST_MakePoint(:lon, :lat), 4326) with bound params (no WKT string interpolation).
        # - Cast to ::geography so :radius_meters is meters (not degrees).
        # - Use .mappings() so rows are dict-like: row["lat"], row["expires_at"], etc.
        query = text("""
            SELECT
                id,
                type,
                cell_id,
                expires_at,
                ST_Y(ST_Centroid(location::geometry)) AS lat,
                ST_X(ST_Centroid(location::geometry)) AS lon
            FROM parking_spots
            WHERE expires_at > :current_time
              AND ST_DWithin(
                    location::geography,
                    ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                    :radius_meters
                  )
            ORDER BY created_at DESC
        """)

        params = {
            "current_time": current_time,
            "lat": lat,
            "lon": lon,
            "radius_meters": radius_meters
        }

        # Key step: mappings() so each row behaves like a dict with the column labels above
        result = db.execute(query, params).mappings()

        spots: list[SpotInfo] = []

        for row in result:
            # row is a Mapping: row["lat"], row["lon"], row["expires_at"], etc.
            cell_id, cell_lat, cell_lon = snap_to_cell(row["lat"], row["lon"])

            # Add small jitter for privacy
            jittered_lat, jittered_lon = add_obfuscation_jitter(cell_lat, cell_lon)

            # Distance in meters (user->obfuscated cell centroid)
            distance_meters = calculate_distance_meters(lat, lon, jittered_lat, jittered_lon)

            # Time & confidence
            expires_at = row["expires_at"]
            if not expires_at:
                # Safety guard: skip corrupt rows without an expiry
                continue

            confidence = calculate_confidence(expires_at, current_time)
            expires_in = get_seconds_remaining(expires_at, current_time)

            # Debug (optional)
            # print(f"[spot {row['id']}] dist={distance_meters:.1f}m ttl={expires_in}s conf={confidence:.2f}")

            if expires_in > 0:
                spots.append(SpotInfo(
                    id=row["id"],
                    cell_lat=jittered_lat,
                    cell_lon=jittered_lon,
                    type=row["type"],
                    expires_in=expires_in,
                    confidence=confidence
                ))

        return SpotsResponse(spots=spots)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch spots: {e}")
