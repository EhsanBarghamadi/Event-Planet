from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, EventStageViewSet

router = DefaultRouter()

router.register(r'event', EventViewSet, basename='event')
router.register(r'eventstage', EventStageViewSet, basename='eventstage')

urlpatterns = [
    path('', include(router.urls))
]