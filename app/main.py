from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import spots
from app.database.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Parking Spot API",
    description="Privacy-safe crowdsourced parking spot reporting API",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(spots.router, prefix="/api/v1", tags=["spots"])

@app.get("/")
def read_root():
    return {"message": "Parking Spot API", "version": "0.1.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}