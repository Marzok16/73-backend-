from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.routers import DefaultRouter
from django.conf import settings
from .models import Memory
from .serializers import MemorySerializer
from api.models import MemoryCategory, MeetingCategory, Colleague


class MemoryViewSet(ReadOnlyModelViewSet):
	queryset = Memory.objects.all()
	serializer_class = MemorySerializer
	permission_classes: list = []

	def list(self, request, *args, **kwargs):
		serializer = self.get_serializer(self.get_queryset(), many=True, context={'request': request})
		return Response(serializer.data)


@api_view(['GET'])
def generate_memory_book_pdf(request):
	"""Generate Arabic-friendly PDF for all website photos grouped by sections."""
	import os
	import sys
	import platform
	import traceback
	
	# Add GTK bin directory to PATH for WeasyPrint (Windows only)
	# On Linux/cloud servers, system libraries should be installed via apt/yum
	if platform.system() == 'Windows':
		gtk_bin_path = r'C:\Program Files\GTK3-Runtime Win64\bin'
		if os.path.exists(gtk_bin_path) and gtk_bin_path not in os.environ.get('PATH', ''):
			os.environ['PATH'] = gtk_bin_path + os.pathsep + os.environ.get('PATH', '')
	
	try:
		from weasyprint import HTML, CSS
	except ImportError as e:
		error_details = traceback.format_exc()
		return HttpResponse(
			(
				"WeasyPrint is not installed. Error: " + str(e) + "\n\n"
				"Please install WeasyPrint: pip install weasyprint\n\n"
				"Full traceback:\n" + error_details
			),
			status=500,
			content_type="text/plain",
		)
	except Exception as e:
		# Check if it's a missing system library issue (common on Linux)
		error_details = traceback.format_exc()
		error_msg = str(e).lower()
		if 'pango' in error_msg or 'cairo' in error_msg or 'lib' in error_msg:
			return HttpResponse(
				(
					"WeasyPrint system dependencies missing.\n\n"
					"On Linux servers, install:\n"
					"  sudo apt-get install -y python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0\n"
					"  sudo apt-get install -y libharfbuzz0b libpango-1.0-0 libpangocairo-1.0-0\n"
					"  sudo apt-get install -y libgdk-pixbuf2.0-0 libffi-dev shared-mime-info\n\n"
					"On Render: Add these to build command or use Docker.\n\n"
					"Error details: " + str(e) + "\n\n"
					"Full traceback:\n" + error_details
				),
				status=500,
				content_type="text/plain",
			)
		else:
			return HttpResponse(
				(
					"WeasyPrint initialization failed. Error: " + str(e) + "\n\n"
					"Full traceback:\n" + error_details
				),
				status=500,
				content_type="text/plain",
			)
	
	# Get all memory categories with their photos (صور تذكارية)
	memory_categories = MemoryCategory.objects.prefetch_related('photos').all().order_by('name')
	
	# Get all meeting categories with their photos (اللقاءات)
	meeting_categories = MeetingCategory.objects.prefetch_related('photos').all().order_by('name')
	
	# Get all colleagues (الزملاء)
	colleagues = Colleague.objects.all().order_by('name')
	
	# Historical photos data (static images from frontend)
	# These will need to be accessible via the media URL or frontend assets
	historical_photos_data = [
		{'section': 'صور تذكارية تاريخية', 'photos': []},  # Will be populated from HistoricalPhotos page data
		{'section': 'صور فترة التأسيس', 'photos': []},  # From Timeline founding images
		{'section': 'تطور شعار الجامعة', 'photos': []},  # From Timeline emblem images
	]
	
	# Build absolute URLs for media files
	media_url = request.build_absolute_uri('/').rstrip('/') + '/media/'
	
	context = {
		'memory_categories': memory_categories,
		'meeting_categories': meeting_categories,
		'colleagues': colleagues,
		'base_url': request.build_absolute_uri('/'),
		'media_url': media_url,
		'has_memory_photos': memory_categories.filter(photos__isnull=False).exists(),
		'has_meeting_photos': meeting_categories.filter(photos__isnull=False).exists(),
		'has_colleagues': colleagues.exists(),
	}
	
	try:
		html_content = render_to_string('pdf/memory_book.html', context)
		# Create HTML document with base_url for resolving image paths
		html = HTML(string=html_content, base_url=context['base_url'])
		# Generate PDF (CSS in template will be used automatically)
		pdf_bytes = html.write_pdf()
		response = HttpResponse(pdf_bytes, content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="memory_book.pdf"'
		return response
	except Exception as e:
		import traceback
		error_details = traceback.format_exc()
		return HttpResponse(
			(
				"WeasyPrint PDF generation failed. Error details:\n\n"
				+ str(e) + "\n\n"
				"Make sure GTK3 Runtime is installed and PATH includes 'C:\\Program Files\\GTK3-Runtime Win64\\bin'\n"
				"Restart the Django server after updating PATH.\n\n"
				"Full traceback:\n" + error_details
			),
			status=500,
			content_type="text/plain",
		)


router = DefaultRouter()
router.register(r'memories', MemoryViewSet, basename='memory')


