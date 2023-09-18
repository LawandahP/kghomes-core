from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response

from django.utils.translation import gettext_lazy as _
from units.filters import UnitFilter
from units.serializers import UnitAssignmentSerializer, UnitSerializer
from units.models import Assignment, Units
from utils.utils import CustomPagination, customResponse


class CreatViewUnits(generics.GenericAPIView):
    serializer_class = UnitSerializer
    filterset_class = UnitFilter
    pagination_class = CustomPagination
    search_fields = ['unit_number']

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
            units = self.get_object(request)
            count = len(units)
            serializer = UnitSerializer(units, many=True)
            return customResponse(payload=serializer.data, status=status.HTTP_200_OK, count=count, success=True)
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

    def get_object(self, request, id):
        queryset = Units.objects.get(account=request.user["account"]["id"], id=id)
        return queryset

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
        
    def get(self, request, id):
        try:
            unit = self.get_object(request, id)
            assignments = Assignment.objects.filter(unit=unit)
            serializer = self.serializer_class(assignments, many=True)
        except Units.DoesNotExist:
            error = {'detail': _("Unit not found")}
            return Response(error, status.HTTP_404_NOT_FOUND)
        return customResponse(payload=serializer.data, status=status.HTTP_200_OK)
    
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
        