from django.urls import path, include
from .views import FusionView

urlpatterns = [
    path('fusion/', FusionView.as_view(), name='fusion'),
]