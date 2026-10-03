import pytest
from django.urls import reverse
from rest_framework import status

from user.factories import CustomUserFactory
from event.factories import EventFactory


@pytest.mark.django_db
def test_participant_can_register_for_published_event(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(published=True)
    registration_url = reverse("registration-list", kwargs={"version": "v1"})

    client = get_auth_client(participant, password="StrongPass9!x")

    data = {"event_id": event.id}

    response = client.post(registration_url, data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["participant"] == participant.id


@pytest.mark.django_db
def test_organizer_cannot_register_for_event(get_auth_client):
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    event = EventFactory(published=True)
    registration_url = reverse("registration-list", kwargs={"version": "v1"})

    client = get_auth_client(organizer, password="StrongPass9!x")

    data = {"event_id": event.id}

    response = client.post(registration_url, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"].code == "permission_denied"


@pytest.mark.django_db
def test_cannot_register_for_non_published_event(get_auth_client):
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    event = EventFactory(published=True)
    registration_url = reverse("registration-list", kwargs={"version": "v1"})

    client = get_auth_client(organizer, password="StrongPass9!x")

    data = {"event_id": event.id}

    response = client.post(registration_url, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"].code == "permission_denied"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "event_status, expected_status",
    [
        ("draft", status.HTTP_400_BAD_REQUEST),
        ("finished", status.HTTP_400_BAD_REQUEST),
        ("closed", status.HTTP_400_BAD_REQUEST),
        ("ongoing", status.HTTP_400_BAD_REQUEST),
        ("cancelled", status.HTTP_400_BAD_REQUEST),
        ("published", status.HTTP_201_CREATED),
    ],
)
def test_registration_behavior_by_event_status(
    get_auth_client, event_status, expected_status
):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(**{event_status: True})
    registration_url = reverse("registration-list", kwargs={"version": "v1"})

    client = get_auth_client(participant, password="StrongPass9!x")

    data = {"event_id": event.id}

    response = client.post(registration_url, data=data)

    assert response.status_code == expected_status
