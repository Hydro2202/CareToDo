from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NurseViewSet, TaskViewSet, home

router = DefaultRouter()
router.register(r'nurses', NurseViewSet)
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    path('', home, name='home'),
    path('api/', include(router.urls)),
]