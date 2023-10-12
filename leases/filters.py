from django_filters import rest_framework as filters
from .models import Invoice



class InvoiceFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=Invoice.PAYMENT_STATUS_CHOICES)
    # min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    # max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")

    due_month = filters.NumberFilter(field_name='due_on', lookup_expr='month')
    due_year = filters.NumberFilter(field_name='due_on', lookup_expr='year')

    # start_date = filters.DateFilter(field_name="due_on", lookup_expr="gte")
    # end_date = filters.DateFilter(field_name="due_on", lookup_expr="lte")
    property = filters.NumberFilter(field_name='property__id')
    tenant = filters.CharFilter(field_name='tenant')
    id = filters.CharFilter(lookup_expr='icontains')


    class Meta:
        model = Invoice
        fields = (
            "status",
            "tenant",
            "property",
            "id"
        )


