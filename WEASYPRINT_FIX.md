# WeasyPrint 502 Error Fix

## Problem
The backend service returns 502 Bad Gateway when trying to access `/api/pdf/book/` endpoint. This is caused by WeasyPrint not being able to load properly even after installing system libraries.

## Solution Steps

### 1. Upload Updated Files to Server

Upload these files to `/var/www/college-backend/`:
- `gunicorn.conf.py` (increased timeout to 120s)
- `college-backend.service` (added environment variables)
- `memories/views.py` (better error handling)
- `test_weasyprint.py` (diagnostic script)

```bash
# On your local machine, from the 73-backend- directory:
scp gunicorn.conf.py kfupm73@srv1118400.gridhost.co.uk:/var/www/college-backend/
scp college-backend.service kfupm73@srv1118400.gridhost.co.uk:/tmp/
scp memories/views.py kfupm73@srv1118400.gridhost.co.uk:/var/www/college-backend/memories/
scp test_weasyprint.py kfupm73@srv1118400.gridhost.co.uk:/var/www/college-backend/
```

### 2. On the Server - Update Service File

```bash
# Copy service file to systemd
sudo cp /tmp/college-backend.service /etc/systemd/system/

# Reload systemd daemon
sudo systemctl daemon-reload
```

### 3. Test WeasyPrint Installation

```bash
# Activate virtual environment
cd /var/www/college-backend
source venv/bin/activate

# Run diagnostic script
python test_weasyprint.py
```

**Expected Output:** All tests should pass with green checkmarks (✓)

If any test fails, the script will tell you which library is missing.

### 4. Check if Additional Libraries are Needed

If the test shows missing libraries, install them:

```bash
# Install additional dependencies
sudo apt-get install -y \
    python3-cffi \
    python3-brotli \
    libffi-dev \
    shared-mime-info \
    fonts-dejavu-core

# Update font cache
sudo fc-cache -fv
```

### 5. Restart the Backend Service

```bash
# Restart the service
sudo systemctl restart college-backend

# Check status
sudo systemctl status college-backend

# Check if it's listening properly
curl -I http://localhost/api/health_check/
```

### 6. Test PDF Generation

```bash
# Test the PDF endpoint
curl -I http://localhost/api/pdf/book/

# If it returns 200 OK, download the PDF:
curl http://localhost/api/pdf/book/ -o test_book.pdf

# Check the file
file test_book.pdf
```

### 7. Check Logs if Still Failing

```bash
# Check Gunicorn error logs
sudo tail -n 100 /var/log/gunicorn/college_error.log

# Check service logs
sudo journalctl -u college-backend -n 100 --no-pager

# Check nginx error logs
sudo tail -n 50 /var/log/nginx/error.log
```

## What Changed

### 1. `gunicorn.conf.py`
- Increased `timeout` from 30 to 120 seconds
- PDF generation can take longer, especially with many images

### 2. `college-backend.service`
- Added `PATH` environment variable
- Added `LD_LIBRARY_PATH` to help find system libraries
- These ensure Gunicorn workers can find the required libraries

### 3. `memories/views.py`
- Added better error handling with full tracebacks
- Added `traceback` import for detailed error messages
- Now shows exactly what went wrong during PDF generation

### 4. `test_weasyprint.py`
- New diagnostic script to test WeasyPrint functionality
- Tests all critical components:
  - Python version
  - WeasyPrint import
  - System libraries (Pango, Cairo)
  - Actual PDF generation
  - Environment variables

## Common Issues and Solutions

### Issue 1: Service Still Returns 502
**Solution:** Check if the socket file exists and has correct permissions:
```bash
ls -la /run/gunicorn/college-backend.sock
# Should be owned by www-data:www-data

# If not, restart the socket:
sudo systemctl restart college-backend.socket
sudo systemctl restart college-backend
```

### Issue 2: "Cannot open shared object file"
**Solution:** The library path isn't set correctly. Verify environment variables:
```bash
# Check if service has the environment variables:
sudo systemctl show college-backend | grep Environment

# Should show:
# Environment=DJANGO_SETTINGS_MODULE=college_backend.settings
# Environment=PATH=...
# Environment=LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu
```

### Issue 3: Gunicorn Workers Keep Dying
**Solution:** Check worker timeout and increase if needed:
```bash
# Edit gunicorn.conf.py and increase timeout further if needed
# Current: timeout = 120

# Can increase to 300 (5 minutes) for large PDFs:
timeout = 300
```

### Issue 4: Fonts Missing in PDF
**Solution:** Install additional fonts:
```bash
sudo apt-get install -y \
    fonts-dejavu \
    fonts-dejavu-core \
    fonts-dejavu-extra \
    fonts-liberation \
    fonts-noto-core

sudo fc-cache -fv
```

## Testing Without Restarting Service

You can test PDF generation directly with Django shell:

```bash
cd /var/www/college-backend
source venv/bin/activate
python manage.py shell
```

Then in the Python shell:
```python
from memories.views import generate_memory_book_pdf
from django.test import RequestFactory

# Create a fake request
factory = RequestFactory()
request = factory.get('/api/pdf/book/')

# Try to generate PDF
response = generate_memory_book_pdf(request)
print(f"Status: {response.status_code}")
print(f"Content-Type: {response.get('Content-Type')}")

# If it's an error (status 500), print the error:
if response.status_code == 500:
    print(response.content.decode())
```

## Verification Checklist

- [ ] All system libraries installed (libpango, libcairo, etc.)
- [ ] `test_weasyprint.py` runs successfully
- [ ] Updated service file in `/etc/systemd/system/`
- [ ] Systemd daemon reloaded
- [ ] Service restarted successfully
- [ ] Service status shows "active (running)"
- [ ] Socket file exists with correct permissions
- [ ] `/api/health_check/` returns 200 OK
- [ ] `/api/pdf/book/` returns 200 OK (not 502)
- [ ] Downloaded PDF opens correctly

## Success Indicators

✓ `curl -I http://localhost/api/pdf/book/` returns:
```
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="memory_book.pdf"
```

✓ `sudo systemctl status college-backend` shows:
```
● college-backend.service - College Backend Gunicorn daemon
     Loaded: loaded (/etc/systemd/system/college-backend.service; enabled)
     Active: active (running)
```

✓ No errors in `/var/log/gunicorn/college_error.log`

## Need More Help?

If you still encounter issues after following all steps:

1. Run the diagnostic script and share output:
   ```bash
   python test_weasyprint.py > weasyprint_test_output.txt 2>&1
   ```

2. Share the error logs:
   ```bash
   sudo journalctl -u college-backend -n 200 --no-pager > service_logs.txt
   sudo tail -n 200 /var/log/gunicorn/college_error.log > gunicorn_logs.txt
   ```

3. Check library versions:
   ```bash
   pip show weasyprint
   dpkg -l | grep -E "libpango|libcairo|libgdk"
   ```
