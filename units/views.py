from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import action

from django.utils.translation import gettext_lazy as _
from bff.utils import UseAuthApi
from properties.models import Property
from units.filters import UnitFilter
from units.serializers import UnitAssignmentSerializer, UnitSerializer
from units.models import Assignment, Units
from utils.responseBody import ResponseBody
from utils.utils import CustomPagination, customResponse, logger, upload_data


from rest_framework import viewsets

class UnitViewSet(ResponseBody, viewsets.ModelViewSet):
    serializer_class = UnitSerializer
    filterset_class = UnitFilter
    pagination_class = CustomPagination
    search_fields = ['unit_number']
    # permission_classes = [IsAuthenticated,]


    def get_queryset(self):
        return Units.objects.filter(account=self.request.user["account"]["id"])

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        serializer = self.get_serializer(data=data, context={'request': request})
        if serializer.is_valid():
            account = user["account"]["id"]
            unit_number = data['unit_number']
            serializer.save(account=account)
            
            return customResponse(
                payload=serializer.data,
                message=_(f"Unit {unit_number} Registered Successfully."),
                status=status.HTTP_201_CREATED
            )
        error = {'detail': serializer.errors}
        return Response(error, status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete_units(self, request):
        try:
            ids = request.data.get('ids', [])
            if not ids:
                return Response({"error": "No Contacts selected."}, status=status.HTTP_400_BAD_REQUEST)

            if not isinstance(ids, list):
                return Response({"error": "Unitss should be provided as a list."}, status=status.HTTP_400_BAD_REQUEST)

            queryset = self.get_queryset().filter(id__in=ids)
            queryset.delete()

            return Response({"message": f"Unitss deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"{str(e)}"}, status=400)
        
    
    @action(detail=False, methods=['post'], url_path="bulk-upload")
    def bulk_upload_units(self, request):
        try:
            with transaction.atomic():
                account = request.user["account"]["id"]
                data = request.data
                units_data = data.get('units')

                if not units_data:
                    return Response({"detail": "No units data provided."}, status=status.HTTP_400_BAD_REQUEST)

                logger.warning(f"Units Data {units_data}")
                # Validate and create units
                unit_serializer = UnitSerializer(data=units_data, many=True)
                if unit_serializer.is_valid():
                    for unit in unit_serializer.validated_data:
                        print("Unit", unit)
                        property_id = unit.get('property')
                        print("Property Id", property_id)
                        if property_id:
                            try:
                                property_instance = Property.objects.get(id=property_id)
                                unit['property'] = property_instance
                            except Property.DoesNotExist:
                                return Response(
                                    {"detail": f"Property with ID {property_id} does not exist."},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                        unit['account'] = account

                        # unit['is_unit'] = True
                    Units.objects.bulk_create([Units(**unit) for unit in unit_serializer.validated_data])

                    return Response({"message": "Units uploaded successfully", "data": data}, status=status.HTTP_201_CREATED)
                else:
                    return Response(unit_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"An error occurred during bulk upload: {str(e)}")
            return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            
    @action(detail=False, methods=['post'], url_path="file-upload", permission_classes=[IsAuthenticated])
    def file_upload_units(self, request, format=None):
        try:
            account = request.user["account"]["id"]
            excel_file = request.FILES['file']
            file_type = request.GET.get('file_type', 'csv')
            fields = ['unit_number', 'size', 'bedrooms', 'bathrooms', 'amenities', 'rent', 'unit_type']
            return upload_data(account, excel_file, Units, fields)
        except Exception as e:
            return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)



class AssignUnitToTenant(generics.GenericAPIView):
    serializer_class = UnitAssignmentSerializer
    authentication_classes = []

    def get_object(self, request, id):
        # try:
        queryset = Units.objects.get(id=id)
        return queryset
        # except:
        #     queryset = Property.objects.get(id=id)
        # return queryset

    def post(self, request, id):
        data = request.data
        
        try:
            unit = self.get_object(request=request, id=id)

            # check if unit is occupied before assigning
            if unit.status == "Occupied":
                return Response({"detail": _("Unit already occupied. Vacate the unit to assign a new tenant.")}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if the tenant is already assigned to another unit
            tenant_id = data["tenant"]
            existing_assignment = Assignment.objects.filter(tenant=tenant_id, vacated_date__isnull=True).exclude(unit=unit)
            if existing_assignment.exists():
                return Response({"detail": _("Tenant is already assigned to another unit.")}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = self.serializer_class(
                data=data, context={'request': request, 'id': id}
            )

            if serializer.is_valid():
                serializer.save(unit=unit)
                return customResponse(
                    payload=serializer.data,
                    message=_("Unit assigned successfully"),
                    status=status.HTTP_200_OK
                )
            error = {'detail': serializer.errors}
            return Response(error, status.HTTP_400_BAD_REQUEST)
        except Units.DoesNotExist:
            error = {'detail': _("Unit not found")}
            return Response(error, status.HTTP_404_NOT_FOUND)

    def getTenants(self, assignments_data):
        try:
            # Get all tenant IDs
            tenant_ids = [assignment["tenant"] for assignment in assignments_data] 
            tenant_ids = set(tenant_ids)
            useAuthApi = UseAuthApi("bulk-user-details")
            tenantData = useAuthApi.fetchBulkUserDetails(tenant_ids)
            return tenantData
        except:
            logger.warning("Error when fetching user details")
    
    def get(self, request, id):
        current_assignment = request.GET.get("assignment", False)
        try:
            unit = self.get_object(request, id)
            assignments = Assignment.objects.filter(unit=unit)

            # Filter tenants where vacated_date is null
            active_tenants = assignments.filter(vacated_date__isnull=True)
            active_tenants_count = active_tenants.count()
            
            serializer = self.serializer_class(assignments, many=True)
            
            assignments_data = serializer.data
            
            modified_assignments = []


            # Make a single API request to fetch tenant data for all tenants
            tenantData = self.getTenants(assignments_data)
            # logger.info(tenantData)
            # fetch tenant details
            for assignment in assignments_data:
                tenant_id = assignment["tenant"]
                for tenant in tenantData:
                    if tenant["id"] == tenant_id:
                        assignment['tenant'] = tenant

                # Check if the assignment should be appended to modified_assignments
                if current_assignment == "current":
                    if 'vacated_date' in assignment and assignment['vacated_date'] is None:
                        modified_assignments.append(assignment)
                elif not current_assignment:
                    modified_assignments.append(assignment)
            return customResponse(payload=modified_assignments, count=active_tenants_count, status=status.HTTP_200_OK)

        except:
            # Get property Tenants
            try:
                tenants = Assignment.objects.filter(property=id)

                # Filter tenants where vacated_date is null
                active_tenants = tenants.filter(vacated_date__isnull=True)
                active_tenants_count = active_tenants.count()

                serializer = self.serializer_class(tenants, many=True)
                
                assignments_data = serializer.data
                
                modified_assignments = []

                # fetch tenant details
                tenantData = self.getTenants(assignments_data)
                # logger.info(tenantData)

                for assignment in assignments_data:
                    tenant_id = assignment["tenant"]
                    for tenant in tenantData:
                        tenant["id"] == tenant_id
                        assignment['tenant'] = tenant
                        modified_assignments.append(assignment)
                return customResponse(payload=modified_assignments, count=active_tenants_count, status=status.HTTP_200_OK)
            except Exception as e:
                logger.warning(f"{e}")
                error = {'detail': _("An error has occured!")}
                return Response(error, status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    
    def patch(self, request, id):
        try:
            unit = self.get_object(request, id)
            vacate = request.data.get('vacate', False)
            swap = request.data.get('swap', False)

            if vacate:
                try:
                    Assignment.vacate_unit(unit)
                    return customResponse(message= _('Unit vacated successfully') , status=status.HTTP_200_OK)
                except:
                    return Response({'detail': _('Unit not found or already vacated')}, status=status.HTTP_404_NOT_FOUND)
            elif swap:
                unit2_id = request.data.get('unit2_id')  # Assuming you pass unit2_id in the request data
                unit2 = Units.objects.get(id=unit2_id)
                Assignment.swap_units(unit, unit2)
                return Response({'message': _('Units swapped successfully')}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': _('No operation specified')}, status=status.HTTP_400_BAD_REQUEST)
        except Assignment.DoesNotExist:
            return Response({'detail': _('Assignment not found')}, status=status.HTTP_404_NOT_FOUND)
        except Units.DoesNotExist:
            return Response({'detail': _('Unit not found')}, status=status.HTTP_404_NOT_FOUND)
        