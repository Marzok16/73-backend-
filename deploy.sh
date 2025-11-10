#!/bin/bash

# Deployment script for College Project
# Run this script as root on your server

set -e  # Exit on any error

echo "🚀 Starting College Project Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root (use sudo)"
    exit 1
fi

print_status "Updating system packages..."
apt update && apt upgrade -y

print_status "Installing required packages..."
apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git curl

print_status "Creating application directories..."
mkdir -p /var/www/college-backend
mkdir -p /var/www/college-frontend
mkdir -p /var/log/gunicorn
mkdir -p /var/run/gunicorn

print_status "Setting up permissions..."
chown -R www-data:www-data /var/www/
chown -R www-data:www-data /var/log/gunicorn
chown -R www-data:www-data /var/run/gunicorn

print_status "Creating database and user..."
sudo -u postgres psql -c "CREATE DATABASE college_db;"
sudo -u postgres psql -c "CREATE USER college_user WITH PASSWORD 'your-strong-database-password';"
sudo -u postgres psql -c "ALTER ROLE college_user SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE college_user SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE college_user SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE college_db TO college_user;"

print_status "Deployment preparation complete!"
print_warning "Next steps:"
echo "1. Upload your backend code to /var/www/college-backend/"
echo "2. Upload your frontend dist files to /var/www/college-frontend/"
echo "3. Run the setup script: /var/www/college-backend/setup_backend.sh"
echo "4. Update the .env file with your database password"