#!/bin/bash
# Script to fix 502 Bad Gateway error

echo "=== Fixing 502 Bad Gateway ==="
echo ""

# 1. Ensure socket directory exists with correct permissions
echo "1. Creating socket directory..."
sudo mkdir -p /run/gunicorn
sudo chown www-data:www-data /run/gunicorn
sudo chmod 755 /run/gunicorn
echo "✓ Socket directory configured"
echo ""

# 2. Stop services
echo "2. Stopping services..."
sudo systemctl stop college-backend
sudo systemctl stop college-backend.socket
echo "✓ Services stopped"
echo ""

# 3. Remove stale socket file
echo "3. Cleaning up old socket..."
sudo rm -f /run/gunicorn/college-backend.sock
sudo rm -f /var/run/gunicorn/college_backend.pid
echo "✓ Old socket removed"
echo ""

# 4. Start socket first (systemd activation)
echo "4. Starting socket service..."
sudo systemctl start college-backend.socket
sudo systemctl enable college-backend.socket
sleep 2
echo "✓ Socket service started"
echo ""

# 5. Start the backend service
echo "5. Starting backend service..."
sudo systemctl start college-backend
sudo systemctl enable college-backend
sleep 3
echo "✓ Backend service started"
echo ""

# 6. Verify socket exists
echo "6. Verifying socket:"
if [ -S /run/gunicorn/college-backend.sock ]; then
    echo "✓ Socket file exists:"
    ls -lh /run/gunicorn/college-backend.sock
else
    echo "✗ Socket file still not found!"
fi
echo ""

# 7. Check service status
echo "7. Service status:"
systemctl status college-backend --no-pager -l | head -n 15
echo ""

# 8. Test Nginx configuration
echo "8. Testing Nginx configuration..."
sudo nginx -t
echo ""

# 9. Reload Nginx
echo "9. Reloading Nginx..."
sudo systemctl reload nginx
echo "✓ Nginx reloaded"
echo ""

# 10. Test the API
echo "10. Testing API endpoint:"
sleep 2
curl -I http://localhost/api/ 2>&1
echo ""

echo "=== Fix Complete ==="
echo ""
echo "If still getting 502, run: sudo ./troubleshoot_502.sh"
