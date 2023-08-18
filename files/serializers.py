from rest_framework import serializers

from .models import Files


class FilesSerializer(serializers.HyperlinkedModelSerializer):
    # image_path = serializers.SerializerMethodField('get_image_path')

    class Meta:
        model = Files
        fields = ["id", "file_url"]

    # def get_image_path(self, obj):
    #     request = self.context.get("request")
    #     return request.build_absolute_uri(obj.image_url.url)

