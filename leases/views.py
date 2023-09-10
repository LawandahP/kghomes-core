from django.http import Http404
from django.utils.translation import gettext_lazy as _


from rest_framework import generics, status
from rest_framework.response import Response

from files.models import Files

from .serializers import LeaseDetailsSerializer, LeaseSerializer
from leases.models import Lease
from utils.utils import customResponse, logger




class CreatViewLease(generics.GenericAPIView):
    serializer_class = LeaseSerializer

    def get_object(self, request):
        queryset = Lease.objects.filter(account=request.user["account"]["id"])
        # filter = self.filter_queryset(queryset)
        # properties = self.paginate_queryset(filter)
        return queryset


    def post(self, request):
        data = request.data
        user = request.user
        

        serializer = self.serializer_class(data=data, context={'request': request})
        if serializer.is_valid():
            account = user["account"]["id"]
            logger.critical(request.FILES)
            
            if request.FILES:
                files = request.FILES.getlist("file")
                logger.critical(files)

                for i in files:
                    file_instance = Files(file_url=i)
                    file_instance.save()
                    serializer.save(file=file_instance, account=account)

            serializer.save(account=account)

            # after creating lease create a CrontabTask that will run every month
            
            
            return customResponse(
                payload=serializer.data,
                message=_("Lease Created Successfully."),
                status=status.HTTP_201_CREATED
            )
        error = {'detail': serializer.errors}
        return Response(error, status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        try:
            leases = self.get_object(request)
            count = len(leases)
            serializer = LeaseDetailsSerializer(leases, many=True)
            return customResponse(payload=serializer.data, status=status.HTTP_200_OK, count=count, success=True)
        except Lease.DoesNotExist:
            error = {'detail': _("Lease not found")}
            return Response(error, status.HTTP_404_NOT_FOUND)

       