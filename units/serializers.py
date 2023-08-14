from rest_framework import serializers

from properties.serializers import PropertySerializer
from .models import Units, Assignment

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Units
        fields = [
            "id", "unit_number", "size", "bedrooms", "unit_type",
            "bathrooms", "monthly_rent", "amenities", "property"
        ] 
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['property'] = PropertySerializer(instance.property).data
        return response

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'
