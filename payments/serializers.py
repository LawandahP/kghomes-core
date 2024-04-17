
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
            'tenant',
            'pay_for',
            'invoice',
            'phonenumber',
            'payment_method',
            'mpesa_receipt_number',
            'amount_paid',
            'checkout_request_id',
            'payment_date',
            'payment_time',
            'notes'
        ]

        read_only_fields = [
            "id",
            "account"
        ]


class PaymentDetailsSerializer(serializers.ModelSerializer):
    invoice = InvoiceSerializer(many=False, read_only=True) 
    payment_time = serializers.SerializerMethodField()
    class Meta:
        model = Payment
        fields = [
            'id',
            'account',
            'tenant',
            'pay_for',
            'invoice',
            'phonenumber',
            'payment_method',
            'mpesa_receipt_number',
            'amount_paid',
            'checkout_request_id',
            'payment_date',
            'payment_time',
            'notes'
        ]
    
    def get_payment_time(self, obj):
        payment_time = obj.payment_time
        if payment_time:
            return payment_time.strftime("%I:%M %p")
        return None

