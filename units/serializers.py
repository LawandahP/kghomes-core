from rest_framework import serializers
from django.db import transaction

from properties.serializers import PropertySerializer
from .models import Units, Assignment

class UnitSerializer(serializers.ModelSerializer):
    # status = serializers.CharField(read_only=True)
    
    class Meta:
        model = Units
        fields = [
            "id", "unit_number", "size", "bedrooms", "unit_type",
            "bathrooms", "monthly_rent", "amenities", "property", 
            "status"
        ] 
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['property'] = PropertySerializer(instance.property).data
        return response


class UnitAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'tenant', 'unit', 'assigned_date', 'vacated_date']

        read_only_fields = [
            "id",
            "unit",
            "assigned_date",
        ]

    def create(self, validated_data):
        id = self.context['id']
        tenant = validated_data.pop('tenant')
        with transaction.atomic():
            # update unit status if tenant is passed
            if tenant:
                unit = Units.objects.select_for_update().get(id=id)
                unit.status = "Occupied"
                unit.save()

            assignment = Assignment.objects.create(
                **validated_data, 
                tenant=tenant
            )
        return assignment

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['unit'] = UnitSerializer(instance.unit).data
        return response
