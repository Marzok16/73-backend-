from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import MemoryCategory, MemoryPhoto, MeetingCategory, MeetingPhoto, Colleague, ColleagueArchiveImage

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
    list_display = ['name', 'photos_count', 'youtube_link_display', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    fieldsets = [
        ('المعلومات الأساسية', {
            'fields': ['name', 'description', 'year']
        }),
        ('رابط يوتيوب', {
            'fields': ['youtube_link']
        }),
        ('التصميم', {
            'fields': ['color']
        })
    ]
    
    def youtube_link_display(self, obj):
        if obj.youtube_link:
            return format_html('<a href="{}" target="_blank">🎬 فتح الفيديو</a>', obj.youtube_link)
        return '-'
    youtube_link_display.short_description = 'فيديو يوتيوب'
    
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


@admin.register(Colleague)
class ColleagueAdmin(admin.ModelAdmin):
    """Admin interface for Colleague model"""
    list_display = ['name', 'status', 'current_workplace', 'is_featured', 'created_at']
    list_filter = ['status', 'is_featured', 'created_at']
    search_fields = ['name', 'position', 'current_workplace', 'description', 'achievements']
    list_editable = ['is_featured']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('المعلومات الأساسية', {
            'fields': ['name', 'position', 'current_workplace']
        }),
        ('النبذة التعريفية', {
            'fields': ['description', 'achievements', 'contact_info']
        }),
        ('الصورة', {
            'fields': ['photo']
        }),
        ('نظام الصور المنظم', {
            'fields': ['photo_1973', 'latest_photo'],
            'classes': ['collapse'],
            'description': 'صورة 1973 والصورة السنوية الأخيرة'
        }),
        ('الحالة والإعدادات', {
            'fields': ['status', 'is_featured']
        }),
        ('معلومات المتوفين', {
            'fields': ['death_year', 'relative_phone', 'relationship_type'],
            'classes': ['collapse'],  # Collapsed by default
            'description': 'تظهر هذه الحقول فقط للزملاء المتوفين'
        }),
        ('معلومات النظام', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related()
    
    def save_model(self, request, obj, form, change):
        """Auto-clear deceased fields if status is not deceased"""
        if obj.status != 'deceased':
            obj.death_year = None
            obj.relative_phone = None
            obj.relationship_type = None
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        """Override delete to show warning about file deletion"""
        colleague_name = obj.name
        has_photo = bool(obj.photo)
        
        super().delete_model(request, obj)
        
        if has_photo:
            self.message_user(
                request, 
                f'تم حذف الزميل "{colleague_name}" وصورته من المجلد.',
                level='INFO'
            )
        else:
            self.message_user(
                request, 
                f'تم حذف الزميل "{colleague_name}".',
                level='INFO'
            )
    
    def delete_queryset(self, request, queryset):
        """Override bulk delete to show warning about file deletion"""
        colleagues_count = queryset.count()
        photos_count = queryset.exclude(photo='').count()
        
        super().delete_queryset(request, queryset)
        
        if photos_count > 0:
            self.message_user(
                request, 
                f'تم حذف {colleagues_count} زميل مع {photos_count} صورة وملفاتها من المجلد.',
                level='WARNING'
            )
        else:
            self.message_user(
                request, 
                f'تم حذف {colleagues_count} زميل.',
                level='INFO'
            )


@admin.register(ColleagueArchiveImage)
class ColleagueArchiveImageAdmin(admin.ModelAdmin):
    """Admin interface for ColleagueArchiveImage model"""
    list_display = ['colleague', 'uploaded_at', 'uploaded_by']
    list_filter = ['uploaded_at', 'colleague']
    search_fields = ['colleague__name']
    ordering = ['-uploaded_at']
    readonly_fields = ['uploaded_at', 'uploaded_by']
    
    fieldsets = [
        ('المعلومات الأساسية', {
            'fields': ['colleague', 'image']
        }),
        ('معلومات النظام', {
            'fields': ['uploaded_at', 'uploaded_by'],
            'classes': ['collapse']
        })
    ]
    
    def delete_model(self, request, obj):
        """Override delete to show warning about file deletion"""
        colleague_name = obj.colleague.name
        super().delete_model(request, obj)
        self.message_user(
            request, 
            f'تم حذف صورة الأرشيف للزميل "{colleague_name}" وملفها من المجلد.',
            level='INFO'
        )
    
    def delete_queryset(self, request, queryset):
        """Override bulk delete to show warning about file deletion"""
        images_count = queryset.count()
        super().delete_queryset(request, queryset)
        self.message_user(
            request, 
            f'تم حذف {images_count} صورة أرشيف وملفاتها من المجلد.',
            level='INFO'
        )
