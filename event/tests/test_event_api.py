import pytest
from django.urls import reverse
from rest_framework import status

from event.factories import EventFactory
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
        "status": "DRAFT"
        }

    client = get_auth_client(organizer, password="StrongPass9!x")
    response = client.post(event_url, data=event_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["organizer"] == organizer.id
    assert response.data["status"] == "DRAFT"
    assert response.data["capacity"] == 150
