from config.auth import CustomBackend
from utils.utils import logger


class CustomAttributesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Run the custom backend authentication
        user = CustomBackend().authenticate(request)
        
        request.user = user
        response = self.get_response(request)
        return response
