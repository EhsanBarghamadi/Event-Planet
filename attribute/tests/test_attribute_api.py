import pytest
from django.urls import reverse
from rest_framework import status

from user.factories import CustomUserFactory
from attribute.factories import AttributeFactory, EventAttributeValueFactory
from event.factories import EventFactory


@pytest.mark.django_db
def test_guest_cannot_list_attributes(api_client):
    list_attributes_url = reverse("attribute-list", kwargs={"version": "v1"})
    response = api_client.get(list_attributes_url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["detail"].code == "not_authenticated"


@pytest.mark.django_db
def test_authenticated_user_can_list_attributes(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    attribute = AttributeFactory()
    list_attributes_url = reverse("attribute-list", kwargs={"version": "v1"})

    client = get_auth_client(participant, password="StrongPass9!x")

    response = client.get(list_attributes_url)

    assert response.status_code == status.HTTP_200_OK
    assert any(attr["id"] == attribute.id for attr in response.data)


@pytest.mark.django_db
def test_non_staff_organizer_cannot_create_attribute(get_auth_client):
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")

    list_attributes_url = reverse("attribute-list", kwargs={"version": "v1"})

    client = get_auth_client(organizer, password="StrongPass9!x")

    data = {
        "data_type": "BOOLEAN",
        "name": "برگزاری جلسه",
    }

    response = client.post(list_attributes_url, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"].code == "permission_denied"


@pytest.mark.django_db
def test_staff_user_can_create_attribute(get_auth_client):
    staff = CustomUserFactory(staff=True, password="StrongPass9!x", is_staff=True)

    list_attributes_url = reverse("attribute-list", kwargs={"version": "v1"})

    client = get_auth_client(staff, password="StrongPass9!x")

    data = {
        "data_type": "BOOLEAN",
        "name": "برگزاری جلسه",
    }

    response = client.post(list_attributes_url, data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["data_type"] == "BOOLEAN"
    assert response.data["name"] == "برگزاری جلسه"


@pytest.mark.django_db
def test_guest_cannot_list_event_attribute_values(api_client):
    list_eventattributevalue_url = reverse(
        "eventattributevalue-list", kwargs={"version": "v1"}
    )
    response = api_client.get(list_eventattributevalue_url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["detail"].code == "not_authenticated"


@pytest.mark.django_db
def test_organizer_can_list_own_draft_event_attribute_values(get_auth_client):
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    event = EventFactory(organizer=organizer)
    event_attribute = EventAttributeValueFactory(event=event)

    list_eventattributevalue_url = reverse(
        "eventattributevalue-list", kwargs={"version": "v1"}
    )

    client = get_auth_client(organizer, password="StrongPass9!x")

    response = client.get(list_eventattributevalue_url)

    assert response.status_code == status.HTTP_200_OK
    assert any(item["id"] == event_attribute.id for item in response.data)
    assert response.data[0]["event"] == event.id


@pytest.mark.django_db
def test_organizer_cannot_list_other_draft_event_attribute_values(get_auth_client):
    organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    other_organizer = CustomUserFactory(organizer=True, password="StrongPass9!x")
    event = EventFactory(organizer=other_organizer)
    event_attribute = EventAttributeValueFactory(event=event)

    list_eventattributevalue_url = reverse(
        "eventattributevalue-list", kwargs={"version": "v1"}
    )

    client = get_auth_client(organizer, password="StrongPass9!x")

    response = client.get(list_eventattributevalue_url)

    assert response.status_code == status.HTTP_200_OK
    assert all(item["id"] != event_attribute.id for item in response.data)


@pytest.mark.django_db
def test_participant_can_list_published_event_attribute_values(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory(published=True)
    event_attribute = EventAttributeValueFactory(event=event)

    list_eventattributevalue_url = reverse(
        "eventattributevalue-list", kwargs={"version": "v1"}
    )

    client = get_auth_client(participant, password="StrongPass9!x")

    response = client.get(list_eventattributevalue_url)

    assert response.status_code == status.HTTP_200_OK
    assert any(item["id"] == event_attribute.id for item in response.data)


@pytest.mark.django_db
def test_participant_cannot_list_draft_event_attribute_values(get_auth_client):
    participant = CustomUserFactory(participant=True, password="StrongPass9!x")
    event = EventFactory()
    event_attribute = EventAttributeValueFactory(event=event)

    list_eventattributevalue_url = reverse(
        "eventattributevalue-list", kwargs={"version": "v1"}
    )

    client = get_auth_client(participant, password="StrongPass9!x")

    response = client.get(list_eventattributevalue_url)

    assert response.status_code == status.HTTP_200_OK
    assert all(item["id"] != event_attribute.id for item in response.data)
