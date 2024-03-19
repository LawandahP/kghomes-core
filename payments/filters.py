from django_filters import rest_framework as filters

from leases.filters import MonthNameToNumberFilter
from .models import Payment



class PaymentFilter(filters.FilterSet):
    pay_for = filters.ChoiceFilter(choices=Payment.PAYMENT_FOR_CHOICES)
    # min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    # max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")

    month = MonthNameToNumberFilter(field_name='TransactionDate')  # Use the custom filter here
    year = filters.NumberFilter(field_name='TransactionDate', lookup_expr='year')
    tenant = filters.CharFilter(field_name='PaidFor')

    paid_from = filters.DateFilter(field_name="TransactionDate", lookup_expr="gte")
    paid_to = filters.DateFilter(field_name="TransactionDate", lookup_expr="lte")

    invoice = filters.NumberFilter(field_name='invoice__id')



    class Meta:
        model = Payment
        fields = (
            "invoice",
            "PhoneNumber",
            "pay_for",
        )


