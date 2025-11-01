from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import MemoryCategory, MemoryPhoto, MeetingCategory, MeetingPhoto

@admin.register(MemoryCategory)
class MemoryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'photos_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    fieldsets = [
        ('المعلومات الأساسية', {
            'fields': ['name', 'description']
        }),
        ('التصميم', {
            'fields': ['color']
        })
    ]
    
    def photos_count(self, obj):
        count = obj.photos.count()
        if count > 0:
            url = reverse('admin:api_memoryphoto_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}"><strong>{} صور</strong></a>', url, count)
        return '0 صور'
    photos_count.short_description = 'عدد الصور'
    
    def delete_model(self, request, obj):
        """Override delete to show warning about file deletion"""
        photos_count = obj.photos.count()
        if photos_count > 0:
            # The signal will handle the actual file deletion
            self.message_user(
                request, 
                f'تم حذف فئة الصور التذكارية "{obj.name}" مع {photos_count} صورة وملفاتها من المجلد.',
                level='WARNING'
            )
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """Override bulk delete to show warning about file deletion"""
        total_photos = sum(obj.photos.count() for obj in queryset)
        categories_count = queryset.count()
        if total_photos > 0:
            self.message_user(
                request, 
                f'تم حذف {categories_count} فئة صور تذكارية مع {total_photos} صورة وملفاتها من المجلد.',
                level='WARNING'
            )
        super().delete_queryset(request, queryset)

@admin.register(MemoryPhoto)
class MemoryPhotoAdmin(admin.ModelAdmin):
    list_display = ['title_ar', 'category', 'is_featured', 'created_at']
    list_filter = ['category', 'is_featured', 'created_at']
    search_fields = ['title_ar', 'description_ar']
    list_editable = ['is_featured']
    ordering = ['-created_at']
    readonly_fields = ['uploaded_by']
    fieldsets = [
        ('المعلومات الأساسية', {
            'fields': ['category', 'title_ar', 'description_ar']
        }),
        ('الصورة', {
            'fields': ['image', 'thumbnail']
        }),
        ('الإعدادات', {
            'fields': ['is_featured', 'uploaded_by']
        })
    ]
    
    def delete_model(self, request, obj):
        """Override delete to show warning about file deletion"""
        self.message_user(
            request, 
            f'تم حذف الصورة التذكارية "{obj.title_ar}" وملفاتها من المجلد.',
            level='INFO'
        )
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """Override bulk delete to show warning about file deletion"""
        photos_count = queryset.count()
        self.message_user(
            request, 
            f'تم حذف {photos_count} صورة تذكارية وملفاتها من المجلد.',
            level='INFO'
        )
        super().delete_queryset(request, queryset)

@admin.register(MeetingCategory)
class MeetingCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'photos_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    fieldsets = [
        ('المعلومات الأساسية', {
            'fields': ['name', 'description']
        }),
        ('التصميم', {
            'fields': ['color']
        })
    ]
    
    def photos_count(self, obj):
        count = obj.photos.count()
        if count > 0:
            url = reverse('admin:api_meetingphoto_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}"><strong>{} صور</strong></a>', url, count)
        return '0 صور'
    photos_count.short_description = 'عدد الصور'
    
    def delete_model(self, request, obj):
        """Override delete to show warning about file deletion"""
        photos_count = obj.photos.count()
        if photos_count > 0:
            # The signal will handle the actual file deletion
            self.message_user(
                request, 
                f'تم حذف فئة اللقاءات "{obj.name}" مع {photos_count} صورة وملفاتها من المجلد.',
                level='WARNING'
            )
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """Override bulk delete to show warning about file deletion"""
        total_photos = sum(obj.photos.count() for obj in queryset)
        categories_count = queryset.count()
        if total_photos > 0:
            self.message_user(
                request, 
                f'تم حذف {categories_count} فئة اللقاءات مع {total_photos} صورة وملفاتها من المجلد.',
                level='WARNING'
            )
        super().delete_queryset(request, queryset)

@admin.register(MeetingPhoto)
class MeetingPhotoAdmin(admin.ModelAdmin):
    list_display = ['title_ar', 'category', 'is_featured', 'created_at']
    list_filter = ['category', 'is_featured', 'created_at']
    search_fields = ['title_ar', 'description_ar']
    list_editable = ['is_featured']
    ordering = ['-created_at']
    readonly_fields = ['uploaded_by']
    fieldsets = [
        ('المعلومات الأساسية', {
            'fields': ['category', 'title_ar', 'description_ar']
        }),
        ('الصورة', {
            'fields': ['image', 'thumbnail']
        }),
        ('الإعدادات', {
            'fields': ['is_featured', 'uploaded_by']
        })
    ]
    
    def delete_model(self, request, obj):
        """Override delete to show warning about file deletion"""
        self.message_user(
            request, 
            f'تم حذف صورة اللقاء "{obj.title_ar}" وملفاتها من المجلد.',
            level='INFO'
        )
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """Override bulk delete to show warning about file deletion"""
        photos_count = queryset.count()
        self.message_user(
            request, 
            f'تم حذف {photos_count} صورة لقاء وملفاتها من المجلد.',
            level='INFO'
        )
        super().delete_queryset(request, queryset)
