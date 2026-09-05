import pytest
from django.urls import reverse
from rest_framework import status

from event.factories import EventFactory
from relation.factories import RegistrationFactory
from user.factories import CustomUserFactory


@pytest.mark.django_db
def test_guest_can_only_see_published_events(api_client):
    event_list_url = reverse("event-list", kwargs={"version": "v1"})
    draft_event = EventFactory()
    published_event = EventFactory(published=True)

    response = api_client.get(event_list_url)

    assert response.status_code == status.HTTP_200_OK
    assert any(event["id"] == published_event.id for event in response.data)
    assert all(event["id"] != draft_event.id for event in response.data)


@pytest.mark.django_db
def test_guest_cannot_retrieve_draft_event(api_client):
    draft_event = EventFactory()
    event_detail_url = reverse(
        "event-detail", kwargs={"version": "v1", "pk": draft_event.id}
    )

    response = api_client.get(event_detail_url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_guest_can_retrieve_published_event(api_client):
    published_event = EventFactory(published=True)
    event_detail_url = reverse(
        "event-detail", kwargs={"version": "v1", "pk": published_event.id}
    )

    response = api_client.get(event_detail_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == published_event.id


@pytest.mark.django_db
def test_organizer_can_see_published_events_and_own_drafts(get_auth_client):
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    other_organizer = CustomUserFactory(organizer=True)
    my_draft = EventFactory(organizer=organizer)
    my_published = EventFactory(organizer=organizer, published=True)
    other_draft = EventFactory(organizer=other_organizer)
    other_published = EventFactory(organizer=other_organizer, published=True)

    client = get_auth_client(organizer, password="StrongPass9!x")

    event_list_url = reverse("event-list", kwargs={"version": "v1"})

    response = client.get(event_list_url)

    assert response.status_code == status.HTTP_200_OK
    assert any(event["id"] == my_draft.id for event in response.data)
    assert any(event["id"] == my_published.id for event in response.data)
    assert any(event["id"] == other_published.id for event in response.data)
    assert all(event["id"] != other_draft.id for event in response.data)


@pytest.mark.django_db
def test_organizer_can_create_event(get_auth_client):
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    other_organizer = CustomUserFactory(organizer=True)

    event_url = reverse("event-list", kwargs={"version": "v1"})

    event_data = {
        "organizer": other_organizer.id,
        "capacity": 150,
        "end_date": "2026-12-20T18:00:00Z",
        "start_date": "2026-11-01T09:00:00Z",
        "title": "همایش تخصصی هوش مصنوعی و یادگیری ماشین",
        "description": "این همایش با هدف آشنایی با جدیدترین دستاوردهای حوزه هوش مصنوعی و کاربردهای آن در صنعت برگزار می‌شود. حضور برای عموم آزاد است.",
        "status": "DRAFT",
    }

    client = get_auth_client(organizer, password="StrongPass9!x")
    response = client.post(event_url, data=event_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["organizer"] == organizer.id
    assert response.data["status"] == "DRAFT"
    assert response.data["capacity"] == 150


@pytest.mark.django_db
def test_participant_cannot_create_event(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")

    event_url = reverse("event-list", kwargs={"version": "v1"})

    event_data = {
        "organizer": participant.id,
        "capacity": 150,
        "end_date": "2026-12-20T18:00:00Z",
        "start_date": "2026-11-01T09:00:00Z",
        "title": "همایش تخصصی هوش مصنوعی و یادگیری ماشین",
        "description": "این همایش با هدف آشنایی با جدیدترین دستاوردهای حوزه هوش مصنوعی و کاربردهای آن در صنعت برگزار می‌شود. حضور برای عموم آزاد است.",
        "status": "DRAFT",
    }

    client = get_auth_client(participant, password="StrongPass9!x")
    response = client.post(event_url, data=event_data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"].code == "permission_denied"


@pytest.mark.django_db
def test_guest_cannot_create_event(api_client):
    event_url = reverse("event-list", kwargs={"version": "v1"})

    event_data = {
        "capacity": 150,
        "end_date": "2026-12-20T18:00:00Z",
        "start_date": "2026-11-01T09:00:00Z",
        "title": "همایش تخصصی هوش مصنوعی و یادگیری ماشین",
        "description": "این همایش با هدف آشنایی با جدیدترین دستاوردهای حوزه هوش مصنوعی و کاربردهای آن در صنعت برگزار می‌شود. حضور برای عموم آزاد است.",
        "status": "DRAFT",
    }

    response = api_client.post(event_url, data=event_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["detail"].code == "not_authenticated"


@pytest.mark.django_db
def test_event_owner_can_update_event(get_auth_client):
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    event = EventFactory(organizer=organizer)

    client = get_auth_client(organizer, password="StrongPass9!x")

    event_detail_url = reverse("event-detail", kwargs={"version": "v1", "pk": event.id})

    data = {"title": "همایش تخصصی هوش مصنوعی و یادگیری ماشین"}

    response = client.patch(event_detail_url, data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "همایش تخصصی هوش مصنوعی و یادگیری ماشین"


@pytest.mark.django_db
def test_organizer_cannot_update_other_organizers_event(get_auth_client):
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    other_organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")

    event = EventFactory(organizer=organizer)

    client = get_auth_client(other_organizer, password="StrongPass9!x")

    event_detail_url = reverse("event-detail", kwargs={"version": "v1", "pk": event.id})

    data = {"title": "همایش تخصصی هوش مصنوعی و یادگیری ماشین"}

    response = client.patch(event_detail_url, data)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_organizer_can_publish_draft_event(get_auth_client):
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")

    event = EventFactory(organizer=organizer)

    client = get_auth_client(organizer, password="StrongPass9!x")

    data = {"status": "PUBLISHED"}

    event_detail_url = reverse("event-detail", kwargs={"version": "v1", "pk": event.id})

    response = client.patch(event_detail_url, data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == "PUBLISHED"


@pytest.mark.django_db
def test_organizer_cannot_finish_draft_event(get_auth_client):
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")

    event = EventFactory(organizer=organizer)

    client = get_auth_client(organizer, password="StrongPass9!x")

    data = {"status": "FINISHED"}

    event_detail_url = reverse("event-detail", kwargs={"version": "v1", "pk": event.id})

    response = client.patch(event_detail_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_organizer_cannot_finish_draft_event(get_auth_client):
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")

    event = EventFactory(organizer=organizer)

    client = get_auth_client(organizer, password="StrongPass9!x")

    data = {"status": "FINISHED"}

    event_detail_url = reverse("event-detail", kwargs={"version": "v1", "pk": event.id})

    response = client.patch(event_detail_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_organizer_cannot_set_capacity_below_registration_count(get_auth_client):
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")

    event = EventFactory(published=True, organizer=organizer, capacity=5)

    participant1 = CustomUserFactory(participant=True)
    participant2 = CustomUserFactory(participant=True)
    participant3 = CustomUserFactory(participant=True)

    RegistrationFactory(participant=participant1, event=event)
    RegistrationFactory(participant=participant2, event=event)
    RegistrationFactory(participant=participant3, event=event)


    client = get_auth_client(organizer, password="StrongPass9!x")

    event_detail_url = reverse("event-detail", kwargs={"version": "v1", "pk": event.id})

    data = {"capacity": 2}

    response = client.patch(event_detail_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
