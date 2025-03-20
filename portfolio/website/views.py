from rest_framework.views import APIView, View
import os
from django.conf import settings
from django.http import Http404
from .misc.parse_ds_project_info import parse_ds_project_info
from .misc.parse_analysis_content import parse_analysis_content
from .misc.make_it_list import process_markdown
from django.shortcuts import render, redirect
import re

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy


class HomeView(APIView):
    def get(self, request, format=None):
        data = {'page_title': 'Home'}
        return render(request, 'website/index.html', data)

class GoogleDocsConverterView(APIView):
    def get(self, request, format=None):
        return render(request, 'website/gdoc_converter.html')
    
    def post(self, request, format=None):
        try:
            input_text = request.POST.get('input_text')
            
            # Validate input
            if not input_text:
                raise ValueError('Please provide some text to convert')

            glossary_part = input_text.split("==Don’t delete this, useful when parsing==")[1]
            
            # Fix markdown numbering
            markdown_content = self._fix_markdown_numbering(input_text)

            # Convert markdown format
            markdown_content = self._reformat_markdown_enumeration(markdown_content)

            markdown_content = markdown_content.replace("==Don’t delete this, useful when parsing==", "----")

            markdown_content = process_markdown(markdown_content)

            markdown_content = markdown_content + "\n\n----" + "\n" + glossary_part
            
            return render(request, 'website/gdoc_converter.html', {
                'markdown_content': markdown_content
            })
            
        except Exception as e:
            return render(request, 'website/gdoc_converter.html', {
                'error': str(e)
            })

    def _reformat_markdown_enumeration(self, markdown_text):
        """
        Reformat markdown enumeration from the format:
            1. Top Level
                1. Second Level
                    1. Third Level
        
        To the format:
            1. Top Level
                1.1. Second Level
                    1.1.1. Third Level
        
        Args:
            markdown_text (str): The markdown text to reformat
            
        Returns:
            str: Reformatted markdown text
        """
        # Split the text into lines
        lines = markdown_text.split('\n')
        
        # Track the current numbering at each level
        current_numbers = []
        
        # Store the reformatted lines
        reformatted_lines = []
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                reformatted_lines.append(line)
                continue
            
            # Determine the indentation level (number of spaces)
            leading_spaces = len(line) - len(line.lstrip())
            
            # Use integer division to determine the level (4 spaces per level)
            level = leading_spaces // 4
            
            # Extract the actual content of the line
            line_content = line.strip()
            
            # Check if the line starts with a number and period (markdown enumeration)
            enum_match = re.match(r'(\d+)\.\s+(.*)', line_content)
            
            if enum_match:
                # It's an enumerated item
                number = int(enum_match.group(1))
                content = enum_match.group(2)
                
                # Update the current_numbers list based on the level
                if level >= len(current_numbers):
                    # Add new level
                    current_numbers.append(number)
                else:
                    # Adjust current_numbers to the current level
                    current_numbers = current_numbers[:level]
                    current_numbers.append(number)
                
                # Build the new enumeration format
                new_enum = '.'.join(str(num) for num in current_numbers)
                
                # Construct the reformatted line
                spaces = ' ' * (4 * level)
                reformatted_line = f"{spaces}- {new_enum}. {content}" 
                reformatted_lines.append(reformatted_line)
            else:
                # Not an enumerated item, keep as is
                reformatted_lines.append(line)
        
        # Join the lines back together
        return '\n'.join(reformatted_lines)

    
    def _fix_markdown_numbering(self, content):
        # First, clean HTML comments
        lines = content.split('\n')
        cleaned_lines = []
        in_comment = False
        
        for line in lines:
            # Check for comment start
            if '<!-----' in line:
                in_comment = True
                continue
            # Check for comment end
            elif '----->' in line:
                in_comment = False
                continue
            # Skip lines while in comment block
            elif not in_comment:
                cleaned_lines.append(line)
        
        # Process the cleaned content for markdown numbering
        result = []
        counters = {}
        current_indent = 0
        found_requirements = False
        
        for line in cleaned_lines:
            if not line.strip():
                result.append(line)
                continue

            # Check for Requirements Specification in bold format
            if not found_requirements and '***Requirements Specification***' in line:
                result.append('# Requirements Specification')
                found_requirements = True
                continue

            # Calculate indentation level
            indent = len(line) - len(line.lstrip())
            text = line.lstrip()
            
            # Check if this is a numbered list item
            if re.match(r'^\d+\.\s+', text):
                # Extract the content after the number
                content = re.sub(r'^\d+\.\s+', '', text)
                
                # Reset counters for deeper levels when indent changes
                if indent > current_indent:
                    current_indent = indent
                elif indent < current_indent:
                    # Clear counters for all deeper levels
                    counters = {k: v for k, v in counters.items() if k <= indent}
                    current_indent = indent
                
                # Initialize or increment counter for this level
                if indent not in counters:
                    counters[indent] = 1
                else:
                    counters[indent] += 1
                
                # Create the line with correct numbering
                spaces = ' ' * indent
                result.append(f'{spaces}{counters[indent]}. {content}')
            else:
                result.append(line)
        
        return '\n'.join(result)

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
        project_endpoint = project_name

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
            'project_endpoint': project_endpoint,
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
