from config.auth import CustomBackend

class CustomAttributesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Run the custom backend authentication
        user = CustomBackend().authenticate(request)
        
        # Set the user on the request object
        request.user = user

        response = self.get_response(request)
        return response
