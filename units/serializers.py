from rest_framework import serializers
from django.db import transaction
from properties.models import Property

from properties.serializers import PropertySerializer
from .models import Units, Assignment
from utils.utils import logger

class UnitSerializer(serializers.ModelSerializer):
    # status = serializers.CharField(read_only=True)
    property = serializers.JSONField()
    
    class Meta:
        model = Units
        fields = [
            "id", "unit_number", "size", "bedrooms", "unit_type",
            "bathrooms", "rent", "amenities", "property", 
            "status"
        ] 

    def create(self, validated_data):
        property = validated_data.pop('property')
        property = Property.objects.get(id=property)
        return Units.objects.create(
            **validated_data, 
            property=property
        )

    def update(self, instance, validated_data):
        property = validated_data.pop('property')
        property = Property.objects.get(id = property["id"])

        logger.info(property)
        # Update the property field with the extracted property_id
        instance.property = property

        # update property in assignment when property in unit is updated
        try:
            assignment = Assignment.objects.get(unit=instance)
            assignment.property = property
            assignment.save()
            logger.info(assignment)
        except:
            logger.warning("Unit has not been assigned before!")
            pass
        
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
        fields = ['id', 'tenant', 'property', 'unit', 'assigned_date', 'vacated_date']

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
            
            # get property instance using unit.property(name)
            unit_property = Property.objects.get(name=unit.property)

            assignment = Assignment.objects.create(
                **validated_data, 
                tenant=tenant_id,
                property=unit_property
            )
        return assignment

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['unit'] = UnitSerializer(instance.unit).data
        return response
