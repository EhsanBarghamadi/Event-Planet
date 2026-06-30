from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegistrationViewSet, FeedbackViewSet

router = DefaultRouter()

router.register(r'registration', RegistrationViewSet, basename='registration')
router.register(r'feedback', FeedbackViewSet, basename='feedback')

urlpatterns = [
    path('', include(router.urls))
]