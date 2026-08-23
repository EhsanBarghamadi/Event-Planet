import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def get_auth_client():
    def auth_client(user, password):
        login_url = reverse("token_obtain_pair", kwargs={"version": "v1"})
        user_data = {"phone": user.phone, "password": password}

        api_client = APIClient()
        response_login = api_client.post(login_url, data=user_data)

        assert response_login.status_code == status.HTTP_200_OK

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {response_login.data['access']}")

        return api_client
    return auth_client
