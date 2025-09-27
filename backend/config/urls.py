"""URL configuration for the Pretium Investment backend."""

from __future__ import annotations

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def healthcheck(_request):
    """Simple health endpoint used by deployment platforms."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("app.accounts.urls")),
    path("healthz/", healthcheck, name="healthz"),
]
