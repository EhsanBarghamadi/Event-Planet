from rest_framework import viewsets
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.response import Response

from core.permissions import IsOrganizer, IsEventOwner
from relation.models import Registration
from relation.serializers import RegistrationReadOnlySerializer
from .models import Event, EventStage
from .serializers import EventSerializer, EventStageSerializer

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
        if self.action == 'participants':
            return [permissions.IsAuthenticated(), IsOrganizer()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        event = Event.objects.filter(id=pk, organizer=request.user)
        if not event.exists():
            raise PermissionDenied('شما مالک این رویداد نیستید یا چنین رویدادی وجود ندارد!')
        registrations = Registration.objects.filter(event_id=pk).select_related('participant')
        serializer = RegistrationReadOnlySerializer(registrations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class EventStageViewSet(viewsets.ModelViewSet):
    serializer_class = EventStageSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOrganizer(), IsEventOwner()]
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role == 'ORGANIZER':
            return EventStage.objects.filter(event__status='PUBLISHED') | EventStage.objects.filter(event__organizer=user)
        return  EventStage.objects.filter(event__status='PUBLISHED')