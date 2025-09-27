# Backend API

Django REST API powering the Pretium Investment portal. The service exposes
JWT-based authentication and two-factor enrolment endpoints that the React
frontend consumes.

## Features

- Django 5 + Django REST Framework stack with a custom user model
- JWT authentication via `djangorestframework-simplejwt`
- Optional time-based one-time password (TOTP) two-factor authentication
- `/healthz` endpoint suitable for platform health checks
- CORS configuration driven by environment variables for frontend integration

## Requirements

- Python 3.11+
- pipenv/virtualenv for dependency isolation (recommended)

Install dependencies:

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
```

Update `.env` with your secrets and database connection URL. The default uses a
SQLite database stored in `backend/db.sqlite3` for local development.

## Running locally

```bash
python manage.py migrate
python manage.py createsuperuser  # optional, for /admin
python manage.py runserver
```

The API will be available at <http://127.0.0.1:8000/>. Auth endpoints are under
`/api/` and Django admin under `/admin/`.

## Deployment

Set the following environment variables in production:

- `SECRET_KEY`
- `DEBUG` (usually `False`)
- `DATABASE_URL`
- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`

The provided `Procfile` starts the ASGI application with gunicorn:

```
web: gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker --workers 2 --timeout 120 --bind 0.0.0.0:$PORT
```

Most platforms (Render, Railway, Fly.io, etc.) populate `PORT` automatically.
Make sure static files are collected and a persistent database is configured
before deploying.
