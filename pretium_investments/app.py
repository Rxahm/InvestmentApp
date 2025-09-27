"""Bridge module exposing the Django WSGI application to gunicorn."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure the Django project is on the import path when invoked from the repo root.
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
