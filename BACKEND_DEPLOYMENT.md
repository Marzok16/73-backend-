# Backend Deployment Guide

Quick reference for deploying backend changes to production server.

## 🚀 Full Deployment Workflow

```bash
# 1. Navigate to your local repo on server
cd ~/college/73-backend-

# 2. Pull latest changes from GitHub
git pull origin main

# 3. Copy updated files to production directory
sudo cp -r api memories college_backend *.py /var/www/college-backend/

# 4. If you changed settings.py, copy it specifically
sudo cp college_backend/settings.py /var/www/college-backend/college_backend/settings.py

# 5. If you updated requirements.txt, install new packages
sudo -u www-data /var/www/college-backend/venv/bin/pip install -r /var/www/college-backend/requirements.txt

# 6. Run migrations if you changed models
sudo -u www-data /var/www/college-backend/venv/bin/python /var/www/college-backend/manage.py migrate

# 7. Collect static files if needed
sudo -u www-data /var/www/college-backend/venv/bin/python /var/www/college-backend/manage.py collectstatic --noinput

# 8. Restart the backend service
sudo systemctl restart college-backend

# 9. Verify it's running
sudo systemctl status college-backend --no-pager
curl -I http://localhost/api/
```

---

## 📝 Quick Reference by Change Type

### ✏️ For Code Changes Only (views, serializers, utils, etc.)

```bash
cd ~/college/73-backend- && git pull origin main
sudo cp -r api memories /var/www/college-backend/
sudo systemctl restart college-backend
```

**When to use:** You modified Python files in `api/` or `memories/` folders (views, serializers, URLs, etc.)

---

### ⚙️ For Settings Changes

```bash
cd ~/college/73-backend- && git pull origin main
sudo cp college_backend/settings.py /var/www/college-backend/college_backend/settings.py
sudo systemctl restart college-backend
```

**When to use:** You modified Django settings (CORS, CSRF, database, etc.)

---

### 🗄️ For Model Changes (Database)

```bash
cd ~/college/73-backend- && git pull origin main
sudo cp -r api memories /var/www/college-backend/

# Run migrations
sudo -u www-data /var/www/college-backend/venv/bin/python /var/www/college-backend/manage.py migrate

sudo systemctl restart college-backend
```

**When to use:** You added/modified database models or created new migrations

**Note:** If you created NEW migrations locally, make sure to commit them first!

---

### 📦 For New Dependencies

```bash
cd ~/college/73-backend- && git pull origin main
sudo cp requirements.txt /var/www/college-backend/

# Install new packages
sudo -u www-data /var/www/college-backend/venv/bin/pip install -r /var/www/college-backend/requirements.txt

sudo systemctl restart college-backend
```

**When to use:** You added new packages to `requirements.txt`

---

### 🎨 For Static Files Changes

```bash
cd ~/college/73-backend- && git pull origin main
sudo cp -r api memories /var/www/college-backend/

# Collect static files
sudo -u www-data /var/www/college-backend/venv/bin/python /var/www/college-backend/manage.py collectstatic --noinput

sudo systemctl restart college-backend
```

**When to use:** You modified Django admin CSS/JS or added static files

---

### 🔧 For Systemd Service File Changes

```bash
cd ~/college/73-backend- && git pull origin main
sudo cp college-backend.service /etc/systemd/system/

# Reload systemd and restart
sudo systemctl daemon-reload
sudo systemctl restart college-backend
```

**When to use:** You modified the systemd service configuration

---

## 🛠️ Useful Maintenance Commands

### Check Backend Status
```bash
sudo systemctl status college-backend --no-pager
```

### View Backend Logs
```bash
# Systemd logs
sudo journalctl -u college-backend -n 50 --no-pager

# Gunicorn error logs
sudo tail -n 50 /var/log/gunicorn/college_error.log

# Gunicorn access logs
sudo tail -n 50 /var/log/gunicorn/college_access.log
```

### Restart Backend
```bash
sudo systemctl restart college-backend
```

### Check Socket Status
```bash
ls -la /run/gunicorn/
sudo lsof -U | grep college
```

### Test API
```bash
curl -I http://localhost/api/
curl http://localhost/api/ | jq
```

### Check Nginx Status
```bash
sudo systemctl status nginx
sudo nginx -t
```

---

## 🚨 Troubleshooting

### Backend Not Starting?
```bash
# Check logs for errors
sudo journalctl -u college-backend -n 100 --no-pager

# Check if processes are running
ps aux | grep gunicorn

# Check socket exists
ls -la /run/gunicorn/college-backend.sock
```

### 502 Bad Gateway?
```bash
# Check if socket exists
ls -la /run/gunicorn/

# Restart backend
sudo systemctl restart college-backend

# Check Nginx error logs
sudo tail -n 50 /var/log/nginx/error.log
```

### Permission Issues?
```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/college-backend

# Fix socket directory
sudo mkdir -p /run/gunicorn
sudo chown www-data:www-data /run/gunicorn
sudo chmod 755 /run/gunicorn
```

---

## 📍 Important Paths

- **Production Code:** `/var/www/college-backend/`
- **Development Repo:** `~/college/73-backend-`
- **Virtual Environment:** `/var/www/college-backend/venv/`
- **Socket File:** `/run/gunicorn/college-backend.sock`
- **Systemd Service:** `/etc/systemd/system/college-backend.service`
- **Nginx Config:** `/etc/nginx/sites-available/college-backend`
- **Logs:** `/var/log/gunicorn/`
- **Media Files:** `/var/www/college-backend/media/`
- **Static Files:** `/var/www/college-backend/staticfiles/`

---

## ✅ Deployment Checklist

Before deploying changes:
- [ ] Changes committed and pushed to GitHub
- [ ] Tested changes locally
- [ ] Created migrations if models changed
- [ ] Updated requirements.txt if dependencies added
- [ ] Backed up database if making major changes

After deploying:
- [ ] Service restarted successfully
- [ ] API responds correctly (`curl -I http://localhost/api/`)
- [ ] No errors in logs
- [ ] Frontend can connect to backend
- [ ] Test critical endpoints
