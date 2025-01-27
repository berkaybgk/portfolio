from django.urls import path, include
from .views import EarthquakeDashboardView, EarthquakeDataAPI

urlpatterns = [
    path('eq-dashboard/', EarthquakeDashboardView.as_view(), name='eq_dashboard'),
    path('eq-dashboard/api/data/', EarthquakeDataAPI.as_view(), name='eq_dashboard'),
]
