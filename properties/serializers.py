from rest_framework import serializers
# from unit.serializers import UnitSerializer

from .models import Amenities, Property, Type, Kind


class PropertyKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kind
        fields = ['name']

class PropertyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ['name']


# Amenities
class AmenitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenities
        fields = [
            'id', 'name',
        ]
      
    def create(self, validated_data):
        request = self.context['request']
        name = self.validated_data['name']
        amenities = Amenities.objects.create(**validated_data)
        # audit(request=request, action_flag=f"Amenity {name} Created")
        return amenities


class PropertySerializer(serializers.ModelSerializer):
    # amenities = serializers.StringRelatedField(many=True, read_only=True)
    # images = FilesSerializer(many=True, read_only=True)
    class Meta:
        model = Property
        fields = [
            'id', 'slug', 'name', 'address' ,
            'address', 'owner', 'property_type', 'account',
        ]
        read_only_fields = [
            "units",
            "id",
            "slug",
        ]

    def create(self, validated_data):        
        request = self.context['request']
        name = self.validated_data['name']
        property = Property.objects.create(**validated_data)
        # audit(request=request, action_flag=f"Property {name} Created")
        return property

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
    # amenities = serializers.StringRelatedField(many=True)
    # property_kind = PropertyKindSerializer(many=False)
    # owner = UserSer(many=False, read_only=True)
    # images = FilesSerializer(many=True, read_only=True)
    class Meta:
        model = Property
        fields = [ 
            'id', 'slug', 'name', 'address', 'amenities', 
            'address', 'owner', 'property_kind', 'property_type'
            ]
        read_only_fields = [ "id", "slug", "amenities", "images" ]

    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     response['property_type'] = PropertyTypeSerializer(instance.property_type).data
    #     return response

class PropertyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['id', 'slug', 'name', 'address', 'amenities', 'address', 'owner', 'kind', 'type', 'images']
        read_only_fields = [ "id", "slug", "amenities", "images" ]


        

class AmenitiesResponseSerializer(serializers.Serializer):
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Amenities
        fields = ['name']

    def get_name(self, instance):
        # return [amenity.name for amenity in instance]
        return [instance.name]



#  Property Type Serializer
class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = [
            'id', 'kind', 'name'
        ]

    def create(self, validated_data):
        request = self.context['request']
        # name = self.validated_data['property_model']
        property = Type.objects.create(**validated_data)
        # audit(request=request, action_flag=f"Property model {name} Created")
        return property


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
