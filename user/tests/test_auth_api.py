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


@pytest.mark.django_db
def test_login_user_with_jwt_success(api_client):
    user = CustomUserFactory(phone="09000000000", password="StrongPass9!x")
    login_url = reverse("token_obtain_pair", kwargs={"version": "v1"})
    user_data = {"phone": user.phone, "password": "StrongPass9!x"}

    response = api_client.post(login_url, data=user_data)

    assert response.status_code == status.HTTP_200_OK
    assert "refresh" in response.data
    assert "access" in response.data
    assert "first_name" in response.data
    assert "role" in response.data
    assert "phone" in response.data
    assert response.data["first_name"] == user.first_name
    assert response.data["role"] == user.role
    assert response.data["phone"] == user.phone


@pytest.mark.django_db
def test_login_user_jwt_with_wrong_password(api_client):
    user = CustomUserFactory(phone="09000000000", password="StrongPass9!x")
    login_url = reverse("token_obtain_pair", kwargs={"version": "v1"})
    user_data = {"phone": user.phone, "password": "wrong_password"}

    response = api_client.post(login_url, data=user_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_refresh_jwt_token_success(api_client):
    user = CustomUserFactory(phone="09000000000", password="StrongPass9!x")
    login_url = reverse("token_obtain_pair", kwargs={"version": "v1"})
    refresh_url = reverse("token_refresh", kwargs={"version": "v1"})
    user_data = {"phone": user.phone, "password": "StrongPass9!x"}

    response_login = api_client.post(login_url, data=user_data)

    assert response_login.status_code == status.HTTP_200_OK

    data = {"refresh": response_login.data["refresh"]}
    response_refresh = api_client.post(refresh_url, data=data)

    assert response_refresh.status_code == status.HTTP_200_OK
    assert "access" in response_refresh.data


@pytest.mark.django_db
def test_logout_jwt_token_success(api_client):
    user = CustomUserFactory(phone="09000000000", password="StrongPass9!x")
    login_url = reverse("token_obtain_pair", kwargs={"version": "v1"})
    user_data = {"phone": user.phone, "password": "StrongPass9!x"}

    response_login = api_client.post(login_url, data=user_data)

    assert response_login.status_code == status.HTTP_200_OK
    assert "access" in response_login.data
    assert "refresh" in response_login.data

    data = {"refresh": response_login.data["refresh"]}
    logout_url = reverse("auth_logout", kwargs={"version": "v1"})

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {response_login.data['access']}")
    response_logout = api_client.post(logout_url, data=data)

    assert response_logout.status_code == status.HTTP_205_RESET_CONTENT


@pytest.mark.django_db
def test_refresh_token_is_blacklisted_after_logout(api_client):
    user = CustomUserFactory(phone="09000000000", password="StrongPass9!x")
    login_url = reverse("token_obtain_pair", kwargs={"version": "v1"})
    user_data = {"phone": user.phone, "password": "StrongPass9!x"}

    response_login = api_client.post(login_url, data=user_data)

    assert response_login.status_code == status.HTTP_200_OK
    assert "access" in response_login.data
    assert "refresh" in response_login.data

    data = {"refresh": response_login.data["refresh"]}
    logout_url = reverse("auth_logout", kwargs={"version": "v1"})

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {response_login.data['access']}")
    response_logout = api_client.post(logout_url, data=data)

    assert response_logout.status_code == status.HTTP_205_RESET_CONTENT

    refresh_url = reverse("token_refresh", kwargs={"version": "v1"})
    response_refresh = api_client.post(refresh_url, data=data)
    api_client.credentials()
    assert response_refresh.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_logout_jwt_token_without_refresh_token(api_client):
    user = CustomUserFactory(phone="09000000000", password="StrongPass9!x")
    login_url = reverse("token_obtain_pair", kwargs={"version": "v1"})
    user_data = {"phone": user.phone, "password": "StrongPass9!x"}

    response_login = api_client.post(login_url, data=user_data)

    assert response_login.status_code == status.HTTP_200_OK
    assert "access" in response_login.data
    assert "refresh" in response_login.data

    logout_url = reverse("auth_logout", kwargs={"version": "v1"})

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {response_login.data['access']}")
    response_logout = api_client.post(logout_url, data={})

    assert response_logout.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_logout_jwt_token_without_authorization(api_client):
    user = CustomUserFactory(phone="09000000000", password="StrongPass9!x")
    login_url = reverse("token_obtain_pair", kwargs={"version": "v1"})
    user_data = {"phone": user.phone, "password": "StrongPass9!x"}

    response_login = api_client.post(login_url, data=user_data)

    assert response_login.status_code == status.HTTP_200_OK
    assert "access" in response_login.data
    assert "refresh" in response_login.data

    data = {"refresh": response_login.data["refresh"]}
    logout_url = reverse("auth_logout", kwargs={"version": "v1"})

    response_logout = api_client.post(logout_url, data=data)

    assert response_logout.status_code == status.HTTP_401_UNAUTHORIZED
