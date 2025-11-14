# Generated migration for adding performance indexes
# This migration is safe and reversible

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),  # Adjust this to your last migration
    ]

    operations = [
        # Add indexes for MemoryCategory
        migrations.AddIndex(
            model_name='memorycategory',
            index=models.Index(fields=['-year', 'name'], name='api_memoryc_year_idx'),
        ),
        migrations.AddIndex(
            model_name='memorycategory',
            index=models.Index(fields=['created_at'], name='api_memoryc_created_idx'),
        ),
        
        # Add indexes for MemoryPhoto
        migrations.AddIndex(
            model_name='memoryphoto',
            index=models.Index(fields=['category', '-created_at'], name='api_memoryp_cat_created_idx'),
        ),
        migrations.AddIndex(
            model_name='memoryphoto',
            index=models.Index(fields=['is_featured'], name='api_memoryp_featured_idx'),
        ),
        migrations.AddIndex(
            model_name='memoryphoto',
            index=models.Index(fields=['-created_at'], name='api_memoryp_created_idx'),
        ),
        
        # Add indexes for MeetingCategory
        migrations.AddIndex(
            model_name='meetingcategory',
            index=models.Index(fields=['-year', 'name'], name='api_meeting_year_idx'),
        ),
        migrations.AddIndex(
            model_name='meetingcategory',
            index=models.Index(fields=['created_at'], name='api_meeting_created_idx'),
        ),
        
        # Add indexes for MeetingPhoto
        migrations.AddIndex(
            model_name='meetingphoto',
            index=models.Index(fields=['category', '-created_at'], name='api_meetingp_cat_created_idx'),
        ),
        migrations.AddIndex(
            model_name='meetingphoto',
            index=models.Index(fields=['is_featured'], name='api_meetingp_featured_idx'),
        ),
        migrations.AddIndex(
            model_name='meetingphoto',
            index=models.Index(fields=['-created_at'], name='api_meetingp_created_idx'),
        ),
        
        # Add indexes for Colleague
        migrations.AddIndex(
            model_name='colleague',
            index=models.Index(fields=['name'], name='api_colleag_name_idx'),
        ),
        migrations.AddIndex(
            model_name='colleague',
            index=models.Index(fields=['status', 'is_featured'], name='api_colleag_status_featured_idx'),
        ),
        migrations.AddIndex(
            model_name='colleague',
            index=models.Index(fields=['graduation_year'], name='api_colleag_grad_year_idx'),
        ),
    ]

