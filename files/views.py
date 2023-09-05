
from concurrent.futures import ThreadPoolExecutor
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _


from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.decorators import api_view

from properties.models import Property
from properties.utils import imageWorker



from .models import Files
from .serializers import FilesSerializer

from utils.utils import customResponse, logger


class FilesCreateListView(generics.GenericAPIView):
    serializer_class = FilesSerializer
    # permission_classes = [IsAuthenticated, ]
    
    def post(self, request, id):
        try:
            property = Property.objects.get(id=id)
            try:
                with ThreadPoolExecutor(max_workers=3) as executor:
                    executor.submit(imageWorker, request, property)
                return customResponse(
                    message=f"Photos Added Successfully.",
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response({"detail": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Property.DoesNotExist:
            return customResponse(message = _("Property does not exist"), status=401 )

    # @method_decorator(group_required('REALTOR'))
    def get(self, request):
        image_obj = Files.objects.all()
        count = image_obj.count()
        serializer = self.serializer_class(image_obj, many=True, context={'request': request})
        return customResponse(payload=serializer.data, status=status.HTTP_200_OK, count=count)
    
    

class FileDetailsView(generics.GenericAPIView):
    serializer_class = FilesSerializer

    def get_object(self, request, id):
        return Files.objects.get(id=id)

    def delete(self, request, id):
        try:
            image = self.get_object(request=request, id=id)
            image.delete()
            return customResponse(message=_("Image Removed successfully"), status=status.HTTP_200_OK)
        except Files.DoesNotExist:
            error = {'detail': _("Image Not Found")}
            return Response(error, status.HTTP_404_NOT_FOUND)
        
