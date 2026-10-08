import pytest
from django.urls import reverse
from rest_framework import status

from user.factories import CustomUserFactory
from event.factories import EventFactory
from relation.factories import RegistrationFactory


@pytest.mark.django_db
def test_organizer_can_create_result_for_finished_event(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    event = EventFactory(finished=True, organizer=organizer)
    RegistrationFactory(participant=participant, event=event)
    result_url = reverse("result-list", kwargs={"version": "v1"})

    client = get_auth_client(organizer, password="StrongPass9!x")

    data = {
        "achievement": "کسب مقام اول",
        "event_id": event.id,
        "participant_id": participant.id,
    }

    response = client.post(result_url, data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["event"]["id"] == event.id
    assert response.data["participant"]["id"] == participant.id


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
def test_organizer_cannot_create_result_for_unfinished_event(
    get_auth_client, event_status, expected_status
):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    event = EventFactory(**{event_status: True}, organizer=organizer)
    RegistrationFactory(participant=participant, event=event)
    result_url = reverse("result-list", kwargs={"version": "v1"})

    client = get_auth_client(organizer, password="StrongPass9!x")

    data = {
        "achievement": "کسب مقام اول",
        "event_id": event.id,
        "participant_id": participant.id,
    }

    response = client.post(result_url, data=data)

    assert response.status_code == expected_status


@pytest.mark.django_db
def test_organizer_cannot_create_result_for_unregistered_participant(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    event = EventFactory(finished=True, organizer=organizer)
    result_url = reverse("result-list", kwargs={"version": "v1"})

    client = get_auth_client(organizer, password="StrongPass9!x")

    data = {
        "achievement": "کسب مقام اول",
        "event_id": event.id,
        "participant_id": participant.id,
    }

    response = client.post(result_url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["participant"][0].code == "invalid"

@pytest.mark.django_db
def test_organizer_cannot_create_duplicate_result(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    event = EventFactory(finished=True, organizer=organizer)
    RegistrationFactory(participant=participant, event=event)
    result_url = reverse("result-list", kwargs={"version": "v1"})

    client = get_auth_client(organizer, password="StrongPass9!x")

    data_1 = {
        "achievement": "کسب مقام اول",
        "event_id": event.id,
        "participant_id": participant.id,
    }
    data_2 = {
        "achievement": "کسب مقام دوم",
        "event_id": event.id,
        "participant_id": participant.id,
    }

    response_1 = client.post(result_url, data=data_1)
    response_2 = client.post(result_url, data=data_2)

    assert response_1.status_code == status.HTTP_201_CREATED
    assert response_1.data["event"]["id"] == event.id
    assert response_1.data["participant"]["id"] == participant.id
    assert response_2.status_code == status.HTTP_400_BAD_REQUEST
    assert response_2.data["non_field_errors"][0].code == "unique"
