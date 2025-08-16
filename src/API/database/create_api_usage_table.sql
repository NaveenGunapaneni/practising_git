-- Create user_api_usage table for API usage tracking
CREATE TABLE IF NOT EXISTS user_api_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    allowed_api_calls INTEGER NOT NULL DEFAULT 50,
    performed_api_calls INTEGER NOT NULL DEFAULT 0,
    user_created_date TIMESTAMP WITH TIME ZONE NOT NULL,
    user_expiry_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_user_api_usage_user_id FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

-- Create indexes for user_api_usage table
CREATE INDEX IF NOT EXISTS idx_user_api_usage_user_id ON user_api_usage (user_id);
CREATE INDEX IF NOT EXISTS idx_user_api_usage_expiry ON user_api_usage (user_expiry_date);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at timestamp
CREATE TRIGGER update_user_api_usage_timestamp 
    BEFORE UPDATE ON user_api_usage
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant privileges
GRANT ALL PRIVILEGES ON TABLE user_api_usage TO geopulse_user;
GRANT USAGE, SELECT ON SEQUENCE user_api_usage_id_seq TO geopulse_user;

-- Verify the table was created
SELECT 'user_api_usage table created successfully!' as status;