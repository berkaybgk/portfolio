"""
URL configuration for portfolio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import render

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls')),
    path('', include('fusion.urls')),
    path('', include('eq_dashboard.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page=''), name='logout'),
]


def custom_error_view(request, error_code, error_message, error_description):
    return render(request, 'error.html', {
        'error_code': error_code,
        'error_message': error_message,
        'error_description': error_description,
    })

# Specific error views
def custom_404_view(request, exception):
    return custom_error_view(request, 404, "Page Not Found", "The page you were looking for doesn't exist.")

def custom_500_view(request):
    return custom_error_view(request, 500, "Server Error", "Something went wrong on our end. Please try again later.")

def custom_403_view(request, exception):
    return custom_error_view(request, 403, "Forbidden", "You don't have permission to access this page.")

def custom_400_view(request, exception):
    return custom_error_view(request, 400, "Bad Request", "The server could not process your request.")

def custom_502_view(request):
    return custom_error_view(request, 502, "Bad Gateway", "The server received an invalid response from an upstream server.")

handler404 = 'portfolio.urls.custom_404_view'
handler500 = 'portfolio.urls.custom_500_view'
handler403 = 'portfolio.urls.custom_403_view'
handler400 = 'portfolio.urls.custom_400_view'
handler502 = 'portfolio.urls.custom_502_view'
