#!/bin/bash

# Backend setup script
# Run this after uploading the backend code

set -e

echo "🔧 Setting up Django backend..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Change to backend directory
cd /var/www/college-backend

print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

print_status "Setting up environment file..."
cp .env.production .env

print_status "Collecting static files..."
python manage.py collectstatic --noinput

print_status "Running database migrations..."
python manage.py migrate

print_status "Creating superuser (you'll be prompted for details)..."
python manage.py createsuperuser --noinput --username admin --email admin@college.com || true

print_status "Setting up Nginx configuration..."
cp nginx.conf /etc/nginx/sites-available/college
ln -sf /etc/nginx/sites-available/college /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

print_status "Setting up systemd services..."
cp college-backend.service /etc/systemd/system/
cp college-backend.socket /etc/systemd/system/

print_status "Starting services..."
systemctl daemon-reload
systemctl enable college-backend.socket
systemctl start college-backend.socket
systemctl enable college-backend.service
systemctl start college-backend.service

print_status "Testing Nginx configuration..."
nginx -t

print_status "Starting Nginx..."
systemctl enable nginx
systemctl restart nginx

print_status "Setting correct permissions..."
chown -R www-data:www-data /var/www/college-backend
chmod -R 755 /var/www/college-backend

print_status "✅ Backend setup complete!"
print_warning "Important reminders:"
echo "1. Update the SECRET_KEY in /var/www/college-backend/.env"
echo "2. Update the database password in /var/www/college-backend/.env"
echo "3. Check service status: systemctl status college-backend"
echo "4. Check logs: journalctl -u college-backend -f"