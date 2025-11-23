# Generated manually for structured image system
# Migration is non-destructive - all new fields are nullable

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        # Depend on 0019 - Django will resolve the actual parent migration
        ('api', '0019_remove_photo_category_remove_photoalbum_category_and_more'),
    ]

    operations = [
        # Add new image fields to Colleague model (all nullable for safety)
        migrations.AddField(
            model_name='colleague',
            name='photo_1973',
            field=models.ImageField(blank=True, null=True, upload_to='colleague_photos/1973/', verbose_name='صورة 1973'),
        ),
        migrations.AddField(
            model_name='colleague',
            name='latest_photo',
            field=models.ImageField(blank=True, null=True, upload_to='colleague_photos/latest/', verbose_name='الصورة السنوية الأخيرة'),
        ),
        # Create ColleagueArchiveImage model
        migrations.CreateModel(
            name='ColleagueArchiveImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='colleague_photos/archive/', verbose_name='صورة الأرشيف')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='تاريخ الرفع')),
                ('colleague', models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name='archive_photos', to='api.colleague', verbose_name='الزميل')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user', verbose_name='رفع بواسطة')),
            ],
            options={
                'verbose_name': 'صورة أرشيف زميل',
                'verbose_name_plural': 'صور أرشيف الزملاء',
                'ordering': ['-uploaded_at'],
            },
        ),
        # Add index for archive images
        migrations.AddIndex(
            model_name='colleaguearchiveimage',
            index=models.Index(fields=['colleague', '-uploaded_at'], name='colleague_archive_idx'),
        ),
    ]

