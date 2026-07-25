from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    if isinstance(response.data, dict):
        response.data.setdefault("status_code", response.status_code)
    else:
        response.data = {
            "detail": response.data,
            "status_code": response.status_code,
        }

    return response