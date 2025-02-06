import json
from rest_framework import serializers
from files.models import Files
from files.serializers import FilesSerializer
# from unit.serializers import UnitSerializer

from units.models import Units
from utils.utils import logger
from .models import Property


class PropertySerializer(serializers.ModelSerializer):
    # amenities = serializers.StringRelatedField(many=True, read_only=True)
    images = FilesSerializer(many=True, read_only=True)
    amenities = serializers.JSONField(required=False)
    
    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = [
            "units",
            "id",
            "slug",
        ]
    
    def create(self, validated_data):
        property = super().create(validated_data)
        self.update_units_count(property)
        return property


    def update_units_count(self, property):
        # Calculate the count of units and update the units_count
        property.unit_count = property.units.count()
        property.rented_units_count = property.units.filter(status=Units.RENTED).count()
        property.vacant_units_count = property.units.filter(status=Units.VACANT).count()
        property.save()

    def to_representation(self, instance):
        # Update contact count before returning the representation
        self.update_units_count(instance)
        return super().to_representation(instance)
    

#   class MaintenanceAdminSerializer(serializers.ModelSerializer):
#     # images = FilesSerializer(many=True, required=False)

#     class Meta:
#         model = Maintenance
#         fields = ["id", "requested_by", "unit", "category", "description", "images", "status", "grant_entry", "created_at", "resolved_on"]

#         def create(self, validated_data):
#             request = self.context['request']
#             maintenance = Maintenance.objects.create(**validated_data)
#             return maintenance


    

    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     response['property_type'] = TypeSerializer(instance.property_type).data
    #     return response


    # def create(self, validated_data):
    #     try:
    #         dance_ids = []
    #         for dance in self.initial_data['dances']:
    #             if 'id' not in dance:
    #                 raise serializers.ValidationError({'detail': 'key error'})
    #             dance_ids.append(dance['id'])

    #         new_event = models.Event.objects.create(**validated_data)
            
    #         if dance_ids:
    #             for dance_id in dance_ids:
    #                 new_event.dances.add(dance_id)
    #         new_event.save()
    #         return new_event

    #     except Exception as e:
    #         raise serializers.ValidationError({'detail': e})

    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     response['owner'] = LandlordSerializer(instance.owner).data
    #     return response


class PropertyDetailsSerializer(serializers.ModelSerializer):
    images = FilesSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = [ 
            'id', 'slug', 'name', 'latlng', 'bounds', 'address', 'amenities', 
            'owner', 'property_type', 'images', 'account', 'description', 'property_type'
            ]
        read_only_fields = [ "id", "slug", "amenities"]


class PropertyUpdateSerializer(serializers.ModelSerializer):
    amenities = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    owner = serializers.JSONField()

    class Meta:
        model = Property
        fields = [
            'id', 'slug', 'name', 'latlng', 'bounds', 'address', 'amenities', 
            'owner', 'images', 'property_type', 'description'
        ]
        read_only_fields = [ "id", "slug", "amenities", "images" ]

    def update(self, instance, validated_data):
        owner_data = validated_data.pop('owner', {})
        owner_id = owner_data.get('id')
        # Update the owner field with the extracted owner_id
        instance.owner = owner_id

        # Update all other fields at once
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance



class PropertyDashboardSerializer(serializers.Serializer):
    total_properties_managed = serializers.IntegerField()
    total_units = serializers.IntegerField()
    occupancy_rate = serializers.FloatField()
    vacancy_rate = serializers.FloatField()
    # total_rental_income = serializers.FloatField()
    active_tenants =  serializers.IntegerField()
    total_deposits_paid = serializers.FloatField()
    total_deposits = serializers.FloatField()