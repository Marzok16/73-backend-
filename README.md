# College Backend (Django)

This is the Django backend for the college project, providing REST API endpoints for the React frontend.

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- PostgreSQL 12 or higher
- Git (optional, for version control)

### Installation

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # On Windows PowerShell
   # or
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up PostgreSQL database:
   - Follow the instructions in `POSTGRESQL_SETUP.md`
   - Create database and user as specified
   - Update the `.env` file with your database credentials

5. Copy environment template:
   ```bash
   # Make sure you have a .env file with database settings
   # See .env file for required variables
   ```

6. Run database migrations:
   ```bash
   python manage.py migrate
   ```

7. Create a superuser (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

8. Start the development server:
   ```bash
   python manage.py runserver
   ```

The backend will be available at `http://127.0.0.1:8000/`

## API Endpoints

- `GET /api/health/` - Health check endpoint
- `GET /api/hello/` - Test endpoint that returns a greeting message
- `GET /admin/` - Django admin interface

## Frontend Integration

The backend is configured with CORS headers to allow requests from the React frontend running on:
- `http://localhost:5173` (Vite default)
- `http://localhost:3000` (Create React App default)

## Project Structure

```
backend/
├── college_backend/        # Main Django project directory
│   ├── __init__.py
│   ├── settings.py        # Django settings
│   ├── urls.py           # Main URL configuration
│   ├── wsgi.py           # WSGI configuration
│   └── asgi.py           # ASGI configuration
├── api/                  # API app
│   ├── __init__.py
│   ├── views.py          # API views
│   ├── urls.py           # API URL configuration
│   ├── models.py         # Database models
│   ├── admin.py          # Admin configuration
│   └── apps.py           # App configuration
├── venv/                 # Virtual environment
├── manage.py             # Django management script
└── requirements.txt      # Python dependencies
```

## Development

To add new API endpoints:
1. Create views in `api/views.py`
2. Add URL patterns in `api/urls.py`
3. Test the endpoints using tools like Postman or curl

## Database

The project uses PostgreSQL for the database. See `POSTGRESQL_SETUP.md` for detailed setup instructions.

### Key Database Features:
- PostgreSQL with psycopg2 adapter
- Environment-based configuration
- Secure credential management with .env files
- Support for development and production environments