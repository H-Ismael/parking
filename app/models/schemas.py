from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

class SpotCreate(BaseModel):
    user_id: str
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    type: Literal["leaving", "found"]
    timestamp: datetime

class SpotResponse(BaseModel):
    status: str
    spot_id: int
    cell_id: str
    expires_at: datetime

class SpotInfo(BaseModel):
    id: int
    cell_lat: float
    cell_lon: float
    type: Literal["leaving", "found"]
    expires_in: int
    confidence: Literal["high", "medium", "low"]

class SpotsResponse(BaseModel):
    spots: list[SpotInfo]