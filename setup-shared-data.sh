#!/bin/bash

# GeoPulse Shared Data Setup Script
# This script creates the necessary directory structure for external data storage

set -e

# Default shared data path
DEFAULT_SHARED_PATH="./shared_data"

# Get shared data path from environment or use default
SHARED_DATA_PATH=${SHARED_DATA_PATH:-$DEFAULT_SHARED_PATH}

echo "🚀 Setting up GeoPulse shared data directory structure..."
echo "📁 Shared data path: $SHARED_DATA_PATH"

# Create main shared data directory
mkdir -p "$SHARED_DATA_PATH"

# Create subdirectories
echo "📂 Creating directory structure..."

# Database directory
mkdir -p "$SHARED_DATA_PATH/database"

# API data directories
mkdir -p "$SHARED_DATA_PATH/uploads"
mkdir -p "$SHARED_DATA_PATH/temp"
mkdir -p "$SHARED_DATA_PATH/logs"
mkdir -p "$SHARED_DATA_PATH/user_data"

# Configuration directory
mkdir -p "$SHARED_DATA_PATH/config"

# Output directory
mkdir -p "$SHARED_DATA_PATH/output"

# Set proper permissions (adjust as needed for your system)
echo "🔐 Setting permissions..."
chmod -R 755 "$SHARED_DATA_PATH"
chmod -R 777 "$SHARED_DATA_PATH/uploads"
chmod -R 777 "$SHARED_DATA_PATH/temp"
chmod -R 777 "$SHARED_DATA_PATH/logs"
chmod -R 777 "$SHARED_DATA_PATH/output"

# Create sample configuration files
echo "📝 Creating sample configuration files..."

# Sample .env file
cat > "$SHARED_DATA_PATH/config/.env" << 'EOF'
# GeoPulse API Environment Configuration
# This file is mounted into the API container

# Database settings
DATABASE_URL=postgresql+asyncpg://geopulse_user:geopulse_secure_123@db:5432/geopulse_db

# Security settings
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production

# CORS settings
CORS_ALLOW_ORIGINS=http://localhost:3001,http://ui:3000

# Logging
LOG_LEVEL=INFO

# File paths (these are mounted from host)
CONFIG_PATH=/app/config
DATA_PATH=/app/data
OUTPUT_PATH=/app/output
EOF

# Sample Sentinel Hub configuration
cat > "$SHARED_DATA_PATH/config/sentinel_hub.yaml" << 'EOF'
# Sentinel Hub Configuration
# Replace with your actual Sentinel Hub credentials

sentinel_hub:
  client_id: "your_sentinel_hub_client_id"
  client_secret: "your_sentinel_hub_client_secret"
  instance_id: "your_sentinel_hub_instance_id"
  
  # API endpoints
  oauth_url: "https://services.sentinel-hub.com/oauth/token"
  api_url: "https://services.sentinel-hub.com/api/v1"
  
  # Default settings
  default_resolution: 10
  default_crs: "EPSG:4326"
  
  # Timeout settings
  timeout: 300
  max_retries: 3
EOF

# Sample application configuration
cat > "$SHARED_DATA_PATH/config/app_config.yaml" << 'EOF'
# GeoPulse Application Configuration

app:
  name: "GeoPulse"
  version: "1.0.0"
  environment: "development"

# File upload settings
upload:
  max_file_size_mb: 50
  allowed_extensions: [".xlsx", ".csv", ".xls"]
  temp_dir: "/app/user_data/temp"
  upload_dir: "/app/user_data/uploads"

# Processing settings
processing:
  max_concurrent_jobs: 5
  timeout_minutes: 30
  output_dir: "/app/output"

# Database settings
database:
  pool_size: 20
  max_overflow: 30
  pool_timeout: 30
  pool_recycle: 3600

# Logging settings
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "/app/logs/api.log"
  max_size_mb: 100
  backup_count: 5
EOF

# Create README for the shared data directory
cat > "$SHARED_DATA_PATH/README.md" << 'EOF'
# GeoPulse Shared Data Directory

This directory contains all persistent data, configuration files, and outputs for the GeoPulse application.

## Directory Structure

```
shared_data/
├── database/          # PostgreSQL database files
├── uploads/           # User uploaded files
├── temp/              # Temporary processing files
├── logs/              # Application logs
├── user_data/         # User-specific data
├── config/            # Configuration files
│   ├── .env           # Environment variables
│   ├── sentinel_hub.yaml  # Sentinel Hub configuration
│   └── app_config.yaml    # Application configuration
└── output/            # Processing outputs and results
```

## Configuration Files

### .env
Contains environment variables for the API service.

### sentinel_hub.yaml
Sentinel Hub API configuration for satellite data access.

### app_config.yaml
General application configuration settings.

## Important Notes

1. **Backup**: This directory contains all your data. Make sure to back it up regularly.
2. **Permissions**: The uploads, temp, logs, and output directories need write permissions.
3. **Security**: Keep configuration files secure, especially those containing API keys.
4. **Migration**: When updating the application, configuration files may need to be updated.

## Environment Variables

Set the `SHARED_DATA_PATH` environment variable to customize the location of this directory:

```bash
export SHARED_DATA_PATH=/path/to/your/shared/data
```

## Docker Usage

When running with Docker Compose, this directory is mounted into the containers:

- Database files are persisted in `database/`
- Uploads are stored in `uploads/`
- Logs are written to `logs/`
- Outputs are saved to `output/`
- Configuration files are read from `config/`
EOF

echo "✅ Shared data directory structure created successfully!"
echo ""
echo "📋 Directory structure created:"
echo "   📁 $SHARED_DATA_PATH/"
echo "   ├── 📁 database/     (PostgreSQL data)"
echo "   ├── 📁 uploads/      (User uploads)"
echo "   ├── 📁 temp/         (Temporary files)"
echo "   ├── 📁 logs/         (Application logs)"
echo "   ├── 📁 user_data/    (User data)"
echo "   ├── 📁 config/       (Configuration files)"
echo "   └── 📁 output/       (Processing outputs)"
echo ""
echo "📝 Sample configuration files created:"
echo "   📄 $SHARED_DATA_PATH/config/.env"
echo "   📄 $SHARED_DATA_PATH/config/sentinel_hub.yaml"
echo "   📄 $SHARED_DATA_PATH/config/app_config.yaml"
echo ""
echo "🔧 Next steps:"
echo "   1. Copy env.example to .env"
echo "   2. Update SHARED_DATA_PATH in .env if needed"
echo "   3. Update configuration files with your settings"
echo "   4. Run: docker-compose up -d"
echo ""
echo "⚠️  Important: Update the configuration files with your actual values!"
