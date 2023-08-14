from django_filters import rest_framework as filters
from .models import Property



class PropertyFilter(filters.FilterSet):
    # status = filters.ChoiceFilter(choices=status_choices)
    # min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    # max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")

    # date_month = filters.NumberFilter(field_name='due_on', lookup_expr='month')
    # date_year = filters.NumberFilter(field_name='due_on', lookup_expr='year')

    # start_date = filters.DateFilter(field_name="due_on", lookup_expr="gte")
    # end_date = filters.DateFilter(field_name="due_on", lookup_expr="lte")
    name = filters.CharFilter(lookup_expr='icontains')


    class Meta:
        model = Property
        fields = (
            "property_type",
            "name"
        )


