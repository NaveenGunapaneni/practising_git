#!/bin/bash

# GeoPulse Docker Startup Script

set -e

echo "🚀 Starting GeoPulse with Docker Compose..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Function to check if ports are available
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $port is already in use. $service might not start properly."
        return 1
    fi
    return 0
}

# Check required ports
echo "🔍 Checking port availability..."
check_port 3001 "UI"
check_port 8000 "API"
check_port 5433 "Database"
check_port 5050 "pgAdmin"

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker-compose ps

# Check health endpoints
echo "🏥 Checking service health..."

# Check API health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is healthy"
else
    echo "❌ API health check failed"
fi

# Check UI health
if curl -f http://localhost:3001 > /dev/null 2>&1; then
    echo "✅ UI is healthy"
else
    echo "❌ UI health check failed"
fi

# Check database health
if docker-compose exec -T db pg_isready -U geopulse_user -d geopulse_db > /dev/null 2>&1; then
    echo "✅ Database is healthy"
else
    echo "❌ Database health check failed"
fi

echo ""
echo "🎉 GeoPulse is starting up!"
echo ""
echo "📱 Access Points:"
echo "   Frontend:     http://localhost:3001"
echo "   API:          http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   Database:     localhost:5433"
echo "   pgAdmin:      http://localhost:5050"
echo ""
echo "📋 Useful Commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop:         docker-compose down"
echo "   Restart:      docker-compose restart"
echo "   Shell access: docker-compose exec api bash"
echo ""
echo "🔍 Monitor services:"
echo "   docker-compose ps"
echo "   docker-compose logs -f [service_name]"
