from django.contrib import admin
from .models import Memory


@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
	list_display = ('title', 'created_at')
	search_fields = ('title', 'description')
	list_filter = ('created_at',)








