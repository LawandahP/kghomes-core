import math
from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response

from django.utils.translation import gettext_lazy as _
from bff.utils import UseAuthApi
from properties.models import Property
from units.filters import UnitFilter
from units.serializers import UnitAssignmentSerializer, UnitSerializer
from units.models import Assignment, Units
from utils.utils import CustomPagination, customResponse, logger


class CreatViewUnits(generics.GenericAPIView):
    serializer_class = UnitSerializer
    filterset_class = UnitFilter
    pagination_class = CustomPagination
    search_fields = ['unit_number']

    def get_all_units(self, request):
        units = Units.objects.filter(account=request.user["account"]["id"])
        return len(units)
    
    def get_object(self, request):
        queryset = Units.objects.filter(account=request.user["account"]["id"])
        filter = self.filter_queryset(queryset)
        units = self.paginate_queryset(filter)
        return units

    
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
                mesage=_(f"Unit {unit_number} Registered Successfully."),
                status=status.HTTP_201_CREATED
            )
        error = {'detail': serializer.errors}
        return Response(error, status.HTTP_400_BAD_REQUEST)
    
    
    def get(self, request):
        try:
            totalCount = self.get_all_units(request)
            page_size = request.GET.get("size", 10)
            totalpages = math.ceil(totalCount/int(page_size))
            
            units = self.get_object(request)
            count = len(units)
            serializer = UnitSerializer(units, many=True)

            filteredPages=math.ceil(count/int(page_size))
            return customResponse(
                payload=serializer.data, 
                status=status.HTTP_200_OK, 
                count=count,
                totalCount=totalCount,
                totalPages=totalpages,
                totalFilteredPages=filteredPages, 
                success=True
            )
        except Http404 as e:
            error = {'detail': str(e)}
            return Response(error, status.HTTP_404_NOT_FOUND)


class UnitDetailView(generics.GenericAPIView):
    serializer_class = UnitSerializer

    def get_object(self, request, id):
        return Units.objects.get(id=id)

    # @method_decorator(group_required('REALTOR', 'LANDLORD'))
    def get(self, request, id):
        try:
            unit = self.get_object(request, id)
            serializer = self.serializer_class(unit, many=False)
        except Units.DoesNotExist:
            error = {'detail': _("Unit not found")}
            return Response(error, status.HTTP_404_NOT_FOUND)
        return customResponse(payload=serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id):
        try:
            unit = self.get_object(request=request, id=id)
            serializer = self.serializer_class(unit, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                #     audit(request=request, action_flag=f"Updated {request.data} for Property {property.name}")
                return customResponse(
                    payload=serializer.data,
                    message=_("Unit updated successfully"),
                    status=status.HTTP_200_OK
                )
            error = {'detail': serializer.errors}
            return Response(error, status.HTTP_400_BAD_REQUEST)
        except Units.DoesNotExist:
            error = {'detail': _("Unit not found")}
            return Response(error, status.HTTP_404_NOT_FOUND)

   
    # @method_decorator(group_required('REALTOR'))
    def delete(self, request, id):
        try:
            unit = self.get_object(request=request, id=id)
            unit.delete()
            return customResponse(message=_("Unit deleted successfully"), status=status.HTTP_200_OK)
        except Units.DoesNotExist:
            error = {'detail': _("Unit Not Found")}
            return Response(error, status.HTTP_404_NOT_FOUND)


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
        