#!/bin/bash

# Complete setup script with correct Python 3.11 paths
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_status "Completing Django setup with Python 3.11..."

# Move .env file to correct location
if [ -f "/home/muhedin/.env" ]; then
    print_status "Moving .env file to project directory..."
    mv /home/muhedin/.env /home/muhedin/BarberShop/social1/.env
    chmod 600 /home/muhedin/BarberShop/social1/.env
    print_success ".env file moved and permissions set"
fi

# Navigate to project directory
cd /home/muhedin/BarberShop/social1

# Activate virtual environment and run Django commands
print_status "Activating virtual environment and running Django commands..."
source /home/muhedin/BarberShop/env/bin/activate

# Verify Python version
print_status "Using Python version: $(python --version)"
print_status "Using pip from: $(which pip)"

# Run migrations
print_status "Running Django migrations..."
python manage.py migrate

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput

print_success "Django setup completed"

# Restart services
print_status "Restarting services..."
sudo systemctl daemon-reload
sudo systemctl restart gunicorn

# Check gunicorn status
if sudo systemctl is-active --quiet gunicorn; then
    print_success "Gunicorn service is running"
else
    print_error "Gunicorn service failed to start"
    sudo systemctl status gunicorn --no-pager
fi

# Test Firebase setup
print_status "Testing Firebase initialization..."
python -c "
try:
    import os
    import sys
    sys.path.append('/home/muhedin/BarberShop/social1')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social1.settings')
    import django
    django.setup()
    from appointment.push_notifications import initialize_firebase
    initialize_firebase()
    print('✅ Firebase initialization successful')
except Exception as e:
    print(f'❌ Firebase initialization failed: {e}')
"

print_success "Setup completed! Your push notifications should be working at https://evoluci4n.online/"