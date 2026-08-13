import pytest
from django.urls import reverse
from rest_framework import status

from user.models import CustomUser
from user.factories import CustomUserFactory


@pytest.mark.django_db
def test_register_user_success(api_client):
    register_url = reverse("register", kwargs={"version": "v1"})
    user_data = {
        "phone": "09000000000",
        "first_name": "Test1",
        "last_name": "Testi1",
        "password": "StrongPass9!x",
        "role": CustomUser.Roles.ORGANIZER,
    }
    response = api_client.post(register_url, data=user_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert CustomUser.objects.filter(phone=user_data["phone"]).exists()
    user = CustomUser.objects.get(phone=user_data["phone"])
    assert user.check_password(user_data["password"])


@pytest.mark.django_db
def test_register_user_with_staff_role(api_client):
    register_url = reverse("register", kwargs={"version": "v1"})
    user_data = {
        "phone": "09000000001",
        "first_name": "Test2",
        "last_name": "Testi2",
        "password": "StrongPass9!x",
        "role": CustomUser.Roles.STAFF,
    }
    response = api_client.post(register_url, data=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_user_with_invalid_role(api_client):
    register_url = reverse("register", kwargs={"version": "v1"})
    user_data = {
        "phone": "09000000002",
        "first_name": "Test3",
        "last_name": "Testi3",
        "password": "StrongPass9!x",
        "role": "ADMIN",
    }
    response = api_client.post(register_url, data=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_user_with_invalid_phone(api_client):
    register_url = reverse("register", kwargs={"version": "v1"})
    user_data = {
        "phone": "1234567890",
        "first_name": "Test4",
        "last_name": "Testi4",
        "password": "StrongPass9!x",
        "role": CustomUser.Roles.ORGANIZER,
    }
    response = api_client.post(register_url, data=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "phone" in response.data

@pytest.mark.django_db
def test_register_user_with_invalid_password(api_client):
    register_url = reverse("register", kwargs={"version": "v1"})
    user_data = {
        "phone": "09000000003",
        "first_name": "Test5",
        "last_name": "Testi5",
        "password": "123456",
        "role": CustomUser.Roles.ORGANIZER,
    }
    response = api_client.post(register_url, data=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password" in response.data

@pytest.mark.django_db
def test_register_user_with_repetitive_phone(api_client):
    user = CustomUserFactory()
    register_url = reverse("register", kwargs={"version": "v1"})
    user_data = {
        "phone": user.phone,
        "first_name": "Test6",
        "last_name": "Testi6",
        "password": "StrongPass9!x",
        "role": CustomUser.Roles.ORGANIZER,
    }
    response = api_client.post(register_url, data=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "phone" in response.data



