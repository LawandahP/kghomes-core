from django_filters import rest_framework as filters, Filter
from django_filters.constants import EMPTY_VALUES

from .models import Invoice, Lease



class MonthNameToNumberFilter(Filter):
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        # Map month names to their corresponding numbers (1-12)
        month_mapping = {
            "January": 1, "February": 2, "March": 3,
            "April": 4, "May": 5, "June": 6,
            "July": 7, "August": 8, "September": 9,
            "October": 10, "November": 11, "December": 12
        }
        # Convert month name to number
        month_number = month_mapping.get(value.capitalize())
        if month_number:
            # Apply the filter with the converted month number
            return qs.filter(**{f"{self.field_name}__month": month_number})
        return qs
    
class InvoiceFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=Invoice.PAYMENT_STATUS_CHOICES)
    # min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    # max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")

    due_month = MonthNameToNumberFilter(field_name='due_on')  # Use the custom filter here
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


class LeaseFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=Lease.LEASE_STATUS)
    property = filters.NumberFilter(field_name='property__id')
    unit = filters.NumberFilter(field_name='unit__id')
    tenant = filters.CharFilter(field_name='tenant')

    class Meta:
        model = Lease
        fields = (
            "status",
            "tenant",
            "property",
            "unit"
        )

