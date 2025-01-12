from django.urls import path
from .views import HomeView, IndexView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('home/', HomeView.as_view(), name='home'),
]