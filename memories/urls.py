from django.urls import path, include
from .views import router, generate_memory_book_pdf


urlpatterns = [
	path('', include(router.urls)),
	path('pdf/book/', generate_memory_book_pdf, name='memory_book_pdf'),
]










