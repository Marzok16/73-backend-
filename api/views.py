from django.shortcuts import render
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Prefetch
from django.utils import timezone
from .models import MemoryCategory, MemoryPhoto, MeetingCategory, MeetingPhoto, Colleague, ColleagueArchiveImage
from .serializers import (
    MemoryCategorySerializer, MemoryPhotoSerializer, MemoryCategoryDetailSerializer,
    MeetingCategorySerializer, MeetingPhotoSerializer, MeetingCategoryDetailSerializer,
    ColleagueSerializer, ColleagueArchiveImageSerializer
)
from .validators import validate_uploaded_image
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.db import transaction
import os
import logging

logger = logging.getLogger(__name__)

# Custom throttle classes
class LoginRateThrottle(AnonRateThrottle):
    """Strict rate limiting for login attempts to prevent brute force attacks"""
    rate = '5/hour'
    scope = 'login'

class UploadRateThrottle(UserRateThrottle):
    """Rate limiting for file uploads"""
    rate = '20/hour'
    scope = 'upload'

# Pagination classes
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 1000  # Increased to allow fetching all colleagues

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 24
    page_size_query_param = 'page_size'
    max_page_size = 200

# Create your views here.

@api_view(['GET'])
def hello_world(request):
    """
    Simple API endpoint to test the connection between frontend and backend
    """
    return Response({
        'message': 'Hello from Django Backend!',
        'status': 'success',
        'data': {
            'version': '1.0.0',
            'timestamp': '2025-09-30'
        }
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint
    """
    return Response({
        'status': 'healthy',
        'service': 'college_backend'
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def dashboard_stats(request):
    """
    Dashboard statistics endpoint - shows server stats and content metrics
    Requires authentication
    """
    from django.conf import settings
    import shutil
    
    try:
        # Get media directory stats
        media_path = settings.MEDIA_ROOT
        disk_usage = shutil.disk_usage(media_path)
        
        # Count photos and colleagues
        memory_photos_count = MemoryPhoto.objects.count()
        meeting_photos_count = MeetingPhoto.objects.count()
        colleagues_count = Colleague.objects.count()
        
        # Count categories
        memory_categories_count = MemoryCategory.objects.count()
        meeting_categories_count = MeetingCategory.objects.count()
        
        # Calculate percentages
        disk_used_percent = (disk_usage.used / disk_usage.total) * 100
        
        # Calculate media directory size
        media_size = 0
        for dirpath, dirnames, filenames in os.walk(media_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.isfile(filepath):
                    media_size += os.path.getsize(filepath)
        
        stats = {
            'photos': {
                'memory_photos': memory_photos_count,
                'meeting_photos': meeting_photos_count,
                'total_photos': memory_photos_count + meeting_photos_count,
            },
            'categories': {
                'memory_categories': memory_categories_count,
                'meeting_categories': meeting_categories_count,
                'total_categories': memory_categories_count + meeting_categories_count,
            },
            'colleagues': {
                'total': colleagues_count,
                'active': Colleague.objects.filter(status='active').count(),
                'promoted': Colleague.objects.filter(status='promoted').count(),
                'deceased': Colleague.objects.filter(status='deceased').count(),
            },
            'storage': {
                'total_gb': round(disk_usage.total / (1024**3), 2),
                'used_gb': round(disk_usage.used / (1024**3), 2),
                'free_gb': round(disk_usage.free / (1024**3), 2),
                'used_percent': round(disk_used_percent, 1),
                'media_size_mb': round(media_size / (1024**2), 2),
            },
            'timestamp': timezone.now().isoformat(),
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {str(e)}")
        return Response({
            'error': 'Failed to fetch stats'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@throttle_classes([LoginRateThrottle])
def admin_login(request):
    """
    Authenticate against Django users and allow ONLY superusers.
    Expected body: { "username": string, "password": string }
    Returns 200 with { username, token } if valid superuser; 401 otherwise.
    
    Rate limited to 5 attempts per hour per IP to prevent brute force attacks.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    # Input validation
    if not username or not password:
        logger.warning(f"Login attempt with missing credentials from {request.META.get('REMOTE_ADDR')}")
        return Response({
            'detail': 'Username and password are required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate input length to prevent DoS
    if len(username) > 150 or len(password) > 128:
        logger.warning(f"Login attempt with oversized credentials from {request.META.get('REMOTE_ADDR')}")
        return Response({
            'detail': 'Invalid credentials format.'
        }, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is None:
        logger.warning(f"Failed login attempt for username '{username}' from {request.META.get('REMOTE_ADDR')}")
        return Response({ 'detail': 'Invalid credentials.' }, status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_active:
        logger.warning(f"Login attempt for inactive user '{username}' from {request.META.get('REMOTE_ADDR')}")
        return Response({ 'detail': 'User account is disabled.' }, status=status.HTTP_403_FORBIDDEN)

    if not user.is_superuser:
        logger.warning(f"Non-superuser '{username}' attempted admin login from {request.META.get('REMOTE_ADDR')}")
        return Response({ 'detail': 'Admin access denied. Superuser required.' }, status=status.HTTP_403_FORBIDDEN)

    # Issue or retrieve an API token for the authenticated admin user
    token, created = Token.objects.get_or_create(user=user)
    
    logger.info(f"Successful admin login for '{username}' from {request.META.get('REMOTE_ADDR')}")

    return Response({ 
        'username': user.username, 
        'is_superuser': True, 
        'token': token.key 
    }, status=status.HTTP_200_OK)

class MemoryCategoryViewSet(ModelViewSet):
    """
    ViewSet for managing memory categories (صور تذكارية)
    Optimized with Count annotation to prevent N+1 queries
    """
    queryset = MemoryCategory.objects.all()  # Base queryset for router
    serializer_class = MemoryCategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Optimize queryset with annotations to prevent N+1 queries"""
        return MemoryCategory.objects.annotate(
            photos_count=Count('photos')
        ).prefetch_related('photos')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MemoryCategoryDetailSerializer
        return MemoryCategorySerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve', 'with_photos']:
            permission_classes = []
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to log file deletion"""
        instance = self.get_object()
        photos_count = instance.photos.count()
        category_name = instance.name
        
        # Perform the deletion (signals will handle file cleanup)
        response = super().destroy(request, *args, **kwargs)
        
        # Log the deletion
        print(f"Memory Category '{category_name}' deleted with {photos_count} photos and their files")
        
        return response
    
    @action(detail=True, methods=['get'])
    def photos(self, request, pk=None):
        """Get all photos for a specific memory category"""
        category = self.get_object()
        photos = category.photos.all()
        serializer = MemoryPhotoSerializer(photos, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[])
    def with_photos(self, request):
        """Get all active memory categories with their photos (with optional pagination)"""
        # Check if pagination is requested
        limit = request.query_params.get('limit')
        
        categories = self.get_queryset()
        
        # If limit is specified, apply it
        if limit:
            try:
                limit_int = int(limit)
                categories = categories[:limit_int]
            except (ValueError, TypeError):
                pass  # Ignore invalid limit values
        
        serializer = MemoryCategoryDetailSerializer(categories, many=True, context={'request': request})
        
        # Add cache control headers for better performance
        response = Response(serializer.data)
        response['Cache-Control'] = 'public, max-age=300'  # Cache for 5 minutes
        return response


class MemoryPhotoViewSet(ModelViewSet):
    """
    ViewSet for managing memory photos
    Optimized with select_related to prevent N+1 queries on category
    """
    queryset = MemoryPhoto.objects.all()  # Base queryset for router
    serializer_class = MemoryPhotoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LargeResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_featured']
    search_fields = ['title_ar', 'description_ar']
    ordering_fields = ['title_ar', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Optimize queryset with select_related for category"""
        return MemoryPhoto.objects.select_related('category', 'uploaded_by')
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = []
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser], throttle_classes=[UploadRateThrottle])
    def bulk_upload(self, request):
        """
        Bulk upload multiple memory photos with optional names and descriptions
        Rate limited to prevent server overload. Validates file size, type, and dimensions.
        """
        try:
            category_id = request.data.get('category')
            if not category_id:
                return Response({
                    'error': 'Category ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify category exists
            try:
                category = MemoryCategory.objects.get(id=category_id)
            except MemoryCategory.DoesNotExist:
                return Response({
                    'error': 'Category not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get uploaded files
            uploaded_files = request.FILES.getlist('images')
            if not uploaded_files:
                return Response({
                    'error': 'No images provided'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Limit number of files per upload to prevent DoS
            max_files = 50
            if len(uploaded_files) > max_files:
                return Response({
                    'error': f'Too many files. Maximum {max_files} files per upload.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate all files before processing
            for idx, file in enumerate(uploaded_files):
                try:
                    validate_uploaded_image(file)
                except Exception as e:
                    return Response({
                        'error': f'File {idx + 1} ({file.name}): {str(e)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get metadata for each image (optional)
            photo_metadata = {}
            for key, value in request.data.items():
                if key.startswith('metadata_'):
                    # Extract the index from the key (e.g., metadata_0_title)
                    parts = key.split('_')
                    if len(parts) >= 3:
                        index = parts[1]
                        field = '_'.join(parts[2:])
                        if index not in photo_metadata:
                            photo_metadata[index] = {}
                        photo_metadata[index][field] = value
            
            created_photos = []
            errors = []
            
            for i, image_file in enumerate(uploaded_files):
                try:
                    # Get metadata for this specific image
                    metadata = photo_metadata.get(str(i), {})
                    
                    # Prepare photo data
                    photo_data = {
                        'category': category_id,
                        'title_ar': metadata.get('title', f'صورة تذكارية {i + 1}'),  # Default title if not provided
                        'description_ar': metadata.get('description', ''),  # Empty description if not provided
                        'is_featured': metadata.get('is_featured', 'false').lower() == 'true',
                        'image': image_file
                    }
                    
                    # Create the photo
                    serializer = MemoryPhotoSerializer(data=photo_data, context={'request': request})
                    if serializer.is_valid():
                        photo = serializer.save(uploaded_by=request.user)
                        created_photos.append(MemoryPhotoSerializer(photo, context={'request': request}).data)
                    else:
                        errors.append({
                            'image_index': i,
                            'image_name': image_file.name,
                            'errors': serializer.errors
                        })
                        
                except Exception as e:
                    errors.append({
                        'image_index': i,
                        'image_name': image_file.name if hasattr(image_file, 'name') else f'Image {i}',
                        'error': str(e)
                    })
            
            response_data = {
                'success': True,
                'created_count': len(created_photos),
                'total_count': len(uploaded_files),
                'created_photos': created_photos
            }
            
            if errors:
                response_data['errors'] = errors
                response_data['error_count'] = len(errors)
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Bulk upload failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MeetingCategoryViewSet(ModelViewSet):
    """
    ViewSet for managing meeting categories (اللقاءات)
    Optimized with Count annotation to prevent N+1 queries
    """
    queryset = MeetingCategory.objects.all()  # Base queryset for router
    serializer_class = MeetingCategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'year']
    ordering = ['-year', 'name']  # Sort by year descending (newest first), then by name
    
    def get_queryset(self):
        """Optimize queryset with annotations to prevent N+1 queries"""
        return MeetingCategory.objects.annotate(
            photos_count=Count('photos')
        ).prefetch_related('photos')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MeetingCategoryDetailSerializer
        return MeetingCategorySerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve', 'with_photos']:
            permission_classes = []
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to log file deletion"""
        instance = self.get_object()
        photos_count = instance.photos.count()
        category_name = instance.name
        
        # Perform the deletion (signals will handle file cleanup)
        response = super().destroy(request, *args, **kwargs)
        
        # Log the deletion
        print(f"Meeting Category '{category_name}' deleted with {photos_count} photos and their files")
        
        return response
    
    @action(detail=True, methods=['get'])
    def photos(self, request, pk=None):
        """Get all photos for a specific meeting category"""
        category = self.get_object()
        photos = category.photos.all()
        serializer = MeetingPhotoSerializer(photos, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[])
    def with_photos(self, request):
        """Get all active meeting categories with their photos (with optional pagination)"""
        # Check if pagination is requested
        limit = request.query_params.get('limit')
        
        categories = self.get_queryset()
        
        # If limit is specified, apply it
        if limit:
            try:
                limit_int = int(limit)
                categories = categories[:limit_int]
            except (ValueError, TypeError):
                pass  # Ignore invalid limit values
        
        serializer = MeetingCategoryDetailSerializer(categories, many=True, context={'request': request})
        
        # Add cache control headers for better performance
        response = Response(serializer.data)
        response['Cache-Control'] = 'public, max-age=300'  # Cache for 5 minutes
        return response


class MeetingPhotoViewSet(ModelViewSet):
    """
    ViewSet for managing meeting photos
    Optimized with select_related to prevent N+1 queries on category
    """
    queryset = MeetingPhoto.objects.all()  # Base queryset for router
    serializer_class = MeetingPhotoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LargeResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_featured']
    search_fields = ['title_ar', 'description_ar']
    ordering_fields = ['title_ar', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Optimize queryset with select_related for category"""
        return MeetingPhoto.objects.select_related('category', 'uploaded_by')
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = []
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser], throttle_classes=[UploadRateThrottle])
    def bulk_upload(self, request):
        """
        Bulk upload multiple meeting photos with optional names and descriptions
        Rate limited to prevent server overload. Validates file size, type, and dimensions.
        """
        try:
            category_id = request.data.get('category')
            if not category_id:
                return Response({
                    'error': 'Category ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify category exists
            try:
                category = MeetingCategory.objects.get(id=category_id)
            except MeetingCategory.DoesNotExist:
                return Response({
                    'error': 'Category not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get uploaded files
            uploaded_files = request.FILES.getlist('images')
            if not uploaded_files:
                return Response({
                    'error': 'No images provided'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Limit number of files per upload to prevent DoS
            max_files = 50
            if len(uploaded_files) > max_files:
                return Response({
                    'error': f'Too many files. Maximum {max_files} files per upload.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate all files before processing
            for idx, file in enumerate(uploaded_files):
                try:
                    validate_uploaded_image(file)
                except Exception as e:
                    return Response({
                        'error': f'File {idx + 1} ({file.name}): {str(e)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get metadata for each image (optional)
            photo_metadata = {}
            for key, value in request.data.items():
                if key.startswith('metadata_'):
                    # Extract the index from the key (e.g., metadata_0_title)
                    parts = key.split('_')
                    if len(parts) >= 3:
                        index = parts[1]
                        field = '_'.join(parts[2:])
                        if index not in photo_metadata:
                            photo_metadata[index] = {}
                        photo_metadata[index][field] = value
            
            created_photos = []
            errors = []
            
            for i, image_file in enumerate(uploaded_files):
                try:
                    # Get metadata for this specific image
                    metadata = photo_metadata.get(str(i), {})
                    
                    # Prepare photo data
                    photo_data = {
                        'category': category_id,
                        'title_ar': metadata.get('title', f'صورة لقاء {i + 1}'),  # Default title if not provided
                        'description_ar': metadata.get('description', ''),  # Empty description if not provided
                        'is_featured': metadata.get('is_featured', 'false').lower() == 'true',
                        'image': image_file
                    }
                    
                    # Create the photo
                    serializer = MeetingPhotoSerializer(data=photo_data, context={'request': request})
                    if serializer.is_valid():
                        photo = serializer.save(uploaded_by=request.user)
                        created_photos.append(MeetingPhotoSerializer(photo, context={'request': request}).data)
                    else:
                        errors.append({
                            'image_index': i,
                            'image_name': image_file.name,
                            'errors': serializer.errors
                        })
                        
                except Exception as e:
                    errors.append({
                        'image_index': i,
                        'image_name': image_file.name if hasattr(image_file, 'name') else f'Image {i}',
                        'error': str(e)
                    })
            
            response_data = {
                'success': True,
                'created_count': len(created_photos),
                'total_count': len(uploaded_files),
                'created_photos': created_photos
            }
            
            if errors:
                response_data['errors'] = errors
                response_data['error_count'] = len(errors)
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Bulk upload failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ColleagueViewSet(ModelViewSet):
    """
    ViewSet for managing colleagues (الزملاء)
    """
    queryset = Colleague.objects.all()
    serializer_class = ColleagueSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'is_featured']
    search_fields = ['name', 'position', 'current_workplace', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Optimize queryset with prefetch_related for archive photos"""
        return Colleague.objects.prefetch_related('archive_photos')
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve', 'by_status', 'promoted', 'deceased']:
            permission_classes = []
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """
        Override create to handle photo uploads during colleague creation
        """
        try:
            # Extract main colleague data
            colleague_data = {
                'name': request.data.get('name'),
                'position': request.data.get('position', ''),
                'current_workplace': request.data.get('current_workplace', ''),
                'description': request.data.get('description', ''),
                'status': request.data.get('status', 'active'),
                'achievements': request.data.get('achievements', ''),
                'contact_info': request.data.get('contact_info', ''),
                'is_featured': request.data.get('is_featured', 'false').lower() == 'true',
            }
            
            # Add deceased-specific fields
            if request.data.get('death_year'):
                colleague_data['death_year'] = request.data.get('death_year')
            if request.data.get('relative_phone'):
                colleague_data['relative_phone'] = request.data.get('relative_phone')
            if request.data.get('relationship_type'):
                colleague_data['relationship_type'] = request.data.get('relationship_type')
            
            # Handle file uploads
            if 'photo' in request.FILES:
                colleague_data['photo'] = request.FILES['photo']
            if 'photo_1973' in request.FILES:
                colleague_data['photo_1973'] = request.FILES['photo_1973']
            if 'latest_photo' in request.FILES:
                colleague_data['latest_photo'] = request.FILES['latest_photo']
            
            # Create colleague
            serializer = self.get_serializer(data=colleague_data)
            serializer.is_valid(raise_exception=True)
            colleague = serializer.save()
            
            # Handle archive photos
            archive_files = request.FILES.getlist('archive_photos')
            if archive_files:
                for archive_file in archive_files:
                    try:
                        validate_uploaded_image(archive_file)
                        ColleagueArchiveImage.objects.create(
                            colleague=colleague,
                            image=archive_file,
                            uploaded_by=request.user if request.user.is_authenticated else None
                        )
                    except Exception as e:
                        logger.warning(f"Failed to upload archive photo: {str(e)}")
            
            # Return full colleague data with archive photos
            response_serializer = ColleagueSerializer(colleague, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating colleague: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to ensure all related photos are deleted
        """
        colleague = self.get_object()
        colleague_name = colleague.name
        archive_count = colleague.archive_photos.count() if hasattr(colleague, 'archive_photos') else 0
        
        # Perform deletion (signals will handle file cleanup)
        response = super().destroy(request, *args, **kwargs)
        
        logger.info(f"Colleague '{colleague_name}' deleted with {archive_count} archive photos")
        return response
    
    @action(detail=False, methods=['get'], permission_classes=[])
    def by_status(self, request):
        """Get colleagues grouped by status"""
        status_param = request.query_params.get('status')
        
        if status_param:
            colleagues = self.get_queryset().filter(status=status_param)
        else:
            colleagues = self.get_queryset()
        
        serializer = ColleagueSerializer(colleagues, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[])
    def promoted(self, request):
        """Get promoted colleagues"""
        colleagues = self.get_queryset().filter(status='promoted')
        serializer = ColleagueSerializer(colleagues, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[])
    def deceased(self, request):
        """Get deceased colleagues"""
        colleagues = self.get_queryset().filter(status='deceased')
        serializer = ColleagueSerializer(colleagues, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser], throttle_classes=[UploadRateThrottle])
    def upload_photo_1973(self, request, pk=None):
        """
        Upload or replace the 1973 photo for a colleague (admin-only)
        Expected: multipart/form-data with 'image' field
        """
        colleague = self.get_object()
        
        if 'image' not in request.FILES:
            return Response({
                'error': 'Image file is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['image']
        
        # Validate image
        try:
            validate_uploaded_image(image_file)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete old photo if exists
        if colleague.photo_1973:
            try:
                old_path = colleague.photo_1973.path
                if os.path.isfile(old_path):
                    os.remove(old_path)
            except Exception:
                pass  # Ignore errors when deleting old file
        
        # Save new photo
        colleague.photo_1973 = image_file
        colleague.save()
        
        serializer = ColleagueSerializer(colleague, context={'request': request})
        return Response({
            'success': True,
            'message': 'Photo 1973 uploaded successfully',
            'colleague': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser], throttle_classes=[UploadRateThrottle])
    def upload_latest_photo(self, request, pk=None):
        """
        Upload or replace the latest annual photo for a colleague (admin-only)
        Expected: multipart/form-data with 'image' field
        """
        colleague = self.get_object()
        
        if 'image' not in request.FILES:
            return Response({
                'error': 'Image file is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['image']
        
        # Validate image
        try:
            validate_uploaded_image(image_file)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete old photo if exists
        if colleague.latest_photo:
            try:
                old_path = colleague.latest_photo.path
                if os.path.isfile(old_path):
                    os.remove(old_path)
            except Exception:
                pass  # Ignore errors when deleting old file
        
        # Save new photo
        colleague.latest_photo = image_file
        colleague.save()
        
        serializer = ColleagueSerializer(colleague, context={'request': request})
        return Response({
            'success': True,
            'message': 'Latest photo uploaded successfully',
            'colleague': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser], throttle_classes=[UploadRateThrottle])
    def add_archive_photo(self, request, pk=None):
        """
        Add a new archive photo for a colleague (admin-only)
        Expected: multipart/form-data with 'image' field
        Supports multiple images via 'images' field (list)
        """
        colleague = self.get_object()
        
        # Support both single image and multiple images
        images = request.FILES.getlist('images') or ([request.FILES.get('image')] if request.FILES.get('image') else [])
        
        if not images:
            return Response({
                'error': 'At least one image file is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Limit number of files per upload
        max_files = 20
        if len(images) > max_files:
            return Response({
                'error': f'Too many files. Maximum {max_files} files per upload.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate all images
        for idx, image_file in enumerate(images):
            try:
                validate_uploaded_image(image_file)
            except Exception as e:
                return Response({
                    'error': f'File {idx + 1} ({image_file.name}): {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        created_images = []
        errors = []
        
        for idx, image_file in enumerate(images):
            try:
                # Check for duplicate (by filename and colleague)
                # Note: The unique constraint in model will prevent true duplicates
                archive_image = ColleagueArchiveImage.objects.create(
                    colleague=colleague,
                    image=image_file,
                    uploaded_by=request.user if request.user.is_authenticated else None
                )
                serializer = ColleagueArchiveImageSerializer(archive_image, context={'request': request})
                created_images.append(serializer.data)
            except Exception as e:
                errors.append({
                    'image_index': idx,
                    'image_name': image_file.name if hasattr(image_file, 'name') else f'Image {idx}',
                    'error': str(e)
                })
        
        response_data = {
            'success': True,
            'created_count': len(created_images),
            'total_count': len(images),
            'created_images': created_images
        }
        
        if errors:
            response_data['errors'] = errors
            response_data['error_count'] = len(errors)
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAdminUser], url_path='photo-1973')
    def delete_photo_1973(self, request, pk=None):
        """
        Delete the 1973 photo for a colleague (admin-only)
        """
        colleague = self.get_object()
        
        if not colleague.photo_1973:
            return Response({
                'error': 'No 1973 photo to delete'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Delete the image file
        try:
            old_path = colleague.photo_1973.path
            if os.path.isfile(old_path):
                os.remove(old_path)
        except Exception:
            pass  # Ignore errors when deleting old file
        
        # Clear the field
        colleague.photo_1973 = None
        colleague.save()
        
        return Response({
            'success': True,
            'message': '1973 photo deleted successfully'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAdminUser], url_path='latest-photo')
    def delete_latest_photo(self, request, pk=None):
        """
        Delete the latest annual photo for a colleague (admin-only)
        """
        colleague = self.get_object()
        
        if not colleague.latest_photo:
            return Response({
                'error': 'No latest photo to delete'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Delete the image file
        try:
            old_path = colleague.latest_photo.path
            if os.path.isfile(old_path):
                os.remove(old_path)
        except Exception:
            pass  # Ignore errors when deleting old file
        
        # Clear the field
        colleague.latest_photo = None
        colleague.save()
        
        return Response({
            'success': True,
            'message': 'Latest photo deleted successfully'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAdminUser], url_path='archive-photo/(?P<archive_id>[^/.]+)')
    def delete_archive_photo(self, request, pk=None, archive_id=None):
        """
        Delete a specific archive photo for a colleague (admin-only)
        """
        colleague = self.get_object()
        
        try:
            archive_image = ColleagueArchiveImage.objects.get(id=archive_id, colleague=colleague)
        except ColleagueArchiveImage.DoesNotExist:
            return Response({
                'error': 'Archive photo not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Delete the image (signal handler will clean up the file)
        archive_image.delete()
        
        return Response({
            'success': True,
            'message': 'Archive photo deleted successfully'
        }, status=status.HTTP_200_OK)
