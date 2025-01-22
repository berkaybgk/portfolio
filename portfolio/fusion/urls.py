from django.urls import path, include
from .views import FusionView, DeletePDFView, get_messages, UserPDFContentsView

urlpatterns = [
    path('fusion/', FusionView.as_view(), name='fusion'),
    path('delete-pdf/', DeletePDFView.as_view(), name='delete_pdf'),
    path('get-messages/', get_messages, name='get_messages'),
    path('get-user-content/', UserPDFContentsView.as_view(), name='get_user_content'),
]