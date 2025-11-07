from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint, Text
from sqlalchemy.sql import func
from geoalchemy2 import Geography
from app.database.database import Base

class ParkingSpot(Base):
    __tablename__ = "parking_spots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Text, nullable=False)
    type = Column(String(10), CheckConstraint("type IN ('leaving', 'found')"), nullable=False)
    location = Column(Geography('POINT', srid=4326), nullable=False)
    cell_id = Column(Text, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    confidence = Column(String(10), nullable=False)