import pytest
from django.urls import reverse
from rest_framework import status

from user.factories import CustomUserFactory
from event.factories import EventFactory
from relation.factories import RegistrationFactory


@pytest.mark.django_db
def test_participant_can_create_feedback_for_finished_event(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(finished=True)
    RegistrationFactory(participant=participant, event=event)
    feedback_url = reverse("feedback-list", kwargs={"version": "v1"})

    client = get_auth_client(participant, password="StrongPass9!x")

    data = {"event_id": event.id, "rating": 1, "comment": "اصلا از این دوره خوشم نیومد"}

    response = client.post(feedback_url, data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["participant"] == participant.id
    assert response.data["event"]["id"] == event.id


@pytest.mark.django_db
@pytest.mark.parametrize(
    "event_status, expected_status",
    [
        ("draft", status.HTTP_400_BAD_REQUEST),
        ("closed", status.HTTP_400_BAD_REQUEST),
        ("ongoing", status.HTTP_400_BAD_REQUEST),
        ("cancelled", status.HTTP_400_BAD_REQUEST),
        ("published", status.HTTP_400_BAD_REQUEST),
    ],
)
def test_participant_cannot_create_feedback_for_unfinished_event(
    get_auth_client, event_status, expected_status
):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(**{event_status: True})
    RegistrationFactory(participant=participant, event=event)
    feedback_url = reverse("feedback-list", kwargs={"version": "v1"})

    client = get_auth_client(participant, password="StrongPass9!x")

    data = {"event_id": event.id, "rating": 1, "comment": "اصلا از این دوره خوشم نیومد"}

    response = client.post(feedback_url, data=data)

    assert response.status_code == expected_status


@pytest.mark.django_db
def test_unregistered_participant_cannot_create_feedback(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(finished=True)
    feedback_url = reverse("feedback-list", kwargs={"version": "v1"})

    client = get_auth_client(participant, password="StrongPass9!x")

    data = {"event_id": event.id, "rating": 1, "comment": "اصلا از این دوره خوشم نیومد"}

    response = client.post(feedback_url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_participant_cannot_create_duplicate_feedback(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(finished=True)
    RegistrationFactory(participant=participant, event=event)
    feedback_url = reverse("feedback-list", kwargs={"version": "v1"})

    client = get_auth_client(participant, password="StrongPass9!x")

    data_1 = {
        "event_id": event.id,
        "rating": 1,
        "comment": "اصلا از این دوره خوشم نیومد",
    }
    data_2 = {"event_id": event.id, "rating": 4, "comment": "از دوره بدم نیومد"}

    response_1 = client.post(feedback_url, data=data_1)
    response_2 = client.post(feedback_url, data=data_2)

    assert response_1.status_code == status.HTTP_201_CREATED
    assert response_2.status_code == status.HTTP_400_BAD_REQUEST
    assert response_1.data["participant"] == participant.id
    assert response_2.data["participant"][0].code == "invalid"
