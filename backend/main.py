"""ASGI entrypoint for the Pretium Investment backend."""

from __future__ import annotations

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = get_asgi_application()
