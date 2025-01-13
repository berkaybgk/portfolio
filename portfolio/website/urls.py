from django.urls import path
from .views import HomeView, IndexView, ChatbotAppView, DSProjectsView, ContactView, ProjectDetailView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),                         # Home Page
    path('home/', HomeView.as_view(), name='home'),                      # Home Page
    path('projects/', DSProjectsView.as_view(), name='ds_projects'),  # Data Science Projects
    path('fusion/', ChatbotAppView.as_view(), name='fusion'),            # Chatbot App
    path('contact/', ContactView.as_view(), name='contact'),             # Contact Page
    path('projects/<str:project_name>/', ProjectDetailView.as_view(), name='project_detail'),
]