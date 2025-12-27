#!/bin/bash

# ===========================================
# KFUPM73 Deployment Script
# ===========================================
# Usage:
#   ./deploy.sh frontend-prepare  - Prepare frontend for WinSCP upload
#   ./deploy.sh frontend-finish   - Finish frontend deployment (after WinSCP)
#   ./deploy.sh backend           - Deploy backend changes
#   ./deploy.sh all               - Full deployment (backend + frontend prepare)
# ===========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_DEPLOY_PATH="/var/www/college-frontend"
BACKEND_DEPLOY_PATH="/var/www/college-backend"
BACKEND_SOURCE_PATH="$HOME/college/73-backend-"
WEB_USER="www-data"
CURRENT_USER=$(whoami)

# Functions
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Frontend: Prepare for WinSCP upload
frontend_prepare() {
    echo ""
    echo "=========================================="
    echo "  Preparing Frontend for WinSCP Upload"
    echo "=========================================="
    echo ""
    
    # Remove old files
    print_status "Removing old frontend files..."
    sudo rm -rf ${FRONTEND_DEPLOY_PATH}/*
    
    # Change ownership to current user for WinSCP upload
    print_status "Setting permissions for upload..."
    sudo chown -R ${CURRENT_USER}:${CURRENT_USER} ${FRONTEND_DEPLOY_PATH}/
    
    echo ""
    print_status "Frontend ready for upload!"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Use WinSCP to upload your dist/* files to ${FRONTEND_DEPLOY_PATH}/"
    echo "  2. Run: ./deploy.sh frontend-finish"
    echo ""
}

# Frontend: Finish deployment after WinSCP upload
frontend_finish() {
    echo ""
    echo "=========================================="
    echo "  Finishing Frontend Deployment"
    echo "=========================================="
    echo ""
    
    # Restore ownership to www-data
    print_status "Restoring file ownership to ${WEB_USER}..."
    sudo chown -R ${WEB_USER}:${WEB_USER} ${FRONTEND_DEPLOY_PATH}/
    
    # Set proper permissions
    print_status "Setting file permissions..."
    sudo chmod -R 755 ${FRONTEND_DEPLOY_PATH}/
    
    # Restart nginx
    print_status "Restarting nginx..."
    sudo systemctl restart nginx
    
    # Check status
    if sudo systemctl is-active --quiet nginx; then
        print_status "Nginx is running!"
    else
        print_error "Nginx failed to start!"
        sudo systemctl status nginx
        exit 1
    fi
    
    echo ""
    print_status "Frontend deployment complete!"
    echo ""
}

# Backend deployment
backend_deploy() {
    echo ""
    echo "=========================================="
    echo "  Deploying Backend"
    echo "=========================================="
    echo ""
    
    # Check if source directory exists
    if [ ! -d "${BACKEND_SOURCE_PATH}" ]; then
        print_error "Backend source not found at ${BACKEND_SOURCE_PATH}"
        exit 1
    fi
    
    # Pull latest changes if git repo
    if [ -d "${BACKEND_SOURCE_PATH}/.git" ]; then
        print_status "Pulling latest changes from git..."
        cd ${BACKEND_SOURCE_PATH}
        git pull
    fi
    
    # Copy backend files (excluding venv, media, .env, __pycache__)
    print_status "Copying backend files..."
    
    # Copy api folder
    sudo cp -r ${BACKEND_SOURCE_PATH}/api/* ${BACKEND_DEPLOY_PATH}/api/
    
    # Copy college_backend folder
    sudo cp -r ${BACKEND_SOURCE_PATH}/college_backend/* ${BACKEND_DEPLOY_PATH}/college_backend/
    
    # Copy memories folder
    sudo cp -r ${BACKEND_SOURCE_PATH}/memories/* ${BACKEND_DEPLOY_PATH}/memories/
    
    # Copy templates folder
    sudo cp -r ${BACKEND_SOURCE_PATH}/templates/* ${BACKEND_DEPLOY_PATH}/templates/
    
    # Copy manage.py
    sudo cp ${BACKEND_SOURCE_PATH}/manage.py ${BACKEND_DEPLOY_PATH}/
    
    # Copy requirements.txt (in case of new dependencies)
    sudo cp ${BACKEND_SOURCE_PATH}/requirements.txt ${BACKEND_DEPLOY_PATH}/
    
    # Set proper ownership
    print_status "Setting file ownership..."
    sudo chown -R ${WEB_USER}:${WEB_USER} ${BACKEND_DEPLOY_PATH}/api/
    sudo chown -R ${WEB_USER}:${WEB_USER} ${BACKEND_DEPLOY_PATH}/college_backend/
    sudo chown -R ${WEB_USER}:${WEB_USER} ${BACKEND_DEPLOY_PATH}/memories/
    sudo chown -R ${WEB_USER}:${WEB_USER} ${BACKEND_DEPLOY_PATH}/templates/
    sudo chown ${WEB_USER}:${WEB_USER} ${BACKEND_DEPLOY_PATH}/manage.py
    sudo chown ${WEB_USER}:${WEB_USER} ${BACKEND_DEPLOY_PATH}/requirements.txt
    
    # Restart backend service
    print_status "Restarting college-backend service..."
    sudo systemctl restart college-backend
    
    # Wait a moment for service to start
    sleep 2
    
    # Check status
    if sudo systemctl is-active --quiet college-backend; then
        print_status "Backend service is running!"
    else
        print_error "Backend service failed to start!"
        sudo systemctl status college-backend
        exit 1
    fi
    
    echo ""
    print_status "Backend deployment complete!"
    echo ""
}

# Install new pip packages
backend_install_deps() {
    echo ""
    echo "=========================================="
    echo "  Installing Backend Dependencies"
    echo "=========================================="
    echo ""
    
    print_status "Installing pip packages..."
    sudo ${BACKEND_DEPLOY_PATH}/venv/bin/pip install -r ${BACKEND_DEPLOY_PATH}/requirements.txt
    
    print_status "Restarting backend service..."
    sudo systemctl restart college-backend
    
    echo ""
    print_status "Dependencies installed!"
    echo ""
}

# Show status
show_status() {
    echo ""
    echo "=========================================="
    echo "  Service Status"
    echo "=========================================="
    echo ""
    
    echo "--- Nginx ---"
    sudo systemctl status nginx --no-pager -l | head -10
    
    echo ""
    echo "--- College Backend ---"
    sudo systemctl status college-backend --no-pager -l | head -10
    
    echo ""
}

# Show logs
show_logs() {
    echo ""
    echo "=========================================="
    echo "  Recent Logs"
    echo "=========================================="
    echo ""
    
    echo "--- Gunicorn Error Log (last 20 lines) ---"
    sudo tail -20 /var/log/gunicorn/college_error.log
    
    echo ""
    echo "--- Gunicorn Access Log (last 10 lines) ---"
    sudo tail -10 /var/log/gunicorn/college_access.log
    
    echo ""
}

# Main
case "$1" in
    frontend-prepare|fp)
        frontend_prepare
        ;;
    frontend-finish|ff)
        frontend_finish
        ;;
    backend|b)
        backend_deploy
        ;;
    backend-deps|bd)
        backend_install_deps
        ;;
    all)
        backend_deploy
        frontend_prepare
        ;;
    status|s)
        show_status
        ;;
    logs|l)
        show_logs
        ;;
    *)
        echo ""
        echo "KFUPM73 Deployment Script"
        echo "========================="
        echo ""
        echo "Usage: ./deploy.sh [command]"
        echo ""
        echo "Commands:"
        echo "  frontend-prepare (fp)  - Clear frontend & set permissions for WinSCP upload"
        echo "  frontend-finish (ff)   - Restore permissions & restart nginx after upload"
        echo "  backend (b)            - Deploy backend from source to /var/www"
        echo "  backend-deps (bd)      - Install pip dependencies from requirements.txt"
        echo "  all                    - Deploy backend + prepare frontend"
        echo "  status (s)             - Show service status"
        echo "  logs (l)               - Show recent logs"
        echo ""
        echo "Example workflow:"
        echo "  1. ./deploy.sh frontend-prepare"
        echo "  2. Upload via WinSCP"
        echo "  3. ./deploy.sh frontend-finish"
        echo ""
        ;;
esac
