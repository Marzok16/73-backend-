#!/bin/bash
# Troubleshooting script for 502 Bad Gateway error

echo "=== College Backend 502 Troubleshooting ==="
echo ""

# 1. Check if socket file exists
echo "1. Checking socket file:"
if [ -S /run/gunicorn/college-backend.sock ]; then
    echo "✓ Socket file exists"
    ls -lh /run/gunicorn/college-backend.sock
else
    echo "✗ Socket file NOT found at /run/gunicorn/college-backend.sock"
fi
echo ""

# 2. Check socket directory permissions
echo "2. Socket directory permissions:"
ls -ld /run/gunicorn/
echo ""

# 3. Check Gunicorn service status
echo "3. Gunicorn service status:"
systemctl is-active college-backend
echo ""

# 4. Check socket service status
echo "4. Socket service status:"
systemctl is-active college-backend.socket
echo ""

# 5. Check if Nginx can access socket
echo "5. Testing socket connectivity:"
sudo -u www-data test -r /run/gunicorn/college-backend.sock && echo "✓ Nginx (www-data) CAN read socket" || echo "✗ Nginx (www-data) CANNOT read socket"
sudo -u www-data test -w /run/gunicorn/college-backend.sock && echo "✓ Nginx (www-data) CAN write to socket" || echo "✗ Nginx (www-data) CANNOT write to socket"
echo ""

# 6. Check Nginx error log
echo "6. Recent Nginx errors:"
sudo tail -n 20 /var/log/nginx/error.log
echo ""

# 7. Check Gunicorn error log
echo "7. Recent Gunicorn errors:"
sudo tail -n 20 /var/log/gunicorn/college_error.log
echo ""

# 8. Check process ownership
echo "8. Gunicorn processes:"
ps aux | grep gunicorn | grep -v grep
echo ""

# 9. Test socket manually
echo "9. Testing socket with curl:"
curl --unix-socket /run/gunicorn/college-backend.sock http://localhost/api/ -v 2>&1 | head -n 20
echo ""

echo "=== Troubleshooting Complete ==="
