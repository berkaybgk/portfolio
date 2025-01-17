from rest_framework.views import APIView, View
import os
from django.conf import settings
from django.http import Http404
from .misc.parse_ds_project_info import parse_ds_project_info
from .misc.parse_analysis_content import parse_analysis_content
from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy


class HomeView(APIView):
    def get(self, request, format=None):
        data = {'page_title': 'Home'}
        return render(request, 'website/index.html', data)

class IndexView(APIView):
    def get(self, request, format=None):
        data = {'page_title': 'Index'}
        return render(request, 'website/index.html', data)

class DSProjectsView(APIView):
    def get(self, request, format=None):
        data = {'page_title': 'DS Projects'}
        return render(request, 'website/ds_projects.html', data)

class ChatbotAppView(APIView):
    def get(self, request, format=None):
        data = {'page_title': 'Fusion'}
        return render(request, 'website/fusion.html', data)

class ContactView(APIView):
    def get(self, request, format=None):
        data = {'page_title': 'Contact'}
        return render(request, 'website/contact.html', data)

class ProjectDetailView(APIView):
    def get(self, request, project_name, format=None):

        project_folder_path = os.path.join(settings.BASE_DIR, '..')
        project_folder_path = os.path.join(project_folder_path, project_name)

        try:
            if not os.path.isdir(project_folder_path):
                raise Http404("Project not found")

            readme_file_path = os.path.join(project_folder_path, 'readme.md')

            if not os.path.isfile(readme_file_path):
                raise Http404("Readme file not found for this project")

        except Http404 as e:
            return render(request, 'error.html', {
                'error_code': 404,
                'error_message': str(e),
                'error_description': 'The requested resource was not found.',
            })

        project_name, project_description, url = parse_ds_project_info(readme_file_path)
        eda, main, eval_content = parse_analysis_content(project_folder_path)

        # Prepare context to send to the template
        context = {
            'project_name': project_name,
            'project_description': project_description,
            'url': url,
            'eda': eda,
            'main': main,
            'eval': eval_content
        }

        return render(request, 'website/project_detail.html', context)


class RegisterView(View):
    template_name = 'registration/register.html'

    def get(self, request):
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')

        return render(request, self.template_name, {'form': form})
