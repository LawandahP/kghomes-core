import json
from rest_framework import serializers
# from unit.serializers import UnitSerializer

from utils.utils import logger
from .models import Property


class PropertySerializer(serializers.ModelSerializer):
    # amenities = serializers.StringRelatedField(many=True, read_only=True)
    # images = FilesSerializer(many=True, read_only=True)
    amenities = serializers.JSONField()
    class Meta:
        model = Property
        fields = [
            'id', 'slug', 'latlng', 'bounds', 'address', 'name', 'owner', 'account', 'amenities', 'property_type'
        ]
        read_only_fields = [
            "units",
            "id",
            "slug",
        ]
    
    def create(self, validated_data):
        request = self.context['request']
        location = validated_data.pop('address')

        owner = validated_data.pop('owner')
        del owner['account']

        logger.critical(owner)
        
        property_type = request.data["category"]
        address = location["address"]

        return Property.objects.create(
            **validated_data, 
            owner=owner,
            address=address, 
            property_type=property_type
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
 
    class Meta:
        model = Property
        fields = [ 
            'id', 'slug', 'name', 'latlng', 'bounds', 'address', 'amenities', 
            'address', 'owner', 'property_type', 'account'
            ]
        read_only_fields = [ "id", "slug", "amenities"]


class PropertyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['id', 'slug', 'name', 'address', 'amenities', 'address', 'owner', 'kind', 'type', 'images']
        read_only_fields = [ "id", "slug", "amenities", "images" ]


# Joint Serializer

# class JointPropertySerializer(serializers.ModelSerializer):


# def create(self, validated_data):        
#         try: 
#             request = self.context['request']
#             name = self.validated_data['name']

#             for amenity in request.data['amenities']:
#                 amenity_obj = Amenities.objects.get(name=amenity['name'])
#                 property.amenities.add(amenity_obj)
            
#             property = Property.objects.create(**validated_data)
#             property.save()
#             audit(request=request, action_flag=f"Property {name} Created")
#             return property

#         except Exception as e:
#             raise serializers.ValidationError({'detail': [e]})
