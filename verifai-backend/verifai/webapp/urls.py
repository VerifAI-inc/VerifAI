from django.urls import path
from .views import ReportHistoryList, UploadAPIView, PreviewModelAPIView, SubmitEvaluationView, generate_report, store_results

urlpatterns = [
    path('reports/', ReportHistoryList.as_view(), name='report-history-list'),
    path('upload/', UploadAPIView.as_view(), name='upload-api'),
    path('preview-model/', PreviewModelAPIView.as_view(), name='preview-model'),
    path('store-results/', store_results, name='store_results'),
    path('generate-report/', generate_report, name='generate_report'),
    path("submit-evaluation/", SubmitEvaluationView.as_view(), name="submit-evaluation"),
]