-- PostgreSQL setup script for GeoPulse API
-- This script will be automatically executed when the container starts

-- Create user
CREATE USER geopulse_user WITH PASSWORD 'password123';

-- Create database
CREATE DATABASE geopulse_db OWNER geopulse_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE geopulse_db TO geopulse_user;

-- Connect to the geopulse_db database
\c geopulse_db;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO geopulse_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO geopulse_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO geopulse_user;

-- Create users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    organization_name VARCHAR(255) NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    logo_path VARCHAR(500),
    file_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create indexes for users table
CREATE UNIQUE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_organization ON users (organization_name);
CREATE INDEX idx_users_created_at ON users (created_at);

-- Create files table
CREATE TABLE files (
    file_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    upload_date DATE NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    line_count INTEGER,
    storage_location VARCHAR(500) NOT NULL,
    input_location VARCHAR(500),
    processed_flag BOOLEAN NOT NULL DEFAULT FALSE,
    engagement_name VARCHAR(255),
    browser_ip VARCHAR(45),
    browser_location VARCHAR(255),
    processing_time_seconds NUMERIC(10, 2),
    file_size_mb NUMERIC(10, 2),
    dates JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT fk_files_user_id FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

-- Create indexes for files table
CREATE INDEX idx_files_user_id ON files (user_id);
CREATE INDEX idx_files_processed_flag ON files (processed_flag);
CREATE INDEX idx_files_upload_date ON files (upload_date);
CREATE INDEX idx_files_user_processed ON files (user_id, processed_flag);
CREATE INDEX idx_files_created_at ON files (created_at);

-- Create function to update user file count
CREATE OR REPLACE FUNCTION update_user_file_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE users SET file_count = file_count + 1 WHERE user_id = NEW.user_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE users SET file_count = file_count - 1 WHERE user_id = OLD.user_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update file count
CREATE TRIGGER trigger_update_user_file_count
    AFTER INSERT OR DELETE ON files
    FOR EACH ROW EXECUTE FUNCTION update_user_file_count();

-- Grant all privileges on the new tables and sequences to geopulse_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO geopulse_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO geopulse_user;

-- Verify setup
SELECT 'Database setup completed successfully!' as status;
\l
\du