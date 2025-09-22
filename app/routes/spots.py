from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

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
    Fetch available parking spots within radius.
    """
    try:
        current_time = datetime.now(timezone.utc)

        # Query spots within radius that haven't expired
        # Using PostGIS ST_DWithin for efficient spatial query
        query = text("""
            SELECT id, type, cell_id, expires_at,
                   ST_Y(ST_Centroid(location::geometry)) as lat,
                   ST_X(ST_Centroid(location::geometry)) as lon
            FROM parking_spots
            WHERE expires_at > :current_time
            AND ST_DWithin(
                location::geometry,
                ST_GeomFromText('POINT(:lon :lat)', 4326)::geometry,
                :radius_meters
            )
            ORDER BY created_at DESC
        """)

        result = db.execute(query, {
            "current_time": current_time,
            "lat": lat,
            "lon": lon,
            "radius_meters": radius_meters
        })

        spots = []
        for row in result:
            # Get cell centroid for obfuscated display
            cell_id, cell_lat, cell_lon = snap_to_cell(row.lat, row.lon)

            # Add small jitter for additional privacy
            jittered_lat, jittered_lon = add_obfuscation_jitter(cell_lat, cell_lon)

            # Calculate confidence and time remaining
            expires_at = row.expires_at
            confidence = calculate_confidence(expires_at, current_time)
            expires_in = get_seconds_remaining(expires_at, current_time)

            if expires_in > 0:  # Only include non-expired spots
                spots.append(SpotInfo(
                    id=row.id,
                    cell_lat=jittered_lat,
                    cell_lon=jittered_lon,
                    type=row.type,
                    expires_in=expires_in,
                    confidence=confidence
                ))

        return SpotsResponse(spots=spots)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch spots: {str(e)}")