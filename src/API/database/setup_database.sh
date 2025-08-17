#!/bin/bash

# GeoPulse Database Setup Script
# This script sets up the PostgreSQL database for GeoPulse API

set -e  # Exit on any error

echo "🚀 Setting up GeoPulse Database..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if PostgreSQL is running
print_status "Checking PostgreSQL service status..."
if ! sudo systemctl is-active --quiet postgresql; then
    print_error "PostgreSQL is not running. Starting PostgreSQL..."
    sudo systemctl start postgresql
    if ! sudo systemctl is-active --quiet postgresql; then
        print_error "Failed to start PostgreSQL. Please check your installation."
        exit 1
    fi
fi
print_success "PostgreSQL is running"

# Check if we can connect to PostgreSQL
print_status "Testing PostgreSQL connection..."
if ! sudo -u postgres psql -c "SELECT 1;" > /dev/null 2>&1; then
    print_error "Cannot connect to PostgreSQL. Please check your installation."
    exit 1
fi
print_success "PostgreSQL connection successful"

# Check if database already exists
print_status "Checking if geopulse_db already exists..."
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw geopulse_db; then
    print_warning "Database 'geopulse_db' already exists!"
    read -p "Do you want to drop and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Dropping existing database..."
        sudo -u postgres psql -c "DROP DATABASE IF EXISTS geopulse_db;"
        print_success "Database dropped"
    else
        print_warning "Skipping database creation. Using existing database."
        # Still run the setup script to ensure tables exist
    fi
fi

# Create database if it doesn't exist
if ! sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw geopulse_db; then
    print_status "Creating database 'geopulse_db'..."
    sudo -u postgres psql -c "CREATE DATABASE geopulse_db;"
    print_success "Database created"
fi

# Check if geopulse_user exists
print_status "Checking if geopulse_user exists..."
if ! sudo -u postgres psql -c "SELECT 1 FROM pg_roles WHERE rolname='geopulse_user';" | grep -q 1; then
    print_status "Creating user 'geopulse_user'..."
    sudo -u postgres psql -c "CREATE USER geopulse_user WITH PASSWORD 'password123';"
    print_success "User created"
else
    print_success "User 'geopulse_user' already exists"
fi

# Grant privileges
print_status "Granting database privileges..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE geopulse_db TO geopulse_user;"
print_success "Database privileges granted"

# Run the main setup script
print_status "Running setup_postgres.sql..."
if [ -f "setup_postgres.sql" ]; then
    sudo -u postgres psql -d geopulse_db -f setup_postgres.sql
    print_success "setup_postgres.sql executed successfully"
else
    print_error "setup_postgres.sql not found in current directory"
    exit 1
fi

# Run the API usage table script if it exists
if [ -f "create_api_usage_table.sql" ]; then
    print_status "Running create_api_usage_table.sql..."
    sudo -u postgres psql -d geopulse_db -f create_api_usage_table.sql
    print_success "create_api_usage_table.sql executed successfully"
else
    print_warning "create_api_usage_table.sql not found, skipping..."
fi

# Test database connection with geopulse_user
print_status "Testing connection with geopulse_user..."
if PGPASSWORD=password123 psql -h localhost -U geopulse_user -d geopulse_db -c "SELECT current_database(), current_user;" > /dev/null 2>&1; then
    print_success "geopulse_user can connect to database"
else
    print_error "geopulse_user cannot connect to database"
    exit 1
fi

# Verify tables were created
print_status "Verifying tables were created..."
TABLES=$(sudo -u postgres psql -d geopulse_db -t -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")

echo "Tables found:"
echo "$TABLES" | while read -r table; do
    if [ ! -z "$table" ]; then
        echo "  - $table"
    fi
done

# Check for required tables
REQUIRED_TABLES=("users" "files" "user_api_usage")
MISSING_TABLES=()

for table in "${REQUIRED_TABLES[@]}"; do
    if ! echo "$TABLES" | grep -q "$table"; then
        MISSING_TABLES+=("$table")
    fi
done

if [ ${#MISSING_TABLES[@]} -eq 0 ]; then
    print_success "All required tables created successfully"
else
    print_error "Missing required tables: ${MISSING_TABLES[*]}"
    exit 1
fi

# Run Alembic migrations if available
if command -v alembic &> /dev/null; then
    print_status "Running Alembic migrations..."
    cd ..  # Go to API directory
    if alembic upgrade head; then
        print_success "Alembic migrations completed"
    else
        print_warning "Alembic migrations failed or no migrations to run"
    fi
    cd database  # Return to database directory
else
    print_warning "Alembic not found, skipping migrations"
fi

# Display database information
print_status "Database setup completed successfully!"
echo ""
echo "📊 Database Information:"
echo "  Database: geopulse_db"
echo "  User: geopulse_user"
echo "  Password: password123"
echo "  Host: localhost"
echo "  Port: 5432"
echo ""
echo "🔗 Connection String:"
echo "  postgresql+asyncpg://geopulse_user:password123@localhost:5432/geopulse_db"
echo ""
echo "📋 Next Steps:"
echo "  1. Update your .env file with the connection string above"
echo "  2. Start your API server: python main.py"
echo "  3. Test the connection: curl http://localhost:8000/api/v1/health"
echo ""
echo "🎉 Database setup completed successfully!"
