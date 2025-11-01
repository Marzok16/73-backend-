from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'memory-categories', views.MemoryCategoryViewSet)
router.register(r'memory-photos', views.MemoryPhotoViewSet)
router.register(r'meeting-categories', views.MeetingCategoryViewSet)
router.register(r'meeting-photos', views.MeetingPhotoViewSet)
router.register(r'colleagues', views.ColleagueViewSet)

urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    path('health/', views.health_check, name='health_check'),
    path('auth/admin-login/', views.admin_login, name='admin_login'),
    path('', include(router.urls)),
]