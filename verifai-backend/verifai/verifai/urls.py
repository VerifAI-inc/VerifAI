# verifai/urls.py
from django.contrib import admin
from django.urls import path, include
from webapp.views import ReportHistoryList
from rest_framework.authtoken.views import obtain_auth_token
from webapp.views import UploadAPIView, PreviewModelAPIView
from auth_app.views import UserProfileAPIView

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin interface at /admin
    path('api/reports/', ReportHistoryList.as_view(), name='report-history'),  # API for reports
    path('auth/', include('auth_app.urls')),
    path('api/user/profile/', UserProfileAPIView.as_view(), name='user-profile'),

    path('api/', include('webapp.urls')),  # Include webapp urls here

    # Upload
    path('api/upload/', UploadAPIView.as_view(), name='upload-api'),
    path('api/preview-model/', PreviewModelAPIView.as_view(), name='preview-model'),
    path('api-token-auth/', obtain_auth_token),
]
