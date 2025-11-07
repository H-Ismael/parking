-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create the parking_spots table
CREATE TABLE IF NOT EXISTS parking_spots (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    type VARCHAR(10) CHECK (type IN ('leaving', 'found')) NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    cell_id TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    confidence VARCHAR(10) NOT NULL
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_parking_spots_cell_id ON parking_spots(cell_id);
CREATE INDEX IF NOT EXISTS idx_parking_spots_expires_at ON parking_spots(expires_at);
CREATE INDEX IF NOT EXISTS idx_parking_spots_location ON parking_spots USING GIST(location);