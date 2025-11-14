from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os
from django.conf import settings
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver

class MemoryCategory(models.Model):
    """Model for memory photo categories (صور تذكارية)"""
    name = models.CharField(max_length=100, verbose_name="اسم الفئة")
    description = models.TextField(blank=True, null=True, verbose_name="وصف الفئة")
    color = models.CharField(max_length=7, default="#3B82F6", verbose_name="لون الفئة")
    year = models.IntegerField(blank=True, null=True, verbose_name="السنة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "فئة صور تذكارية"
        verbose_name_plural = "فئات الصور التذكارية"
        ordering = ['-year', 'name']  # Sort by year descending (newest first), then by name
    
    def __str__(self):
        return self.name


class MemoryPhoto(models.Model):
    """Model for memory photos within categories"""
    category = models.ForeignKey(MemoryCategory, on_delete=models.CASCADE, related_name='photos', verbose_name="الفئة", db_index=True)
    title_ar = models.CharField(max_length=200, verbose_name="عنوان الصورة")
    description_ar = models.TextField(blank=True, null=True, verbose_name="وصف الصورة")
    image = models.ImageField(upload_to='memory_photos/', verbose_name="الصورة")
    thumbnail = models.ImageField(upload_to='memory_thumbnails/', blank=True, null=True, verbose_name="صورة مصغرة")
    is_featured = models.BooleanField(default=False, verbose_name="صورة مميزة", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء", db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="رفع بواسطة")
    
    class Meta:
        verbose_name = "صورة تذكارية"
        verbose_name_plural = "الصور التذكارية"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at'], name='memory_photo_created_idx'),
            models.Index(fields=['category', '-created_at'], name='memory_cat_date_idx'),
            models.Index(fields=['category', 'is_featured'], name='memory_cat_featured_idx'),
            models.Index(fields=['is_featured', '-created_at'], name='memory_featured_date_idx'),
        ]
    
    def __str__(self):
        return self.title_ar


class MeetingCategory(models.Model):
    """Model for meeting photo categories (اللقاءات)"""
    name = models.CharField(max_length=100, verbose_name="اسم فئة اللقاء")
    description = models.TextField(blank=True, null=True, verbose_name="وصف فئة اللقاء")
    color = models.CharField(max_length=7, default="#10B981", verbose_name="لون الفئة")
    year = models.IntegerField(blank=True, null=True, verbose_name="السنة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "فئة اللقاءات"
        verbose_name_plural = "فئات اللقاءات"
        ordering = ['-year', 'name']  # Sort by year descending (newest first), then by name
    
    def __str__(self):
        return self.name


class MeetingPhoto(models.Model):
    """Model for meeting photos within categories"""
    category = models.ForeignKey(MeetingCategory, on_delete=models.CASCADE, related_name='photos', verbose_name="فئة اللقاء", db_index=True)
    title_ar = models.CharField(max_length=200, verbose_name="عنوان صورة اللقاء")
    description_ar = models.TextField(blank=True, null=True, verbose_name="وصف صورة اللقاء")
    image = models.ImageField(upload_to='meeting_photos/', verbose_name="صورة اللقاء")
    thumbnail = models.ImageField(upload_to='meeting_thumbnails/', blank=True, null=True, verbose_name="صورة مصغرة")
    is_featured = models.BooleanField(default=False, verbose_name="صورة مميزة", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء", db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="رفع بواسطة")
    
    class Meta:
        verbose_name = "صورة اللقاء"
        verbose_name_plural = "صور اللقاءات"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at'], name='meeting_photo_created_idx'),
            models.Index(fields=['category', '-created_at'], name='meeting_cat_date_idx'),
            models.Index(fields=['category', 'is_featured'], name='meeting_cat_featured_idx'),
            models.Index(fields=['is_featured', '-created_at'], name='meeting_featured_date_idx'),
        ]
    
    def __str__(self):
        return self.title_ar


class Colleague(models.Model):
    """Model for colleagues/alumni"""
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('promoted', 'وصل لمنصب عالي'),
        ('deceased', 'متوفى'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="الاسم", db_index=True)
    position = models.CharField(max_length=200, blank=True, null=True, verbose_name="التخصص")
    current_workplace = models.CharField(max_length=300, blank=True, null=True, verbose_name="جهة العمل الحالية")
    description = models.TextField(blank=True, null=True, verbose_name="نبذة تعريفية")
    photo = models.ImageField(upload_to='colleague_photos/', blank=True, null=True, verbose_name="الصورة")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="الحالة", db_index=True)
    graduation_year = models.IntegerField(blank=True, null=True, verbose_name="سنة التخرج", db_index=True)
    achievements = models.TextField(blank=True, null=True, verbose_name="الإنجازات")
    contact_info = models.TextField(blank=True, null=True, verbose_name="معلومات التواصل")
    is_featured = models.BooleanField(default=False, verbose_name="مميز", db_index=True)
    # Fields for deceased colleagues
    death_year = models.IntegerField(blank=True, null=True, verbose_name="سنة الوفاة")
    relative_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="رقم قريب له")
    RELATIONSHIP_CHOICES = [
        ('son', 'ابن'),
        ('daughter', 'ابنة'),
        ('brother', 'أخ'),
        ('sister', 'أخت'),
        ('father', 'أب'),
        ('mother', 'أم'),
        ('other', 'آخر'),
    ]
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES, blank=True, null=True, verbose_name="وصلة القرابة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "زميل"
        verbose_name_plural = "الزملاء"
        ordering = ['name']
        indexes = [
            models.Index(fields=['status', 'name'], name='colleague_status_name_idx'),
            models.Index(fields=['graduation_year'], name='colleague_grad_year_idx'),
            models.Index(fields=['is_featured', 'name'], name='colleague_featured_name_idx'),
        ]
    
    def __str__(self):
        return self.name


# Signal handlers for file deletion
def delete_file_if_exists(file_path):
    """
    Utility function to safely delete a file from the filesystem
    """
    if file_path and os.path.isfile(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass  # File was already deleted or doesn't exist

@receiver(post_delete, sender=MemoryPhoto)
def memory_photo_delete_handler(sender, instance, **kwargs):
    """
    Delete memory photo files when MemoryPhoto instance is deleted
    Uses transaction.on_commit() to avoid race conditions
    """
    from django.db import transaction
    
    # Store paths before they're potentially invalidated
    image_path = instance.image.path if instance.image else None
    thumbnail_path = instance.thumbnail.path if instance.thumbnail else None
    
    # Schedule file deletion after transaction commits
    if image_path:
        transaction.on_commit(lambda: delete_file_if_exists(image_path))
    if thumbnail_path:
        transaction.on_commit(lambda: delete_file_if_exists(thumbnail_path))

@receiver(pre_delete, sender=MemoryCategory)
def memory_category_delete_handler(sender, instance, **kwargs):
    """
    Delete all memory photos and their files when MemoryCategory is deleted
    Uses transaction.on_commit() to avoid race conditions
    """
    from django.db import transaction
    
    # Get all photos in this category before deletion and store their paths
    file_paths = []
    photos = instance.photos.all()
    for photo in photos:
        if photo.image:
            file_paths.append(photo.image.path)
        if photo.thumbnail:
            file_paths.append(photo.thumbnail.path)
    
    # Schedule file deletion after transaction commits
    for path in file_paths:
        transaction.on_commit(lambda p=path: delete_file_if_exists(p))

@receiver(post_delete, sender=MeetingPhoto)
def meeting_photo_delete_handler(sender, instance, **kwargs):
    """
    Delete meeting photo files when MeetingPhoto instance is deleted
    Uses transaction.on_commit() to avoid race conditions
    """
    from django.db import transaction
    
    # Store paths before they're potentially invalidated
    image_path = instance.image.path if instance.image else None
    thumbnail_path = instance.thumbnail.path if instance.thumbnail else None
    
    # Schedule file deletion after transaction commits
    if image_path:
        transaction.on_commit(lambda: delete_file_if_exists(image_path))
    if thumbnail_path:
        transaction.on_commit(lambda: delete_file_if_exists(thumbnail_path))

@receiver(pre_delete, sender=MeetingCategory)
def meeting_category_delete_handler(sender, instance, **kwargs):
    """
    Delete all meeting photos and their files when MeetingCategory is deleted
    Uses transaction.on_commit() to avoid race conditions
    """
    from django.db import transaction
    
    # Get all photos in this category before deletion and store their paths
    file_paths = []
    photos = instance.photos.all()
    for photo in photos:
        if photo.image:
            file_paths.append(photo.image.path)
        if photo.thumbnail:
            file_paths.append(photo.thumbnail.path)
    
    # Schedule file deletion after transaction commits
    for path in file_paths:
        transaction.on_commit(lambda p=path: delete_file_if_exists(p))

@receiver(post_delete, sender=Colleague)
def colleague_delete_handler(sender, instance, **kwargs):
    """
    Delete colleague photo file when Colleague instance is deleted
    Uses transaction.on_commit() to avoid race conditions
    """
    from django.db import transaction
    
    # Store path before it's potentially invalidated
    photo_path = instance.photo.path if instance.photo else None
    
    # Schedule file deletion after transaction commits
    if photo_path:
        transaction.on_commit(lambda: delete_file_if_exists(photo_path))
