# Deployment Guide - دفعة 1973 Backend

## Deploying Backend to Render (Recommended - Free Tier Available)

### Step 1: Prepare Your Repository
1. Push your backend code to a GitHub repository
2. Make sure `Procfile`, `requirements.txt`, and `runtime.txt` are in the root of backend folder

### Step 2: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"

### Step 3: Connect Repository
1. Connect your GitHub repository
2. Select the repository

### Step 4: Configure Service
- **Name**: `college-backend-73` (or any name)
- **Environment**: `Python 3`
- **Build Command**: `cd backend && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput`
- **Start Command**: `cd backend && gunicorn college_backend.wsgi:application`

### Step 5: Environment Variables
Add these in Render dashboard → Environment:

```
SECRET_KEY=your-secret-key-here (generate a strong random key)
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host (from Render PostgreSQL service)
DB_PORT=5432
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
CORS_ALLOW_ALL_ORIGINS=False
```

### Step 6: Database Setup
1. In Render, create a PostgreSQL database:
   - Click "New +" → "PostgreSQL"
   - Copy the connection details
   - Use them in Environment Variables

### Step 7: Deploy
- Click "Create Web Service"
- Wait for deployment
- Get your backend URL: `https://your-app.onrender.com`

## Deploying Backend to Railway (Alternative)

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Add PostgreSQL service
5. Set environment variables
6. Deploy

## After Deployment

1. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

2. Update frontend API URL:
   - In Vercel, add environment variable: `VITE_API_BASE_URL=https://your-backend-url.onrender.com/api`

3. Test the API:
   - Visit: `https://your-backend-url.onrender.com/api/health/`

