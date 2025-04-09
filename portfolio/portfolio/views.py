from django.shortcuts import render

def handler404(request, exception):
    return render(request, 'errors/error.html', {
        'error_code': '404',
        'error_message': 'Page Not Found',
        'error_description': 'The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.'
    }, status=404)

def handler500(request):
    return render(request, 'errors/error.html', {
        'error_code': '500',
        'error_message': 'Server Error',
        'error_description': 'Something went wrong on our end. Please try again later.'
    }, status=500)

def handler403(request, exception):
    return render(request, 'errors/error.html', {
        'error_code': '403',
        'error_message': 'Access Denied',
        'error_description': 'You do not have permission to access this page.'
    }, status=403)

def csrf_failure(request, reason=""):
    return render(request, 'errors/error.html', {
        'error_code': '403',
        'error_message': 'CSRF Verification Failed',
        'error_description': 'For security reasons, we could not verify your request. Please try again from a new tab.'
    }, status=403)

def handler400(request, exception):
    return render(request, 'errors/error.html', {
        'error_code': '400',
        'error_message': 'Bad Request',
        'error_description': 'The request could not be processed. Please try again.'
    }, status=400)

def handler405(request, exception):
    return render(request, 'errors/error.html', {
        'error_code': '405',
        'error_message': 'Method Not Allowed',
        'error_description': 'The method is not allowed for the requested URL.'
    }, status=405)
