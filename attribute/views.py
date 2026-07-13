from rest_framework import viewsets
from rest_framework import permissions

from core.permissions import IsEventOwner
from .serializers import AttributeSerializer, EventAttributeValueSerializer
from .models import Attribute, EventAttributeValue

class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    
    def get_permissions(self):
        if self.action in ['retrieve', 'list']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

class EventAttributeValueViewSet(viewsets.ModelViewSet):
    serializer_class = EventAttributeValueSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role == 'ORGANIZER':
            qs = EventAttributeValue.objects.filter(event__status='PUBLISHED') | EventAttributeValue.objects.filter(event__organizer=user)
        else:
            qs = EventAttributeValue.objects.filter(event__status='PUBLISHED')
        
        event_id = self.request.query_params.get('event_id')
        if event_id:
            qs = qs.filter(event_id=event_id)
        return qs

    def get_permissions(self):
        if self.action in ['retrieve', 'list']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsEventOwner()]