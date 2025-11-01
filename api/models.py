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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "فئة صور تذكارية"
        verbose_name_plural = "فئات الصور التذكارية"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class MemoryPhoto(models.Model):
    """Model for memory photos within categories"""
    category = models.ForeignKey(MemoryCategory, on_delete=models.CASCADE, related_name='photos', verbose_name="الفئة")
    title_ar = models.CharField(max_length=200, verbose_name="عنوان الصورة")
    description_ar = models.TextField(blank=True, null=True, verbose_name="وصف الصورة")
    image = models.ImageField(upload_to='memory_photos/', verbose_name="الصورة")
    thumbnail = models.ImageField(upload_to='memory_thumbnails/', blank=True, null=True, verbose_name="صورة مصغرة")
    is_featured = models.BooleanField(default=False, verbose_name="صورة مميزة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="رفع بواسطة")
    
    class Meta:
        verbose_name = "صورة تذكارية"
        verbose_name_plural = "الصور التذكارية"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title_ar


class MeetingCategory(models.Model):
    """Model for meeting photo categories (اللقاءات)"""
    name = models.CharField(max_length=100, verbose_name="اسم فئة اللقاء")
    description = models.TextField(blank=True, null=True, verbose_name="وصف فئة اللقاء")
    color = models.CharField(max_length=7, default="#10B981", verbose_name="لون الفئة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "فئة اللقاءات"
        verbose_name_plural = "فئات اللقاءات"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class MeetingPhoto(models.Model):
    """Model for meeting photos within categories"""
    category = models.ForeignKey(MeetingCategory, on_delete=models.CASCADE, related_name='photos', verbose_name="فئة اللقاء")
    title_ar = models.CharField(max_length=200, verbose_name="عنوان صورة اللقاء")
    description_ar = models.TextField(blank=True, null=True, verbose_name="وصف صورة اللقاء")
    image = models.ImageField(upload_to='meeting_photos/', verbose_name="صورة اللقاء")
    thumbnail = models.ImageField(upload_to='meeting_thumbnails/', blank=True, null=True, verbose_name="صورة مصغرة")
    is_featured = models.BooleanField(default=False, verbose_name="صورة مميزة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="رفع بواسطة")
    
    class Meta:
        verbose_name = "صورة اللقاء"
        verbose_name_plural = "صور اللقاءات"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title_ar


class Colleague(models.Model):
    """Model for colleagues/alumni"""
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('promoted', 'وصل لمنصب عالي'),
        ('deceased', 'متوفى'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="الاسم")
    position = models.CharField(max_length=200, blank=True, null=True, verbose_name="المنصب")
    current_workplace = models.CharField(max_length=300, blank=True, null=True, verbose_name="جهة العمل الحالية")
    description = models.TextField(blank=True, null=True, verbose_name="نبذة تعريفية")
    photo = models.ImageField(upload_to='colleague_photos/', blank=True, null=True, verbose_name="الصورة")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="الحالة")
    graduation_year = models.IntegerField(blank=True, null=True, verbose_name="سنة التخرج")
    achievements = models.TextField(blank=True, null=True, verbose_name="الإنجازات")
    contact_info = models.TextField(blank=True, null=True, verbose_name="معلومات التواصل")
    is_featured = models.BooleanField(default=False, verbose_name="مميز")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "زميل"
        verbose_name_plural = "الزملاء"
        ordering = ['name']
    
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
    """
    if instance.image:
        delete_file_if_exists(instance.image.path)
    if instance.thumbnail:
        delete_file_if_exists(instance.thumbnail.path)

@receiver(pre_delete, sender=MemoryCategory)
def memory_category_delete_handler(sender, instance, **kwargs):
    """
    Delete all memory photos and their files when MemoryCategory is deleted
    """
    # Get all photos in this category before deletion
    photos = instance.photos.all()
    for photo in photos:
        # Delete the files
        if photo.image:
            delete_file_if_exists(photo.image.path)
        if photo.thumbnail:
            delete_file_if_exists(photo.thumbnail.path)

@receiver(post_delete, sender=MeetingPhoto)
def meeting_photo_delete_handler(sender, instance, **kwargs):
    """
    Delete meeting photo files when MeetingPhoto instance is deleted
    """
    if instance.image:
        delete_file_if_exists(instance.image.path)
    if instance.thumbnail:
        delete_file_if_exists(instance.thumbnail.path)

@receiver(pre_delete, sender=MeetingCategory)
def meeting_category_delete_handler(sender, instance, **kwargs):
    """
    Delete all meeting photos and their files when MeetingCategory is deleted
    """
    # Get all photos in this category before deletion
    photos = instance.photos.all()
    for photo in photos:
        # Delete the files
        if photo.image:
            delete_file_if_exists(photo.image.path)
        if photo.thumbnail:
            delete_file_if_exists(photo.thumbnail.path)

@receiver(post_delete, sender=Colleague)
def colleague_delete_handler(sender, instance, **kwargs):
    """
    Delete colleague photo file when Colleague instance is deleted
    """
    if instance.photo:
        delete_file_if_exists(instance.photo.path)
