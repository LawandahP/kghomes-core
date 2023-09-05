
from rest_framework import serializers

from files.serializers import FilesSerializer
from leases.models import Lease
from units.serializers import UnitSerializer


class LeaseSerializer(serializers.ModelSerializer):
    file = FilesSerializer(many=False, read_only=True)
    tenant = serializers.JSONField()

    class Meta:
        model = Lease
        fields = [
            "property", "unit",             
            "tenant", "term",             
            "rent", "security_deposit", 
            "rent_frequency", "start_date",       
            "end_date", "file", "account"
        ]
        read_only_fields = [
            "id",
            "account"
        ]

    def create(self, validated_data):
        request = self.context['request']

        tenant = validated_data.pop('tenant')
        del tenant['account']

        return Lease.objects.create(
            **validated_data, 
            tenant=tenant,
        )
    
    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     response['unit'] = UnitSerializer(instance.unit).data
    #     return response
    
class LeaseDetailsSerializer(serializers.ModelSerializer):
    file = FilesSerializer(many=False, read_only=True)
    tenant = serializers.JSONField()
    unit = UnitSerializer(many=False, read_only=True)

    class Meta:
        model = Lease
        fields = [
            "property", "unit",             
            "tenant", "term",             
            "rent", "security_deposit", 
            "rent_frequency", "start_date",       
            "end_date", "file", "account"
        ]
        read_only_fields = [
            "id",
            "account"
        ]