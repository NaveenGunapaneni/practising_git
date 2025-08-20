# GeoPulse Docker Setup

This document explains how to run GeoPulse using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB of available RAM
- At least 10GB of available disk space

## Quick Start

### Development Environment

1. **Clone the repository and navigate to the project root:**
   ```bash
   cd GeoPulse
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Check service status:**
   ```bash
   docker-compose ps
   ```

4. **View logs:**
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f api
   docker-compose logs -f ui
   docker-compose logs -f db
   ```

### Production Environment

1. **Set environment variables (create .env file):**
   ```bash
   POSTGRES_PASSWORD=your_secure_password
   SECRET_KEY=your_secret_key_here
   JWT_SECRET_KEY=your_jwt_secret_key_here
   CORS_ALLOW_ORIGINS=http://yourdomain.com
   ```

2. **Start production services:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Services

### Database (PostgreSQL)
- **Port:** 5432
- **Container:** geopulse-db
- **Data:** Persisted in `postgres_data` volume
- **Credentials:**
  - Database: `geopulse_db`
  - User: `geopulse_user`
  - Password: `geopulse_secure_123` (change in production)

### API (FastAPI)
- **Port:** 8000
- **Container:** geopulse-api
- **Health Check:** http://localhost:8000/health
- **API Documentation:** http://localhost:8000/docs
- **Data:** User uploads and logs persisted in volumes

### UI (React)
- **Port:** 3000
- **Container:** geopulse-ui
- **Health Check:** http://localhost:3000
- **Proxy:** Configured to forward API calls to backend

### pgAdmin (Optional)
- **Port:** 5050
- **Container:** geopulse-pgadmin
- **URL:** http://localhost:5050
- **Credentials:**
  - Email: `admin@geopulse.com`
  - Password: `admin123`

## Access Points

- **Frontend:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Database Admin:** http://localhost:5050
- **Database:** localhost:5432

## Useful Commands

### Development

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild and start
docker-compose up -d --build

# View logs
docker-compose logs -f

# Execute commands in containers
docker-compose exec api bash
docker-compose exec db psql -U geopulse_user -d geopulse_db
docker-compose exec ui sh

# Run database migrations
docker-compose exec api alembic upgrade head

# Create database backup
docker-compose exec db pg_dump -U geopulse_user geopulse_db > backup.sql
```

### Production

```bash
# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Stop production services
docker-compose -f docker-compose.prod.yml down

# View production logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

## Environment Variables

### Database
- `POSTGRES_DB`: Database name (default: geopulse_db)
- `POSTGRES_USER`: Database user (default: geopulse_user)
- `POSTGRES_PASSWORD`: Database password (default: geopulse_secure_123)

### API
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Application secret key
- `JWT_SECRET_KEY`: JWT signing key
- `CORS_ALLOW_ORIGINS`: Allowed CORS origins
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)

### UI
- `REACT_APP_API_URL`: API URL for frontend
- `REACT_APP_API_BASE_URL`: Internal API URL

## Volumes

- `postgres_data`: PostgreSQL database files
- `api_data`: API user data and uploads
- `api_logs`: API log files
- `ui_node_modules`: UI node modules (development only)

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   ```bash
   # Check what's using the ports
   lsof -i :3000
   lsof -i :8000
   lsof -i :5432
   ```

2. **Database connection issues:**
   ```bash
   # Check database logs
   docker-compose logs db
   
   # Test database connection
   docker-compose exec api python -c "from app.core.database import engine; print('DB OK')"
   ```

3. **API not starting:**
   ```bash
   # Check API logs
   docker-compose logs api
   
   # Check if database is ready
   docker-compose exec db pg_isready -U geopulse_user -d geopulse_db
   ```

4. **UI not loading:**
   ```bash
   # Check UI logs
   docker-compose logs ui
   
   # Check if API is accessible
   curl http://localhost:8000/health
   ```

### Reset Everything

```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Start fresh
docker-compose up -d --build
```

## Security Considerations

1. **Change default passwords** in production
2. **Use environment variables** for sensitive data
3. **Enable SSL/TLS** in production
4. **Restrict network access** to database
5. **Regular security updates** for base images

## Performance Tuning

### Database
- Adjust `POSTGRES_SHARED_BUFFERS` and `POSTGRES_EFFECTIVE_CACHE_SIZE`
- Monitor query performance with pgAdmin

### API
- Enable connection pooling
- Monitor memory usage
- Use production WSGI server (Gunicorn)

### UI
- Enable gzip compression
- Use CDN for static assets
- Implement caching strategies

## Monitoring

### Health Checks
All services include health checks:
- Database: `pg_isready`
- API: `curl /health`
- UI: `wget /`

### Logs
```bash
# Follow all logs
docker-compose logs -f

# Filter logs
docker-compose logs -f api | grep ERROR
```

### Metrics
Consider adding monitoring tools like:
- Prometheus + Grafana
- ELK Stack
- Docker stats: `docker stats`
