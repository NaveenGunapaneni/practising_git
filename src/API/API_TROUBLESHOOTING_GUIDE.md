# GeoPulse API - Troubleshooting Guide

## 🔧 Common Issues and Solutions

### 1. "Internal Server Error" (500)

#### Issue: Missing `greenlet` dependency
**Error:** `ValueError: the greenlet library is required to use this function. No module named 'greenlet'`

**Solution:**
```bash
source geopulse_env/bin/activate
pip install greenlet 'sqlalchemy[asyncio]'
# Restart API server
pkill -f "python main.py"
python main.py &
```

#### Issue: Database connection problems
**Error:** Database-related 500 errors

**Solution:**
```bash
# Check if PostgreSQL container is running
cd database
docker-compose ps

# If not running, start it
docker-compose up -d

# Check database health
curl http://localhost:8000/api/v1/health/detailed
```

### 2. "Not authenticated" (401)

#### Issue: JWT token format problems
**Error:** `{"detail": "Not authenticated"}` or `{"detail": {"status": "error", "error_code": "E004", "message": "Invalid token"}}`

**Root Cause:** JWT library expects `sub` (subject) to be a string, but was generating integer.

**Solution:** ✅ **FIXED** - Updated JWT generation to use string user IDs.

**How to test:**
```bash
# 1. Register a user (use real domain like gmail.com)
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "Test Organization",
    "user_name": "John Doe",
    "contact_phone": "+1-555-0123",
    "email": "testuser@gmail.com",
    "password": "SecurePassword123!"
  }'

# 2. Login to get JWT token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser@gmail.com",
    "password": "SecurePassword123!"
  }'

# 3. Use the token in Authorization header
curl -X POST http://localhost:8000/api/v1/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@sample_data.csv" \
  -F "engagement_name=Test Engagement" \
  -F "date1=2025-08-01" \
  -F "date2=2025-08-15" \
  -F "date3=2025-08-30" \
  -F "date4=2025-09-15"
```

### 3. Email Validation Errors (422)

#### Issue: Invalid email format
**Error:** `{"field": "email", "message": "Value error, Invalid email format"}`

**Root Cause:** `email_validator` library performs DNS validation and rejects domains like `example.com`.

**Solution:** Use real email domains in tests:
- ✅ `testuser@gmail.com`
- ✅ `testuser@yahoo.com`
- ✅ `testuser@outlook.com`
- ❌ `testuser@example.com`
- ❌ `testuser@test.com`

**Postman Fix:** Updated collection to use `@gmail.com` instead of `@example.com`.

### 4. File Upload Issues (400)

#### Issue: File type validation
**Error:** `Invalid file type. Content-Type: application/octet-stream`

**Root Cause:** File MIME type detection issues.

**Solutions:**

1. **Create proper CSV file:**
```csv
Name,Age,City,Country,Salary
John Doe,30,New York,USA,75000
Jane Smith,25,London,UK,65000
```

2. **Use proper file extensions:**
   - ✅ `.csv` for CSV files
   - ✅ `.xlsx` for Excel files
   - ✅ `.xls` for legacy Excel files

3. **Check file size:** Maximum 50MB allowed

### 5. Database Connection Issues

#### Issue: Database not accessible
**Error:** Database health check fails

**Solution:**
```bash
# Check Docker containers
cd database
docker-compose ps

# Check logs
docker-compose logs postgres

# Restart if needed
docker-compose down
docker-compose up -d

# Verify connection
docker-compose exec postgres psql -U geopulse_user -d geopulse_db -c "SELECT 1;"
```

### 6. Port Already in Use

#### Issue: API server won't start
**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill existing process
pkill -f "python main.py"

# Or kill by PID
kill -9 PID_NUMBER

# Start server again
source geopulse_env/bin/activate
python main.py &
```

## 🧪 Testing Workflow

### Recommended Testing Order:

1. **Health Checks**
   ```bash
   curl http://localhost:8000/api/v1/health
   curl http://localhost:8000/api/v1/health/detailed
   ```

2. **User Registration**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"organization_name": "Test Org", "user_name": "Test User", "contact_phone": "+1-555-0123", "email": "test@gmail.com", "password": "SecurePassword123!"}'
   ```

3. **User Login**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "test@gmail.com", "password": "SecurePassword123!"}'
   ```

4. **File Operations** (with JWT token)
   ```bash
   curl -X POST http://localhost:8000/api/v1/files/upload \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@sample_data.csv" \
     -F "engagement_name=Test" \
     -F "date1=2025-08-01" \
     -F "date2=2025-08-15" \
     -F "date3=2025-08-30" \
     -F "date4=2025-09-15"
   ```

## 🔍 Debugging Tips

### 1. Check API Server Logs
The API server outputs detailed logs. Look for:
- Request received/completed messages
- Error messages with stack traces
- Authentication success/failure logs

### 2. Verify Environment Variables
```bash
source geopulse_env/bin/activate
python -c "from app.config import settings; print(f'JWT Secret: {settings.jwt_secret_key[:10]}...'); print(f'Database URL: {settings.database_url}')"
```

### 3. Test JWT Token Manually
```bash
source geopulse_env/bin/activate
python -c "
import jwt
from app.config import settings
token = 'YOUR_TOKEN_HERE'
try:
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    print('Token valid:', payload)
except Exception as e:
    print('Token invalid:', str(e))
"
```

### 4. Check Database Tables
```bash
cd database
docker-compose exec postgres psql -U geopulse_user -d geopulse_db -c "
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
SELECT COUNT(*) as user_count FROM users;
SELECT COUNT(*) as file_count FROM files;
"
```

## 🚀 Quick Fix Commands

### Reset Everything
```bash
# Stop API
pkill -f "python main.py"

# Reset database
cd database
docker-compose down -v
docker-compose up -d

# Restart API
cd ..
source geopulse_env/bin/activate
python main.py &
```

### Reinstall Dependencies
```bash
source geopulse_env/bin/activate
pip install --upgrade pip
pip install greenlet 'sqlalchemy[asyncio]' PyJWT
```

### Check All Services
```bash
# API Health
curl http://localhost:8000/api/v1/health

# Database Health
curl http://localhost:8000/api/v1/health/detailed

# pgAdmin (if needed)
open http://localhost:8080
```

## 📞 Still Having Issues?

1. **Check Prerequisites:**
   - Python 3.11+ environment active
   - PostgreSQL Docker container running
   - All dependencies installed

2. **Verify File Paths:**
   - API server running from correct directory
   - Test files exist and are accessible
   - Environment variables properly set

3. **Review Logs:**
   - API server console output
   - Docker container logs
   - Postman console (if using Postman)

4. **Test Step by Step:**
   - Start with health checks
   - Test authentication separately
   - Verify JWT token format
   - Test file operations last

The API is now fully functional with proper JWT authentication! 🎉