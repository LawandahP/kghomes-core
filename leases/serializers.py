
import humanize
from rest_framework import serializers

from files.serializers import FilesSerializer
from leases.models import Bills, Invoice, Lease
from properties.models import Property
from properties.serializers import PropertySerializer
from units.models import Units
from units.serializers import UnitSerializer
from datetime import datetime
from django.utils import timezone
# from utils.utils import logger

class CustomDateField(serializers.CharField):

    def to_internal_value(self, data):
        try:
            # Parse the date string into a datetime object
            date_obj = datetime.strptime(data, '%a, %d %b %Y %H:%M:%S GMT').strftime('%Y-%m-%d')
            return date_obj
        except ValueError:
            raise serializers.ValidationError('Invalid date format')



class LeaseSerializer(serializers.ModelSerializer):
    file = FilesSerializer(many=False, read_only=True)
    tenant = serializers.JSONField()
    unit = serializers.JSONField()
    property = serializers.JSONField()

    class Meta:
        model = Lease
        fields = [
            "id", "property", "unit",             
            "tenant", "term",             
            "rent", "due_day", "security_deposit", 
            "rent_frequency", "start_date",       
            "end_date", "file", "account", "first_rent_date"
        ]
        read_only_fields = [
            "id",
            "account"
        ]

    def create(self, validated_data):
        # data sent as object
        tenant = validated_data.pop('tenant')
        unit = validated_data.pop('unit')
        property_ = validated_data.pop('property') 

        tenant = tenant["tenant"]["id"]
        unit = Units.objects.get(id=unit["id"])
        property_ = Property.objects.get(id=property_["id"])


        return Lease.objects.create(
            **validated_data, 
            tenant=tenant,
            unit=unit,
            property=property_
        )
    
    
    
class LeaseDetailsSerializer(serializers.ModelSerializer):
    file = FilesSerializer(many=False, read_only=True)
    unit = UnitSerializer(many=False, read_only=True)
    expire_in_days = serializers.SerializerMethodField()
    # property = PropertySerializer(many=False, read_only=True)

    class Meta:
        model = Lease
        fields = [
            "id", "property", "unit",             
            "tenant", "term", "status",        
            "rent", "security_deposit", 
            "rent_frequency", "start_date",       
            "end_date", "expire_in_days",
            "file", "account", "due_day"
        ]
        read_only_fields = [
            "id",
            "account"
        ]
        
    def get_expire_in_days(self, obj):
        today = timezone.now().date()
        if obj.end_date and today:
            difference_in_days = (obj.end_date - today).days
            if difference_in_days == 0:
                return "Today"
            elif difference_in_days < 0:
                return "Expired " + humanize.naturaldelta(obj.end_date - today) + " ago"
            else:
                return "Expires in " + humanize.naturaldelta(obj.end_date - today)
        else:
            return None


class BillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bills
        fields = ["id", "invoice", "item", "quantity", "description", "rate", "amount"]

        def create(self, validated_data):
            request = self.context['request']
            invoice = validated_data.pop("invoice")
            invoice = Invoice.objects.get(id=invoice)

            bills = Bills.objects.create(**validated_data, invoice=invoice)   
            # audit(request=request, action_flag="created fees for")         
            return bills


class InvoiceSerializer(serializers.ModelSerializer):
    due_in_days = serializers.SerializerMethodField()
    class Meta:
        model = Invoice
        fields = [
                "id", "lease", "unit", "due_on", "property", "paid_on", "status",
                "amount_paid", "balance", "created_at", "updated_at", "total_amount", 
                "tenant", "due_in_days"
            ]

    def get_due_in_days(self, obj):
        today = timezone.now().date()
        if obj.due_on and today:
            difference_in_days = (obj.due_on - today).days
            if difference_in_days == 0:
                return "Today"
            elif difference_in_days < 0:
                return humanize.naturaldelta(obj.due_on - today) + " ago"
            else:
                return "in " + humanize.naturaldelta(obj.due_on - today)
        else:
            return None


class InvoiceDetailSerializer(serializers.ModelSerializer):
    unit = UnitSerializer(many=False, read_only=True) 
    invoiceBills = BillsSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
                "id", "lease", "unit", "due_on", "property", "paid_on", "status", "invoiceBills",
                "amount_paid", "balance", "created_at", "updated_at", "total_amount", 
                "tenant"
            ]