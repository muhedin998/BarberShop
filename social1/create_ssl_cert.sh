#!/bin/bash
# Create self-signed SSL certificate for local development

# Create a directory for certificates
mkdir -p ssl_certs
cd ssl_certs

# Generate private key
openssl genrsa -out localhost.key 2048

# Generate certificate signing request
openssl req -new -key localhost.key -out localhost.csr -subj "/C=US/ST=State/L=City/O=Organization/CN=192.168.0.34"

# Generate self-signed certificate
openssl x509 -req -days 365 -in localhost.csr -signkey localhost.key -out localhost.crt

echo "SSL certificate created in ssl_certs/"
echo "To run with HTTPS:"
echo "python3 manage.py runsslserver 192.168.0.34:8443 --certificate ssl_certs/localhost.crt --key ssl_certs/localhost.key"