release: apt-get update && apt-get install -y python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info || true
web: gunicorn college_backend.wsgi:application --bind 0.0.0.0:$PORT

