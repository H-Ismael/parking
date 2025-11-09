from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/parking_db")
    CELL_SIZE_METERS: float = float(os.getenv("CELL_SIZE_METERS", 100))
    PUBLISH_DELAY_SECONDS: int = int(os.getenv("PUBLISH_DELAY_SECONDS", 75))
    OBFUSCATION_JITTER_METERS: float = float(os.getenv("OBFUSCATION_JITTER_METERS", 15))
    TTL_BANDS: str = os.getenv("TTL_BANDS", "CBD_PEAK:180|URBAN:360|RESIDENTIAL:600")
    CONFIDENCE_THRESHOLDS: str = os.getenv("CONFIDENCE_THRESHOLDS", "FRESH:90|FADING:240|LOW:999999")

settings = Settings()