# verifai/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', lambda request: HttpResponse("VerifAI backend is running.")), 
    path('admin/', admin.site.urls),  # Admin interface at /admin
    path('api/auth/', include('auth_app.urls')),
    path('api/', include('webapp.urls')),  # Include webapp urls here
    path('api-token-auth/', obtain_auth_token),
]
