# College Project Deployment Guide

## Quick Overview
This deployment consists of:
- **Frontend**: React app served by Nginx at `/` 
- **Backend**: Django API served by Gunicorn at `/api/`
- **Database**: PostgreSQL
- **Web Server**: Nginx as reverse proxy

## Files Created:
- `nginx.conf` - Nginx configuration
- `gunicorn.conf.py` - Gunicorn WSGI server config
- `.env.production` - Production environment variables
- `college-backend.service` - Systemd service for Django
- `college-backend.socket` - Systemd socket for Gunicorn
- `deploy.sh` - Initial server setup script
- `setup_backend.sh` - Backend application setup script

## Deployment Process:

### 1. Prepare files on your local machine:
- Backend code is in `73-backend-` folder
- Frontend built files are in `73/dist` folder

### 2. Upload to server:
```bash
# Upload backend
scp -r 73-backend-/* root@72.61.147.23:/tmp/backend/

# Upload frontend dist
scp -r 73/dist/* root@72.61.147.23:/tmp/frontend/
```

### 3. Run on server:
```bash
# Initial setup
chmod +x /tmp/backend/deploy.sh
./tmp/backend/deploy.sh

# Move files
mv /tmp/backend/* /var/www/college-backend/
mv /tmp/frontend/* /var/www/college-frontend/

# Setup backend
chmod +x /var/www/college-backend/setup_backend.sh
/var/www/college-backend/setup_backend.sh
```

### 4. Configure environment:
Edit `/var/www/college-backend/.env` with your database password and secret key.

## Important Security Notes:
1. Generate a new SECRET_KEY for production
2. Use a strong database password
3. Consider setting up SSL/HTTPS later
4. Regularly update system packages

## Monitoring:
- Check Django service: `systemctl status college-backend`
- Check logs: `journalctl -u college-backend -f`
- Check Nginx: `systemctl status nginx`