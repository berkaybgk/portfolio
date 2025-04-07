from django.urls import path
from . import views

app_name = 'watch_data'

urlpatterns = [
    path('predict-watch-price/', views.watch_feature_form, name='watch_feature_form'),
]