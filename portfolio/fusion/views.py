import os
from datetime import datetime, timezone

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
import json

from .models import Chat
# from .rag.main import handle_pdf_upload
# from .rag.vector_db_utils import VectorDbUtils
from .rag.main import handle_message
from django.conf import settings


class FusionView(LoginRequiredMixin, View):
    template_name = 'fusion/fusion_home.html'
    login_url = '/login/'

    # def get_real(self, request):
    #     vdb = VectorDbUtils()
    #     uploaded_pdfs_by_user = vdb.get_users_pdfs(request.user.username)
    #     return render(request, self.template_name, {
    #         'uploaded_pdfs': uploaded_pdfs_by_user
    #     })

    def get(self, request):
        dummy_pdfs = [
            "dummy_pdf_1",
            "dummy_pdf_2",
            "dummy_pdf_3",
        ]

        return render(request, self.template_name, {
            'uploaded_pdfs': dummy_pdfs
        })


    def post(self, request):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            action = request.POST.get('action')

            if action == 'upload_pdf':
                # TODO: more than 1.2MB causes crash, need to fix
                try:
                    # Get the file from request.FILES
                    pdf_file = request.FILES.get('pdf-file')
                    if pdf_file is None:
                        return JsonResponse({
                            'success': False,
                            'error': 'No file was uploaded'
                        })

                    # Add size validation (0.5), also to the nginx config
                    if pdf_file.size > 0.5 * 1024 * 1024:
                        return JsonResponse({
                            'success': False,
                            'error': 'File size must be under 0.5MB for now.'
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

                    # Save directly to persist directory
                    persist_dir = os.path.join(settings.BASE_DIR, 'persist', 'pdfs')
                    os.makedirs(persist_dir, exist_ok=True)

                    pdf_path = os.path.join(persist_dir, f"{pdf_name}_{username}.pdf")

                    with open(pdf_path, 'wb') as destination:
                        destination.write(pdf_file.read())

                    try:
                        # # Call PDF handling function
                        # upload_success = handle_pdf_upload(
                        #     username=username,
                        #     pdf_name=pdf_name,
                        #     pdf_description=pdf_description,
                        #     pdf_path=pdf_path
                        # )
                        #
                        # if not upload_success:
                        #     if os.path.exists(pdf_path):
                        #         os.unlink(pdf_path)
                        #     return JsonResponse({
                        #         'success': False,
                        #         'error': 'A PDF with this name already exists'
                        #     })

                        return JsonResponse({
                            'success': True,
                            'data': {
                                'pdf_name': pdf_name,
                            }
                        })

                    finally:
                        # Clean up the file after handle_pdf_upload is done
                        if os.path.exists(pdf_path):
                            os.unlink(pdf_path)

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

                    # Add a delay for 3 seconds if the users last message is within 2 seconds
                    last_message = Chat.objects.filter(user=request.user).order_by('-timestamp').first()

                    if last_message:
                        current_time = datetime.now(timezone.utc)  # Get current time in UTC

                        time_since_last = current_time - last_message.timestamp
                        if time_since_last.total_seconds() < 3:
                            return JsonResponse({
                                'success': False,
                                'error': 'Please wait 2 seconds between messages',
                            })

                    # Save the message to the database
                    chat = Chat.objects.create(
                        user=request.user,
                        message=message,
                        timestamp=datetime.now(),
                        response=handle_message(request.user, message)
                    )

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

                # vector_db = VectorDbUtils()
                # vector_db.delete_collection(pdf_name, request.user.username)

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


@login_required
def get_messages(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':

        # Check if user is authenticated
        if not request.user.is_authenticated:
            raise PermissionDenied

        # Return permission denied if the user in the request is not the same as the logged in user
        if request.user.username != request.GET.get('user'):
            raise PermissionDenied

        # Get the last 100 messages and reverse them
        messages = Chat.objects.filter(user=request.user).order_by('timestamp')[:100]

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


class UserPDFContentsView(LoginRequiredMixin, View):
    # def get_real(self, request, *args, **kwargs):
    #
    #     vdb = VectorDbUtils()
    #
    #     # Get the pdfs of the user
    #     user_pdfs = vdb.get_chunks_of_user(request.user.username)
    #
    #     return JsonResponse({
    #         'success': True,
    #         'data': user_pdfs
    #     })

    def get(self, request, *args, **kwargs):
        user_pdfs = {
            "pdf1": [
                {
                    "id": "1",
                    "content": "This is a test content for pdf1"
                },
                {
                    "id": "2",
                    "content": "This is another test content for pdf1"
                }
            ],
            "pdf2": [
                {
                    "id": "1",
                    "content": "This is a test content for pdf2"
                },
                {
                    "id": "2",
                    "content": "This is another test content for pdf2"
                }
            ]
        }

        return JsonResponse({
            'success': True,
            'data': user_pdfs
        })