from rest_framework import viewsets
from rest_framework import permissions
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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        event_id = self.request.query_params.get('event_id')
        if event_id:
            return EventAttributeValue.objects.filter(event_id=event_id)
        return EventAttributeValue.objects.all()