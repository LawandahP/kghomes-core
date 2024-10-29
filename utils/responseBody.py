from rest_framework.response import Response
from rest_framework.views import exception_handler

class ResponseBody:
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            "status": "success",
            "message": "Data retrieved successfully",
            "data": response.data,
            "status_code": response.status_code
        }, status=response.status_code)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({
            "status": "success",
            "message": "Data retrieved successfully",
            "data": response.data,
            "status_code": response.status_code
        }, status=response.status_code)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "status": "success",
            "message": "Data created successfully",
            "data": response.data,
            "status_code": response.status_code
        }, status=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "status": "success",
            "message": "Data updated successfully",
            "data": response.data,
            "status_code": response.status_code
        }, status=response.status_code)

    # def destroy(self, request, *args, **kwargs):
    #     response = super().destroy(request, *args, **kwargs)
    #     return Response({
    #         "status": "success",
    #         "message": "Data deleted successfully",
    #         "data": [],
    #         "status_code": response.status_code
    #     }, status=response.status_code)

    def handle_exception(self, exc):
        response = exception_handler(exc, self.get_exception_handler_context())
        if response is not None:
            response.data = {
                "status": "error",
                "message": str(exc),
                "detail": response.data,
                "status_code": response.status_code
            }
        return response