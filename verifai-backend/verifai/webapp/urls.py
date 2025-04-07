from django.urls import path
from . import views

urlpatterns = [
    path('store-results/', views.store_results, name='store_results'),
]