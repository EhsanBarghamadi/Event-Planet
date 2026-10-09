import pytest
from django.urls import reverse
from rest_framework import status

from user.factories import CustomUserFactory
from event.factories import EventFactory
from relation.factories import RegistrationFactory, ResultFactory


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


@pytest.mark.django_db
def test_participant_cannot_create_result(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    event = EventFactory(finished=True, organizer=organizer)
    RegistrationFactory(participant=participant, event=event)
    result_url = reverse("result-list", kwargs={"version": "v1"})

    client = get_auth_client(participant, password="StrongPass9!x")

    data = {
        "achievement": "کسب مقام اول",
        "event_id": event.id,
        "participant_id": participant.id,
    }

    response = client.post(result_url, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"].code == "permission_denied"


@pytest.mark.django_db
def test_participant_can_list_event_results(get_auth_client):
    participant_1 = CustomUserFactory(participant=True, password="StrongPass9!x")
    participant_2 = CustomUserFactory(participant=True, password="StrongPass9!x")
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    event = EventFactory(finished=True, organizer=organizer)
    RegistrationFactory(participant=participant_1, event=event)
    RegistrationFactory(participant=participant_2, event=event)
    result = ResultFactory(participant=participant_1, event=event)
    result_url = reverse("result-list", kwargs={"version": "v1"})

    client = get_auth_client(participant_2, password="StrongPass9!x")

    response = client.get(result_url)

    assert response.status_code == status.HTTP_200_OK
    assert any(item["achievement"] == result.achievement for item in response.data)


@pytest.mark.django_db
def test_participant_can_retrieve_own_result(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    event = EventFactory(finished=True, organizer=organizer)
    RegistrationFactory(participant=participant, event=event)
    result = ResultFactory(participant=participant, event=event)

    result_url = reverse(
        "result-detail",
        kwargs={"version": "v1", "pk": result.id},
    )

    client = get_auth_client(participant, password="StrongPass9!x")

    response = client.get(result_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["achievement"] == result.achievement


@pytest.mark.django_db
def test_participant_cannot_retrieve_another_participant_result(get_auth_client):
    participant_1 = CustomUserFactory(participant=True, password="StrongPass9!x")
    participant_2 = CustomUserFactory(participant=True, password="StrongPass9!x")
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    event = EventFactory(finished=True, organizer=organizer)
    RegistrationFactory(participant=participant_1, event=event)
    result = ResultFactory(participant=participant_1, event=event)
    result_url = reverse(
        "result-detail",
        kwargs={"version": "v1", "pk": result.id},
    )

    client = get_auth_client(participant_2, password="StrongPass9!x")

    response = client.get(result_url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"].code == "not_found"


@pytest.mark.django_db
def test_organizer_can_list_own_event_results(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    event = EventFactory(finished=True, organizer=organizer)
    RegistrationFactory(participant=participant, event=event)
    result = ResultFactory(participant=participant, event=event)
    result_url = reverse("result-list", kwargs={"version": "v1"})

    client = get_auth_client(organizer, password="StrongPass9!x")

    response = client.get(result_url)

    assert response.status_code == status.HTTP_200_OK
    assert any(item["achievement"] == result.achievement for item in response.data)


@pytest.mark.django_db
def test_organizer_cannot_list_another_organizer_event_results(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    organizer_1 = CustomUserFactory(organizer=True, password="StrongPass9!x")
    organizer_2 = CustomUserFactory(organizer=True, password="StrongPass9!x")
    event = EventFactory(finished=True, organizer=organizer_1)
    RegistrationFactory(participant=participant, event=event)
    result = ResultFactory(participant=participant, event=event)
    result_url = reverse("result-list", kwargs={"version": "v1"})

    client = get_auth_client(organizer_2, password="StrongPass9!x")

    response = client.get(result_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_organizer_can_retrieve_own_event_result(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    event = EventFactory(finished=True, organizer=organizer)
    RegistrationFactory(participant=participant, event=event)
    result = ResultFactory(participant=participant, event=event)
    result_url = reverse(
        "result-detail",
        kwargs={"version": "v1", "pk": result.id},
    )

    client = get_auth_client(organizer, password="StrongPass9!x")

    response = client.get(result_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["achievement"] == result.achievement


@pytest.mark.django_db
def test_organizer_cannot_retrieve_another_organizer_event_result(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    organizer_1 = CustomUserFactory(organizer=True, password="StrongPass9!x")
    organizer_2 = CustomUserFactory(organizer=True, password="StrongPass9!x")
    event = EventFactory(finished=True, organizer=organizer_1)
    RegistrationFactory(participant=participant, event=event)
    result = ResultFactory(participant=participant, event=event)
    result_url = reverse(
        "result-detail",
        kwargs={"version": "v1", "pk": result.id},
    )

    client = get_auth_client(organizer_2, password="StrongPass9!x")

    response = client.get(result_url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_participant_cannot_list_unregistered_event_results(get_auth_client):
    participant_1 = CustomUserFactory(participant=True, password="StrongPass9!x")
    participant_2 = CustomUserFactory(participant=True, password="StrongPass9!x")
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    event = EventFactory(finished=True, organizer=organizer)
    RegistrationFactory(participant=participant_1, event=event)
    ResultFactory(participant=participant_1, event=event)
    result_url = reverse("result-list", kwargs={"version": "v1"})

    client = get_auth_client(participant_2, password="StrongPass9!x")

    response = client.get(result_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []

