
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator


from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.decorators import api_view



from .models import Files
from .serializers import FilesSerializer

from utils.utils import customResponse


class FilesCreateListView(generics.GenericAPIView):
    serializer_class = FilesSerializer
    permission_classes = [IsAuthenticated, ]
 
    # @method_decorator(group_required('REALTOR'))
    def get(self, request):
        image_obj = Files.objects.all()
        count = image_obj.count()
        serializer = self.serializer_class(image_obj, many=True, context={'request': request})
        return customResponse(payload=serializer.data, status=status.HTTP_200_OK, count=count)