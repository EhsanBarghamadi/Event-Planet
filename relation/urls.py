from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegistrationViewSet, FeedbackViewSet, ResultViewSet

router = DefaultRouter()

router.register(r'registration', RegistrationViewSet, basename='registration')
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'result', ResultViewSet, basename='result')

urlpatterns = [
    path('', include(router.urls))
]