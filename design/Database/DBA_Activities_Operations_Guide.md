# DBA Activities & Operations Guide
## GeoPulse PostgreSQL Database

**Document Version:** 1.0  
**Date:** August 2025  
**Database:** PostgreSQL 15+  
**Environment:** Production/Development  

---

## Table of Contents
1. [Database Backup Operations](#database-backup-operations)
2. [Database Recovery Procedures](#database-recovery-procedures)
3. [Data Migration Between Servers](#data-migration-between-servers)
4. [Connection Management & Security](#connection-management--security)
5. [Database Monitoring & Maintenance](#database-monitoring--maintenance)
6. [Emergency Procedures](#emergency-procedures)

---

## Database Backup Operations

### 1. Automated Backup Scripts

#### Daily Full Backup Script
```bash
#!/bin/bash
# daily_backup.sh - Daily full database backup
# Usage: ./daily_backup.sh [database_name]

DB_NAME=${1:-geopulse_db}
DB_USER="geopulse_user"
BACKUP_DIR="/opt/backups/geopulse"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/full_backup_${DB_NAME}_${DATE}.sql"
LOG_FILE="${BACKUP_DIR}/backup_log_${DATE}.log"

# Create backup directory if it doesn't exist
mkdir -p ${BACKUP_DIR}

# Set environment variables
export PGPASSWORD="your_secure_password"

echo "Starting daily backup for ${DB_NAME} at $(date)" | tee -a ${LOG_FILE}

# Perform full backup with compression
pg_dump -h localhost -U ${DB_USER} -d ${DB_NAME} \
  --verbose \
  --clean \
  --create \
  --if-exists \
  --no-password \
  --format=custom \
  --compress=9 \
  --file="${BACKUP_FILE}.dump" 2>&1 | tee -a ${LOG_FILE}

# Check backup status
if [ $? -eq 0 ]; then
    echo "Backup completed successfully: ${BACKUP_FILE}.dump" | tee -a ${LOG_FILE}
    
    # Calculate backup size
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}.dump" | cut -f1)
    echo "Backup size: ${BACKUP_SIZE}" | tee -a ${LOG_FILE}
    
    # Create backup metadata
    cat > "${BACKUP_FILE}.meta" << EOF
BACKUP_TYPE=full
DATABASE=${DB_NAME}
BACKUP_DATE=${DATE}
BACKUP_SIZE=${BACKUP_SIZE}
BACKUP_FILE=${BACKUP_FILE}.dump
COMPRESSION=yes
EOF
    
    # Clean old backups (keep last 30 days)
    find ${BACKUP_DIR} -name "full_backup_*.dump" -mtime +30 -delete
    find ${BACKUP_DIR} -name "backup_log_*.log" -mtime +30 -delete
    
else
    echo "Backup failed! Check log file: ${LOG_FILE}" | tee -a ${LOG_FILE}
    exit 1
fi

echo "Daily backup completed at $(date)" | tee -a ${LOG_FILE}
```

#### Incremental Backup Script
```bash
#!/bin/bash
# incremental_backup.sh - Incremental backup using WAL archiving
# Usage: ./incremental_backup.sh

DB_NAME="geopulse_db"
DB_USER="geopulse_user"
WAL_ARCHIVE_DIR="/opt/backups/geopulse/wal_archive"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/opt/backups/geopulse/incremental_log_${DATE}.log"

# Create WAL archive directory
mkdir -p ${WAL_ARCHIVE_DIR}

echo "Starting incremental backup at $(date)" | tee -a ${LOG_FILE}

# Trigger WAL switch
psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "SELECT pg_switch_wal();" 2>&1 | tee -a ${LOG_FILE}

# Archive WAL files
pg_archivecleanup ${WAL_ARCHIVE_DIR} 000000010000000000000001 2>&1 | tee -a ${LOG_FILE}

echo "Incremental backup completed at $(date)" | tee -a ${LOG_FILE}
```

### 2. PostgreSQL Configuration for Backup

#### postgresql.conf Backup Settings
```ini
# Backup Configuration
wal_level = replica                    # Enable WAL archiving
archive_mode = on                      # Enable archive mode
archive_command = 'cp %p /opt/backups/geopulse/wal_archive/%f'
archive_timeout = 300                  # Force WAL switch every 5 minutes
max_wal_senders = 3                    # Allow WAL streaming
wal_keep_segments = 32                 # Keep WAL segments for replication

# Backup Performance
checkpoint_timeout = 15min             # Checkpoint frequency
checkpoint_completion_target = 0.9     # Spread checkpoint writes
max_wal_size = 2GB                     # Maximum WAL size before checkpoint
min_wal_size = 80MB                    # Minimum WAL size

# Connection Settings for Backup
max_connections = 100                  # Maximum concurrent connections
shared_preload_libraries = 'pg_stat_statements'  # Performance monitoring
```

#### pg_hba.conf for Backup Access
```ini
# Backup user access
local   geopulse_db    geopulse_backup    md5
host    geopulse_db    geopulse_backup    127.0.0.1/32    md5
host    geopulse_db    geopulse_backup    ::1/128         md5

# Replication access for backup
local   replication    geopulse_backup    md5
host    replication    geopulse_backup    127.0.0.1/32    md5
host    replication    geopulse_backup    ::1/128         md5
```

### 3. Backup Verification Script
```bash
#!/bin/bash
# verify_backup.sh - Verify backup integrity
# Usage: ./verify_backup.sh [backup_file]

BACKUP_FILE=${1}
TEST_DB="geopulse_test_$(date +%Y%m%d_%H%M%S)"
DB_USER="geopulse_user"

echo "Verifying backup: ${BACKUP_FILE}"

# Create test database
createdb -h localhost -U ${DB_USER} ${TEST_DB}

# Restore backup to test database
pg_restore -h localhost -U ${DB_USER} -d ${TEST_DB} --verbose ${BACKUP_FILE}

if [ $? -eq 0 ]; then
    echo "Backup verification successful"
    
    # Run basic integrity checks
    psql -h localhost -U ${DB_USER} -d ${TEST_DB} -c "
        SELECT 'users' as table_name, COUNT(*) as row_count FROM users
        UNION ALL
        SELECT 'files' as table_name, COUNT(*) as row_count FROM files;
    "
    
    # Clean up test database
    dropdb -h localhost -U ${DB_USER} ${TEST_DB}
else
    echo "Backup verification failed!"
    exit 1
fi
```

---

## Database Recovery Procedures

### 1. Point-in-Time Recovery (PITR)

#### Recovery Configuration
```bash
#!/bin/bash
# pitr_recovery.sh - Point-in-Time Recovery
# Usage: ./pitr_recovery.sh [backup_file] [recovery_time]

BACKUP_FILE=${1}
RECOVERY_TIME=${2:-"2025-08-01 10:00:00"}
RECOVERY_DB="geopulse_recovery_$(date +%Y%m%d_%H%M%S)"
DB_USER="geopulse_user"

echo "Starting PITR recovery to: ${RECOVERY_TIME}"

# Stop PostgreSQL service
sudo systemctl stop postgresql

# Backup current data directory
sudo cp -r /var/lib/postgresql/15/main /var/lib/postgresql/15/main_backup_$(date +%Y%m%d_%H%M%S)

# Restore base backup
pg_restore -h localhost -U ${DB_USER} -d ${RECOVERY_DB} --verbose ${BACKUP_FILE}

# Create recovery.conf
cat > /var/lib/postgresql/15/main/recovery.conf << EOF
restore_command = 'cp /opt/backups/geopulse/wal_archive/%f %p'
recovery_target_time = '${RECOVERY_TIME}'
recovery_target_action = 'promote'
EOF

# Start PostgreSQL in recovery mode
sudo systemctl start postgresql

# Monitor recovery progress
tail -f /var/log/postgresql/postgresql-15-main.log

echo "PITR recovery completed"
```

### 2. Full Database Recovery

#### Complete Database Restore
```bash
#!/bin/bash
# full_recovery.sh - Complete database recovery
# Usage: ./full_recovery.sh [backup_file]

BACKUP_FILE=${1}
DB_NAME="geopulse_db"
DB_USER="geopulse_user"

echo "Starting full database recovery from: ${BACKUP_FILE}"

# Stop application services
sudo systemctl stop geopulse-api
sudo systemctl stop geopulse-frontend

# Stop PostgreSQL
sudo systemctl stop postgresql

# Backup current database (if exists)
if pg_isready -h localhost -U ${DB_USER} -d ${DB_NAME}; then
    pg_dump -h localhost -U ${DB_USER} -d ${DB_NAME} --format=custom --file="/opt/backups/geopulse/pre_recovery_backup_$(date +%Y%m%d_%H%M%S).dump"
fi

# Drop existing database
dropdb -h localhost -U ${DB_USER} ${DB_NAME}

# Restore from backup
pg_restore -h localhost -U ${DB_USER} --create --clean --if-exists --verbose ${BACKUP_FILE}

# Verify recovery
psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "
    SELECT 'Recovery verification:' as status;
    SELECT COUNT(*) as user_count FROM users;
    SELECT COUNT(*) as file_count FROM files;
    SELECT MAX(created_at) as latest_record FROM files;
"

# Start services
sudo systemctl start postgresql
sudo systemctl start geopulse-api
sudo systemctl start geopulse-frontend

echo "Full database recovery completed"
```

### 3. Emergency Recovery Procedures

#### Emergency Recovery Checklist
```bash
#!/bin/bash
# emergency_recovery_checklist.sh

echo "=== EMERGENCY RECOVERY CHECKLIST ==="
echo "1. Assess the situation"
echo "   - Database status: $(pg_isready -h localhost && echo 'ONLINE' || echo 'OFFLINE')"
echo "   - Disk space: $(df -h /var/lib/postgresql | tail -1)"
echo "   - Memory usage: $(free -h | grep Mem)"

echo "2. Stop all application services"
sudo systemctl stop geopulse-api
sudo systemctl stop geopulse-frontend

echo "3. Backup current state (if possible)"
if pg_isready -h localhost; then
    pg_dump -h localhost -U geopulse_user -d geopulse_db --format=custom --file="/opt/backups/geopulse/emergency_backup_$(date +%Y%m%d_%H%M%S).dump"
fi

echo "4. Check PostgreSQL logs"
tail -50 /var/log/postgresql/postgresql-15-main.log

echo "5. Verify backup availability"
ls -la /opt/backups/geopulse/full_backup_*.dump | tail -5

echo "6. Ready for recovery procedure"
```

---

## Data Migration Between Servers

### 1. Database Migration Script

#### Source to Target Migration
```bash
#!/bin/bash
# migrate_database.sh - Migrate database between servers
# Usage: ./migrate_database.sh [source_host] [target_host] [database_name]

SOURCE_HOST=${1:-"source-server.com"}
TARGET_HOST=${2:-"target-server.com"}
DB_NAME=${3:-"geopulse_db"}
DB_USER="geopulse_user"
BACKUP_FILE="/tmp/migration_backup_$(date +%Y%m%d_%H%M%S).dump"

echo "Starting database migration from ${SOURCE_HOST} to ${TARGET_HOST}"

# Step 1: Create backup on source server
echo "Creating backup on source server..."
pg_dump -h ${SOURCE_HOST} -U ${DB_USER} -d ${DB_NAME} \
  --verbose \
  --clean \
  --create \
  --if-exists \
  --no-password \
  --format=custom \
  --compress=9 \
  --file="${BACKUP_FILE}"

# Step 2: Transfer backup file to target server
echo "Transferring backup file to target server..."
scp ${BACKUP_FILE} ${DB_USER}@${TARGET_HOST}:/tmp/

# Step 3: Restore on target server
echo "Restoring database on target server..."
ssh ${DB_USER}@${TARGET_HOST} "
    # Stop application services
    sudo systemctl stop geopulse-api
    
    # Drop existing database if exists
    dropdb -h localhost -U ${DB_USER} ${DB_NAME} 2>/dev/null || true
    
    # Restore from backup
    pg_restore -h localhost -U ${DB_USER} --create --clean --if-exists --verbose /tmp/$(basename ${BACKUP_FILE})
    
    # Start application services
    sudo systemctl start geopulse-api
    
    # Verify migration
    psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c 'SELECT COUNT(*) as user_count FROM users;'
    psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c 'SELECT COUNT(*) as file_count FROM files;'
"

# Step 4: Clean up
rm -f ${BACKUP_FILE}
ssh ${DB_USER}@${TARGET_HOST} "rm -f /tmp/$(basename ${BACKUP_FILE})"

echo "Database migration completed successfully"
```

### 2. Live Migration with Replication

#### Setup Logical Replication
```sql
-- On source server (publisher)
-- Create publication
CREATE PUBLICATION geopulse_pub FOR TABLE users, files;

-- Grant replication privileges
GRANT REPLICATION ON ALL TABLES IN SCHEMA public TO geopulse_repl;

-- On target server (subscriber)
-- Create subscription
CREATE SUBSCRIPTION geopulse_sub 
CONNECTION 'host=source-server.com port=5432 dbname=geopulse_db user=geopulse_repl password=repl_password'
PUBLICATION geopulse_pub;

-- Monitor replication lag
SELECT 
    pid,
    application_name,
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) as lag_bytes
FROM pg_stat_replication;
```

### 3. Data Synchronization Script
```bash
#!/bin/bash
# sync_databases.sh - Synchronize data between servers
# Usage: ./sync_databases.sh [source_host] [target_host]

SOURCE_HOST=${1}
TARGET_HOST=${2}
DB_NAME="geopulse_db"
DB_USER="geopulse_user"

echo "Synchronizing databases between ${SOURCE_HOST} and ${TARGET_HOST}"

# Create sync script
cat > /tmp/sync_script.sql << 'EOF'
-- Export data from source
\copy (SELECT * FROM users) TO '/tmp/users_export.csv' WITH CSV HEADER;
\copy (SELECT * FROM files) TO '/tmp/files_export.csv' WITH CSV HEADER;

-- Import data to target
\copy users FROM '/tmp/users_export.csv' WITH CSV HEADER;
\copy files FROM '/tmp/files_export.csv' WITH CSV HEADER;
EOF

# Execute sync on source
psql -h ${SOURCE_HOST} -U ${DB_USER} -d ${DB_NAME} -f /tmp/sync_script.sql

# Transfer export files
scp /tmp/*_export.csv ${DB_USER}@${TARGET_HOST}:/tmp/

# Execute sync on target
ssh ${DB_USER}@${TARGET_HOST} "
    psql -h localhost -U ${DB_USER} -d ${DB_NAME} -f /tmp/sync_script.sql
    rm -f /tmp/*_export.csv
"

# Clean up
rm -f /tmp/sync_script.sql /tmp/*_export.csv

echo "Database synchronization completed"
```

---

## Connection Management & Security

### 1. Connection Pooling Configuration

#### PgBouncer Configuration
```ini
# /etc/pgbouncer/pgbouncer.ini
[databases]
geopulse_db = host=localhost port=5432 dbname=geopulse_db

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
max_db_connections = 50
max_user_connections = 50
server_reset_query = DISCARD ALL
server_check_query = SELECT 1
server_check_delay = 30
tcp_keepalive = 1
tcp_keepidle = 600
tcp_keepintvl = 60
tcp_keepcnt = 3

# Logging
log_connections = 1
log_disconnections = 1
log_pooler_errors = 1
log_stats = 1
stats_period = 60
```

#### PgBouncer User Authentication
```ini
# /etc/pgbouncer/userlist.txt
"geopulse_user" "md5_hashed_password"
"geopulse_app" "md5_hashed_password"
```

### 2. Connection Limiting Scripts

#### Connection Monitoring Script
```bash
#!/bin/bash
# monitor_connections.sh - Monitor database connections
# Usage: ./monitor_connections.sh

DB_NAME="geopulse_db"
DB_USER="geopulse_user"

echo "=== Database Connection Monitor ==="
echo "Timestamp: $(date)"
echo ""

# Current connections
echo "Current Connections:"
psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "
SELECT 
    datname as database,
    usename as username,
    application_name,
    client_addr,
    state,
    query_start,
    state_change
FROM pg_stat_activity 
WHERE datname = '${DB_NAME}'
ORDER BY query_start DESC;
"

echo ""
echo "Connection Summary:"
psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "
SELECT 
    state,
    COUNT(*) as connection_count
FROM pg_stat_activity 
WHERE datname = '${DB_NAME}'
GROUP BY state
ORDER BY connection_count DESC;
"

echo ""
echo "Long-running Queries (>5 minutes):"
psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query_start,
    EXTRACT(EPOCH FROM (now() - query_start)) as duration_seconds,
    LEFT(query, 100) as query_preview
FROM pg_stat_activity 
WHERE datname = '${DB_NAME}'
  AND state = 'active'
  AND query_start < now() - interval '5 minutes'
ORDER BY query_start;
"
```

#### Connection Limiting Script
```bash
#!/bin/bash
# limit_connections.sh - Limit database connections
# Usage: ./limit_connections.sh [max_connections] [username]

MAX_CONNECTIONS=${1:-10}
LIMIT_USER=${2:-"geopulse_user"}
DB_NAME="geopulse_db"
DB_USER="geopulse_user"

echo "Limiting connections for user ${LIMIT_USER} to ${MAX_CONNECTIONS}"

# Get current connections for user
CURRENT_CONNECTIONS=$(psql -h localhost -U ${DB_USER} -d ${DB_NAME} -t -c "
SELECT COUNT(*) 
FROM pg_stat_activity 
WHERE usename = '${LIMIT_USER}' 
  AND datname = '${DB_NAME}'
  AND state = 'active';
")

echo "Current active connections: ${CURRENT_CONNECTIONS}"

if [ ${CURRENT_CONNECTIONS} -gt ${MAX_CONNECTIONS} ]; then
    echo "Connection limit exceeded. Terminating excess connections..."
    
    # Terminate oldest connections
    psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "
SELECT pg_terminate_backend(pid)
FROM (
    SELECT pid, query_start
    FROM pg_stat_activity 
    WHERE usename = '${LIMIT_USER}' 
      AND datname = '${DB_NAME}'
      AND state = 'active'
    ORDER BY query_start ASC
    LIMIT (${CURRENT_CONNECTIONS} - ${MAX_CONNECTIONS})
) as excess_connections;
"
    
    echo "Excess connections terminated"
else
    echo "Connection count within limits"
fi
```

### 3. Network Security Configuration

#### Firewall Rules for Database
```bash
#!/bin/bash
# setup_database_firewall.sh - Configure firewall for database security

echo "Setting up database firewall rules"

# Allow only specific IPs to connect to PostgreSQL
sudo ufw allow from 192.168.1.0/24 to any port 5432
sudo ufw allow from 10.0.0.0/8 to any port 5432

# Allow PgBouncer connections
sudo ufw allow from 192.168.1.0/24 to any port 6432
sudo ufw allow from 10.0.0.0/8 to any port 6432

# Block all other PostgreSQL connections
sudo ufw deny 5432
sudo ufw deny 6432

# Allow SSH for administration
sudo ufw allow ssh

# Enable firewall
sudo ufw enable

echo "Firewall rules configured"
```

#### PostgreSQL Network Security
```ini
# pg_hba.conf - Network access control
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections
local   all             postgres                                peer
local   geopulse_db     geopulse_user                          md5
local   geopulse_db     geopulse_app                           md5

# Network connections (restricted)
host    geopulse_db     geopulse_user    192.168.1.0/24        md5
host    geopulse_db     geopulse_user    10.0.0.0/8            md5
host    geopulse_db     geopulse_app     192.168.1.0/24        md5
host    geopulse_db     geopulse_app     10.0.0.0/8            md5

# Replication connections
host    replication     geopulse_repl    192.168.1.0/24        md5
host    replication     geopulse_repl    10.0.0.0/8            md5

# Deny all other connections
host    all             all             0.0.0.0/0              reject
```

### 4. SSL/TLS Configuration

#### PostgreSQL SSL Configuration
```ini
# postgresql.conf SSL settings
ssl = on
ssl_cert_file = '/etc/ssl/certs/postgresql.crt'
ssl_key_file = '/etc/ssl/private/postgresql.key'
ssl_ca_file = '/etc/ssl/certs/ca-certificates.crt'
ssl_crl_file = '/etc/ssl/certs/ca-crl.pem'
ssl_prefer_server_ciphers = on
ssl_min_protocol_version = 'TLSv1.2'
ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'
```

#### SSL Certificate Generation
```bash
#!/bin/bash
# generate_ssl_certificates.sh - Generate SSL certificates for PostgreSQL

echo "Generating SSL certificates for PostgreSQL"

# Create SSL directory
sudo mkdir -p /etc/ssl/postgresql
cd /etc/ssl/postgresql

# Generate private key
sudo openssl genrsa -out postgresql.key 2048

# Generate certificate signing request
sudo openssl req -new -key postgresql.key -out postgresql.csr -subj "/C=US/ST=State/L=City/O=Organization/CN=postgresql.server.com"

# Generate self-signed certificate (for development)
sudo openssl x509 -req -in postgresql.csr -signkey postgresql.key -out postgresql.crt -days 365

# Set proper permissions
sudo chown postgres:postgres postgresql.key postgresql.crt
sudo chmod 600 postgresql.key
sudo chmod 644 postgresql.crt

# Copy to PostgreSQL directory
sudo cp postgresql.crt /etc/ssl/certs/
sudo cp postgresql.key /etc/ssl/private/

echo "SSL certificates generated and configured"
```

---

## Database Monitoring & Maintenance

### 1. Automated Maintenance Scripts

#### Daily Maintenance Script
```bash
#!/bin/bash
# daily_maintenance.sh - Daily database maintenance tasks

DB_NAME="geopulse_db"
DB_USER="geopulse_user"
LOG_FILE="/var/log/postgresql/maintenance_$(date +%Y%m%d).log"

echo "Starting daily maintenance at $(date)" | tee -a ${LOG_FILE}

# Update table statistics
echo "Updating table statistics..." | tee -a ${LOG_FILE}
psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "ANALYZE;" 2>&1 | tee -a ${LOG_FILE}

# Vacuum tables
echo "Running VACUUM..." | tee -a ${LOG_FILE}
psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "VACUUM ANALYZE;" 2>&1 | tee -a ${LOG_FILE}

# Check for long-running transactions
echo "Checking for long-running transactions..." | tee -a ${LOG_FILE}
psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "
SELECT 
    pid,
    usename,
    application_name,
    state,
    query_start,
    EXTRACT(EPOCH FROM (now() - query_start)) as duration_seconds
FROM pg_stat_activity 
WHERE state = 'active' 
  AND query_start < now() - interval '1 hour'
ORDER BY query_start;
" 2>&1 | tee -a ${LOG_FILE}

# Check database size
echo "Database size check..." | tee -a ${LOG_FILE}
psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
" 2>&1 | tee -a ${LOG_FILE}

echo "Daily maintenance completed at $(date)" | tee -a ${LOG_FILE}
```

#### Weekly Maintenance Script
```bash
#!/bin/bash
# weekly_maintenance.sh - Weekly database maintenance tasks

DB_NAME="geopulse_db"
DB_USER="geopulse_user"
LOG_FILE="/var/log/postgresql/weekly_maintenance_$(date +%Y%m%d).log"

echo "Starting weekly maintenance at $(date)" | tee -a ${LOG_FILE}

# Full VACUUM
echo "Running full VACUUM..." | tee -a ${LOG_FILE}
psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "VACUUM FULL;" 2>&1 | tee -a ${LOG_FILE}

# Reindex tables
echo "Reindexing tables..." | tee -a ${LOG_FILE}
psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "
SELECT 'REINDEX TABLE ' || tablename || ';' as reindex_command
FROM pg_tables 
WHERE schemaname = 'public';
" | grep REINDEX | psql -h localhost -U ${DB_USER} -d ${DB_NAME} 2>&1 | tee -a ${LOG_FILE}

# Update table statistics
echo "Updating table statistics..." | tee -a ${LOG_FILE}
psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "ANALYZE;" 2>&1 | tee -a ${LOG_FILE}

# Check for bloat
echo "Checking for table bloat..." | tee -a ${LOG_FILE}
psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
" 2>&1 | tee -a ${LOG_FILE}

echo "Weekly maintenance completed at $(date)" | tee -a ${LOG_FILE}
```

### 2. Performance Monitoring

#### Performance Monitoring Script
```bash
#!/bin/bash
# monitor_performance.sh - Monitor database performance

DB_NAME="geopulse_db"
DB_USER="geopulse_user"

echo "=== Database Performance Monitor ==="
echo "Timestamp: $(date)"
echo ""

# Connection statistics
echo "Connection Statistics:"
psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "
SELECT 
    'Active Connections' as metric,
    COUNT(*) as value
FROM pg_stat_activity 
WHERE state = 'active'
UNION ALL
SELECT 
    'Idle Connections' as metric,
    COUNT(*) as value
FROM pg_stat_activity 
WHERE state = 'idle'
UNION ALL
SELECT 
    'Total Connections' as metric,
    COUNT(*) as value
FROM pg_stat_activity;
"

echo ""
echo "Cache Hit Ratio:"
psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "
SELECT 
    schemaname,
    tablename,
    heap_blks_read,
    heap_blks_hit,
    CASE 
        WHEN (heap_blks_hit + heap_blks_read) = 0 THEN 0
        ELSE ROUND(100.0 * heap_blks_hit / (heap_blks_hit + heap_blks_read), 2)
    END as cache_hit_ratio
FROM pg_statio_user_tables
ORDER BY cache_hit_ratio DESC;
"

echo ""
echo "Slow Queries (>1 second):"
psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
WHERE mean_time > 1000
ORDER BY mean_time DESC
LIMIT 10;
"

echo ""
echo "Table Access Statistics:"
psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    n_tup_ins,
    n_tup_upd,
    n_tup_del
FROM pg_stat_user_tables
ORDER BY n_tup_ins + n_tup_upd + n_tup_del DESC;
"
```

### 3. Automated Alerts

#### Alert Monitoring Script
```bash
#!/bin/bash
# database_alerts.sh - Monitor database for alerts

DB_NAME="geopulse_db"
DB_USER="geopulse_user"
ALERT_LOG="/var/log/postgresql/alerts.log"

echo "Checking database alerts at $(date)" | tee -a ${ALERT_LOG}

# Check connection count
CONNECTION_COUNT=$(psql -h localhost -U ${DB_USER} -d ${DB_NAME} -t -c "
SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active';
")

if [ ${CONNECTION_COUNT} -gt 80 ]; then
    echo "ALERT: High connection count: ${CONNECTION_COUNT}" | tee -a ${ALERT_LOG}
fi

# Check disk space
DISK_USAGE=$(df /var/lib/postgresql | tail -1 | awk '{print $5}' | sed 's/%//')

if [ ${DISK_USAGE} -gt 85 ]; then
    echo "ALERT: High disk usage: ${DISK_USAGE}%" | tee -a ${ALERT_LOG}
fi

# Check for long-running queries
LONG_QUERIES=$(psql -h localhost -U ${DB_USER} -d ${DB_NAME} -t -c "
SELECT COUNT(*) 
FROM pg_stat_activity 
WHERE state = 'active' 
  AND query_start < now() - interval '5 minutes';
")

if [ ${LONG_QUERIES} -gt 0 ]; then
    echo "ALERT: ${LONG_QUERIES} long-running queries detected" | tee -a ${ALERT_LOG}
fi

# Check replication lag (if applicable)
if psql -h localhost -U ${DB_USER} -d ${DB_NAME} -c "SELECT 1 FROM pg_stat_replication LIMIT 1;" >/dev/null 2>&1; then
    REPLICATION_LAG=$(psql -h localhost -U ${DB_USER} -d ${DB_NAME} -t -c "
    SELECT MAX(pg_wal_lsn_diff(sent_lsn, replay_lsn)) 
    FROM pg_stat_replication;
    ")
    
    if [ ${REPLICATION_LAG:-0} -gt 1048576 ]; then  # 1MB lag
        echo "ALERT: High replication lag: ${REPLICATION_LAG} bytes" | tee -a ${ALERT_LOG}
    fi
fi

echo "Alert check completed" | tee -a ${ALERT_LOG}
```

---

## Emergency Procedures

### 1. Emergency Response Checklist

#### Emergency Response Script
```bash
#!/bin/bash
# emergency_response.sh - Emergency database response procedures

echo "=== EMERGENCY DATABASE RESPONSE ==="
echo "Timestamp: $(date)"
echo ""

# Step 1: Assess the situation
echo "1. ASSESSING SITUATION"
echo "   Database status: $(pg_isready -h localhost && echo 'ONLINE' || echo 'OFFLINE')"
echo "   Disk space: $(df -h /var/lib/postgresql | tail -1)"
echo "   Memory usage: $(free -h | grep Mem)"
echo "   CPU usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo ""

# Step 2: Stop application services
echo "2. STOPPING APPLICATION SERVICES"
sudo systemctl stop geopulse-api
sudo systemctl stop geopulse-frontend
echo "   Application services stopped"
echo ""

# Step 3: Create emergency backup
echo "3. CREATING EMERGENCY BACKUP"
if pg_isready -h localhost; then
    pg_dump -h localhost -U geopulse_user -d geopulse_db --format=custom --file="/opt/backups/geopulse/emergency_backup_$(date +%Y%m%d_%H%M%S).dump"
    echo "   Emergency backup created"
else
    echo "   Database not accessible - skipping backup"
fi
echo ""

# Step 4: Check PostgreSQL logs
echo "4. CHECKING POSTGRESQL LOGS"
echo "   Recent error messages:"
tail -20 /var/log/postgresql/postgresql-15-main.log | grep -i error || echo "   No recent errors found"
echo ""

# Step 5: Check system resources
echo "5. CHECKING SYSTEM RESOURCES"
echo "   Active connections: $(psql -h localhost -U geopulse_user -d geopulse_db -t -c 'SELECT COUNT(*) FROM pg_stat_activity WHERE state = \"active\";' 2>/dev/null || echo 'N/A')"
echo "   Locked processes: $(psql -h localhost -U geopulse_user -d geopulse_db -t -c 'SELECT COUNT(*) FROM pg_locks WHERE NOT granted;' 2>/dev/null || echo 'N/A')"
echo ""

# Step 6: Determine recovery action
echo "6. RECOVERY ACTIONS"
echo "   Available recovery options:"
echo "   a) Restart PostgreSQL service"
echo "   b) Restore from latest backup"
echo "   c) Point-in-time recovery"
echo "   d) Emergency maintenance mode"
echo ""

echo "Emergency assessment completed"
```

### 2. Emergency Recovery Procedures

#### Emergency Recovery Script
```bash
#!/bin/bash
# emergency_recovery.sh - Emergency database recovery
# Usage: ./emergency_recovery.sh [recovery_type]

RECOVERY_TYPE=${1:-"restart"}

echo "Starting emergency recovery: ${RECOVERY_TYPE}"

case ${RECOVERY_TYPE} in
    "restart")
        echo "Performing service restart recovery"
        sudo systemctl restart postgresql
        sleep 10
        if pg_isready -h localhost; then
            echo "Recovery successful - database is online"
            sudo systemctl start geopulse-api
            sudo systemctl start geopulse-frontend
        else
            echo "Recovery failed - database still offline"
            exit 1
        fi
        ;;
    
    "backup_restore")
        echo "Performing backup restore recovery"
        LATEST_BACKUP=$(ls -t /opt/backups/geopulse/full_backup_*.dump | head -1)
        if [ -n "${LATEST_BACKUP}" ]; then
            sudo systemctl stop postgresql
            dropdb -h localhost -U geopulse_user geopulse_db
            pg_restore -h localhost -U geopulse_user --create --clean --if-exists "${LATEST_BACKUP}"
            sudo systemctl start postgresql
            sudo systemctl start geopulse-api
            sudo systemctl start geopulse-frontend
            echo "Backup restore recovery completed"
        else
            echo "No backup files found"
            exit 1
        fi
        ;;
    
    "maintenance_mode")
        echo "Entering maintenance mode"
        sudo systemctl stop geopulse-api
        sudo systemctl stop geopulse-frontend
        
        # Create maintenance page
        echo "System under maintenance" > /var/www/html/maintenance.html
        
        # Restart database in single-user mode
        sudo systemctl stop postgresql
        sudo -u postgres postgres --single -D /var/lib/postgresql/15/main geopulse_db
        
        echo "Maintenance mode activated"
        ;;
    
    *)
        echo "Unknown recovery type: ${RECOVERY_TYPE}"
        echo "Available types: restart, backup_restore, maintenance_mode"
        exit 1
        ;;
esac

echo "Emergency recovery completed"
```

### 3. Disaster Recovery Plan

#### Disaster Recovery Checklist
```bash
#!/bin/bash
# disaster_recovery_checklist.sh

echo "=== DISASTER RECOVERY CHECKLIST ==="
echo ""

echo "PRE-RECOVERY CHECKLIST:"
echo "□ Assess the scope of the disaster"
echo "□ Identify affected systems and data"
echo "□ Notify stakeholders and management"
echo "□ Document the incident"
echo "□ Secure the environment"
echo ""

echo "RECOVERY PROCEDURES:"
echo "□ Stop all application services"
echo "□ Create emergency backup (if possible)"
echo "□ Assess backup integrity"
echo "□ Choose recovery strategy:"
echo "  - Full restore from backup"
echo "  - Point-in-time recovery"
echo "  - Failover to standby server"
echo "□ Execute recovery procedure"
echo "□ Verify data integrity"
echo "□ Test application functionality"
echo "□ Restore application services"
echo ""

echo "POST-RECOVERY ACTIONS:"
echo "□ Document recovery steps taken"
echo "□ Analyze root cause of disaster"
echo "□ Implement preventive measures"
echo "□ Update disaster recovery plan"
echo "□ Conduct post-mortem review"
echo "□ Update stakeholders"
echo ""

echo "CONTACT INFORMATION:"
echo "DBA Team: dba@geopulse.com"
echo "System Admin: sysadmin@geopulse.com"
echo "Management: management@geopulse.com"
echo "Emergency: +1-555-EMERGENCY"
echo ""

echo "BACKUP LOCATIONS:"
echo "Primary: /opt/backups/geopulse/"
echo "Secondary: /mnt/backup-drive/geopulse/"
echo "Offsite: s3://geopulse-backups/"
echo ""

echo "Recovery checklist completed"
```

---

## Summary

This comprehensive DBA activities guide provides:

### ✅ **Backup Operations**
- Automated daily and incremental backup scripts
- Backup verification and integrity checks
- Backup retention and cleanup procedures

### ✅ **Recovery Procedures**
- Point-in-time recovery (PITR) procedures
- Full database recovery scripts
- Emergency recovery checklists

### ✅ **Data Migration**
- Server-to-server migration scripts
- Live migration with replication
- Data synchronization procedures

### ✅ **Connection Management**
- Connection pooling with PgBouncer
- Connection monitoring and limiting
- Network security and firewall configuration

### ✅ **Security Measures**
- SSL/TLS certificate configuration
- Network access control (pg_hba.conf)
- Firewall rules and IP restrictions

### ✅ **Monitoring & Maintenance**
- Automated daily and weekly maintenance
- Performance monitoring scripts
- Automated alerting system

### ✅ **Emergency Procedures**
- Emergency response checklists
- Disaster recovery procedures
- Emergency recovery scripts

### 🎯 **Key Benefits for College Graduates**
- **Step-by-step procedures** with detailed commands
- **Automated scripts** for common DBA tasks
- **Security best practices** for database protection
- **Monitoring and alerting** for proactive maintenance
- **Emergency procedures** for crisis management
- **Documentation templates** for operational procedures

This guide ensures that even new DBAs can perform critical database operations safely and efficiently while maintaining security and data integrity.
