from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Property, Lease, Payment
from .serializers import PropertyDashboardSerializer

class PropertyDashboardView(APIView):
    def get(self, request, format=None):
        owner_id = request.query_params.get('owner_id')
        property_id = request.query_params.get('property_id')
        # Add more filters as needed

        filters = {}
        if owner_id:
            filters['owner__id'] = owner_id
        if property_id:
            filters['id'] = property_id

        properties = Property.objects.filter(**filters)
        total_properties = properties.count()
        total_units = properties.aggregate(total_units=Sum('total_units'))['total_units'] or 0
        
        occupied_units = Lease.objects.filter(property__in=properties, start_date__lte=timezone.now(), end_date__gte=timezone.now()).count()
        vacancy_rate = ((total_units - occupied_units) / total_units) * 100 if total_units else 0
        occupancy_rate = (occupied_units / total_units) * 100 if total_units else 0
        
        total_rental_income = Payment.objects.filter(lease__property__in=properties).aggregate(total_income=Sum('amount'))['total_income'] or 0
        total_deposit_paid = Lease.objects.filter(property__in=properties).aggregate(total_deposit=Sum('deposit'))['total_deposit'] or 0

        data = {
            'total_properties_managed': total_properties,
            'total_units': total_units,
            'occupancy_rate': occupancy_rate,
            'vacancy_rate': vacancy_rate,
            'total_rental_income': total_rental_income,
            'total_deposit_paid': total_deposit_paid,
        }

        serializer = PropertyDashboardSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.validated_data)
        else:
            return Response(serializer.errors, status=400)