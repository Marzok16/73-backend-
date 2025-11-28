from rest_framework import serializers
from .models import MemoryCategory, MemoryPhoto, MeetingCategory, MeetingPhoto, Colleague, ColleagueArchiveImage

class MemoryCategorySerializer(serializers.ModelSerializer):
    # Use IntegerField to receive annotated count from queryset
    photos_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = MemoryCategory
        fields = [
            'id', 'name', 'description', 'color', 'year', 'created_at', 'updated_at',
            'photos_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'photos_count']


class MemoryPhotoSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MemoryPhoto
        fields = [
            'id', 'category', 'category_name', 'title_ar',
            'description_ar', 'image', 'image_url', 'thumbnail',
            'is_featured', 'created_at', 'updated_at', 'uploaded_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'uploaded_by']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None
    
    def create(self, validated_data):
        # Set the uploaded_by field to the current user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['uploaded_by'] = request.user
        return super().create(validated_data)


class MemoryCategoryDetailSerializer(serializers.ModelSerializer):
    photos = MemoryPhotoSerializer(many=True, read_only=True)
    
    class Meta:
        model = MemoryCategory
        fields = [
            'id', 'name', 'description', 'color', 'created_at', 'updated_at',
            'photos'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MeetingCategorySerializer(serializers.ModelSerializer):
    # Use IntegerField to receive annotated count from queryset
    photos_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = MeetingCategory
        fields = [
            'id', 'name', 'description', 'color', 'year', 'youtube_link', 'created_at', 'updated_at',
            'photos_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'photos_count']


class MeetingPhotoSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MeetingPhoto
        fields = [
            'id', 'category', 'category_name', 'title_ar',
            'description_ar', 'image', 'image_url', 'thumbnail',
            'is_featured', 'created_at', 'updated_at', 'uploaded_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'uploaded_by']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None
    
    def create(self, validated_data):
        # Set the uploaded_by field to the current user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['uploaded_by'] = request.user
        return super().create(validated_data)


class MeetingCategoryDetailSerializer(serializers.ModelSerializer):
    photos = MeetingPhotoSerializer(many=True, read_only=True)
    
    class Meta:
        model = MeetingCategory
        fields = [
            'id', 'name', 'description', 'color', 'year', 'youtube_link', 'created_at', 'updated_at',
            'photos'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ColleagueArchiveImageSerializer(serializers.ModelSerializer):
    """Serializer for archive images"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ColleagueArchiveImage
        fields = ['id', 'image', 'image_url', 'uploaded_at', 'uploaded_by']
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None


class ColleagueSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    photo_1973_url = serializers.SerializerMethodField()
    latest_photo_url = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    archive_photos = ColleagueArchiveImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Colleague
        fields = [
            'id', 'name', 'position', 'current_workplace', 'description',
            'photo', 'photo_url', 'photo_1973', 'photo_1973_url',
            'latest_photo', 'latest_photo_url', 'status', 'status_display',
            'achievements', 'contact_info', 'is_featured', 'death_year',
            'relative_phone', 'relationship_type', 'archive_photos',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'archive_photos']
    
    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
        return None
    
    def get_photo_1973_url(self, obj):
        if obj.photo_1973:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo_1973.url)
        return None
    
    def get_latest_photo_url(self, obj):
        if obj.latest_photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.latest_photo.url)
        return None