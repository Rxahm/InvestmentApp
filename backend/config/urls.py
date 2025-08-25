# backend/config/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app.accounts.urls')),  # Mount all account endpoints under /api/
]
