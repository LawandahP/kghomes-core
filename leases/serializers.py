
from rest_framework import serializers

from files.serializers import FilesSerializer
from leases.models import Bills, Invoice, Lease
from units.serializers import UnitSerializer
from datetime import datetime


class CustomDateField(serializers.CharField):
    # def to_representation(self, obj):
    #     return datetime.strftime(obj, '%Y-%m-%d')

    def to_internal_value(self, data):
        try:
            # Parse the date string into a datetime object
            date_obj = datetime.strptime(data, '%a, %d %b %Y %H:%M:%S GMT').strftime('%Y-%m-%d')
            return date_obj
        except ValueError:
            raise serializers.ValidationError('Invalid date format')



class LeaseSerializer(serializers.ModelSerializer):
    file = FilesSerializer(many=False, read_only=True)
    start_date = CustomDateField()
    first_rent_date = CustomDateField()
    end_date = CustomDateField()

    class Meta:
        model = Lease
        fields = [
            "id", "property", "unit",             
            "tenant", "term",             
            "rent", "security_deposit", 
            "rent_frequency", "start_date",       
            "end_date", "file", "account", "first_rent_date"
        ]
        read_only_fields = [
            "id",
            "account"
        ]

    # def dateConfig(self, dateStr=None):
    #     formatDate = datetime.strptime(dateStr, '%a %b %d %Y %H:%M:%S GMT%z (%Z)')
    #     return formatDate.strftime('%Y-%m-%d')



    # def create(self, validated_data):
    #     request = self.context['request']

    #     start_date = validated_data.pop('start_date')
    #     end_date = validated_data.pop('end_date')
    #     first_rent_date = validated_data.pop('first_rent_date')
      

    #     start_date = self.dateConfig(start_date)
    #     end_date = self.dateConfig(end_date)
    #     first_rent_date = self.dateConfig(first_rent_date)

    #     return Lease.objects.create(
    #         **validated_data, 
    #         first_rent_date=first_rent_date,
    #         end_date=end_date,
    #         start_date=start_date
    #     )
    
    
class LeaseDetailsSerializer(serializers.ModelSerializer):
    file = FilesSerializer(many=False, read_only=True)
    unit = UnitSerializer(many=False, read_only=True)

    class Meta:
        model = Lease
        fields = [
            "id", "property", "unit",             
            "tenant", "term",             
            "rent", "security_deposit", 
            "rent_frequency", "start_date",       
            "end_date", "file", "account"
        ]
        read_only_fields = [
            "id",
            "account"
        ]


class BillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bills
        fields = ["id", "lease", "invoice", "item", "quantity", "description", "rate", "amount"]

        def create(self, validated_data):
            request = self.context['request']
            bills = Bills.objects.create(**validated_data)   
            # audit(request=request, action_flag="created fees for")         
            return bills


class InvoiceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Invoice
        fields = [
                "id", "lease", "unit", "due_on", "property", "paid_on", "payment_status",
                "amount_paid", "balance", "created_at", "updated_at", "total_amount", 
                "tenant"
            ]

        # def create(self, validated_data):
        #     request = self.context['request']
        #     lease = Invoice.objects.create(**validated_data)   
        #     # audit(request=request, action_flag="created lease for")         
        #     return lease


class InvoiceDetailSerializer(serializers.ModelSerializer):
    unit = UnitSerializer(many=False, read_only=True) 
    invoiceBills = BillsSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
                "id", "lease", "unit", "due_on", "property", "paid_on", "payment_status", "invoiceBills",
                "amount_paid", "balance", "created_at", "updated_at", "total_amount", 
                "tenant"
            ]