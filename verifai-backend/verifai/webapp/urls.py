from django.urls import path
from .views import ReportHistoryList, UploadAPIView, PreviewModelAPIView
from . import views

urlpatterns = [
    path('reports/', ReportHistoryList.as_view(), name='report-history-list'),
    path('upload/', UploadAPIView.as_view(), name='upload-api'),
    path('preview-model/', PreviewModelAPIView.as_view(), name='preview-model'),
    path('store-results/', views.store_results, name='store_results'),
]