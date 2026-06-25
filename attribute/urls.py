from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventAttributeValueViewSet, AttributeViewSet

router = DefaultRouter()

router.register(r'eventattributevalue', EventAttributeValueViewSet, basename='eventattributevalue')
router.register(r'attribute', AttributeViewSet, basename='attribute')

urlpatterns = [
    path('api/', include(router.urls)),
]