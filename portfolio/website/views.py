from rest_framework.views import APIView
from django.shortcuts import render

class HomeView(APIView):
    def get(self, request, format=None):
        data = {'page_title': 'Home'}
        return render(request, 'website/index.html', data)

class IndexView(APIView):
    def get(self, request, format=None):
        data = {'page_title': 'Index'}
        return render(request, 'website/index.html', data)