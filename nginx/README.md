# GeoPulse Nginx Configuration

This directory contains the nginx configuration for the GeoPulse application, providing SSL termination, reverse proxy, and load balancing capabilities.

## Files Overview

- `nginx.conf` - Main nginx configuration for standalone deployment
- `nginx.docker.conf` - Nginx configuration optimized for Docker deployment
- `Dockerfile` - Dockerfile for building the nginx container
- `generate-ssl-certs.sh` - Script to generate self-signed SSL certificates
- `docker-compose.nginx.yml` - Docker Compose file with nginx included
- `README.md` - This documentation file

## Features

### SSL/TLS Support
- Self-signed certificate generation
- TLS 1.2 and 1.3 support
- Strong cipher configuration
- HTTP to HTTPS redirect

### Reverse Proxy
- API backend proxy (FastAPI)
- UI frontend proxy (React)
- Health check endpoints
- Rate limiting for API endpoints

### Security
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- Rate limiting for login and API endpoints
- CORS configuration
- Request size limits

### Performance
- Gzip compression
- Static file caching
- Connection keepalive
- Buffer optimization

## Quick Start

### Option 1: Docker Deployment (Recommended)

1. **Start the application with nginx:**
   ```bash
   docker-compose -f nginx/docker-compose.nginx.yml up -d
   ```

2. **Access the application:**
   - Web UI: https://localhost
   - API: https://localhost/api
   - pgAdmin: http://localhost:5050

### Option 2: Standalone Nginx

1. **Generate SSL certificates:**
   ```bash
   sudo chmod +x nginx/generate-ssl-certs.sh
   sudo ./nginx/generate-ssl-certs.sh
   ```

2. **Copy configuration:**
   ```bash
   sudo cp nginx/nginx.conf /etc/nginx/nginx.conf
   ```

3. **Test and reload nginx:**
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

## Configuration Details

### Upstream Servers
- **API Backend**: `api:8000` (Docker) or `127.0.0.1:8000` (standalone)
- **UI Frontend**: `ui:3000` (Docker) or `127.0.0.1:3001` (standalone)

### Rate Limiting
- **API endpoints**: 10 requests/second with burst of 20
- **Login endpoint**: 5 requests/minute with burst of 5

### SSL Configuration
- **Certificate**: Self-signed (365 days validity)
- **Protocols**: TLS 1.2, TLS 1.3
- **Ciphers**: Strong ECDHE and DHE ciphers

### File Upload Limits
- **Maximum body size**: 100MB
- **Upload timeouts**: 300 seconds

## PostgreSQL Access

The configuration includes commented sections for PostgreSQL access via nginx. To enable:

1. **Uncomment the stream block** in the configuration
2. **Update the PostgreSQL server IP** (currently set to `31.97.205.38:5432`)
3. **Restart nginx**

```nginx
stream {
    upstream postgres_backend {
        server 31.97.205.38:5432;
    }
    
    server {
        listen 5432 ssl;
        proxy_pass postgres_backend;
        
        ssl_certificate /etc/nginx/ssl/nginx-selfsigned.crt;
        ssl_certificate_key /etc/nginx/ssl/nginx-selfsigned.key;
        ssl_protocols TLSv1.2 TLSv1.3;
    }
}
```

## Environment Variables

The following environment variables can be configured:

```bash
# Database
POSTGRES_DB=geopulse_db
POSTGRES_USER=geopulse_user
POSTGRES_PASSWORD=geopulse_secure_123
POSTGRES_PORT=5433

# API
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production
CORS_ALLOW_ORIGINS=http://localhost:3001,http://ui:3000,https://localhost

# pgAdmin
PGADMIN_EMAIL=admin@geopulse.com
PGADMIN_PASSWORD=admin123
PGADMIN_PORT=5050

# Shared data path
SHARED_DATA_PATH=./shared_data
```

## Troubleshooting

### SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in /etc/nginx/ssl/nginx-selfsigned.crt -text -noout

# Regenerate certificates
sudo ./nginx/generate-ssl-certs.sh
```

### Nginx Configuration Test
```bash
# Test configuration
nginx -t

# Check nginx status
systemctl status nginx

# View logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### Docker Issues
```bash
# Check container logs
docker logs geopulse-nginx

# Restart nginx container
docker-compose -f nginx/docker-compose.nginx.yml restart nginx

# Rebuild nginx container
docker-compose -f nginx/docker-compose.nginx.yml build nginx
```

## Security Considerations

1. **Self-signed certificates** are used for development/testing
2. **For production**, use Let's Encrypt or commercial CA certificates
3. **Rate limiting** is configured to prevent abuse
4. **Security headers** are set to protect against common attacks
5. **PostgreSQL access** is disabled by default for security

## Performance Tuning

The configuration includes several performance optimizations:

- **Worker processes**: Auto-detected based on CPU cores
- **Worker connections**: 1024 per worker
- **Keepalive**: 65 seconds
- **Gzip compression**: Enabled for text-based content
- **Static file caching**: 1 year for assets, 1 hour for HTML

## Monitoring

### Health Checks
- **Nginx**: `https://localhost/health`
- **API**: `https://localhost/api/v1/health`
- **UI**: `https://localhost`

### Logs
- **Access logs**: `/var/log/nginx/access.log`
- **Error logs**: `/var/log/nginx/error.log`
- **Docker logs**: `docker logs geopulse-nginx`

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review nginx error logs
3. Verify SSL certificate configuration
4. Ensure all services are running and healthy
