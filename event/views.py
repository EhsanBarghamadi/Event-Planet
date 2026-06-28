from rest_framework import viewsets
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from core.permissions import IsOrganizer, IsEventOwner
from .models import Event
from .serializer import EventSerializer

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['status']
    search_fields = ['title', 'description']

    def get_queryset(self):
        user = self.request.user
        if self.action in ['list', 'retrieve']:
            if user.is_authenticated and user.role == 'ORGANIZER':
                return Event.objects.filter(status='PUBLISHED') | Event.objects.filter(organizer=user)
            return Event.objects.filter(status='PUBLISHED')
        return Event.objects.all()
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsOrganizer()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOrganizer(), IsEventOwner()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)