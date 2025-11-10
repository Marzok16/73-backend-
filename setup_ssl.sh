#!/bin/bash
# SSL Setup Script for kfupm73.com
# Run this script on your server after DNS propagation

set -e  # Exit on error

echo "============================================"
echo "SSL Setup for kfupm73.com"
echo "============================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root or with sudo"
    exit 1
fi

# Step 1: Install Certbot
echo "Step 1: Installing Certbot..."
apt update
apt install -y certbot python3-certbot-nginx

# Step 2: Create certbot directory
echo "Step 2: Creating certbot directory..."
mkdir -p /var/www/certbot
chown -R www-data:www-data /var/www/certbot

# Step 3: Backup current nginx config
echo "Step 3: Backing up nginx configuration..."
cp /etc/nginx/sites-available/college-backend /etc/nginx/sites-available/college-backend.backup.$(date +%Y%m%d)

# Step 4: Ask for email
echo ""
read -p "Enter your email for SSL certificate notifications: " EMAIL

# Step 5: Verify DNS
echo ""
echo "Step 5: Verifying DNS propagation..."
DOMAIN_IP=$(dig +short kfupm73.com | head -n1)
WWW_IP=$(dig +short www.kfupm73.com | head -n1)

if [ "$DOMAIN_IP" != "72.61.147.23" ]; then
    echo "WARNING: kfupm73.com does not resolve to 72.61.147.23"
    echo "Current IP: $DOMAIN_IP"
    echo "Please wait for DNS propagation before continuing."
    read -p "Do you want to continue anyway? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        exit 1
    fi
fi

if [ "$WWW_IP" != "72.61.147.23" ]; then
    echo "WARNING: www.kfupm73.com does not resolve to 72.61.147.23"
    echo "Current IP: $WWW_IP"
fi

# Step 6: Test nginx config
echo ""
echo "Step 6: Testing nginx configuration..."
nginx -t

if [ $? -ne 0 ]; then
    echo "ERROR: Nginx configuration test failed!"
    echo "Please update /etc/nginx/sites-available/college-backend with the new configuration"
    exit 1
fi

# Step 7: Reload nginx
echo "Step 7: Reloading nginx..."
systemctl reload nginx

# Step 8: Obtain SSL certificate
echo ""
echo "Step 8: Obtaining SSL certificate..."
certbot certonly --webroot \
    -w /var/www/certbot \
    -d kfupm73.com \
    -d www.kfupm73.com \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --non-interactive

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to obtain SSL certificate"
    echo "Please check the error messages above"
    exit 1
fi

# Step 9: Update environment file
echo ""
echo "Step 9: Updating environment variables..."
ENV_FILE="/var/www/college-backend/.env"

if [ -f "$ENV_FILE" ]; then
    # Backup .env
    cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d)"
    
    # Update ALLOWED_HOSTS
    sed -i 's/^ALLOWED_HOSTS=.*/ALLOWED_HOSTS=kfupm73.com,www.kfupm73.com,72.61.147.23,localhost,127.0.0.1/' "$ENV_FILE"
    
    # Update CORS_ALLOWED_ORIGINS
    sed -i 's/^CORS_ALLOWED_ORIGINS=.*/CORS_ALLOWED_ORIGINS=https:\/\/kfupm73.com,https:\/\/www.kfupm73.com/' "$ENV_FILE"
    
    # Add or update CSRF_TRUSTED_ORIGINS
    if grep -q "^CSRF_TRUSTED_ORIGINS=" "$ENV_FILE"; then
        sed -i 's/^CSRF_TRUSTED_ORIGINS=.*/CSRF_TRUSTED_ORIGINS=https:\/\/kfupm73.com,https:\/\/www.kfupm73.com/' "$ENV_FILE"
    else
        echo "CSRF_TRUSTED_ORIGINS=https://kfupm73.com,https://www.kfupm73.com" >> "$ENV_FILE"
    fi
    
    echo "Environment file updated successfully"
else
    echo "WARNING: Environment file not found at $ENV_FILE"
    echo "Please create it manually with the correct settings"
fi

# Step 10: Reload nginx with SSL
echo ""
echo "Step 10: Reloading nginx with SSL configuration..."
nginx -t && systemctl reload nginx

# Step 11: Restart backend service
echo ""
echo "Step 11: Restarting backend service..."
systemctl restart college-backend
sleep 2
systemctl status college-backend --no-pager

# Step 12: Test auto-renewal
echo ""
echo "Step 12: Testing SSL auto-renewal..."
certbot renew --dry-run

# Summary
echo ""
echo "============================================"
echo "Setup Complete!"
echo "============================================"
echo ""
echo "Your site should now be available at:"
echo "  ✅ https://kfupm73.com"
echo "  ✅ https://www.kfupm73.com"
echo ""
echo "Testing URLs:"
echo "  - Frontend: https://kfupm73.com"
echo "  - API: https://kfupm73.com/api/"
echo "  - Admin: https://kfupm73.com/admin/"
echo ""
echo "Next steps:"
echo "1. Test the site in your browser"
echo "2. Deploy the updated frontend code"
echo "3. Monitor logs for any issues"
echo ""
echo "Logs:"
echo "  - Nginx: sudo tail -f /var/log/nginx/error.log"
echo "  - Backend: sudo journalctl -u college-backend -f"
echo ""
