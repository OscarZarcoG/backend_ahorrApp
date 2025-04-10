# ahorraAPP_API/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect
from django.conf import settings


def redirect_to_frontend(request):
    return HttpResponseRedirect("http://192.168.1.74:3000/dashboard/")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('view-site/', redirect_to_frontend, name='view-site'),
    path('api/user/', include('userAPI.urls')),
    path('api/finanzas/', include('finanzasAPI.urls')),
    #path('api/ml-suggestions/', include('ml_suggestions.urls')),
]

