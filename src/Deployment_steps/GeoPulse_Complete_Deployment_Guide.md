# GeoPulse Complete Deployment & Validation Guide

This comprehensive guide provides detailed instructions for deploying and validating the GeoPulse project on a server with the following architecture:
- **Database**: PostgreSQL running locally (not Docker)
- **API**: FastAPI application running in conda environment
- **UI**: React application accessible to the world
- **Communication**: All services communicate via localhost

## Table of Contents

### Part 1: Deployment
1. [Prerequisites](#prerequisites)
2. [Server Preparation](#server-preparation)
3. [Database Setup](#database-setup)
4. [API Deployment](#api-deployment)
5. [UI Deployment](#ui-deployment)
6. [Screen Session Management](#screen-session-management)
7. [Nginx Configuration](#nginx-configuration)
8. [SSL Certificate Setup](#ssl-certificate-setup)

### Part 2: System Monitoring & Commands
9. [System Monitoring and Commands](#system-monitoring-and-commands)
10. [Monitoring and Maintenance](#monitoring-and-maintenance)

### Part 3: Validation & Testing
11. [Deployment Validation](#deployment-validation)
12. [End-to-End Testing](#end-to-end-testing)
13. [Performance Testing](#performance-testing)
14. [Security Validation](#security-validation)

### Part 4: Troubleshooting
15. [Troubleshooting](#troubleshooting)
16. [Emergency Procedures](#emergency-procedures)

---

## Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: Minimum 20GB free space
- **CPU**: 2+ cores
- **Network**: Public IP address with ports 80, 443, and 22 open

### Software Requirements
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 15+
- Nginx
- Conda/Miniconda
- Screen
- Git

---

## Server Preparation

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git vim htop unzip software-properties-common net-tools
```

### 2. Install Python and Conda
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
rm Miniconda3-latest-Linux-x86_64.sh

echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
conda init bash
source ~/.bashrc
```

### 3. Install Node.js and npm
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version && npm --version
```

### 4. Install PostgreSQL
```bash
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo systemctl status postgresql
```

### 5. Install Nginx
```bash
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl status nginx
```

---

## Database Setup

### 1. Configure PostgreSQL
```bash
sudo -u postgres psql

# Create database user and database
CREATE USER geopulse_user WITH PASSWORD 'password123';
CREATE DATABASE geopulse_db OWNER geopulse_user;
GRANT ALL PRIVILEGES ON DATABASE geopulse_db TO geopulse_user;

# Connect to the database
\c geopulse_db

# Grant schema privileges
GRANT ALL ON SCHEMA public TO geopulse_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO geopulse_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO geopulse_user;

\q
```

### 2. Configure PostgreSQL for Local Connections
```bash
sudo nano /etc/postgresql/*/main/postgresql.conf
# Add: listen_addresses = 'localhost'

sudo nano /etc/postgresql/*/main/pg_hba.conf
# Add:
# local   all             all                                     md5
# host    all             all             127.0.0.1/32            md5
# host    all             all             ::1/128                 md5

sudo systemctl restart postgresql
```

### 3. Create Database Tables
```bash
cd ~/geopulse/API
sudo -u postgres psql -d geopulse_db -f database/setup_postgres.sql
alembic upgrade head
```

---

## API Deployment

### 1. Clone and Setup Project
```bash
cd ~
git clone <your-repository-url> geopulse
cd geopulse/API
```

### 2. Create Conda Environment
```bash
conda env create -f environment.yml
conda activate geopulse_env
python --version && pip list
```

### 3. Configure API Environment
```bash
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://geopulse_user:password123@localhost:5432/geopulse_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
BCRYPT_ROUNDS=12
USER_JSON_DIR=./user_data
UPLOAD_DIR=./user_data/uploads
UPLOAD_TEMP_DIR=./user_data/temp
DEFAULT_LOGO_PATH=/defaults/datalegos.png
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=[".xlsx", ".csv", ".xls"]
LOG_LEVEL=INFO
LOG_FILE=./logs/api.log
API_TITLE=GeoPulse API
API_VERSION=1.0.0
API_DESCRIPTION=GeoPulse File Upload and Processing API
CORS_ALLOW_ORIGINS=*
CORS_ALLOW_CREDENTIALS=true
SECURITY_HEADERS_ENABLED=true
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
EOF
```

### 4. Create Required Directories
```bash
mkdir -p logs user_data/uploads user_data/temp
chmod 755 user_data user_data/uploads user_data/temp logs
```

### 5. Test API Installation
```bash
python -c "
from app.core.database import check_database_connection
import asyncio
result = asyncio.run(check_database_connection())
print(f'Database connection: {result}')
"

python main.py
# Press Ctrl+C to stop after confirming it starts
```

---

## UI Deployment

### 1. Navigate to UI Directory
```bash
cd ~/geopulse/UI
```

### 2. Install Dependencies
```bash
npm install
npm list --depth=0
```

### 3. Configure UI Environment
```bash
cat > .env << EOF
REACT_APP_API_URL=http://localhost:8000
GENERATE_SOURCEMAP=false
INLINE_RUNTIME_CHUNK=false
EOF
```

### 4. Build UI for Production
```bash
npm run build
ls -la build/
```

### 5. Test UI Build
```bash
npm install -g serve
serve -s build -l 3000
# Visit http://localhost:3000 to verify
# Press Ctrl+C to stop
```

---

## Screen Session Management

### 1. Install Screen
```bash
sudo apt install -y screen
```

### 2. Create Screen Sessions
```bash
# API Session
screen -S geopulse-api
cd ~/geopulse/API
conda activate geopulse_env
python main.py
# Press Ctrl+A, then D to detach

# UI Session
screen -S geopulse-ui
cd ~/geopulse/UI
npm start
# Press Ctrl+A, then D to detach
```

### 3. Screen Session Management
```bash
screen -ls                    # List sessions
screen -r geopulse-api        # Reattach to API
screen -r geopulse-ui         # Reattach to UI
screen -S session-name -X quit # Kill session
```

### 4. Create Startup Scripts
```bash
cat > ~/start_api.sh << 'EOF'
#!/bin/bash
cd ~/geopulse/API
source ~/miniconda3/etc/profile.d/conda.sh
conda activate geopulse_env
python main.py
EOF

cat > ~/start_ui.sh << 'EOF'
#!/bin/bash
cd ~/geopulse/UI
npm start
EOF

chmod +x ~/start_api.sh ~/start_ui.sh
```

---

## Nginx Configuration

### 1. Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/geopulse

# Add configuration:
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        root /home/your-username/geopulse/UI/build;
        try_files $uri $uri/ /index.html;
        index index.html index.htm;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";
    }

    location /health {
        proxy_pass http://localhost:8000/api/v1/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript;
}
```

### 2. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/geopulse /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

---

## SSL Certificate Setup

### 1. Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Obtain SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
sudo certbot renew --dry-run
```

---

## System Monitoring and Commands

### 1. Port Checking Commands
```bash
# Check all listening ports
sudo netstat -tulpn | grep LISTEN

# Check specific ports
sudo netstat -tulpn | grep -E "(80|443|8000|3000|5432)"

# Alternative using ss command
sudo ss -tulpn | grep LISTEN

# Check if specific port is open
sudo lsof -i :80
sudo lsof -i :443
sudo lsof -i :8000
sudo lsof -i :3000

# Check firewall status
sudo ufw status
sudo iptables -L -n -v
```

### 2. Application and Process Monitoring
```bash
# Check running processes
ps aux | grep python
ps aux | grep node
ps aux | grep nginx
ps aux | grep postgres

# Check process tree
pstree -p

# Check systemd services
sudo systemctl list-units --type=service --state=running

# Check what ports each application is using
sudo lsof -i -P -n | grep LISTEN
```

### 3. Memory and Disk Usage Commands

#### Memory Usage
```bash
free -h
cat /proc/meminfo
ps aux --sort=-%mem | head -10
top
htop
swapon --show
watch -n 1 free -h
```

#### Disk Usage (DF and DU)
```bash
# DF Commands (Disk Filesystem)
df -h
df -h /
df -h /home
df -i
df -T
df -h --exclude-type=tmpfs --exclude-type=devtmpfs
df -h --total
watch -n 5 df -h

# DU Commands (Disk Usage)
du -h
du -sh /home/your-username/geopulse
du -h /home/your-username/geopulse | sort -hr | head -10
du -h --exclude="node_modules" /home/your-username/geopulse
du -ch /home/your-username/geopulse/*.log
watch -n 5 'du -sh /home/your-username/geopulse'
```

### 4. System Resource Monitoring Scripts
```bash
# Create system monitoring script
cat > ~/system_monitor.sh << 'EOF'
#!/bin/bash
echo "=== SYSTEM RESOURCE MONITORING ==="
echo "Date: $(date)"
echo ""
echo "=== DISK USAGE ==="
df -h
echo ""
echo "=== MEMORY USAGE ==="
free -h
echo ""
echo "=== TOP PROCESSES BY MEMORY ==="
ps aux --sort=-%mem | head -5
echo ""
echo "=== TOP PROCESSES BY CPU ==="
ps aux --sort=-%cpu | head -5
echo ""
echo "=== OPEN PORTS ==="
sudo netstat -tulpn | grep LISTEN | head -10
echo ""
echo "=== APPLICATION STATUS ==="
echo "Nginx: $(sudo systemctl is-active nginx)"
echo "PostgreSQL: $(sudo systemctl is-active postgresql)"
echo "Screen sessions: $(screen -ls | wc -l)"
echo ""
echo "=== LARGEST DIRECTORIES ==="
du -h ~/geopulse | sort -hr | head -5
echo ""
echo "=== LOG FILE SIZES ==="
find ~/geopulse -name "*.log" -exec ls -lh {} \; 2>/dev/null
echo ""
EOF

chmod +x ~/system_monitor.sh
```

---

## Monitoring and Maintenance

### 1. Create Health Check Script
```bash
cat > ~/health_check.sh << 'EOF'
#!/bin/bash
echo "=== HEALTH CHECK REPORT ==="
echo "Date: $(date)"
echo ""

# Check API health
echo "Checking API health..."
if curl -f http://localhost:8000/api/v1/health >/dev/null 2>&1; then
    echo "✅ API is running"
else
    echo "❌ API is down!"
fi

# Check UI health
echo "Checking UI health..."
if curl -f http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ UI is running"
else
    echo "❌ UI is down!"
fi

# Check database connection
echo "Checking database..."
if sudo -u postgres psql -d geopulse_db -c "SELECT 1;" >/dev/null 2>&1; then
    echo "✅ Database is running"
else
    echo "❌ Database is down!"
fi

# Check screen sessions
echo "Checking screen sessions..."
screen -ls

# Check disk space
echo "Checking disk space..."
df -h /

# Check memory usage
echo "Checking memory usage..."
free -h

# Check open ports
echo "Checking open ports..."
sudo netstat -tulpn | grep -E "(80|443|8000|3000|5432)"
EOF

chmod +x ~/health_check.sh
```

### 2. Create Backup Script
```bash
cat > ~/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/your-username/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/geopulse_db_$DATE.sql"

mkdir -p $BACKUP_DIR

# Create database backup
sudo -u postgres pg_dump geopulse_db > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup created: $BACKUP_FILE.gz"
EOF

chmod +x ~/backup_db.sh

# Add to crontab for daily backups
crontab -e
# Add: 0 2 * * * /home/your-username/backup_db.sh
```

---

## Deployment Validation

### 1. System-Level Validation
```bash
# Check all critical services
echo "=== SYSTEM SERVICES STATUS ==="
echo "Nginx: $(sudo systemctl is-active nginx)"
echo "PostgreSQL: $(sudo systemctl is-active postgresql)"
echo "Screen sessions: $(screen -ls | grep -c 'geopulse')"

# Check listening ports
echo "=== PORT ACCESSIBILITY CHECK ==="
echo "Port 80 (HTTP): $(sudo netstat -tulpn | grep :80 || echo 'NOT LISTENING')"
echo "Port 443 (HTTPS): $(sudo netstat -tulpn | grep :443 || echo 'NOT LISTENING')"
echo "Port 8000 (API): $(sudo netstat -tulpn | grep :8000 || echo 'NOT LISTENING')"
echo "Port 3000 (UI Dev): $(sudo netstat -tulpn | grep :3000 || echo 'NOT LISTENING')"
echo "Port 5432 (PostgreSQL): $(sudo netstat -tulpn | grep :5432 || echo 'NOT LISTENING')"

# Test port connectivity
nc -zv localhost 80
nc -zv localhost 443
nc -zv localhost 8000
nc -zv localhost 3000
nc -zv localhost 5432
```

### 2. Database Validation
```bash
# Test database connectivity
echo "=== DATABASE CONNECTION TEST ==="
sudo -u postgres psql -c "SELECT version();"
PGPASSWORD=password123 psql -h localhost -U geopulse_user -d geopulse_db -c "SELECT current_database(), current_user;"

# Check if all tables exist
echo "=== DATABASE SCHEMA VALIDATION ==="
sudo -u postgres psql -d geopulse_db -c "
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
"

# Test database permissions
echo "=== DATABASE PERMISSIONS TEST ==="
PGPASSWORD=password123 psql -h localhost -U geopulse_user -d geopulse_db -c "
SELECT COUNT(*) FROM users;
INSERT INTO users (organization_name, user_name, contact_phone, email, password_hash) 
VALUES ('Test Org', 'Test User', '1234567890', 'test@example.com', 'test_hash')
ON CONFLICT (email) DO NOTHING;
UPDATE users SET updated_at = NOW() WHERE email = 'test@example.com';
DELETE FROM users WHERE email = 'test@example.com';
"
```

### 3. API Validation
```bash
# Test API health endpoint
echo "=== API HEALTH CHECK ==="
curl -f http://localhost:8000/api/v1/health
curl -f http://localhost:8000/api/v1/health/detailed
curl -f http://localhost:8000/docs

# Test user registration
echo "=== API AUTHENTICATION TEST ==="
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "Test Organization",
    "user_name": "Test User",
    "contact_phone": "1234567890",
    "email": "test@example.com",
    "password": "TestPassword123!"
  }')

echo "Registration Response: $REGISTER_RESPONSE"

# Test user login
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }')

echo "Login Response: $LOGIN_RESPONSE"

# Extract JWT token
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
echo "JWT Token: $TOKEN"
```

### 4. UI Validation
```bash
# Test UI accessibility
echo "=== UI ACCESSIBILITY TEST ==="
ls -la ~/geopulse/UI/build/
curl -f http://localhost:3000/
curl -f http://localhost:3000/static/js/main.js
curl -f http://localhost:3000/static/css/main.css

# Test UI through Nginx
curl -f http://your-domain.com/
curl -f http://your-domain.com/static/js/main.js

# Test UI functionality
echo "=== UI FUNCTIONALITY TEST ==="
curl -f http://localhost:3000/login
curl -f http://localhost:3000/register
curl -f http://localhost:3000/dashboard
curl -f http://localhost:3000/upload
curl -f http://localhost:3000/api/v1/health
```

---

## End-to-End Testing

### 1. Complete User Flow Test
```bash
echo "=== COMPLETE USER FLOW TEST ==="

# Step 1: User Registration
REGISTER_DATA='{
  "organization_name": "Integration Test Org",
  "user_name": "Integration Test User",
  "contact_phone": "5551234567",
  "email": "integration@example.com",
  "password": "IntegrationTest123!"
}'

REGISTER_RESULT=$(curl -s -X POST http://localhost:8000/api/v1/register \
  -H "Content-Type: application/json" \
  -d "$REGISTER_DATA")

echo "Registration Result: $REGISTER_RESULT"

# Step 2: User Login
LOGIN_DATA='{
  "email": "integration@example.com",
  "password": "IntegrationTest123!"
}'

LOGIN_RESULT=$(curl -s -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d "$LOGIN_DATA")

echo "Login Result: $LOGIN_RESULT"

# Extract token for further testing
INTEGRATION_TOKEN=$(echo $LOGIN_RESULT | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# Step 3: Access Dashboard
if [ ! -z "$INTEGRATION_TOKEN" ]; then
    DASHBOARD_RESULT=$(curl -s -X GET http://localhost:8000/api/v1/dashboard \
      -H "Authorization: Bearer $INTEGRATION_TOKEN" \
      -H "Content-Type: application/json")
    
    echo "Dashboard Result: $DASHBOARD_RESULT"
else
    echo "No valid token for dashboard test"
fi
```

### 2. Database Integration Test
```bash
echo "=== DATABASE INTEGRATION TEST ==="

# Verify user was created in database
echo "Verifying user in database:"
sudo -u postgres psql -d geopulse_db -c "
SELECT user_id, organization_name, user_name, email, created_at 
FROM users 
WHERE email = 'integration@example.com';
"

# Check if user data is consistent
echo "Checking user data consistency:"
sudo -u postgres psql -d geopulse_db -c "
SELECT 
    u.user_id,
    u.organization_name,
    u.user_name,
    u.email,
    COUNT(f.file_id) as file_count
FROM users u
LEFT JOIN files f ON u.user_id = f.user_id
WHERE u.email = 'integration@example.com'
GROUP BY u.user_id, u.organization_name, u.user_name, u.email;
"
```

---

## Performance Testing

### 1. API Performance Test
```bash
echo "=== API PERFORMANCE TEST ==="

# Install Apache Bench if not available
sudo apt install -y apache2-utils

# Test API response time
echo "Testing API response time:"
ab -n 100 -c 10 http://localhost:8000/api/v1/health

# Test database query performance
echo "Testing database query performance:"
sudo -u postgres psql -d geopulse_db -c "
\timing on
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM files;
SELECT u.organization_name, COUNT(f.file_id) 
FROM users u 
LEFT JOIN files f ON u.user_id = f.user_id 
GROUP BY u.organization_name;
\timing off
"
```

### 2. System Resource Usage Test
```bash
echo "=== SYSTEM RESOURCE USAGE TEST ==="

echo "System resources before test:"
free -h
uptime

# Run load test
echo "Running load test..."
for i in {1..50}; do
    curl -s http://localhost:8000/api/v1/health > /dev/null &
    curl -s http://localhost:3000/ > /dev/null &
done
wait

echo "System resources after test:"
free -h
uptime
```

---

## Security Validation

### 1. Authentication Security Test
```bash
echo "=== AUTHENTICATION SECURITY TEST ==="

# Test password validation
echo "Testing password validation:"
curl -s -X POST http://localhost:8000/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "Test",
    "user_name": "Test",
    "contact_phone": "1234567890",
    "email": "security@example.com",
    "password": "weak"
  }'

# Test SQL injection prevention
echo "Testing SQL injection prevention:"
curl -s -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com\"; DROP TABLE users; --",
    "password": "password"
  }'

# Test JWT token validation
echo "Testing JWT token validation:"
curl -s -X GET http://localhost:8000/api/v1/dashboard \
  -H "Authorization: Bearer invalid_token"
```

### 2. CORS Security Test
```bash
echo "=== CORS SECURITY TEST ==="

# Test CORS headers
echo "Testing CORS headers:"
curl -s -I -H "Origin: http://malicious-site.com" \
  http://localhost:8000/api/v1/health

# Test preflight requests
echo "Testing preflight requests:"
curl -s -X OPTIONS \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  http://localhost:8000/api/v1/register
```

---

## Troubleshooting

### 1. Common Issues and Solutions

#### API Won't Start
```bash
conda activate geopulse_env
pip list
python -c "
from app.core.database import check_database_connection
import asyncio
result = asyncio.run(check_database_connection())
print(f'Database connection: {result}')
"
tail -f ~/geopulse/API/logs/api.log
sudo lsof -i :8000
sudo fuser -k 8000/tcp
```

#### UI Won't Start
```bash
node --version && npm --version
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
sudo netstat -tulpn | grep :3000
sudo lsof -i :3000
sudo fuser -k 3000/tcp
```

#### Database Connection Issues
```bash
sudo systemctl status postgresql
sudo tail -f /var/log/postgresql/postgresql-*.log
sudo -u postgres psql -d geopulse_db -c "SELECT version();"
sudo nano /etc/postgresql/*/main/postgresql.conf
sudo nano /etc/postgresql/*/main/pg_hba.conf
sudo netstat -tulpn | grep :5432
```

#### Nginx Issues
```bash
sudo systemctl status nginx
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443
sudo nginx -T | grep -E "(server_name|listen|location)"
```

### 2. Screen Session Issues
```bash
screen -ls
pkill screen
screen -S geopulse-api -d -m bash -c "cd ~/geopulse/API && conda activate geopulse_env && python main.py"
screen -S geopulse-ui -d -m bash -c "cd ~/geopulse/UI && npm start"
ps aux | grep screen
```

### 3. Performance Monitoring
```bash
htop
df -h
du -sh /home/your-username/geopulse
free -h
ps aux --sort=-%mem | head -10
sudo netstat -tulpn
ps aux | grep -E "(python|node|nginx|postgres)"
iostat -x 1 5
uptime
cat /proc/loadavg
```

---

## Emergency Procedures

### 1. Emergency Restart All Services
```bash
sudo systemctl restart nginx
sudo systemctl restart postgresql
pkill screen
screen -S geopulse-api -d -m bash -c "cd ~/geopulse/API && conda activate geopulse_env && python main.py"
screen -S geopulse-ui -d -m bash -c "cd ~/geopulse/UI && npm start"
```

### 2. Check System Resources in Emergency
```bash
df -h
free -h
sudo netstat -tulpn | grep LISTEN
sudo fuser -k 8000/tcp
sudo fuser -k 3000/tcp
sudo journalctl -xe
sudo tail -f /var/log/syslog
```

---

## Final Verification Checklist

After completing all steps, verify:

### System Level
- [ ] All services are running (Nginx, PostgreSQL, Screen sessions)
- [ ] All required ports are accessible
- [ ] System resources are adequate
- [ ] Logs are being generated properly

### Database Level
- [ ] Database connection is working
- [ ] All tables exist with correct structure
- [ ] User permissions are properly configured
- [ ] Database performance is acceptable

### API Level
- [ ] API health endpoints are responding
- [ ] User registration and login work correctly
- [ ] JWT authentication is functioning
- [ ] Protected endpoints require authentication
- [ ] Error handling works properly
- [ ] API performance is acceptable

### UI Level
- [ ] UI is accessible via browser
- [ ] Static assets are loading correctly
- [ ] UI can communicate with API
- [ ] User interface is responsive
- [ ] Error messages are displayed properly

### Integration Level
- [ ] Complete user flow works end-to-end
- [ ] Database integration is working
- [ ] File upload functionality works
- [ ] Data consistency is maintained
- [ ] Performance is acceptable under load

### Security Level
- [ ] Authentication is secure
- [ ] CORS is properly configured
- [ ] SQL injection is prevented
- [ ] JWT tokens are validated
- [ ] Sensitive data is protected

### Monitoring Level
- [ ] Health checks are working
- [ ] Logs are being generated
- [ ] Monitoring scripts are functional
- [ ] Alerts are configured (if applicable)

---

## Quick Reference Commands

```bash
# System monitoring
~/system_monitor.sh
~/health_check.sh
~/port_monitor.sh

# Service management
sudo systemctl status nginx postgresql
screen -ls
screen -r geopulse-api
screen -r geopulse-ui

# Port checking
sudo netstat -tulpn | grep LISTEN
sudo lsof -i -P -n | grep LISTEN

# Resource monitoring
df -h
free -h
htop
ps aux --sort=-%mem | head -10

# Database testing
PGPASSWORD=password123 psql -h localhost -U geopulse_user -d geopulse_db -c "SELECT 1;"

# API testing
curl -f http://localhost:8000/api/v1/health
curl -X POST http://localhost:8000/api/v1/register -H "Content-Type: application/json" -d '{"organization_name":"Test","user_name":"Test","contact_phone":"1234567890","email":"test@example.com","password":"TestPassword123!"}'

# UI testing
curl -f http://localhost:3000/
curl -f http://your-domain.com/
```

---

## Security Recommendations

1. **Change default passwords** for database and application
2. **Use strong secret keys** in .env file
3. **Enable firewall** and restrict access to necessary ports
4. **Regular security updates** for the system
5. **Monitor logs** for suspicious activity
6. **Use HTTPS** in production
7. **Implement rate limiting** for API endpoints
8. **Regular backups** of database and application files
9. **Monitor system resources** regularly
10. **Set up automated monitoring** for critical services

---

## Support and Maintenance

### Regular Maintenance Tasks
- **Daily**: Check application logs and system resources
- **Weekly**: Review system resources and clean up old files
- **Monthly**: Update system packages and review security
- **Quarterly**: Review and update security configurations

### Emergency Procedures
1. **Application down**: Restart screen sessions and check logs
2. **Database issues**: Check PostgreSQL logs and restart if needed
3. **Nginx issues**: Check configuration and restart service
4. **System issues**: Reboot server if necessary
5. **Resource issues**: Clean up disk space and restart services

### Contact Information
- **System Administrator**: [Your Contact Info]
- **Application Support**: [Your Contact Info]
- **Emergency Contact**: [Your Contact Info]

---

*This comprehensive deployment guide should be updated as the application evolves. Keep a copy of this guide in a secure location and update it whenever changes are made to the deployment process.*
