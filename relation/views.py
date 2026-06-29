from rest_framework import viewsets
from rest_framework import permissions
from core.permissions import IsParticipant
from .models import Registration
from .serializers import RegistrationSerializer

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