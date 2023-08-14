import csv
import json
from django.http import Http404
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from openpyxl import load_workbook
import requests
from config.permissions import IsRealtor

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser


# from django_filters.rest_framework import FilterSet

from utils.utils import CustomPagination, customResponse, logger


from .models import Property
from .filters import PropertyFilter
# from files.models import Files

from .serializers import PropertySerializer, PropertyDetailsSerializer, PropertyUpdateSerializer
# from landlord.serializers import LandlordSerializer

# from unit.models import Unit
# from unit.serializers import UnitSerializer
from django.http import JsonResponse


from config.auth import CustomBackend

fs = FileSystemStorage(location='tmp/')

class PropertyCreateListView(generics.GenericAPIView):
    queryset = Property.objects.all()  # Set your queryset here
    pagination_class = CustomPagination
    serializer_class = PropertySerializer
    permission_classes = [IsRealtor]

    filterset_class = PropertyFilter
    search_fields = ['name']


    def get_object(self, request):
        queryset = Property.objects.filter(account=request.user["account"]["id"])
        filter = self.filter_queryset(queryset)
        properties = self.paginate_queryset(filter)
        return properties

    def post(self, request):
        data = request.data
        user = request.user
        
        serializer = self.serializer_class(
            data=data, context={'request': request})
        if serializer.is_valid():
            account = user["account"]["id"]
            name = data['name']
            serializer.save(account=account)
            
            return customResponse(
                payload=serializer.data,
                message=f"Property {name} Registered Successfully.",
                status=status.HTTP_201_CREATED
            )
        error = {'detail': serializer.errors}
        return Response(error, status.HTTP_400_BAD_REQUEST)

    
    def get(self, request):
        try:
            properties = self.get_object(request)
            count = len(properties)
            serializer = PropertyDetailsSerializer(properties, many=True)
        except Http404 as e:
            error = {'detail': str(e)}
            return Response(error, status.HTTP_404_NOT_FOUND)
        return customResponse(payload=serializer.data, status=status.HTTP_200_OK, count=count, success=True)

       

class PropertyDetailView(generics.GenericAPIView):
    serializer_class = PropertyDetailsSerializer

    def get_object(self, request, slug):
        return Property.objects.get(slug=slug)

    # @method_decorator(group_required('REALTOR', 'LANDLORD'))
    def get(self, request, slug):
        try:
            property = self.get_object(request, slug)
            serializer = self.serializer_class(property, many=False)
        except Exception as e:
            error = {'detail': str(e)}
            return Response(error, status.HTTP_404_NOT_FOUND)
        return customResponse(payload=serializer.data, status=status.HTTP_200_OK)

    # @method_decorator(group_required('REALTOR'))
    def patch(self, request, slug):
        try:
            property = self.get_object(request=request, slug=slug)
            serializer = self.serializer_class(property, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                #     audit(request=request, action_flag=f"Updated {request.data} for Property {property.name}")
                return customResponse(
                    payload=serializer.data,
                    message=_("Property updated successfully"),
                    status=status.HTTP_200_OK
                )
        except Property.DoesNotExist:
            error = {'detail': serializer.errors}
            return Response(error, status.HTTP_404_NOT_FOUND)
            # return gitHomesResponse(error="Property you are trying to access does not exist", status=status.HTTP_200_OK)

    # @method_decorator(group_required('REALTOR'))
    def put(self, request, slug):
        property = self.get_object(request=request, slug=slug)
        data = request.data
        serializer = PropertyUpdateSerializer(
            instance=property, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return customResponse(
                payload=serializer.data,
                success="Property updated successfully",
                status=status.HTTP_200_OK
            )
        error = {'detail': serializer.errors}
        return Response(error, status.HTTP_400_BAD_REQUEST)
        
    # @method_decorator(group_required('REALTOR'))
    def delete(self, request, slug):
        try:
            property = self.get_object(request=request, slug=slug)
            property.delete()
        except Property.DoesNotExist:
            error = {'detail': ["Property Not Found"]}
            return Response(error, status.HTTP_404_NOT_FOUND)
        return customResponse(success="Property deleted successfully", status=status.HTTP_200_OK)




class FileUploadView(APIView):    

    def post(self, request, format=None):
        file = request.FILES.get("file")

        if file is None:
            raise ParseError('No file was uploaded')

        if file.name.endswith('.csv'):
            try:
                data = []
                decoded_file = file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)
                header = next(reader)
                for row in reader:
                    data.append(row)
            except Exception as e:
                    raise ParseError('Error parsing CSV file')

        elif file.name.endswith('.xlsx'):
            # Process XLSX file
            try:
                workbook = load_workbook(file)
                sheet = workbook.active
                data = [list(row) for row in sheet.iter_rows(values_only=True)]
                header = data[0]
                data = data[1:]
            except Exception as e:
                raise ParseError('Error parsing XLSX file')
        
        else:
            raise ParseError('Unsupported file format')

        # Create instances of YourModel using the extracted data
        instances = []
        # for row in data:
        #     related_instance = User.objects.get(id=row[2])
        #     if not all(cell is None for cell in row):
        #         instance = Property(
        #             name=row[0] if len(row) > 0 else None,
        #             address=row[1] if len(row) > 1 else None,
        #             owner=related_instance if len(row) > 1 else None,
        #         )
        #         instances.append(instance)

        # Save the instances to the database
        Property.objects.bulk_create(instances)
        return customResponse(
            success="Data Successfully Uploaded",
            status=status.HTTP_201_CREATED
        )
