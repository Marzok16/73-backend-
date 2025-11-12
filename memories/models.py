from django.db import models


class Memory(models.Model):
	"""A single memory entry with Arabic-friendly fields and an image."""
	title = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	image = models.ImageField(upload_to='memory_photos/')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self) -> str:
		return self.title










