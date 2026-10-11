-- STREAMING_CHUNK:Creating the distance_logs table...
-- Create the main telemetry table for HC-SR04 distance readings
CREATE TABLE IF NOT EXISTS distance_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    distance DOUBLE PRECISION NOT NULL,
    threshold DOUBLE PRECISION DEFAULT 50.0,
    mode VARCHAR(50) DEFAULT 'continuous',
    regulator BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- STREAMING_CHUNK:Enabling indexing for fast query performance...
-- Create an index on created_at for fast historical retrieval
CREATE INDEX IF NOT EXISTS idx_distance_logs_created_at ON distance_logs (created_at DESC);

-- STREAMING_CHUNK:Enabling Row Level Security (RLS)...
-- Enable Row Level Security (RLS) for security
ALTER TABLE distance_logs ENABLE ROW LEVEL SECURITY;

-- Create policy to allow public inserts (from backend or ESP32) and reads (for dashboard history)
CREATE POLICY "Allow public insert on distance_logs" 
    ON distance_logs FOR INSERT 
    WITH CHECK (true);

CREATE POLICY "Allow public read on distance_logs" 
    ON distance_logs FOR SELECT 
    USING (true);

-- STREAMING_CHUNK:Enabling Supabase Realtime...
-- Optional: Enable Realtime broadcast for the distance_logs table
ALTER PUBLICATION supabase_realtime ADD TABLE distance_logs;