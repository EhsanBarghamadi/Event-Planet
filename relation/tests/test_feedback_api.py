import pytest
from django.urls import reverse
from rest_framework import status

from relation.models import Feedback
from user.factories import CustomUserFactory
from event.factories import EventFactory
from relation.factories import RegistrationFactory, FeedbackFactory


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


@pytest.mark.django_db
def test_participant_cannot_list_another_participant_feedback(get_auth_client):
    participant_1 = CustomUserFactory(participant=True, password="StrongPass9!x")
    participant_2 = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(finished=True)
    RegistrationFactory(participant=participant_1, event=event)
    RegistrationFactory(participant=participant_2, event=event)
    FeedbackFactory(participant=participant_1, event=event)
    feedback_url = reverse("feedback-list", kwargs={"version": "v1"})

    client = get_auth_client(participant_2, password="StrongPass9!x")

    response = client.get(feedback_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_participant_can_list_own_feedback(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(finished=True)
    RegistrationFactory(participant=participant, event=event)
    feedback = FeedbackFactory(participant=participant, event=event)
    feedback_url = reverse("feedback-list", kwargs={"version": "v1"})

    client = get_auth_client(participant, password="StrongPass9!x")

    response = client.get(feedback_url)

    assert response.status_code == status.HTTP_200_OK
    assert any(item["participant"] == participant.id for item in response.data)
    assert any(item["comment"] == feedback.comment for item in response.data)


@pytest.mark.django_db
def test_participant_cannot_retrieve_another_participant_feedback(get_auth_client):
    participant_1 = CustomUserFactory(participant=True, password="StrongPass9!x")
    participant_2 = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(finished=True)
    RegistrationFactory(participant=participant_1, event=event)
    RegistrationFactory(participant=participant_2, event=event)
    feedback = FeedbackFactory(participant=participant_1, event=event)
    feedback_url = reverse(
        "feedback-detail", kwargs={"version": "v1", "pk": feedback.id}
    )

    client = get_auth_client(participant_2, password="StrongPass9!x")

    response = client.get(feedback_url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"].code == "not_found"


@pytest.mark.django_db
def test_participant_can_retrieve_own_feedback(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(finished=True)
    RegistrationFactory(participant=participant, event=event)
    feedback = FeedbackFactory(participant=participant, event=event)
    feedback_url = reverse(
        "feedback-detail", kwargs={"version": "v1", "pk": feedback.id}
    )

    client = get_auth_client(participant, password="StrongPass9!x")

    response = client.get(feedback_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["comment"] == feedback.comment


@pytest.mark.django_db
def test_organizer_can_list_participant_feedback(get_auth_client):
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(finished=True, organizer=organizer)
    RegistrationFactory(participant=participant, event=event)
    feedback = FeedbackFactory(participant=participant, event=event)
    feedback_url = reverse("feedback-list", kwargs={"version": "v1"})

    client = get_auth_client(organizer, password="StrongPass9!x")

    response = client.get(feedback_url)

    assert response.status_code == status.HTTP_200_OK
    assert any(item["comment"] == feedback.comment for item in response.data)


@pytest.mark.django_db
def test_organizer_can_retrieve_participant_feedback(get_auth_client):
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(finished=True, organizer=organizer)
    RegistrationFactory(participant=participant, event=event)
    feedback = FeedbackFactory(participant=participant, event=event)
    feedback_url = reverse(
        "feedback-detail", kwargs={"version": "v1", "pk": feedback.id}
    )

    client = get_auth_client(organizer, password="StrongPass9!x")

    response = client.get(feedback_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["comment"] == feedback.comment


@pytest.mark.django_db
def test_participant_can_update_own_feedback(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(finished=True)
    RegistrationFactory(participant=participant, event=event)
    feedback = FeedbackFactory(participant=participant, event=event)
    feedback_url = reverse(
        "feedback-detail", kwargs={"version": "v1", "pk": feedback.id}
    )

    data = {"comment": "پیام جدید"}

    client = get_auth_client(participant, password="StrongPass9!x")

    response = client.patch(feedback_url, data=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["comment"] == "پیام جدید"


@pytest.mark.django_db
def test_participant_cannot_update_another_participant_feedback(get_auth_client):
    participant_1 = CustomUserFactory(participant=True, password="StrongPass9!x")
    participant_2 = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(finished=True)
    RegistrationFactory(participant=participant_1, event=event)
    feedback = FeedbackFactory(participant=participant_1, event=event)
    feedback_url = reverse(
        "feedback-detail", kwargs={"version": "v1", "pk": feedback.id}
    )

    data = {"comment": "پیام جدید"}

    client = get_auth_client(participant_2, password="StrongPass9!x")

    response = client.patch(feedback_url, data=data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"].code == "not_found"


@pytest.mark.django_db
def test_participant_can_delete_own_feedback(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(finished=True)
    RegistrationFactory(participant=participant, event=event)
    feedback = FeedbackFactory(participant=participant, event=event)
    feedback_url = reverse(
        "feedback-detail", kwargs={"version": "v1", "pk": feedback.id}
    )

    client = get_auth_client(participant, password="StrongPass9!x")

    response = client.delete(feedback_url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.data is None
    assert not Feedback.objects.filter(id=feedback.id).exists()


@pytest.mark.django_db
def test_participant_cannot_delete_another_participant_feedback(get_auth_client):
    participant_1 = CustomUserFactory(participant=True, password="StrongPass9!x")
    participant_2 = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(finished=True)
    RegistrationFactory(participant=participant_1, event=event)
    feedback = FeedbackFactory(participant=participant_1, event=event)
    feedback_url = reverse(
        "feedback-detail", kwargs={"version": "v1", "pk": feedback.id}
    )

    client = get_auth_client(participant_2, password="StrongPass9!x")

    response = client.delete(feedback_url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"].code == "not_found"
    assert Feedback.objects.filter(id=feedback.id).exists()
