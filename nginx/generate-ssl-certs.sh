#!/bin/bash

# Generate Self-Signed SSL Certificates for GeoPulse Nginx
# This script creates SSL certificates for HTTPS access

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Generating Self-Signed SSL Certificates for GeoPulse...${NC}"

# Create SSL directory if it doesn't exist
SSL_DIR="/etc/nginx/ssl"
if [ ! -d "$SSL_DIR" ]; then
    echo -e "${YELLOW}Creating SSL directory: $SSL_DIR${NC}"
    sudo mkdir -p "$SSL_DIR"
fi

# Generate private key
echo -e "${YELLOW}Generating private key...${NC}"
sudo openssl genrsa -out "$SSL_DIR/nginx-selfsigned.key" 2048

# Generate certificate signing request (CSR)
echo -e "${YELLOW}Generating certificate signing request...${NC}"
sudo openssl req -new -key "$SSL_DIR/nginx-selfsigned.key" -out "$SSL_DIR/nginx-selfsigned.csr" -subj "/C=US/ST=State/L=City/O=GeoPulse/OU=IT/CN=geopulse.local"

# Generate self-signed certificate
echo -e "${YELLOW}Generating self-signed certificate...${NC}"
sudo openssl x509 -req -days 365 -in "$SSL_DIR/nginx-selfsigned.csr" -signkey "$SSL_DIR/nginx-selfsigned.key" -out "$SSL_DIR/nginx-selfsigned.crt"

# Set proper permissions
echo -e "${YELLOW}Setting proper permissions...${NC}"
sudo chmod 600 "$SSL_DIR/nginx-selfsigned.key"
sudo chmod 644 "$SSL_DIR/nginx-selfsigned.crt"
sudo chmod 644 "$SSL_DIR/nginx-selfsigned.csr"

# Create a combined certificate file (optional)
echo -e "${YELLOW}Creating combined certificate file...${NC}"
sudo cat "$SSL_DIR/nginx-selfsigned.crt" "$SSL_DIR/nginx-selfsigned.key" | sudo tee "$SSL_DIR/nginx-selfsigned.pem" > /dev/null
sudo chmod 600 "$SSL_DIR/nginx-selfsigned.pem"

# Verify the certificate
echo -e "${YELLOW}Verifying certificate...${NC}"
sudo openssl x509 -in "$SSL_DIR/nginx-selfsigned.crt" -text -noout | head -20

echo -e "${GREEN}SSL certificates generated successfully!${NC}"
echo -e "${YELLOW}Certificate files created:${NC}"
echo -e "  - Private Key: $SSL_DIR/nginx-selfsigned.key"
echo -e "  - Certificate: $SSL_DIR/nginx-selfsigned.crt"
echo -e "  - CSR: $SSL_DIR/nginx-selfsigned.csr"
echo -e "  - Combined: $SSL_DIR/nginx-selfsigned.pem"
echo ""
echo -e "${YELLOW}Note: These are self-signed certificates. Browsers will show security warnings.${NC}"
echo -e "${YELLOW}For production use, consider using Let's Encrypt or a commercial CA.${NC}"
