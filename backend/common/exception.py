from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    default_data = response.data
    message = default_data.get("detail")
    error = (
        default_data.get("error") or default_data
        if not default_data.get("detail")
        else ""
    )
    data = {"status": "error", "message": message, "error": error}
    response.data = data
    return response
