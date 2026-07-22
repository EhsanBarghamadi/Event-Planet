from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserRegisterView,
    UserSessionLoginView,
    MyTokenObtainPairView,
    UserSessionLogoutView,
    LogoutView,
)

urlpatterns = [
    # Session Auth Endpoints
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserSessionLoginView.as_view(), name='login'),
    path('logout/', UserSessionLogoutView.as_view(), name='logout'),

    # JWT Token Endpoints
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/logout/', LogoutView.as_view(), name='auth_logout'),
]

