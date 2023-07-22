from corsheaders.signals import check_request_enabled
from rest_framework.permissions import SAFE_METHODS
from django.conf import settings


def cors_allow_api_to_everyone(sender, request, **kwargs):
    return (request.path in settings.EXTERNAL_API_PATHS) and (
        request.method in SAFE_METHODS
    )


check_request_enabled.connect(cors_allow_api_to_everyone)
