from rest_framework import status
from django.http import JsonResponse


def not_found(request, exception, *args, **kwargs):
    """Generic 404 error handler"""
    data = {
        "status": "error",
        "message": "The requested endpoint was not found on the server",
        "error": "",
    }
    return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)


def server(request, *args, **kwargs):
    """500 error handler"""
    data = {"status": "error", "message": "Server error", "error": ""}
    return JsonResponse(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
