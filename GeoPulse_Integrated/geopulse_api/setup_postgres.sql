-- PostgreSQL setup script for GeoPulse API
-- Run this as postgres superuser

-- Create user
CREATE USER geopulse_user WITH PASSWORD 'password123';

-- Create database
CREATE DATABASE geopulse_db OWNER geopulse_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE geopulse_db TO geopulse_user;

-- Connect to the database and grant schema privileges
\c geopulse_db;
GRANT ALL ON SCHEMA public TO geopulse_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO geopulse_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO geopulse_user;

-- Verify setup
\l
\du