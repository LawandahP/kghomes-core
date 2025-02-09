
import humanize
from rest_framework import serializers

from files.serializers import FilesSerializer
from leases.models import Bills, Invoice, Lease, LineItem
from properties.models import Property
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


class LineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineItem
        fields = '__all__'
        
from utils.utils import customResponse, logger

class BillsSerializer(serializers.ModelSerializer):
    item = serializers.JSONField()

    class Meta:
        model = Bills
        fields = ["invoice", "item", "quantity", "description", "rate", "amount"]

    def create(self, validated_data):
        item_data = validated_data.pop('item')
        item_id = item_data.get('id')

        item = LineItem.objects.get(id=item_id)
        invoice = validated_data.pop("invoice")

        bills = Bills.objects.create(
            **validated_data, 
            invoice=invoice,
            item=item
        )   
        # audit(request=request, action_flag="created fees for")         
        return bills
    
    def update(self, instance, validated_data):
        item_data = validated_data.pop('item', None)
        if item_data:
            item_id = item_data.get('id')
            item = LineItem.objects.get(id=item_id)
            instance.item = item

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class BillDetailSerializer(serializers.ModelSerializer):
    item = LineItemSerializer()
    
    class Meta:
        model = Bills
        fields = ["id", "invoice", "item", "quantity", "description", "rate", "amount"]

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
    invoiceBills = BillDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
                "id", "lease", "unit", "due_on", "property", "paid_on", "status", "invoiceBills",
                "amount_paid", "balance", "created_at", "updated_at", "total_amount", 
                "tenant"
            ]