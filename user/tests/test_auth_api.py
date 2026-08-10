import pytest
from django.urls import reverse
from rest_framework import status

from user.models import CustomUser


@pytest.mark.django_db
def test_register_user_success(api_client):
    register_url = reverse("register", kwargs={"version": "v1"})
    user_data = {
        "phone": "09000000000",
        "first_name": "Test",
        "last_name": "Testi",
        "password": "StrongPass9!x",
        "role": CustomUser.Roles.ORGANIZER,
    }
    response = api_client.post(register_url, data=user_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert CustomUser.objects.filter(phone=user_data["phone"]).exists()
    user = CustomUser.objects.get(phone=user_data["phone"])
    assert user.check_password(user_data["password"])
