# Domain Setup Instructions for kfupm73.com

## Prerequisites
Your domain `kfupm73.com` should be configured with these nameservers:
- ns1.dns-parking.com
- ns2.dns-parking.com

## DNS Configuration
Before running any server commands, configure these DNS records in your domain registrar:

### Required DNS Records:
1. **A Record**:
   - Type: `A`
   - Name: `@` (or leave blank for root domain)
   - Value: `72.61.147.23`
   - TTL: `14400` (or automatic)

2. **A Record (www subdomain)**:
   - Type: `A`
   - Name: `www`
   - Value: `72.61.147.23`
   - TTL: `14400`

3. **Optional - CNAME Record** (alternative to www A record):
   - Type: `CNAME`
   - Name: `www`
   - Value: `kfupm73.com`
   - TTL: `14400`

**Wait 10-30 minutes for DNS propagation before proceeding.**

### Verify DNS Propagation:
```bash
# Check if domain resolves to your IP
nslookup kfupm73.com
nslookup www.kfupm73.com

# Or use dig
dig kfupm73.com
dig www.kfupm73.com
```

---

## Server Setup Commands

Run these commands on your server (72.61.147.23) **AFTER** DNS propagation:

### 1. Install Certbot (Let's Encrypt SSL)
```bash
# Update system
sudo apt update

# Install Certbot and Nginx plugin
sudo apt install -y certbot python3-certbot-nginx

# Create directory for certbot challenges
sudo mkdir -p /var/www/certbot
sudo chown -R www-data:www-data /var/www/certbot
```

### 2. Update Nginx Configuration
```bash
# Backup current nginx config
sudo cp /etc/nginx/sites-available/college-backend /etc/nginx/sites-available/college-backend.backup

# Copy the new nginx.conf to the server
# Upload the updated nginx.conf from your repo to: /etc/nginx/sites-available/college-backend
sudo nano /etc/nginx/sites-available/college-backend
# Paste the content from the updated nginx.conf file

# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

### 3. Obtain SSL Certificate
```bash
# Get SSL certificate for both domain and www subdomain
sudo certbot certonly --webroot \
  -w /var/www/certbot \
  -d kfupm73.com \
  -d www.kfupm73.com \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email

# Note: Replace 'your-email@example.com' with your actual email
```

### 4. Update Nginx with SSL Configuration
```bash
# The nginx.conf is already configured for SSL
# Just reload nginx after certbot creates the certificates
sudo nginx -t
sudo systemctl reload nginx
```

### 5. Update Environment Variables
```bash
# Update the .env file on the server
sudo nano /var/www/college-backend/.env

# Update these values:
DEBUG=False
ALLOWED_HOSTS=kfupm73.com,www.kfupm73.com,72.61.147.23,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=https://kfupm73.com,https://www.kfupm73.com
CSRF_TRUSTED_ORIGINS=https://kfupm73.com,https://www.kfupm73.com
```

### 6. Restart Backend Services
```bash
# Restart Gunicorn
sudo systemctl restart college-backend

# Check status
sudo systemctl status college-backend

# Check logs if there are issues
sudo journalctl -u college-backend -n 50
```

### 7. Setup Auto-Renewal for SSL Certificate
```bash
# Test auto-renewal
sudo certbot renew --dry-run

# Certbot automatically creates a cron job for renewal
# Verify the timer is active
sudo systemctl status certbot.timer
```

### 8. Verify HTTPS is Working
```bash
# Test the site
curl -I https://kfupm73.com
curl -I https://www.kfupm73.com

# Should return 200 OK with redirect from HTTP to HTTPS
curl -I http://kfupm73.com
```

---

## Troubleshooting

### If SSL certificate fails:
```bash
# Check if port 80 is accessible
sudo netstat -tlnp | grep :80

# Check nginx error logs
sudo tail -f /var/log/nginx/error.log

# Verify DNS is pointing to your server
dig +short kfupm73.com
# Should return: 72.61.147.23
```

### If Django returns 400 Bad Request:
```bash
# Check ALLOWED_HOSTS in .env
cat /var/www/college-backend/.env | grep ALLOWED_HOSTS

# Restart backend
sudo systemctl restart college-backend
```

### If CORS errors in browser:
```bash
# Verify CORS settings in .env
cat /var/www/college-backend/.env | grep CORS

# Check Django settings
sudo su - www-data -s /bin/bash
cd /var/www/college-backend
source venv/bin/activate
python manage.py shell
>>> from django.conf import settings
>>> print(settings.CORS_ALLOWED_ORIGINS)
>>> print(settings.ALLOWED_HOSTS)
>>> exit()
```

---

## Post-Deployment Checklist

- [ ] DNS records configured (A records for @ and www)
- [ ] DNS propagated (wait 10-30 minutes)
- [ ] Certbot installed
- [ ] SSL certificate obtained for kfupm73.com and www.kfupm73.com
- [ ] Nginx configuration updated and reloaded
- [ ] Environment variables updated with new domain
- [ ] Backend service restarted
- [ ] HTTPS working (https://kfupm73.com)
- [ ] HTTP redirects to HTTPS
- [ ] www redirects to non-www
- [ ] Frontend can communicate with backend API
- [ ] Admin panel accessible at https://kfupm73.com/admin

---

## Frontend Deployment

After server setup is complete:

1. Push your changes to GitHub
2. Build and deploy frontend:
   ```bash
   cd /var/www/college-frontend
   git pull origin main
   npm install
   npm run build
   sudo cp -r dist/* /var/www/college-frontend/
   ```

---

## Security Best Practices

1. **Firewall Configuration**:
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. **Regular Updates**:
   ```bash
   # Update system regularly
   sudo apt update && sudo apt upgrade -y
   ```

3. **Monitor SSL Certificate Expiry**:
   - Let's Encrypt certificates expire every 90 days
   - Certbot auto-renewal should handle this
   - Check: `sudo certbot certificates`

4. **Backup Configuration**:
   ```bash
   # Backup nginx config
   sudo cp /etc/nginx/sites-available/college-backend ~/nginx-backup-$(date +%Y%m%d).conf
   
   # Backup .env
   sudo cp /var/www/college-backend/.env ~/env-backup-$(date +%Y%m%d).env
   ```

---

## Expected Behavior After Setup

1. ✅ `http://kfupm73.com` → Redirects to → `https://kfupm73.com`
2. ✅ `http://www.kfupm73.com` → Redirects to → `https://kfupm73.com`
3. ✅ `https://www.kfupm73.com` → Redirects to → `https://kfupm73.com`
4. ✅ `https://kfupm73.com/api/` → Returns API response
5. ✅ `https://kfupm73.com/admin/` → Django admin login
6. ✅ Browser shows padlock icon (secure HTTPS connection)

---

## Contact & Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Review nginx error logs: `sudo tail -f /var/log/nginx/error.log`
3. Review gunicorn logs: `sudo journalctl -u college-backend -f`
4. Check Django logs for detailed error messages
