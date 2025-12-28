# Gunicorn configuration file
# /var/www/college-backend/gunicorn.conf.py

import multiprocessing

# Server socket
bind = "unix:/run/gunicorn/college-backend.sock"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 300  # Increased timeout for Word/PDF generation with large datasets
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "/var/log/gunicorn/college_access.log"
errorlog = "/var/log/gunicorn/college_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "college_backend"

# Server mechanics
daemon = False
pidfile = "/var/run/gunicorn/college_backend.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# SSL (if you add HTTPS later)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
preload_app = True