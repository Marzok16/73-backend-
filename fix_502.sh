#!/bin/bash
# Script to fix 502 Bad Gateway error - IMPROVED VERSION

echo "=== Fixing 502 Bad Gateway ==="
echo ""

# 1. Stop services completely
echo "1. Stopping all services..."
sudo systemctl stop college-backend
sudo systemctl stop college-backend.socket
sleep 2
echo "✓ Services stopped"
echo ""

# 2. Clean up everything
echo "2. Cleaning up old socket and PID files..."
sudo rm -f /run/gunicorn/college-backend.sock
sudo rm -f /run/gunicorn/college_backend.pid
sudo rm -f /var/run/gunicorn/college_backend.pid
echo "✓ Old files removed"
echo ""

# 3. Ensure socket directory exists with correct permissions
echo "3. Setting up socket directory..."
sudo mkdir -p /run/gunicorn
sudo chown www-data:www-data /run/gunicorn
sudo chmod 755 /run/gunicorn
echo "✓ Socket directory configured"
echo ""

# 4. Reload systemd to pick up any service file changes
echo "4. Reloading systemd daemon..."
sudo systemctl daemon-reload
echo "✓ Systemd reloaded"
echo ""

# 5. Start socket service (must be first)
echo "5. Starting socket service..."
sudo systemctl start college-backend.socket
sudo systemctl enable college-backend.socket
sleep 2
echo "✓ Socket service started"
echo ""

# 6. Start the backend service (will be triggered by socket)
echo "6. Starting backend service..."
sudo systemctl start college-backend
sudo systemctl enable college-backend
sleep 3
echo "✓ Backend service started"
echo ""

# 7. Verify socket exists
echo "7. Verifying socket:"
if [ -S /run/gunicorn/college-backend.sock ]; then
    echo "✓ Socket file exists:"
    ls -lh /run/gunicorn/college-backend.sock
else
    echo "✗ Socket file NOT found! Checking logs..."
    sudo journalctl -u college-backend -n 20 --no-pager
fi
echo ""

# 8. Check service status
echo "8. Service status:"
systemctl is-active college-backend && echo "✓ Backend is active" || echo "✗ Backend is NOT active"
systemctl is-active college-backend.socket && echo "✓ Socket is active" || echo "✗ Socket is NOT active"
echo ""

# 9. Test Nginx configuration
echo "9. Testing Nginx configuration..."
sudo nginx -t
echo ""

# 10. Reload Nginx
echo "10. Reloading Nginx..."
sudo systemctl reload nginx
echo "✓ Nginx reloaded"
echo ""

# 11. Test the API
echo "11. Testing API endpoint:"
sleep 2
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/)
if [ "$HTTP_STATUS" = "200" ]; then
    echo "✓ API is responding: HTTP $HTTP_STATUS"
else
    echo "✗ API returned: HTTP $HTTP_STATUS"
    echo "Checking nginx error logs..."
    sudo tail -n 5 /var/log/nginx/error.log
fi
echo ""

echo "=== Fix Complete ==="
echo ""
echo "If still getting 502, check logs with:"
echo "  sudo journalctl -u college-backend -n 50 --no-pager"
echo "  sudo tail -n 50 /var/log/nginx/error.log"
