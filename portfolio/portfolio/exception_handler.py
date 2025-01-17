from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.http import Http404

def custom_exception_handler(exc, context):
    # Handle Http404 error specifically
    if isinstance(exc, Http404):
        return Response({
            'detail': 'The requested resource was not found.',
            'error_code': '404',
            'error_message': str(exc),
        }, status=404)

    # Call the default exception handler
    response = exception_handler(exc, context)
    return response
