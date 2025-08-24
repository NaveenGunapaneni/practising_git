# GeoPulse Nginx Dockerfile
FROM nginx:alpine

# Install required packages
RUN apk add --no-cache \
    openssl \
    curl \
    && rm -rf /var/cache/apk/*

# Create SSL directory
RUN mkdir -p /etc/nginx/ssl

# Copy nginx configuration
COPY nginx.docker.conf /etc/nginx/nginx.conf

# Copy SSL certificate generation script
COPY generate-ssl-certs.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/generate-ssl-certs.sh

# Create nginx user if it doesn't exist
RUN addgroup -g 101 -S nginx && \
    adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx

# Create necessary directories
RUN mkdir -p /var/log/nginx /var/cache/nginx /etc/nginx/conf.d

# Set proper permissions
RUN chown -R nginx:nginx /var/log/nginx /var/cache/nginx /etc/nginx/conf.d

# Expose ports
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
