from django.urls import path
from .views import ReportHistoryList
# from .views import ProfileView
from . import views

urlpatterns = [
    path('api/reports/', ReportHistoryList.as_view(), name='report-history-list'),
    # path('', ProfileView.as_view(), name='profile'),  # <-- Add this line to load profile at root
    path('store-results/', views.store_results, name='store_results'),
]
