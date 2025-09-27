"""URL configuration for the Pretium Investment backend."""

from __future__ import annotations

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def healthcheck(_request):
    """Simple health endpoint used by deployment platforms."""
    return JsonResponse({"status": "ok"})


def index(_request):
    """Default root endpoint to confirm the API is online."""
    return JsonResponse({
        "status": "ok",
        "service": "Pretium Investment API",
    })


urlpatterns = [
    path("", index, name="index"),
    path("healthz/", healthcheck, name="healthz"),
    path("admin/", admin.site.urls),
    path("api/", include("app.accounts.urls")),
]
