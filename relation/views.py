from rest_framework import viewsets
from rest_framework import permissions
from django.db import transaction
from django.db.models import Prefetch

from core.permissions import IsParticipant, IsEventOwner, IsOrganizer, IsFeedbackOwner
from event.models import Event
from attribute.models import EventAttributeValue
from .models import Registration, Feedback, Result
from .serializers import (
    RegistrationSerializer,
    FeedbackSerializer,
    ResultSerializer,
    RegistrationReadOnlySerializer,
)


class RegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = RegistrationSerializer
    http_method_names = ["get", "post", "delete"]

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsParticipant()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        if getattr(self, "swagger_fake_view", False):
            return Registration.objects.none()

        return Registration.objects.select_related("event").filter(participant=user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(participant=self.request.user)


class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        user = self.request.user
        base = Feedback.objects.select_related("event").prefetch_related(
            Prefetch(
            "event__attribute_values",
            queryset=EventAttributeValue.objects.select_related("attribute"),
        )
        )
        if getattr(self, "swagger_fake_view", False):
            return Feedback.objects.none()
        if user.role == "PARTICIPANT":
            return base.filter(participant=user)
        if user.role == "ORGANIZER" and user.events.exists():
            return base.filter(event__organizer=user)
        return Feedback.objects.none()

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsParticipant()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsParticipant(), IsFeedbackOwner()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(participant=self.request.user)


class ResultViewSet(viewsets.ModelViewSet):
    serializer_class = ResultSerializer

    def get_permissions(self):
        if self.action in ["create", "partial_update", "update", "destroy"]:
            return [permissions.IsAuthenticated(), IsOrganizer(), IsEventOwner()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Result.objects.none()
        base = Result.objects.select_related("event", "participant").prefetch_related(
            "event__attribute_values__attribute"
        )
        if user.role == "PARTICIPANT":
            return base.filter(
                event__status="FINISHED", event__registrations__participant=user
            )
        if user.role == "ORGANIZER":
            return base.filter(event__status="FINISHED", event__organizer=user)
        if user.role == "STAFF":
            return base.filter(event__status="FINISHED")
        return Result.objects.none()
