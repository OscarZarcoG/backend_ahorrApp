# ahorraAPP_API/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('userAPI.urls')),
    path('api/finanzas/', include('finanzasAPI.urls')),
    path('api/ml-suggestions/', include('ml_suggestions.urls')),
]