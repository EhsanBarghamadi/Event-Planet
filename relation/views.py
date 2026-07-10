from rest_framework import viewsets
from rest_framework import permissions

from core.permissions import IsParticipant, IsEventOwner, IsOrganizer
from event.models import Event
from .models import Registration, Feedback, Result
from .serializers import RegistrationSerializer, FeedbackSerializer, ResultSerializer, RegistrationReadOnlySerializer

class RegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = RegistrationSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsParticipant()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        return Registration.objects.select_related('event').filter(participant=user)

    def perform_create(self, serializer):
        serializer.save(participant=self.request.user)

class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'PARTICIPANT':
            return Feedback.objects.filter(participant=user)
        if user.role == 'ORGANIZER' and user.events.exists():
            return Feedback.objects.filter(event__organizer=user)
        return Feedback.objects.none()
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsParticipant()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save(participant=self.request.user)

class ResultViewSet(viewsets.ModelViewSet):
    serializer_class = ResultSerializer

    def get_permissions(self):
        if self.action in ['create', 'partial_update', 'update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOrganizer(), IsEventOwner()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return Result.objects.filter(event__status='FINISHED')