import pytest
from django.urls import reverse
from rest_framework import status

from relation.models import Registration
from user.factories import CustomUserFactory
from event.factories import EventFactory
from relation.factories import RegistrationFactory


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


@pytest.mark.django_db
def test_participant_cannot_register_for_same_event_twice(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(published=True)
    registration_url = reverse("registration-list", kwargs={"version": "v1"})

    client = get_auth_client(participant, password="StrongPass9!x")

    data = {"event_id": event.id}

    response_1 = client.post(registration_url, data=data)
    response_2 = client.post(registration_url, data=data)

    assert response_1.status_code == status.HTTP_201_CREATED
    assert response_1.data["participant"] == participant.id
    assert response_2.status_code == status.HTTP_400_BAD_REQUEST
    assert response_2.data["participant"][0].code == "invalid"


@pytest.mark.django_db
def test_participant_can_register_for_different_published_events(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    event_1 = EventFactory(published=True)
    event_2 = EventFactory(published=True)
    registration_url = reverse("registration-list", kwargs={"version": "v1"})

    client = get_auth_client(participant, password="StrongPass9!x")

    data_1 = {"event_id": event_1.id}
    data_2 = {"event_id": event_2.id}

    response_1 = client.post(registration_url, data=data_1)
    response_2 = client.post(registration_url, data=data_2)

    assert response_1.status_code == status.HTTP_201_CREATED
    assert response_1.data["event"]["id"] == event_1.id
    assert response_2.status_code == status.HTTP_201_CREATED
    assert response_2.data["event"]["id"] == event_2.id


@pytest.mark.django_db
def test_participant_cannot_see_another_participant_registrations(get_auth_client):
    participant_1 = CustomUserFactory(participant=True, password="StrongPass9!x")
    participant_2 = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(published=True)
    RegistrationFactory(participant=participant_1, event=event)
    registration_url = reverse("registration-list", kwargs={"version": "v1"})

    client = get_auth_client(participant_2, password="StrongPass9!x")

    response = client.get(registration_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_participant_cannot_retrieve_another_participant_registration(get_auth_client):
    participant_1 = CustomUserFactory(participant=True, password="StrongPass9!x")
    participant_2 = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(published=True)
    registration = RegistrationFactory(participant=participant_1, event=event)
    registration_url = reverse(
        "registration-detail", kwargs={"version": "v1", "pk": registration.id}
    )

    client = get_auth_client(participant_2, password="StrongPass9!x")

    response = client.get(registration_url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"].code == "not_found"


@pytest.mark.django_db
def test_participant_can_retrieve_own_registration(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(published=True)
    registration = RegistrationFactory(participant=participant, event=event)
    registration_url = reverse(
        "registration-detail", kwargs={"version": "v1", "pk": registration.id}
    )

    client = get_auth_client(participant, password="StrongPass9!x")

    response = client.get(registration_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == registration.id


@pytest.mark.django_db
def test_participant_can_list_own_registrations(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    event_1 = EventFactory(published=True)
    event_2 = EventFactory(published=True)
    registration_1 = RegistrationFactory(participant=participant, event=event_1)
    registration_2 = RegistrationFactory(participant=participant, event=event_2)
    registration_url = reverse("registration-list", kwargs={"version": "v1"})

    client = get_auth_client(participant, password="StrongPass9!x")

    response = client.get(registration_url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert any(
        registration["id"] == registration_1.id for registration in response.data
    )
    assert any(
        registration["id"] == registration_2.id for registration in response.data
    )


@pytest.mark.django_db
def test_participant_cannot_list_another_participant_registrations(get_auth_client):
    participant_1 = CustomUserFactory(participant=True, password="StrongPass9!x")
    participant_2 = CustomUserFactory(participant=True, password="StrongPass9!x")
    event_1 = EventFactory(published=True)
    event_2 = EventFactory(published=True)
    RegistrationFactory(participant=participant_1, event=event_1)
    RegistrationFactory(participant=participant_1, event=event_2)
    registration_url = reverse("registration-list", kwargs={"version": "v1"})

    client = get_auth_client(participant_2, password="StrongPass9!x")

    response = client.get(registration_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_participant_can_delete_own_registration(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(published=True)
    registration = RegistrationFactory(participant=participant, event=event)
    registration_url = reverse(
        "registration-detail", kwargs={"version": "v1", "pk": registration.id}
    )

    client = get_auth_client(participant, password="StrongPass9!x")

    response_1 = client.delete(registration_url)

    assert response_1.status_code == status.HTTP_204_NO_CONTENT
    assert response_1.data is None
    assert not Registration.objects.filter(id=registration.id).exists()
