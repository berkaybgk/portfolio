from django.urls import path, include
from .views import HomeView, IndexView, DSProjectsView, ContactView, ProjectDetailView, RegisterView, GoogleDocsConverterView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),                         # Home Page
    path('home/', HomeView.as_view(), name='home'),                      # Home Page
    path('projects/', DSProjectsView.as_view(), name='ds_projects'),  # Data Science Projects
    path('contact/', ContactView.as_view(), name='contact'),             # Contact Page
    path('projects/<str:project_name>/', ProjectDetailView.as_view(), name='project_detail'),
    path('register/', RegisterView.as_view(), name='register'),
    path('gdoc-converter/', GoogleDocsConverterView.as_view(), name='gdoc_converter'),
    path('', include('django.contrib.auth.urls')),  # This includes login, logout, etc.
]