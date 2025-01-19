from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
import json

from .models import Chat
from .rag.main import handle_pdf_upload
from .rag.vector_db_utils import VectorDbUtils


class FusionView(LoginRequiredMixin, View):
    template_name = 'fusion/fusion_home.html'
    login_url = '/login/'

    def get(self, request):
        vdb = VectorDbUtils()
        uploaded_pdfs_by_user = vdb.get_users_pdfs(request.user.username)
        return render(request, self.template_name, {
            'uploaded_pdfs': uploaded_pdfs_by_user
        })

    def post(self, request):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            action = request.POST.get('action')

            if action == 'upload_pdf':
                try:
                    # Get the file from request.FILES
                    pdf_file = request.FILES.get('pdf-file')
                    if pdf_file is None:
                        return JsonResponse({
                            'success': False,
                            'error': 'No file was uploaded'
                        })

                    # Get other form data
                    pdf_name = request.POST.get('pdf-name')
                    if not pdf_name:
                        return JsonResponse({
                            'success': False,
                            'error': 'PDF name is required'
                        })

                    pdf_description = request.POST.get('pdf-description')
                    if not pdf_description:
                        return JsonResponse({
                            'success': False,
                            'error': 'PDF description is required'
                        })

                    username = request.user.username

                    # Validate file type
                    if not pdf_file.name.endswith('.pdf'):
                        return JsonResponse({
                            'success': False,
                            'error': 'File must be a PDF'
                        })

                    # Create a temporary file
                    from tempfile import NamedTemporaryFile
                    import shutil

                    with NamedTemporaryFile(delete=False) as tmp_file:
                        for chunk in pdf_file.chunks():
                            tmp_file.write(chunk)
                        tmp_file_path = tmp_file.name

                    try:
                        # Call PDF handling function
                        upload_success = handle_pdf_upload(
                            username=username,
                            pdf_name=pdf_name,
                            pdf_description=pdf_description,
                            pdf_file=tmp_file_path
                        )

                        if not upload_success:
                            return JsonResponse({
                                'success': False,
                                'error': 'A PDF with this name already exists'
                            })

                        return JsonResponse({
                            'success': True,
                            'data': {
                                'pdf_name': pdf_name,
                            }
                        })

                    finally:
                        # Clean up the temporary file
                        import os
                        if os.path.exists(tmp_file_path):
                            os.unlink(tmp_file_path)

                except Exception as e:
                    import traceback
                    print("Error:", str(e))
                    print("Traceback:", traceback.format_exc())
                    return JsonResponse({
                        'success': False,
                        'error': str(e)
                    })

            elif action == 'send_message':
                try:
                    message = request.POST.get('message')

                    if not message:
                        return JsonResponse({
                            'success': False,
                            'error': 'Message cannot be empty'
                        })

                    # Save the message to the database
                    chat = Chat.objects.create(
                        user=request.user,
                        message=message,
                        timestamp=datetime.now(),
                        response='This is a placeholder response'
                    )
                    print(message)

                    return JsonResponse({
                        'success': True,
                        'data': {
                            'response': chat.response,
                            'timestamp': chat.timestamp.isoformat()
                        }
                    })

                except Exception as e:
                    return JsonResponse({
                        'success': False,
                        'error': str(e)
                    })

            return JsonResponse({
                'success': False,
                'error': 'Invalid action specified'
            })

        # If not an AJAX request, render the template
        # TODO
        vdb = VectorDbUtils()
        uploaded_pdfs_by_user = vdb.get_users_pdfs(request.user.username)
        return render(request, self.template_name, {
            'uploaded_pdfs': uploaded_pdfs_by_user
        })

class DeletePDFView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            # Parse the JSON data from request body
            data = json.loads(request.body)
            pdf_name = data.get('pdf_name')

            if not pdf_name:
                return JsonResponse({
                    'success': False,
                    'error': 'PDF name is required'
                })

            try:

                vector_db = VectorDbUtils()
                vector_db.delete_collection(pdf_name, request.user.username)

                return JsonResponse({
                    'success': True,
                    'message': f'Successfully deleted {pdf_name}'
                })

            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Error deleting from vector database: {str(e)}'
                })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            })


def get_messages(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        messages = Chat.objects.filter(user=request.user).order_by('timestamp')

        message_list = []

        # Create two entries for each Chat object
        for msg in messages:
            # Add user message
            message_list.append({
                'type': 'user',
                'content': msg.message,
                'timestamp': msg.timestamp.isoformat()
            })
            # Add bot response
            message_list.append({
                'type': 'bot',
                'content': msg.response,
                'timestamp': msg.timestamp.isoformat()
            })

        return JsonResponse({
            'success': True,
            'messages': message_list
        })
    return JsonResponse({'success': False, 'error': 'Invalid request'})
