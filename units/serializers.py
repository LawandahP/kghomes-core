from rest_framework import serializers
from django.db import transaction
from properties.models import Property

from properties.serializers import PropertySerializer
from .models import Units, Assignment

class UnitSerializer(serializers.ModelSerializer):
    # status = serializers.CharField(read_only=True)
    property = serializers.JSONField()
    
    class Meta:
        model = Units
        fields = [
            "id", "unit_number", "size", "bedrooms", "unit_type",
            "bathrooms", "monthly_rent", "amenities", "property", 
            "status"
        ] 


    def create(self, validated_data):
        property = validated_data.pop('property')
        property = Property.objects.get(id = property["id"])
        return Units.objects.create(
            **validated_data, 
            property=property
        )

    def update(self, instance, validated_data):
        property = validated_data.pop('property')
        property = Property.objects.get(id = property["id"])
        # Update the owner field with the extracted owner_id
        instance.owner = property

        # Update all other fields at once
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance

     
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['property'] = PropertySerializer(instance.property).data
        return response


class UnitAssignmentSerializer(serializers.ModelSerializer):
    tenant = serializers.JSONField()
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
                tenant_id = tenant["id"]
                unit = Units.objects.select_for_update().get(id=id)
                unit.status = "Occupied"
                unit.save()

            assignment = Assignment.objects.create(
                **validated_data, 
                tenant=tenant_id
            )
        return assignment

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['unit'] = UnitSerializer(instance.unit).data
        return response
