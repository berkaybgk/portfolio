from django.urls import path, include
from .views import FusionView, DeletePDFView

urlpatterns = [
    path('fusion/', FusionView.as_view(), name='fusion'),
    path('delete-pdf/', DeletePDFView.as_view(), name='delete_pdf'),
]