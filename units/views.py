from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from config.auth import CustomBackend

from units.serializers import UnitSerializer
from units.models import Units
from utils.utils import customResponse




class CreatViewUnits(generics.GenericAPIView):
    serializer_class = UnitSerializer

    def get_object(self, request):
        queryset = Units.objects.filter(account=request.user["account"]["id"])
        # filter = self.filter_queryset(queryset)
        # properties = self.paginate_queryset(filter)
        return queryset


    def post(self, request):
        data = request.data
        user = request.user

        serializer = self.serializer_class(data=data, context={'request': request})
        if serializer.is_valid():
            account = user["account"]["id"]
            unit_number = data['unit_number']
            serializer.save(account=account)
            
            return customResponse(
                payload=serializer.data,
                message=f"Unit {unit_number} Registered Successfully.",
                status=status.HTTP_201_CREATED
            )
        error = {'detail': serializer.errors}
        return Response(error, status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        try:
            units = self.get_object(request)
            count = len(units)
            serializer = UnitSerializer(units, many=True)
            return customResponse(payload=serializer.data, status=status.HTTP_200_OK, count=count, success=True)
        except Http404 as e:
            error = {'detail': str(e)}
            return Response(error, status.HTTP_404_NOT_FOUND)

       