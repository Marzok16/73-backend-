from rest_framework import serializers
from .models import Memory


class MemorySerializer(serializers.ModelSerializer):
	image_url = serializers.SerializerMethodField()

	class Meta:
		model = Memory
		fields = ['id', 'title', 'description', 'image', 'image_url', 'created_at']

	def get_image_url(self, obj):
		request = self.context.get('request')
		if not request:
			return obj.image.url if obj.image and hasattr(obj.image, 'url') else None
		return request.build_absolute_uri(obj.image.url) if obj.image and hasattr(obj.image, 'url') else None








