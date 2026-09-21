import pytest
from django.urls import reverse
from rest_framework import status

from user.factories import CustomUserFactory
from attribute.factories import AttributeFactory


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
