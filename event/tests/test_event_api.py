import pytest
from django.urls import reverse
from rest_framework import status

from event.factories import EventFactory


@pytest.mark.django_db
def test_guest_can_only_see_published_events(api_client):
    event_list_url = reverse("event-list", kwargs={"version": "v1"})
    draft_event = EventFactory()
    published_event = EventFactory(published=True)

    response = api_client.get(event_list_url)

    assert response.status_code == status.HTTP_200_OK
    assert any(event['id'] == published_event.id for event in response.data)
    assert all(event['id'] != draft_event.id for event in response.data)

@pytest.mark.django_db
def test_guest_cannot_retrieve_draft_event(api_client):
    draft_event = EventFactory()
    event_detail_url = reverse("event-detail", kwargs={"version": "v1", "pk": draft_event.id})

    response = api_client.get(event_detail_url)

    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_guest_can_retrieve_published_event(api_client):
    published_event = EventFactory(published=True)
    event_detail_url = reverse("event-detail", kwargs={"version": "v1", "pk": published_event.id})

    response = api_client.get(event_detail_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == published_event.id