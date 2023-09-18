from django_filters import rest_framework as filters
from django.utils.translation import gettext_lazy as _

from .models import Units

UNIT_STATUS = [
    ('Vacant', _('Vacant')),
    ('Occupied', _('Occupied'))
]

class UnitFilter(filters.FilterSet):
    
    status = filters.ChoiceFilter(field_name="status", choices=UNIT_STATUS)
    # min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    # max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")

    # date_month = filters.NumberFilter(field_name='due_on', lookup_expr='month')
    # date_year = filters.NumberFilter(field_name='due_on', lookup_expr='year')

    # start_date = filters.DateFilter(field_name="due_on", lookup_expr="gte")
    # end_date = filters.DateFilter(field_name="due_on", lookup_expr="lte")
    property_id = filters.NumberFilter(field_name='property__id')
    unit_number = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Units
        fields = (
            "status",
            "unit_number",
            "property_id"
        )


