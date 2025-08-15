# GeoPulse API - Complete Development & Operations Playbook

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture & Design](#architecture--design)
3. [Environment Setup](#environment-setup)
4. [Development Workflow](#development-workflow)
5. [Database Operations](#database-operations)
6. [Testing Strategy](#testing-strategy)
7. [API Documentation](#api-documentation)
8. [Deployment Guide](#deployment-guide)
9. [Monitoring & Logging](#monitoring--logging)
10. [Troubleshooting](#troubleshooting)
11. [Security Guidelines](#security-guidelines)
12. [Performance Optimization](#performance-optimization)

---

## Project Overview

### Technology Stack
- **Framework**: FastAPI (Async Python Web Framework)
- **Database**: PostgreSQL with AsyncPG driver
- **ORM**: SQLAlchemy 2.0 (Async)
- **Authentication**: JWT with Python-Jose
- **Password Hashing**: Bcrypt
- **Validation**: Pydantic v2
- **Migrations**: Alembic
- **Testing**: Pytest with AsyncIO support
- **Server**: Uvicorn ASGI server

### Architecture Pattern
**Modular Monolith with Domain-Driven Design (DDD)**
- Clean Architecture principles
- Repository Pattern for data access
- Service Layer for business logic
- Dependency Injection throughout
- Hexagonal Architecture influences

### Core Features
- User Registration & Authentication
- File Upload & Processing (CSV/XLSX)
- Dashboard Data Management
- JWT-based Security
- Comprehensive Logging
- Rate Limiting & Security Headers
- Health Monitoring

---

## Architecture & Design

### Project Structure
```
geopulse/
├── app/                          # Main application package
│   ├── core/                     # Core infrastructure
│   │   ├── app_factory.py        # FastAPI app factory
│   │   ├── database.py           # DB connection management
│   │   ├── exceptions.py         # Custom exceptions
│   │   ├── logger.py             # Logging configuration
│   │   └── middleware.py         # Middleware orchestration
│   ├── modules/                  # Business domain modules
│   │   ├── registration/         # User registration domain
│   │   ├── login/               # Authentication domain
│   │   ├── dashboard/           # Dashboard data domain
│   │   └── upload/              # File processing domain
│   ├── shared/                   # Shared components
│   │   ├── models/              # Database models
│   │   ├── schemas/             # Pydantic schemas
│   │   └── utils/               # Utility functions
│   ├── middleware/              # Custom middleware
│   └── api/v1/                  # API routing
├── alembic/                     # Database migrations
├── tests/                       # Test suite
├── logs/                        # Application logs
├── user_data/                   # File storage
└── GeoPulse-API-Testing/        # Postman collections
```

### Module Architecture (Each Domain)
```
modules/{domain}/
├── __init__.py
├── models.py          # Domain models
├── schemas.py         # Request/Response schemas
├── repository.py      # Data access layer
├── services.py        # Business logic layer
├── routes.py          # API endpoints
└── exceptions.py      # Domain-specific exceptions
```

---

## Environment Setup

### Prerequisites
```bash
# System Requirements
- Python 3.11+
- PostgreSQL 15+
- Git
- pip or poetry
```

### Quick Setup Commands
```bash
# 1. Clone and navigate
git clone <repository-url>
cd geopulse

# 2. Create virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 3. Install dependencies
pip install -e .

# 4. Setup environment variables
copy .env.example .env
# Edit .env with your configuration

# 5. Setup PostgreSQL database
psql -U postgres -f setup_postgres.sql

# 6. Run database migrations
alembic upgrade head

# 7. Create required directories
mkdir -p logs user_data/uploads user_data/temp

# 8. Start the application
python main.py
```

### Environment Variables (.env)
```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://geopulse_user:password123@localhost:5432/geopulse_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Security Configuration
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
BCRYPT_ROUNDS=12

# File System Configuration
USER_JSON_DIR=./user_data
UPLOAD_DIR=./user_data/uploads
UPLOAD_TEMP_DIR=./user_data/temp
DEFAULT_LOGO_PATH=/defaults/datalegos.png

# File Upload Limits
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=[".xlsx", ".csv", ".xls"]

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=./logs/api.log

# API Configuration
API_TITLE=GeoPulse API
API_VERSION=1.0.0
API_DESCRIPTION=GeoPulse File Upload and Processing API

# CORS & Security
CORS_ALLOW_ORIGINS=*
CORS_ALLOW_CREDENTIALS=true
SECURITY_HEADERS_ENABLED=true

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

---

## Development Workflow

### Daily Development Commands
```bash
# Start development server with auto-reload
python main.py

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Code formatting
black app/ tests/
isort app/ tests/

# Type checking
mypy app/

# Database migration workflow
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head

# View current migration status
alembic current
alembic history
```

### Git Workflow
```bash
# Feature development
git checkout -b feature/new-feature
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# Create pull request and merge
# After merge, cleanup
git checkout main
git pull origin main
git branch -d feature/new-feature
```

### Code Quality Checklist
- [ ] All tests pass (`pytest`)
- [ ] Code coverage > 80% (`pytest --cov`)
- [ ] Type hints added (`mypy app/`)
- [ ] Code formatted (`black`, `isort`)
- [ ] No security vulnerabilities
- [ ] Documentation updated
- [ ] Environment variables documented

---

## Database Operations

### PostgreSQL Setup
```sql
-- Run as postgres superuser
CREATE USER geopulse_user WITH PASSWORD 'password123';
CREATE DATABASE geopulse_db OWNER geopulse_user;
GRANT ALL PRIVILEGES ON DATABASE geopulse_db TO geopulse_user;

-- Connect to database and grant schema privileges
\c geopulse_db;
GRANT ALL ON SCHEMA public TO geopulse_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO geopulse_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO geopulse_user;
```

### Migration Commands
```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history --verbose

# Check current version
alembic current

# Upgrade to specific revision
alembic upgrade <revision_id>

# Downgrade to specific revision
alembic downgrade <revision_id>
```

### Database Backup & Restore
```bash
# Backup database
pg_dump -U geopulse_user -h localhost geopulse_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
psql -U geopulse_user -h localhost geopulse_db < backup_file.sql

# Backup with compression
pg_dump -U geopulse_user -h localhost geopulse_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Restore from compressed backup
gunzip -c backup_file.sql.gz | psql -U geopulse_user -h localhost geopulse_db
```

---

## Testing Strategy

### Test Structure
```
tests/
├── __init__.py
├── README.md                    # Testing documentation
├── test_user_repository.py      # Repository layer tests
├── test_password_service.py     # Service layer tests
├── test_file_service.py         # File operations tests
└── test_file_upload_service.py  # Upload processing tests
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_user_repository.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html --cov-report=term

# Run async tests
pytest -k "async" --asyncio-mode=auto

# Run tests matching pattern
pytest -k "test_user"

# Run tests with markers
pytest -m "slow"  # if you have marked slow tests

# Generate coverage report
pytest --cov=app --cov-report=html
# View report at htmlcov/index.html
```

### Test Categories
1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test module interactions
3. **Repository Tests**: Test database operations
4. **Service Tests**: Test business logic
5. **API Tests**: Test endpoint behavior (via Postman)

### Test Best Practices
- Use fixtures for common setup
- Mock external dependencies
- Test both success and failure scenarios
- Maintain test isolation
- Aim for 80%+ code coverage
- Use descriptive test names

---

## API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints Overview

#### Authentication Endpoints
```
POST /api/v1/auth/register    # User registration
POST /api/v1/auth/login       # User authentication
```

#### File Management Endpoints
```
POST /api/v1/files/upload     # Upload and process files
GET  /api/v1/files/list       # List user's files
GET  /api/v1/files/{id}/status # Get file processing status
GET  /api/v1/files/{id}/download # Download processed file
```

#### Dashboard Endpoints
```
GET  /api/v1/dashboard        # Get dashboard data
GET  /api/v1/dashboard/stats  # Get dashboard statistics
```

#### Health & Monitoring
```
GET  /                        # Basic health check
GET  /api/v1/health          # Detailed health check
GET  /middleware-info        # Middleware configuration
```

### Postman Testing
```bash
# Import collections from GeoPulse-API-Testing/
1. GeoPulse-Complete-API-Tests.postman_collection.json
2. GeoPulse-Environment.postman_environment.json

# Test sequence:
1. User Registration (creates test user)
2. User Authentication (gets JWT token)
3. Dashboard Data (requires authentication)
4. File Upload Processing (requires authentication)
```

---

## Deployment Guide

### Production Environment Setup
```bash
# 1. Server preparation
sudo apt update && sudo apt upgrade -y
sudo apt install python3.11 python3.11-venv postgresql nginx -y

# 2. Application deployment
git clone <repository-url> /opt/geopulse
cd /opt/geopulse
python3.11 -m venv venv
source venv/bin/activate
pip install -e .

# 3. Environment configuration
cp .env.example .env.production
# Edit .env.production with production values

# 4. Database setup
sudo -u postgres psql -f setup_postgres.sql
alembic upgrade head

# 5. Create systemd service
sudo cp deployment/geopulse.service /etc/systemd/system/
sudo systemctl enable geopulse
sudo systemctl start geopulse

# 6. Nginx configuration
sudo cp deployment/nginx.conf /etc/nginx/sites-available/geopulse
sudo ln -s /etc/nginx/sites-available/geopulse /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

### Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://geopulse_user:password123@db:5432/geopulse_db
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: geopulse_db
      POSTGRES_USER: geopulse_user
      POSTGRES_PASSWORD: password123
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Production Checklist
- [ ] Environment variables secured
- [ ] Database credentials rotated
- [ ] SSL/TLS certificates configured
- [ ] Firewall rules configured
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] Log rotation configured
- [ ] Rate limiting enabled
- [ ] Security headers enabled

---

## Monitoring & Logging

### Application Logs
```bash
# View real-time logs
tail -f logs/api.log

# Search logs
grep "ERROR" logs/api.log
grep "user_id" logs/api.log

# Log rotation (add to crontab)
0 0 * * * /usr/sbin/logrotate /etc/logrotate.d/geopulse
```

### Health Monitoring
```bash
# Basic health check
curl http://localhost:8000/

# Detailed health check
curl http://localhost:8000/api/v1/health

# Middleware information
curl http://localhost:8000/middleware-info
```

### Performance Monitoring
```bash
# Database connection monitoring
SELECT * FROM pg_stat_activity WHERE datname = 'geopulse_db';

# Application metrics
curl http://localhost:8000/api/v1/health | jq '.database.pool_status'

# File system monitoring
df -h user_data/
du -sh user_data/uploads/
```

### Log Analysis Commands
```bash
# Error analysis
grep -c "ERROR" logs/api.log
grep "ERROR" logs/api.log | tail -10

# Request analysis
grep "POST /api/v1" logs/api.log | wc -l
grep "GET /api/v1" logs/api.log | wc -l

# Performance analysis
grep "slow query" logs/api.log
grep "timeout" logs/api.log
```

---

## Troubleshooting

### Common Issues & Solutions

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database connectivity
psql -U geopulse_user -h localhost -d geopulse_db -c "SELECT 1;"

# Check connection pool
grep "pool" logs/api.log
```

#### File Upload Issues
```bash
# Check file permissions
ls -la user_data/uploads/
chmod 755 user_data/uploads/

# Check disk space
df -h user_data/

# Check file processing logs
grep "file_upload" logs/api.log
```

#### Authentication Issues
```bash
# Check JWT configuration
grep "JWT" .env

# Verify token generation
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

#### Performance Issues
```bash
# Check database performance
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;

# Check memory usage
free -h
ps aux | grep python

# Check CPU usage
top -p $(pgrep -f "python main.py")
```

### Debug Commands
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py

# Database query debugging
export SQLALCHEMY_ECHO=true
python main.py

# Profile application
python -m cProfile -o profile.stats main.py
```

---

## Security Guidelines

### Security Checklist
- [ ] Strong secret keys in production
- [ ] JWT tokens with appropriate expiration
- [ ] Password hashing with bcrypt (12+ rounds)
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (SQLAlchemy ORM)
- [ ] File upload validation (type, size, content)
- [ ] Rate limiting enabled
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] Sensitive data not logged

### Security Commands
```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Check for security vulnerabilities
pip audit

# Scan for secrets in code
git secrets --scan

# Check file permissions
find . -type f -name "*.py" -exec ls -la {} \;
```

### Security Monitoring
```bash
# Monitor failed login attempts
grep "401" logs/api.log | grep "login"

# Monitor rate limiting
grep "rate_limit" logs/api.log

# Monitor file upload attempts
grep "upload" logs/api.log | grep "ERROR"
```

---

## Performance Optimization

### Database Optimization
```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_files_user_id ON files(user_id);
CREATE INDEX idx_files_created_at ON files(created_at);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

### Application Optimization
```bash
# Profile application
python -m cProfile -o profile.stats main.py
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(10)"

# Memory profiling
pip install memory-profiler
python -m memory_profiler main.py
```

### Caching Strategy
```python
# Redis caching (if implemented)
# Cache frequently accessed data
# Cache expensive computations
# Cache file processing results
```

### Performance Monitoring
```bash
# Monitor response times
grep "response_time" logs/api.log

# Monitor database query times
grep "query_time" logs/api.log

# Monitor file processing times
grep "processing_time" logs/api.log
```

---

## Useful Commands Reference

### Development Commands
```bash
# Start development server
python main.py

# Run tests
pytest
pytest --cov=app
pytest -v
pytest -k "test_name"

# Code quality
black app/ tests/
isort app/ tests/
mypy app/
flake8 app/

# Database
alembic upgrade head
alembic revision --autogenerate -m "message"
alembic current
alembic history
```

### Production Commands
```bash
# Start production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Process management
sudo systemctl start geopulse
sudo systemctl stop geopulse
sudo systemctl restart geopulse
sudo systemctl status geopulse

# Log management
tail -f logs/api.log
grep "ERROR" logs/api.log
logrotate /etc/logrotate.d/geopulse
```

### Monitoring Commands
```bash
# Health checks
curl http://localhost:8000/
curl http://localhost:8000/api/v1/health

# Performance monitoring
htop
iotop
netstat -tulpn | grep 8000

# Database monitoring
psql -U geopulse_user -d geopulse_db -c "SELECT * FROM pg_stat_activity;"
```

### Backup Commands
```bash
# Database backup
pg_dump -U geopulse_user geopulse_db > backup_$(date +%Y%m%d).sql

# File backup
tar -czf user_data_backup_$(date +%Y%m%d).tar.gz user_data/

# Full application backup
tar -czf geopulse_backup_$(date +%Y%m%d).tar.gz \
  --exclude=venv --exclude=__pycache__ --exclude=.git .
```

---

## Conclusion

This playbook provides comprehensive guidance for developing, testing, deploying, and maintaining the GeoPulse API. The modular monolith architecture with DDD principles ensures scalability and maintainability while keeping operational complexity manageable.

Key success factors:
- Follow the established architectural patterns
- Maintain comprehensive test coverage
- Monitor application health and performance
- Keep security practices up to date
- Document changes and decisions
- Use the provided commands and workflows

For additional support or questions, refer to the API documentation at `/docs` or the test collection in `GeoPulse-API-Testing/`.