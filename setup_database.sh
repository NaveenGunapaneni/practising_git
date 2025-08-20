#!/bin/bash

echo "🗄️ Setting up GeoPulse Database..."

# Check if Docker is installed
if ! command -v docker >/dev/null 2>&1; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose >/dev/null 2>&1; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Navigate to API directory
cd src/API

# Start PostgreSQL with Docker Compose
echo "🐘 Starting PostgreSQL database..."
docker-compose -f database/docker-compose.yml up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Check if database is running
if docker-compose -f database/docker-compose.yml ps | grep -q "Up"; then
    echo "✅ Database is running"
else
    echo "❌ Failed to start database"
    exit 1
fi

# Run database migrations
echo "🔄 Running database migrations..."
cd src/API
source venv/bin/activate 2>/dev/null || echo "⚠️ Virtual environment not found, continuing..."
alembic upgrade head

echo ""
echo "🎉 Database setup complete!"
echo "📊 PostgreSQL is running on localhost:5432"
echo "🔧 Database: geopulse_db"
echo "👤 Username: geopulse_user"
echo "🔑 Password: geopulse_password"
echo ""
echo "You can now start the application with: ./start.sh"

