# GeoPulse Database SQL Queries

This document contains SQL queries to explore and manage the **geopulse_db** database. Run these queries in pgAdmin or any PostgreSQL client.

## 🐳 Starting PostgreSQL with Docker Compose

### Prerequisites
- Docker and Docker Compose installed on your system
- Navigate to the `API/database/` directory

### Start PostgreSQL Database
```bash
# Navigate to the database directory
cd API/database/

# Start PostgreSQL and pgAdmin containers
docker-compose up -d

# Check if containers are running
docker-compose ps

# View logs
docker-compose logs -f
```

### Stop PostgreSQL Database
```bash
# Stop containers
docker-compose down

# Stop and remove volumes (WARNING: This will delete all data)
docker-compose down -v
```

### Restart PostgreSQL Database
```bash
# Restart containers
docker-compose restart

# Or stop and start again
docker-compose down
docker-compose up -d
```

### Database Container Status
```bash
# Check container health
docker-compose ps

# View real-time logs
docker-compose logs -f postgres

# Access PostgreSQL directly
docker-compose exec postgres psql -U geopulse_user -d geopulse_db
```

## Database Access

- **pgAdmin Web Interface**: http://localhost:8080
- **Database**: `geopulse_db`
- **Username**: `geopulse_user`
- **Password**: `password123`
- **PostgreSQL Port**: 5432

---

## 1. Database Overview Queries

### List All Tables
```sql
SELECT table_name, table_type
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_catalog = 'geopulse_db'
ORDER BY table_name;
```

### Complete Table Structure Overview
```sql
SELECT 
    t.table_name,
    c.column_name,
    c.data_type,
    c.character_maximum_length,
    c.is_nullable,
    c.column_default
FROM information_schema.tables t
JOIN information_schema.columns c ON t.table_name = c.table_name
WHERE t.table_schema = 'public' 
  AND t.table_catalog = 'geopulse_db'
ORDER BY t.table_name, c.ordinal_position;
```

### Database and User Information
```sql
-- Current database info
SELECT current_database() as current_db, current_user as current_user;

-- Database size
SELECT 
    pg_database.datname as database_name,
    pg_size_pretty(pg_database_size(pg_database.datname)) as size
FROM pg_database
WHERE datname = 'geopulse_db';
```

---

## 2. Table Structure Queries

### Users Table Details
```sql
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'users' 
  AND table_schema = 'public'
  AND table_catalog = 'geopulse_db'
ORDER BY ordinal_position;
```

### Files Table Details
```sql
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'files' 
  AND table_schema = 'public'
  AND table_catalog = 'geopulse_db'
ORDER BY ordinal_position;
```

---

## 3. Index and Constraint Queries

### All Indexes in Database
```sql
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND schemaname IN (
    SELECT schema_name 
    FROM information_schema.schemata 
    WHERE catalog_name = 'geopulse_db'
  )
ORDER BY tablename, indexname;
```

### Foreign Key Relationships
```sql
SELECT
    tc.table_name AS table_name,
    kcu.column_name AS column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    tc.constraint_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
    AND tc.table_catalog = 'geopulse_db';
```

---

## 4. Triggers and Functions

### List Triggers
```sql
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE trigger_schema = 'public'
  AND trigger_catalog = 'geopulse_db';
```

### List Custom Functions
```sql
SELECT 
    routine_name,
    routine_type,
    data_type AS return_type
FROM information_schema.routines
WHERE routine_schema = 'public'
  AND routine_catalog = 'geopulse_db'
  AND routine_type = 'FUNCTION';
```

---

## 5. Data Exploration Queries

### Table Record Counts
```sql
SELECT 
    'users' as table_name, 
    COUNT(*) as record_count,
    'Active users in system' as description
FROM users
UNION ALL
SELECT 
    'files' as table_name, 
    COUNT(*) as record_count,
    'Total files uploaded' as description
FROM files;
```

### Sample Data from Users Table
```sql
SELECT 
    user_id,
    organization_name,
    user_name,
    email,
    file_count,
    created_at,
    updated_at
FROM users
ORDER BY created_at DESC
LIMIT 10;
```

### Sample Data from Files Table
```sql
SELECT 
    file_id,
    user_id,
    filename,
    original_filename,
    processed_flag,
    upload_date,
    file_size_mb,
    processing_time_seconds,
    created_at
FROM files
ORDER BY created_at DESC
LIMIT 10;
```

---

## 6. Analytics and Reporting Queries

### User Statistics
```sql
SELECT 
    COUNT(*) as total_users,
    COUNT(CASE WHEN file_count > 0 THEN 1 END) as users_with_files,
    AVG(file_count) as avg_files_per_user,
    MAX(file_count) as max_files_per_user
FROM users;
```

### File Processing Statistics
```sql
SELECT 
    COUNT(*) as total_files,
    COUNT(CASE WHEN processed_flag = true THEN 1 END) as processed_files,
    COUNT(CASE WHEN processed_flag = false THEN 1 END) as pending_files,
    ROUND(AVG(processing_time_seconds), 2) as avg_processing_time,
    ROUND(AVG(file_size_mb), 2) as avg_file_size
FROM files;
```

### Files by Upload Date
```sql
SELECT 
    upload_date,
    COUNT(*) as files_uploaded,
    COUNT(CASE WHEN processed_flag = true THEN 1 END) as processed,
    COUNT(CASE WHEN processed_flag = false THEN 1 END) as pending
FROM files
GROUP BY upload_date
ORDER BY upload_date DESC
LIMIT 30;
```

### Top Organizations by File Count
```sql
SELECT 
    u.organization_name,
    COUNT(f.file_id) as total_files,
    COUNT(CASE WHEN f.processed_flag = true THEN 1 END) as processed_files,
    ROUND(AVG(f.file_size_mb), 2) as avg_file_size
FROM users u
LEFT JOIN files f ON u.user_id = f.user_id
GROUP BY u.organization_name
ORDER BY total_files DESC
LIMIT 10;
```

---

## 7. Database Maintenance Queries

### Comprehensive Database Summary
```sql
SELECT 
    'Database' as component,
    'geopulse_db' as name,
    pg_size_pretty(pg_database_size('geopulse_db')) as size
UNION ALL
SELECT 
    'Table' as component,
    'users' as name,
    pg_size_pretty(pg_total_relation_size('users')) as size
UNION ALL
SELECT 
    'Table' as component,
    'files' as name,
    pg_size_pretty(pg_total_relation_size('files')) as size;
```

### Check Table Sizes
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Recent Activity
```sql
-- Recent user registrations
SELECT 
    user_id,
    organization_name,
    user_name,
    email,
    created_at
FROM users
WHERE created_at >= NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;

-- Recent file uploads
SELECT 
    f.file_id,
    u.organization_name,
    f.filename,
    f.processed_flag,
    f.created_at
FROM files f
JOIN users u ON f.user_id = u.user_id
WHERE f.created_at >= NOW() - INTERVAL '7 days'
ORDER BY f.created_at DESC;
```

---

## 8. Troubleshooting Queries

### Check for Orphaned Records
```sql
-- Files without users (should be empty due to foreign key)
SELECT f.*
FROM files f
LEFT JOIN users u ON f.user_id = u.user_id
WHERE u.user_id IS NULL;
```

### Verify Trigger Functionality
```sql
-- Check if file_count matches actual file count
SELECT 
    u.user_id,
    u.organization_name,
    u.file_count as stored_count,
    COUNT(f.file_id) as actual_count,
    (u.file_count - COUNT(f.file_id)) as difference
FROM users u
LEFT JOIN files f ON u.user_id = f.user_id
GROUP BY u.user_id, u.organization_name, u.file_count
HAVING u.file_count != COUNT(f.file_id);
```

### Check for Data Integrity Issues
```sql
-- Users with invalid email formats
SELECT user_id, email
FROM users
WHERE email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';

-- Files with invalid dates
SELECT file_id, upload_date, created_at
FROM files
WHERE upload_date > CURRENT_DATE;
```

---

## Quick Reference

### Essential Queries for Daily Use
1. **List tables**: Query #1 from Database Overview
2. **Check record counts**: Query from Data Exploration section
3. **View recent activity**: Queries from Recent Activity section
4. **Check database size**: Query from Database Maintenance section

### Performance Monitoring
- Use the analytics queries to monitor system usage
- Check table sizes regularly for growth patterns
- Monitor processing times and file sizes

### Data Validation
- Run troubleshooting queries periodically
- Verify trigger functionality after bulk operations
- Check for data integrity issues monthly