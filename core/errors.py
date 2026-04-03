from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        error_code = getattr(exc, 'default_code', 'error')
        error_code = error_code.upper() if isinstance(error_code, str) else 'ERROR'
        
        message = str(exc.detail) if hasattr(exc, 'detail') else str(exc)
        if isinstance(message, dict):
            message = str(message)
            
        response.data = {
            'error': {
                'code': error_code,
                'message': message,
                'details': []
            }
        }
    return response


class APIException(Exception):
    def __init__(self, code, message, details=None, status_code=status.HTTP_400_BAD_REQUEST):
        self.code = code
        self.message = message
        self.details = details or []
        self.status_code = status_code
        super().__init__(message)
