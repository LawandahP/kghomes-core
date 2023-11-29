import json
from rest_framework import serializers
from files.models import Files
from files.serializers import FilesSerializer
# from unit.serializers import UnitSerializer

from utils.utils import logger
from .models import Property


class PropertySerializer(serializers.ModelSerializer):
    # amenities = serializers.StringRelatedField(many=True, read_only=True)
    images = FilesSerializer(many=True, read_only=True)
    amenities = serializers.JSONField()
    owner = serializers.JSONField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'slug', 'latlng', 'bounds', 'address', 'name', 'images',
            'owner', 'account', 'amenities', 'property_type', 'description'
        ]
        read_only_fields = [
            "units",
            "id",
            "slug",
        ]
    
    def create(self, validated_data):
        location = validated_data.pop('address')
        owner = validated_data.pop('owner')
        owner = owner["id"]

        if location:
            address = location["address"]
        else:
            address = None

        return Property.objects.create(
            **validated_data, 
            address=address, 
            owner=owner
        )

    

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



