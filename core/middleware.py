import time
from django.http import JsonResponse


RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60


def rate_limit_middleware(get_response):
    def middleware(request):
        return get_response(request)
    return middleware
