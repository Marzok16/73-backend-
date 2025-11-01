#!/bin/bash
# Build script for Render/Railway deployment
python manage.py collectstatic --noinput
python manage.py migrate --noinput

