
from datetime import datetime
import pytz
from rest_framework import serializers

from leases.serializers import InvoiceSerializer
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'account',
            'PayFor',
            'Invoice',
            'PhoneNumber',
            'MpesaReceiptNumber',
            'Amount',
            'CheckoutRequestID',
            'TransactionDate',
        ]

        read_only_fields = [
            "id",
            "account",
            "TransactionDate"
        ]


class PaymentDetailsSerializer(serializers.ModelSerializer):
    Invoice = InvoiceSerializer(many=False, read_only=True) 
    class Meta:
        model = Payment
        fields = [
            'id',
            'account',
            'PayFor',
            'Invoice',
            'PhoneNumber',
            'MpesaReceiptNumber',
            'Amount',
            'CheckoutRequestID',
            'TransactionDate',
        ]