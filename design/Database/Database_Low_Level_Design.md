# Database Low-Level Design Document
## GeoPulse Web Application

**Document Version:** 1.0  
**Date:** August 2025  
**Project:** GeoPulse  
**Document Type:** Database Low-Level Design  

---

## Table of Contents
1. [Technology Stack](#technology-stack)
2. [Database Architecture](#database-architecture)
3. [Schema Design](#schema-design)
4. [Database Setup](#database-setup)
5. [Migration Management](#migration-management)
6. [Indexing Strategy](#indexing-strategy)
7. [Backup and Recovery](#backup-and-recovery)
8. [Performance Optimization](#performance-optimization)
9. [Security Configuration](#security-configuration)
10. [Development Setup](#development-setup)

---

## Technology Stack

### Database Technologies
- **Database Engine:** PostgreSQL 15+
- **Database GUI:** pgAdmin 4
- **ORM:** SQLAlchemy 2.0+
- **Migration Tool:** Alembic
- **Connection Pooling:** SQLAlchemy connection pooling
- **Backup Tool:** pg_dump/pg_restore

### Development Tools
- **Database Client:** pgAdmin, DBeaver, or psql
- **Containerization:** Docker
- **Version Control:** Git
- **IDE:** VS Code with PostgreSQL extensions

---

## Database Architecture

### Database Overview
The GeoPulse application uses PostgreSQL as its primary database with the following characteristics:

- **Database Name:** `geopulse_db`
- **Character Set:** UTF-8
- **Collation:** en_US.UTF-8
- **Timezone:** UTC
- **Connection Pool:** 20-50 connections
- **Backup Strategy:** Daily automated backups

### Database Connection String Format
```
postgresql://username:password@hostname:port/database_name
```

### Example Connection Strings
```python
# Development
DATABASE_URL = "postgresql://geopulse_user:password123@localhost:5432/geopulse_dev"

# Production
DATABASE_URL = "postgresql://geopulse_user:password123@prod-server:5432/geopulse_prod"

# Testing
DATABASE_URL = "postgresql://test_user:test_pass@localhost:5432/geopulse_test"
```

---

## Schema Design

### 1. Users Table
```sql
-- Users table to store user registration information
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    organization_name VARCHAR(255) NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    logo_path VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Comments for documentation
COMMENT ON TABLE users IS 'Stores user registration and authentication information';
COMMENT ON COLUMN users.user_id IS 'Auto-generated unique user identifier';
COMMENT ON COLUMN users.organization_name IS 'Name of the organization the user belongs to';
COMMENT ON COLUMN users.user_name IS 'Full name of the user';
COMMENT ON COLUMN users.contact_phone IS 'Contact phone number of the user';
COMMENT ON COLUMN users.email IS 'Unique email address for login and communication';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hashed password for security';
COMMENT ON COLUMN users.logo_path IS 'Path to organization logo file (optional)';
COMMENT ON COLUMN users.created_at IS 'Timestamp when user was created';
COMMENT ON COLUMN users.updated_at IS 'Timestamp when user was last updated';
```

### 2. Files Table
```sql
-- Files table to store file upload and processing metadata
CREATE TABLE files (
    file_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    upload_date DATE NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    line_count INTEGER,
    storage_location VARCHAR(500) NOT NULL,
    processed_flag BOOLEAN DEFAULT FALSE,
    engagement_name VARCHAR(255),
    browser_ip VARCHAR(45),
    browser_location VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Comments for documentation
COMMENT ON TABLE files IS 'Stores file upload and processing metadata';
COMMENT ON COLUMN files.file_id IS 'Auto-generated unique file identifier';
COMMENT ON COLUMN files.user_id IS 'Foreign key reference to users table';
COMMENT ON COLUMN files.upload_date IS 'Date when file was uploaded';
COMMENT ON COLUMN files.filename IS 'System-generated filename for storage';
COMMENT ON COLUMN files.original_filename IS 'Original filename uploaded by user';
COMMENT ON COLUMN files.line_count IS 'Number of data rows in file (excluding header)';
COMMENT ON COLUMN files.storage_location IS 'Full path to file in storage system';
COMMENT ON COLUMN files.processed_flag IS 'Flag indicating if file has been processed';
COMMENT ON COLUMN files.engagement_name IS 'User-provided engagement name for search';
COMMENT ON COLUMN files.browser_ip IS 'IP address of user browser (if captured)';
COMMENT ON COLUMN files.browser_location IS 'Geographic location of user (if captured)';
COMMENT ON COLUMN files.created_at IS 'Timestamp when file record was created';
COMMENT ON COLUMN files.updated_at IS 'Timestamp when file record was last updated';
```

### 3. Database Constraints and Indexes

#### Primary Keys
```sql
-- Primary keys are automatically created with SERIAL columns
-- users.user_id (SERIAL PRIMARY KEY)
-- files.file_id (SERIAL PRIMARY KEY)
```

#### Foreign Keys
```sql
-- Foreign key constraint for files.user_id
ALTER TABLE files 
ADD CONSTRAINT fk_files_user_id 
FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;
```

#### Unique Constraints
```sql
-- Email must be unique for users
ALTER TABLE users 
ADD CONSTRAINT uk_users_email UNIQUE (email);
```

#### Check Constraints
```sql
-- Phone number format validation
ALTER TABLE users 
ADD CONSTRAINT chk_users_phone 
CHECK (contact_phone ~ '^[0-9+\-\s\(\)]{10,20}$');

-- Email format validation
ALTER TABLE users 
ADD CONSTRAINT chk_users_email 
CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- File size validation (assuming line_count represents file size)
ALTER TABLE files 
ADD CONSTRAINT chk_files_line_count 
CHECK (line_count > 0 AND line_count <= 1000000);
```

---

## Database Setup

### 1. Docker Setup for PostgreSQL

#### Docker Compose File (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: geopulse-postgres
    environment:
      POSTGRES_DB: geopulse_db
      POSTGRES_USER: geopulse_user
      POSTGRES_PASSWORD: password123
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=en_US.UTF-8 --lc-ctype=en_US.UTF-8"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
      - /opt:/opt  # Shared volume for file storage
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U geopulse_user -d geopulse_db"]
      interval: 30s
      timeout: 10s
      retries: 3

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: geopulse-pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@geopulse.com
      PGADMIN_DEFAULT_PASSWORD: admin123
      PGADMIN_CONFIG_SERVER_MODE: 'False'
    ports:
      - "5050:80"
    volumes:
      - pgadmin_data:/var/lib/pgadmin
    depends_on:
      - postgres
    restart: unless-stopped

volumes:
  postgres_data:
  pgadmin_data:
```

#### Database Initialization Script (`init-scripts/01-init.sql`)
```sql
-- Create database and user
CREATE DATABASE geopulse_db;
CREATE USER geopulse_user WITH PASSWORD 'password123';
GRANT ALL PRIVILEGES ON DATABASE geopulse_db TO geopulse_user;

-- Connect to the database
\c geopulse_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Set timezone
SET timezone = 'UTC';

-- Create schema
CREATE SCHEMA IF NOT EXISTS public;

-- Grant privileges
GRANT ALL ON SCHEMA public TO geopulse_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO geopulse_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO geopulse_user;
```

### 2. Manual PostgreSQL Installation

#### Ubuntu/Debian Installation
```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Switch to postgres user
sudo -i -u postgres

# Create database and user
createdb geopulse_db
createuser --interactive geopulse_user
# Enter password when prompted

# Connect to PostgreSQL
psql

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE geopulse_db TO geopulse_user;
\q
```

#### macOS Installation (using Homebrew)
```bash
# Install PostgreSQL
brew install postgresql

# Start PostgreSQL service
brew services start postgresql

# Create database and user
createdb geopulse_db
createuser --interactive geopulse_user
# Enter password when prompted

# Connect to PostgreSQL
psql geopulse_db

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE geopulse_db TO geopulse_user;
\q
```

### 3. Database Connection Configuration

#### Python Database Configuration (`app/database.py`)
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,  # Number of connections to maintain
    max_overflow=30,  # Additional connections that can be created
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=settings.DEBUG  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """
    Database dependency for FastAPI
    Creates a new database session for each request
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database tables
    Creates all tables defined in models
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise
```

---

## Migration Management

### 1. Alembic Setup

#### Alembic Configuration (`alembic.ini`)
```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://geopulse_user:password123@localhost:5432/geopulse_db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

#### Alembic Environment (`alembic/env.py`)
```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from app.core.config import settings
from app.models import user, file  # Import all models
from app.database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url():
    return settings.DATABASE_URL

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 2. Migration Commands

#### Initialize Alembic
```bash
# Initialize alembic in your project
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration to database
alembic upgrade head
```

#### Common Migration Commands
```bash
# Create a new migration
alembic revision --autogenerate -m "Add new column to users table"

# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade +1

# Rollback one migration
alembic downgrade -1

# Rollback to specific migration
alembic downgrade <revision_id>

# Show current migration status
alembic current

# Show migration history
alembic history
```

### 3. Example Migration Files

#### Initial Migration (`alembic/versions/001_initial_migration.py`)
```python
"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-08-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('organization_name', sa.String(length=255), nullable=False),
        sa.Column('user_name', sa.String(length=255), nullable=False),
        sa.Column('contact_phone', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('logo_path', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)

    # Create files table
    op.create_table('files',
        sa.Column('file_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('upload_date', sa.Date(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('line_count', sa.Integer(), nullable=True),
        sa.Column('storage_location', sa.String(length=500), nullable=False),
        sa.Column('processed_flag', sa.Boolean(), nullable=True),
        sa.Column('engagement_name', sa.String(length=255), nullable=True),
        sa.Column('browser_ip', sa.String(length=45), nullable=True),
        sa.Column('browser_location', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('file_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_files_file_id'), 'files', ['file_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_files_file_id'), table_name='files')
    op.drop_table('files')
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
```

---

## Indexing Strategy

### 1. Primary Indexes
```sql
-- Primary key indexes are automatically created
-- users.user_id (PRIMARY KEY)
-- files.file_id (PRIMARY KEY)
```

### 2. Foreign Key Indexes
```sql
-- Index on foreign key for better join performance
CREATE INDEX idx_files_user_id ON files(user_id);
```

### 3. Search Indexes
```sql
-- Index for email searches (unique)
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Index for user name searches
CREATE INDEX idx_users_user_name ON users(user_name);

-- Index for organization searches
CREATE INDEX idx_users_organization ON users(organization_name);

-- Index for file upload date searches
CREATE INDEX idx_files_upload_date ON files(upload_date);

-- Index for engagement name searches
CREATE INDEX idx_files_engagement_name ON files(engagement_name);

-- Index for processed flag searches
CREATE INDEX idx_files_processed_flag ON files(processed_flag);
```

### 4. Composite Indexes
```sql
-- Composite index for user files by date
CREATE INDEX idx_files_user_date ON files(user_id, upload_date);

-- Composite index for processed files by user
CREATE INDEX idx_files_user_processed ON files(user_id, processed_flag);
```

### 5. Full-Text Search Indexes
```sql
-- Full-text search on engagement names
CREATE INDEX idx_files_engagement_fts ON files USING gin(to_tsvector('english', engagement_name));

-- Full-text search on organization names
CREATE INDEX idx_users_organization_fts ON users USING gin(to_tsvector('english', organization_name));
```

---

## Backup and Recovery

### 1. Automated Backup Script (`scripts/backup.sh`)
```bash
#!/bin/bash

# Database backup script for GeoPulse
# This script creates daily backups of the PostgreSQL database

# Configuration
DB_NAME="geopulse_db"
DB_USER="geopulse_user"
DB_HOST="localhost"
DB_PORT="5432"
BACKUP_DIR="/opt/backups/geopulse"
RETENTION_DAYS=30

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Generate backup filename with timestamp
BACKUP_FILE="$BACKUP_DIR/geopulse_$(date +%Y%m%d_%H%M%S).sql"

# Create backup
echo "Creating backup: $BACKUP_FILE"
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME > $BACKUP_FILE

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup completed successfully: $BACKUP_FILE"
    
    # Compress backup file
    gzip $BACKUP_FILE
    echo "Backup compressed: $BACKUP_FILE.gz"
    
    # Remove old backups (older than RETENTION_DAYS)
    find $BACKUP_DIR -name "geopulse_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    echo "Old backups cleaned up"
else
    echo "Backup failed!"
    exit 1
fi
```

### 2. Restore Script (`scripts/restore.sh`)
```bash
#!/bin/bash

# Database restore script for GeoPulse
# This script restores the database from a backup file

# Configuration
DB_NAME="geopulse_db"
DB_USER="geopulse_user"
DB_HOST="localhost"
DB_PORT="5432"
BACKUP_FILE=$1

# Check if backup file is provided
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 /opt/backups/geopulse/geopulse_20250801_120000.sql.gz"
    exit 1
fi

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Confirm restore operation
echo "WARNING: This will overwrite the current database!"
echo "Backup file: $BACKUP_FILE"
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restore cancelled"
    exit 1
fi

# Drop and recreate database
echo "Dropping existing database..."
dropdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME

echo "Creating new database..."
createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME

# Restore from backup
echo "Restoring from backup..."
if [[ $BACKUP_FILE == *.gz ]]; then
    gunzip -c $BACKUP_FILE | psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME
else
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME < $BACKUP_FILE
fi

if [ $? -eq 0 ]; then
    echo "Restore completed successfully"
else
    echo "Restore failed!"
    exit 1
fi
```

### 3. Cron Job Setup
```bash
# Add to crontab for daily backups at 2 AM
# crontab -e
0 2 * * * /opt/geopulse/scripts/backup.sh >> /var/log/geopulse/backup.log 2>&1
```

---

## Performance Optimization

### 1. Database Configuration (`postgresql.conf`)
```ini
# Memory Configuration
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Connection Configuration
max_connections = 100
superuser_reserved_connections = 3

# Write-Ahead Logging
wal_buffers = 16MB
checkpoint_completion_target = 0.9
checkpoint_timeout = 5min

# Query Planning
random_page_cost = 1.1
effective_io_concurrency = 200

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = 1000
```

### 2. Query Optimization Examples

#### Optimized User Queries
```sql
-- Get user with files count (optimized)
SELECT 
    u.user_id,
    u.user_name,
    u.email,
    u.organization_name,
    COUNT(f.file_id) as file_count,
    SUM(CASE WHEN f.processed_flag = true THEN 1 ELSE 0 END) as processed_files
FROM users u
LEFT JOIN files f ON u.user_id = f.user_id
WHERE u.email = $1
GROUP BY u.user_id, u.user_name, u.email, u.organization_name;

-- Get user files with pagination (optimized)
SELECT 
    f.file_id,
    f.filename,
    f.upload_date,
    f.processed_flag,
    f.engagement_name,
    f.line_count
FROM files f
WHERE f.user_id = $1
ORDER BY f.upload_date DESC, f.created_at DESC
LIMIT $2 OFFSET $3;
```

#### Optimized File Queries
```sql
-- Get file processing statistics (optimized)
SELECT 
    DATE_TRUNC('month', upload_date) as month,
    COUNT(*) as total_files,
    SUM(CASE WHEN processed_flag = true THEN 1 ELSE 0 END) as processed_files,
    AVG(line_count) as avg_lines_per_file
FROM files
WHERE user_id = $1
GROUP BY DATE_TRUNC('month', upload_date)
ORDER BY month DESC;

-- Search files by engagement name (with full-text search)
SELECT 
    file_id,
    filename,
    upload_date,
    engagement_name,
    processed_flag
FROM files
WHERE user_id = $1
AND to_tsvector('english', engagement_name) @@ plainto_tsquery('english', $2)
ORDER BY upload_date DESC;
```

### 3. Connection Pooling Configuration
```python
# Enhanced database configuration with connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,  # Number of connections to maintain
    max_overflow=30,  # Additional connections that can be created
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_timeout=30,  # Timeout for getting connection from pool
    echo=settings.DEBUG  # Log SQL queries in debug mode
)
```

---

## Security Configuration

### 1. Database Security Settings (`pg_hba.conf`)
```ini
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
local   geopulse_db     geopulse_user                          md5
host    geopulse_db     geopulse_user    127.0.0.1/32          md5
host    geopulse_db     geopulse_user    ::1/128               md5
host    all             all             0.0.0.0/0              reject
```

### 2. User Permissions
```sql
-- Create application user with limited permissions
CREATE USER geopulse_user WITH PASSWORD 'strong_password_here';

-- Grant necessary permissions
GRANT CONNECT ON DATABASE geopulse_db TO geopulse_user;
GRANT USAGE ON SCHEMA public TO geopulse_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO geopulse_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO geopulse_user;

-- Grant permissions for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO geopulse_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO geopulse_user;
```

### 3. Row Level Security (RLS)
```sql
-- Enable RLS on files table
ALTER TABLE files ENABLE ROW LEVEL SECURITY;

-- Create policy for users to see only their own files
CREATE POLICY files_user_policy ON files
    FOR ALL
    USING (user_id = current_setting('app.current_user_id')::integer);

-- Create policy for users to see only their own data
CREATE POLICY users_own_policy ON users
    FOR SELECT
    USING (user_id = current_setting('app.current_user_id')::integer);
```

---

## Development Setup

### 1. Local Development Environment
```bash
# Start PostgreSQL with Docker
docker-compose up -d postgres

# Wait for database to be ready
sleep 10

# Run database migrations
alembic upgrade head

# Create test data (optional)
python scripts/create_test_data.py

# Verify database connection
python -c "
from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT version()'))
    print('Database connected:', result.fetchone()[0])
"
```

### 2. Database Testing Setup
```python
# Test database configuration
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app

# Test database URL
TEST_DATABASE_URL = "postgresql://test_user:test_pass@localhost:5432/geopulse_test"

# Create test engine
test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

### 3. Database Monitoring Queries
```sql
-- Check database size
SELECT 
    pg_size_pretty(pg_database_size('geopulse_db')) as database_size;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Check slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

---

## Next Steps for Developers

1. **Set up PostgreSQL** - Install and configure PostgreSQL database
2. **Create database schema** - Run migrations to create tables and indexes
3. **Configure connection pooling** - Set up SQLAlchemy with proper connection management
4. **Implement data models** - Create SQLAlchemy models for all tables
5. **Set up migrations** - Configure Alembic for database version control
6. **Create backup strategy** - Implement automated backup and restore procedures
7. **Optimize queries** - Add proper indexes and optimize slow queries
8. **Implement security** - Configure user permissions and row-level security
9. **Set up monitoring** - Monitor database performance and health
10. **Test thoroughly** - Create comprehensive database tests

Remember to:
- Always use migrations for database changes
- Test all queries with realistic data volumes
- Monitor database performance regularly
- Keep backups up to date
- Use connection pooling for better performance
- Implement proper security measures
- Document all database changes
- Use prepared statements to prevent SQL injection
